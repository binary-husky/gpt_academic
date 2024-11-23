import asyncio
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock as ThreadLock
from typing import Generator
from typing import List, Dict, Optional

from crazy_functions.crazy_utils import input_clipping
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.rag_fns.arxiv_fns.arxiv_splitter import ArxivSplitter, save_fragments_to_file
from crazy_functions.rag_fns.arxiv_fns.section_fragment import SectionFragment as Fragment
from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker
from toolbox import CatchException, update_ui, get_log_folder, update_ui_lastest_msg

# 全局常量配置
MAX_HISTORY_ROUND = 5  # 最大历史对话轮数
MAX_CONTEXT_TOKEN_LIMIT = 4096  # 上下文最大token数
REMEMBER_PREVIEW = 1000  # 记忆预览长度
VECTOR_STORE_TYPE = "Simple"  # 向量存储类型：Simple或Milvus
MAX_CONCURRENT_PAPERS = 5  # 最大并行处理论文数
MAX_WORKERS = 3  # 最大工作线程数

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingTask:
    """论文处理任务数据类"""
    arxiv_id: str
    status: str = "pending"  # pending, processing, completed, failed
    error: Optional[str] = None
    fragments: List[Fragment] = None
    start_time: float = field(default_factory=time.time)


class ArxivRagWorker:
    def __init__(self, user_name: str, llm_kwargs: Dict, arxiv_id: str = None):
        """初始化ArxivRagWorker"""
        self.user_name = user_name
        self.llm_kwargs = llm_kwargs
        self.arxiv_id = self._normalize_arxiv_id(arxiv_id) if arxiv_id else None


        # 初始化基础目录
        self.base_dir = Path(get_log_folder(user_name, plugin_name='rag_cache'))
        self._setup_directories()

        # 初始化处理状态

        # 线程安全的计数器和集合
        self._processing_lock = ThreadLock()
        self._processed_fragments = set()
        self._processed_count = 0

        # 优化的线程池配置
        cpu_count = os.cpu_count() or 1
        self.thread_pool = ThreadPoolExecutor(
            max_workers=min(32, cpu_count * 4),
            thread_name_prefix="arxiv_worker"
        )

        # 批处理配置
        self._batch_size = min(20, cpu_count * 2)  # 动态设置批大小
        self.max_concurrent_papers = MAX_CONCURRENT_PAPERS
        self._semaphore = None
        self._loop = None

        # 初始化处理队列
        self.processing_queue = {}

        # 初始化工作组件
        self._init_workers()

    def _setup_directories(self):
        """设置工作目录"""

        if self.arxiv_id:
            self.checkpoint_dir = self.base_dir / self.arxiv_id
            self.vector_store_dir = self.checkpoint_dir / "vector_store"
            self.fragment_store_dir = self.checkpoint_dir / "fragments"
        else:
            self.checkpoint_dir = self.base_dir
            self.vector_store_dir = self.base_dir / "vector_store"
            self.fragment_store_dir = self.base_dir / "fragments"

        self.paper_path = self.checkpoint_dir / f"{self.arxiv_id}.processed"
        self.loading = self.paper_path.exists()
        # 创建必要的目录
        for directory in [self.checkpoint_dir, self.vector_store_dir, self.fragment_store_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def _init_workers(self):
        """初始化工作组件"""
        try:
            self.rag_worker = LlamaIndexRagWorker(
                user_name=self.user_name,
                llm_kwargs=self.llm_kwargs,
                checkpoint_dir=str(self.vector_store_dir),
                auto_load_checkpoint=True
            )

            self.arxiv_splitter = ArxivSplitter(
                root_dir=str(self.checkpoint_dir / "arxiv_cache")
            )
        except Exception as e:
            logger.error(f"Error initializing workers: {str(e)}")
            raise

    def _ensure_loop(self):
        """确保存在事件循环"""
        if threading.current_thread() is threading.main_thread():
            if self._loop is None:
                self._loop = asyncio.get_event_loop()
        else:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    @property
    def semaphore(self):
        """延迟创建semaphore"""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent_papers)
        return self._semaphore

    async def _process_fragments(self, fragments: List[Fragment]) -> None:
        """优化的并行处理论文片段"""
        if not fragments:
            logger.warning("No fragments to process")
            return

        start_time = time.time()
        total_fragments = len(fragments)

        try:
            # 1. 处理论文概述
            overview = self._create_overview(fragments[0])
            overview_success = self._safe_add_to_vector_store_sync(overview['text'])
            if not overview_success:
                raise RuntimeError("Failed to add overview to vector store")

            # 2. 并行处理片段
            successful_fragments = await self._parallel_process_fragments(fragments)

            # 3. 保存处理结果
            if successful_fragments > 0:
                await self._save_results(fragments, overview['arxiv_id'], successful_fragments)

        except Exception as e:
            logger.error(f"Error in fragment processing: {str(e)}")
            raise
        finally:
            self._log_processing_stats(start_time, total_fragments)

    def _create_overview(self, first_fragment: Fragment) -> Dict:
        """创建论文概述"""
        return {
            'arxiv_id': first_fragment.arxiv_id,
            'text': (
                f"Paper Title: {first_fragment.title}\n"
                f"ArXiv ID: {first_fragment.arxiv_id}\n"
                f"Abstract: {first_fragment.abstract}\n"
                f"Section Tree:{first_fragment.section_tree}\n"
                f"Type: OVERVIEW"
            )
        }

    async def _parallel_process_fragments(self, fragments: List[Fragment]) -> int:
        """并行处理所有片段"""
        successful_count = 0
        loop = self._ensure_loop()

        for i in range(0, len(fragments), self._batch_size):
            batch = fragments[i:i + self._batch_size]
            batch_futures = []

            for j, fragment in enumerate(batch):
                if not self._is_fragment_processed(fragment, i + j):
                    future = loop.run_in_executor(
                        self.thread_pool,
                        self._process_single_fragment_sync,
                        fragment,
                        i + j
                    )
                    batch_futures.append(future)

            if batch_futures:
                results = await asyncio.gather(*batch_futures, return_exceptions=True)
                successful_count += sum(1 for r in results if isinstance(r, bool) and r)

        return successful_count

    def _is_fragment_processed(self, fragment: Fragment, index: int) -> bool:
        """检查片段是否已处理"""
        fragment_id = f"{fragment.arxiv_id}_{index}"
        with self._processing_lock:
            return fragment_id in self._processed_fragments

    def _safe_add_to_vector_store_sync(self, text: str) -> bool:
        """线程安全的向量存储添加"""
        with self._processing_lock:
            try:
                self.rag_worker.add_text_to_vector_store(text)
                return True
            except Exception as e:
                logger.error(f"Error adding to vector store: {str(e)}")
                return False

    def _process_single_fragment_sync(self, fragment: Fragment, index: int) -> bool:
        """处理单个片段"""
        fragment_id = f"{fragment.arxiv_id}_{index}"
        try:
            text = self._build_fragment_text(fragment)
            if self._safe_add_to_vector_store_sync(text):
                with self._processing_lock:
                    self._processed_fragments.add(fragment_id)
                    self._processed_count += 1
                logger.info(f"Successfully processed fragment {index}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing fragment {index}: {str(e)}")
            return False

    def _build_fragment_text(self, fragment: Fragment) -> str:
        """构建片段文本"""
        return "".join([
            f"Paper Title: {fragment.title}\n",
            f"Section: {fragment.current_section}\n",
            f"Content: {fragment.content}\n",
            f"Bibliography: {fragment.bibliography}\n",
            "Type: FRAGMENT"
        ])

    async def _save_results(self, fragments: List[Fragment], arxiv_id: str, successful_count: int) -> None:
        """保存处理结果"""
        if successful_count > 0:
            loop = self._ensure_loop()
            await loop.run_in_executor(
                self.thread_pool,
                save_fragments_to_file,
                fragments,
                str(self.fragment_store_dir / f"{arxiv_id}_fragments.json")
            )

    def _log_processing_stats(self, start_time: float, total_fragments: int) -> None:
        """记录处理统计信息"""
        elapsed_time = time.time() - start_time
        processing_rate = total_fragments / elapsed_time if elapsed_time > 0 else 0
        logger.info(
            f"Processed {self._processed_count}/{total_fragments} fragments "
            f"in {elapsed_time:.2f}s (rate: {processing_rate:.2f} fragments/s)"
        )

    async def process_paper(self, arxiv_id: str) -> bool:
        """处理论文主函数"""
        try:
            arxiv_id = self._normalize_arxiv_id(arxiv_id)
            logger.info(f"Starting to process paper: {arxiv_id}")

            if self.paper_path.exists():
                logger.info(f"Paper {arxiv_id} already processed")
                return True

            task = self._create_processing_task(arxiv_id)

            try:
                async with self.semaphore:
                    fragments = await self.arxiv_splitter.process(arxiv_id)
                    if not fragments:
                        raise ValueError(f"No fragments extracted from paper {arxiv_id}")

                    logger.info(f"Extracted {len(fragments)} fragments from paper {arxiv_id}")
                    await self._process_fragments(fragments)

                    self._complete_task(task, fragments, self.paper_path)
                    return True

            except Exception as e:
                self._fail_task(task, str(e))
                raise

        except Exception as e:
            logger.error(f"Error processing paper {arxiv_id}: {str(e)}")
            return False

    def _create_processing_task(self, arxiv_id: str) -> ProcessingTask:
        """创建处理任务"""
        task = ProcessingTask(arxiv_id=arxiv_id)
        with self._processing_lock:
            self.processing_queue[arxiv_id] = task
            task.status = "processing"
        return task

    def _complete_task(self, task: ProcessingTask, fragments: List[Fragment], paper_path: Path) -> None:
        """完成任务处理"""
        with self._processing_lock:
            task.status = "completed"
            task.fragments = fragments
        paper_path.touch()
        logger.info(f"Paper {task.arxiv_id} processed successfully with {self._processed_count} fragments")

    def _fail_task(self, task: ProcessingTask, error: str) -> None:
        """任务失败处理"""
        with self._processing_lock:
            task.status = "failed"
            task.error = error

    def _normalize_arxiv_id(self, input_str: str) -> str:
        """规范化ArXiv ID"""
        if not input_str:
            return ""

        input_str = input_str.strip().lower()
        if 'arxiv.org/' in input_str:
            if '/pdf/' in input_str:
                arxiv_id = input_str.split('/pdf/')[-1]
            else:
                arxiv_id = input_str.split('/abs/')[-1]
            return arxiv_id.split('v')[0].strip()
        return input_str.split('v')[0].strip()

    async def wait_for_paper(self, arxiv_id: str, timeout: float = 300.0) -> bool:
        """等待论文处理完成"""
        start_time = time.time()
        try:
            while True:
                with self._processing_lock:
                    task = self.processing_queue.get(arxiv_id)
                if not task:
                    return False

                if task.status == "completed":
                    return True
                if task.status == "failed":
                    return False

                if time.time() - start_time > timeout:
                    logger.error(f"Processing paper {arxiv_id} timed out")
                    return False

                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error waiting for paper {arxiv_id}: {str(e)}")
            return False

    def retrieve_and_generate(self, query: str) -> str:
        """检索相关内容并生成提示词"""
        try:
            nodes = self.rag_worker.retrieve_from_store_with_query(query)
            return self.rag_worker.build_prompt(query=query, nodes=nodes)
        except Exception as e:
            logger.error(f"Error in retrieve and generate: {str(e)}")
            return ""

    def remember_qa(self, question: str, answer: str) -> None:
        """记忆问答对"""
        try:
            self.rag_worker.remember_qa(question, answer)
        except Exception as e:
            logger.error(f"Error remembering QA: {str(e)}")

    async def auto_analyze_paper(self, chatbot: List, history: List, system_prompt: str) -> None:
        """自动分析论文的关键问题"""
        key_questions = [
            "What is the main research question or problem addressed in this paper?",
            "What methods or approaches did the authors use to investigate the problem?",
            "What are the key findings or results presented in the paper?",
            "How do the findings of this paper contribute to the broader field or topic of study?",
            "What are the limitations of this study, and what future research directions do the authors suggest?"
        ]

        results = []
        for question in key_questions:
            try:
                prompt = self.retrieve_and_generate(question)
                if prompt:
                    response = await request_gpt_model_in_new_thread_with_ui_alive(
                        inputs=prompt,
                        inputs_show_user=question,
                        llm_kwargs=self.llm_kwargs,
                        chatbot=chatbot,
                        history=history,
                        sys_prompt=system_prompt
                    )
                    results.append(f"Q: {question}\nA: {response}\n")
                    self.remember_qa(question, response)
            except Exception as e:
                logger.error(f"Error in auto analysis: {str(e)}")

        # 合并所有结果
        summary = "\n\n".join(results)
        chatbot[-1] = (chatbot[-1][0], f"论文已成功加载并完成初步分析：\n\n{summary}\n\n您现在可以继续提问更多细节。")

@CatchException
def Arxiv论文对话(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
                  history: List, system_prompt: str, web_port: str) -> Generator:
    """
    Arxiv论文对话主函数
    Args:
        txt: arxiv ID/URL
        llm_kwargs: LLM配置参数
        plugin_kwargs: 插件配置参数，包含 advanced_arg 字段作为用户询问指令
        chatbot: 对话历史
        history: 聊天历史
        system_prompt: 系统提示词
        web_port: Web端口
    """
    # 初始化时，提示用户需要 arxiv ID/URL
    if len(history) == 0 and not txt.lower().strip().startswith(('https://arxiv.org', 'arxiv.org', '0', '1', '2')):
        chatbot.append((txt, "请先提供Arxiv论文链接或ID。"))
        yield from update_ui(chatbot=chatbot, history=history)
        return

    user_name = chatbot.get_user()
    worker = ArxivRagWorker(user_name, llm_kwargs, arxiv_id=txt)

    # 处理新论文的情况
    if txt.lower().strip().startswith(('https://arxiv.org', 'arxiv.org', '0', '1', '2')) and not worker.loading:
        chatbot.append((txt, "正在处理论文，请稍等..."))
        yield from update_ui(chatbot=chatbot, history=history)

        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 使用超时控制
            success = False
            try:
                # 设置超时时间为5分钟
                success = loop.run_until_complete(
                    asyncio.wait_for(worker.process_paper(txt), timeout=300)
                )
                if success:
                    arxiv_id = worker._normalize_arxiv_id(txt)
                    success = loop.run_until_complete(
                        asyncio.wait_for(worker.wait_for_paper(arxiv_id), timeout=60)
                    )
                    if success:
                        chatbot[-1] = (txt, "论文处理完成，您现在可以开始提问。")
                    else:
                        chatbot[-1] = (txt, "论文处理超时，请重试。")
                else:
                    chatbot[-1] = (txt, "论文处理失败，请检查论文ID是否正确或稍后重试。")
            except asyncio.TimeoutError:
                chatbot[-1] = (txt, "论文处理超时，请重试。")
                success = False
            finally:
                loop.close()

            if not success:
                yield from update_ui(chatbot=chatbot, history=history)
                return

        except Exception as e:
            logger.error(f"Error in main process: {str(e)}")
            chatbot[-1] = (txt, f"处理过程中发生错误: {str(e)}")
            yield from update_ui(chatbot=chatbot, history=history)
            return

        yield from update_ui(chatbot=chatbot, history=history)
        return
    # 处理用户询问的情况
    # 获取用户询问指令
    user_query = plugin_kwargs.get("advanced_arg",
                                   "What is the main research question or problem addressed in this paper?")
    if not user_query:
        user_query = "What is the main research question or problem addressed in this paper about graph attention network?"
        # chatbot.append((txt, "请提供您的问题。"))
        # yield from update_ui(chatbot=chatbot, history=history)
        # return

    # 处理历史对话长度
    if len(history) > MAX_HISTORY_ROUND * 2:
        history = history[-(MAX_HISTORY_ROUND * 2):]

    # 处理询问指令
    query_clip, history, flags = input_clipping(
        user_query,
        history,
        max_token_limit=MAX_CONTEXT_TOKEN_LIMIT,
        return_clip_flags=True
    )

    if flags["original_input_len"] != flags["clipped_input_len"]:
        yield from update_ui_lastest_msg('检测到长输入，正在处理...', chatbot, history, delay=0)
        if len(user_query) > REMEMBER_PREVIEW:
            HALF = REMEMBER_PREVIEW // 2
            query_to_remember = user_query[
                                :HALF] + f" ...\n...(省略{len(user_query) - REMEMBER_PREVIEW}字)...\n... " + user_query[
                                                                                                             -HALF:]
        else:
            query_to_remember = query_clip
    else:
        query_to_remember = query_clip

    chatbot.append((user_query, "正在思考中..."))
    yield from update_ui(chatbot=chatbot, history=history)

    # 生成提示词
    prompt = worker.retrieve_and_generate(query_clip)
    if not prompt:
        chatbot[-1] = (user_query, "抱歉，处理您的问题时出现错误，请重试。")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 获取回答
    response = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=prompt,
        inputs_show_user=query_clip,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=history,
        sys_prompt=system_prompt
    )

    # 记忆问答对
    # worker.remember_qa(query_to_remember, response)
    history.extend([user_query, response])

    yield from update_ui(chatbot=chatbot, history=history)


if __name__ == "__main__":
    # 测试代码
    llm_kwargs = {
        'api_key': os.getenv("one_api_key"),
        'client_ip': '127.0.0.1',
        'embed_model': 'text-embedding-3-small',
        'llm_model': 'one-api-Qwen2.5-72B-Instruct',
        'max_length': 4096,
        'most_recent_uploaded': None,
        'temperature': 1,
        'top_p': 1
    }
    plugin_kwargs = {}
    chatbot = []
    history = []
    system_prompt = "You are a helpful assistant."
    web_port = "8080"

    # 测试论文导入
    arxiv_url = "https://arxiv.org/abs/2312.12345"
    for response in Arxiv论文对话(
            arxiv_url, llm_kwargs, plugin_kwargs,
            chatbot, history, system_prompt, web_port
    ):
        print(response)

    # 测试问答
    question = "这篇论文的主要贡献是什么？"
    for response in Arxiv论文对话(
            question, llm_kwargs, plugin_kwargs,
            chatbot, history, system_prompt, web_port
    ):
        print(response)
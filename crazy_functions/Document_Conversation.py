import os
import threading
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Generator
from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
from crazy_functions.rag_fns.rag_file_support import extract_text
from request_llms.bridge_all import model_info
from toolbox import update_ui, CatchException, report_exception
from shared_utils.fastapi_server import validate_path_safety


@dataclass
class FileFragment:
    """文件片段数据类，用于组织处理单元"""
    file_path: str
    content: str
    rel_path: str
    fragment_index: int
    total_fragments: int


class BatchDocumentSummarizer:
    """优化的文档总结器 - 批处理版本"""

    def __init__(self, llm_kwargs: Dict, query: str, chatbot: List, history: List, system_prompt: str):
        """初始化总结器"""
        self.llm_kwargs = llm_kwargs
        self.query = query
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.failed_files = []
        self.file_summaries_map = {}

    def _get_token_limit(self) -> int:
        """获取模型token限制"""
        max_token = model_info[self.llm_kwargs['llm_model']]['max_token']
        return max_token * 3 // 4

    def _create_batch_inputs(self, fragments: List[FileFragment]) -> Tuple[List, List, List]:
        """创建批处理输入"""
        inputs_array = []
        inputs_show_user_array = []
        history_array = []

        for frag in fragments:
            if self.query:
                i_say = (f'请按照用户要求对文件内容进行处理，文件名为{os.path.basename(frag.file_path)}，'
                         f'用户要求为：{self.query}：'
                         f'文件内容是 ```{frag.content}```')
                i_say_show_user = (f'正在处理 {frag.rel_path} (片段 {frag.fragment_index + 1}/{frag.total_fragments})')
            else:
                i_say = (f'请对下面的内容用中文做总结，不超过500字，文件名是{os.path.basename(frag.file_path)}，'
                         f'内容是 ```{frag.content}```')
                i_say_show_user = f'正在处理 {frag.rel_path} (片段 {frag.fragment_index + 1}/{frag.total_fragments})'

            inputs_array.append(i_say)
            inputs_show_user_array.append(i_say_show_user)
            history_array.append([])

        return inputs_array, inputs_show_user_array, history_array

    def _process_single_file_with_timeout(self, file_info: Tuple[str, str], mutable_status: List) -> List[FileFragment]:
        """包装了超时控制的文件处理函数"""

        def timeout_handler():
            thread = threading.current_thread()
            if hasattr(thread, '_timeout_occurred'):
                thread._timeout_occurred = True

        # 设置超时标记
        thread = threading.current_thread()
        thread._timeout_occurred = False

        # 设置超时时间为30秒，给予更多处理时间
        TIMEOUT_SECONDS = 30
        timer = threading.Timer(TIMEOUT_SECONDS, timeout_handler)
        timer.start()

        try:
            fp, project_folder = file_info
            fragments = []

            # 定期检查是否超时
            def check_timeout():
                if hasattr(thread, '_timeout_occurred') and thread._timeout_occurred:
                    raise TimeoutError(f"处理文件 {os.path.basename(fp)} 超时（{TIMEOUT_SECONDS}秒）")

            # 更新状态
            mutable_status[0] = "检查文件大小"
            mutable_status[1] = time.time()
            check_timeout()

            # 文件大小检查
            if os.path.getsize(fp) > self.max_file_size:
                self.failed_files.append((fp, f"文件过大：超过{self.max_file_size / 1024 / 1024}MB"))
                mutable_status[2] = "文件过大"
                return fragments

            # 更新状态
            mutable_status[0] = "提取文件内容"
            mutable_status[1] = time.time()

            # 提取内容 - 使用单独的超时控制
            content = None
            extract_start_time = time.time()
            try:
                while True:
                    check_timeout()  # 检查全局超时

                    # 检查提取过程是否超时（10秒）
                    if time.time() - extract_start_time > 10:
                        raise TimeoutError("文件内容提取超时（10秒）")

                    try:
                        content = extract_text(fp)
                        break
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            continue  # 如果是临时超时，重试
                        raise  # 其他错误直接抛出

            except Exception as e:
                self.failed_files.append((fp, f"文件读取失败：{str(e)}"))
                mutable_status[2] = "读取失败"
                return fragments

            if content is None:
                self.failed_files.append((fp, "文件解析失败：不支持的格式或文件损坏"))
                mutable_status[2] = "格式不支持"
                return fragments
            elif not content.strip():
                self.failed_files.append((fp, "文件内容为空"))
                mutable_status[2] = "内容为空"
                return fragments

            check_timeout()

            # 更新状态
            mutable_status[0] = "分割文本"
            mutable_status[1] = time.time()

            # 分割文本 - 添加超时检查
            split_start_time = time.time()
            try:
                while True:
                    check_timeout()  # 检查全局超时

                    # 检查分割过程是否超时（5秒）
                    if time.time() - split_start_time > 5:
                        raise TimeoutError("文本分割超时（5秒）")

                    paper_fragments = breakdown_text_to_satisfy_token_limit(
                        txt=content,
                        limit=self._get_token_limit(),
                        llm_model=self.llm_kwargs['llm_model']
                    )
                    break

            except Exception as e:
                self.failed_files.append((fp, f"文本分割失败：{str(e)}"))
                mutable_status[2] = "分割失败"
                return fragments

            # 处理片段
            rel_path = os.path.relpath(fp, project_folder)
            for i, frag in enumerate(paper_fragments):
                check_timeout()  # 每处理一个片段检查一次超时
                if frag.strip():
                    fragments.append(FileFragment(
                        file_path=fp,
                        content=frag,
                        rel_path=rel_path,
                        fragment_index=i,
                        total_fragments=len(paper_fragments)
                    ))

            mutable_status[2] = "处理完成"
            return fragments

        except TimeoutError as e:
            self.failed_files.append((fp, str(e)))
            mutable_status[2] = "处理超时"
            return []
        except Exception as e:
            self.failed_files.append((fp, f"处理失败：{str(e)}"))
            mutable_status[2] = "处理异常"
            return []
        finally:
            timer.cancel()

    def prepare_fragments(self, project_folder: str, file_paths: List[str]) -> Generator:
        import concurrent.futures

        from concurrent.futures import ThreadPoolExecutor
        from typing import Generator, List
        """并行准备所有文件的处理片段"""
        all_fragments = []
        total_files = len(file_paths)

        # 配置参数
        self.refresh_interval = 0.2  # UI刷新间隔
        self.watch_dog_patience = 5  # 看门狗超时时间
        self.max_file_size = 10 * 1024 * 1024  # 10MB限制
        self.max_workers = min(32, len(file_paths))  # 最多32个线程

        # 创建有超时控制的线程池
        executor = ThreadPoolExecutor(max_workers=self.max_workers)

        # 用于跨线程状态传递的可变列表 - 增加文件名信息
        mutable_status_array = [["等待中", time.time(), "pending", file_path] for file_path in file_paths]

        # 创建文件处理任务
        file_infos = [(fp, project_folder) for fp in file_paths]

        # 提交所有任务，使用带超时控制的处理函数
        futures = [
            executor.submit(
                self._process_single_file_with_timeout,
                file_info,
                mutable_status_array[i]
            ) for i, file_info in enumerate(file_infos)
        ]

        # 更新UI的计数器
        cnt = 0

        try:
            # 监控任务执行
            while True:
                time.sleep(self.refresh_interval)
                cnt += 1

                # 检查任务完成状态
                worker_done = [f.done() for f in futures]

                # 更新状态显示
                status_str = ""
                for i, (status, timestamp, desc, file_path) in enumerate(mutable_status_array):
                    # 获取文件名（去掉路径）
                    file_name = os.path.basename(file_path)
                    if worker_done[i]:
                        status_str += f"文件 {file_name}: {desc}\n\n"
                    else:
                        status_str += f"文件 {file_name}: {status} {desc}\n\n"

                # 更新UI
                self.chatbot[-1] = [
                    "处理进度",
                    f"正在处理文件...\n\n{status_str}" + "." * (cnt % 10 + 1)
                ]
                yield from update_ui(chatbot=self.chatbot, history=self.history)

                # 检查是否所有任务完成
                if all(worker_done):
                    break

        finally:
            # 确保线程池正确关闭
            executor.shutdown(wait=False)

        # 收集结果
        processed_files = 0
        for future in futures:
            try:
                fragments = future.result(timeout=0.1)  # 给予一个短暂的超时时间来获取结果
                all_fragments.extend(fragments)
                processed_files += 1
            except concurrent.futures.TimeoutError:
                # 处理获取结果超时
                file_index = futures.index(future)
                self.failed_files.append((file_paths[file_index], "结果获取超时"))
                continue
            except Exception as e:
                # 处理其他异常
                file_index = futures.index(future)
                self.failed_files.append((file_paths[file_index], f"未知错误：{str(e)}"))
                continue

        # 最终进度更新
        self.chatbot.append([
            "文件处理完成",
            f"成功处理 {len(all_fragments)} 个片段，失败 {len(self.failed_files)} 个文件"
        ])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        return all_fragments

    def _process_fragments_batch(self, fragments: List[FileFragment]) -> Generator:
        """批量处理文件片段"""
        from collections import defaultdict
        batch_size = 64  # 每批处理的片段数
        max_retries = 3  # 最大重试次数
        retry_delay = 5  # 重试延迟（秒）
        results = defaultdict(list)

        # 按批次处理
        for i in range(0, len(fragments), batch_size):
            batch = fragments[i:i + batch_size]

            inputs_array, inputs_show_user_array, history_array = self._create_batch_inputs(batch)
            sys_prompt_array = ["请总结以下内容："] * len(batch)

            # 添加重试机制
            for retry in range(max_retries):
                try:
                    response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
                        inputs_array=inputs_array,
                        inputs_show_user_array=inputs_show_user_array,
                        llm_kwargs=self.llm_kwargs,
                        chatbot=self.chatbot,
                        history_array=history_array,
                        sys_prompt_array=sys_prompt_array,
                    )

                    # 处理响应
                    for j, frag in enumerate(batch):
                        summary = response_collection[j * 2 + 1]
                        if summary and summary.strip():
                            results[frag.rel_path].append({
                                'index': frag.fragment_index,
                                'summary': summary,
                                'total': frag.total_fragments
                            })
                    break  # 成功处理，跳出重试循环

                except Exception as e:
                    if retry == max_retries - 1:  # 最后一次重试失败
                        for frag in batch:
                            self.failed_files.append((frag.file_path, f"处理失败：{str(e)}"))
                    else:
                        yield from update_ui(self.chatbot.append([f"批次处理失败，{retry_delay}秒后重试...", str(e)]))
                        time.sleep(retry_delay)

        return results

    def _generate_final_summary_request(self) -> Tuple[List, List, List]:
        """准备最终总结请求"""
        if not self.file_summaries_map:
            return (["无可用的文件总结"], ["生成最终总结"], [[]])

        summaries = list(self.file_summaries_map.values())
        if all(not summary for summary in summaries):
            return (["所有文件处理均失败"], ["生成最终总结"], [[]])

        if self.plugin_kwargs.get("advanced_arg"):
            i_say = "根据以上所有文件的处理结果，按要求进行综合处理：" + self.plugin_kwargs['advanced_arg']
        else:
            i_say = "请根据以上所有文件的处理结果，生成最终的总结，不超过1000字。"

        return ([i_say], [i_say], [summaries])

    def process_files(self, project_folder: str, file_paths: List[str]) -> Generator:
        """处理所有文件"""
        total_files = len(file_paths)
        self.chatbot.append([f"开始处理", f"总计 {total_files} 个文件"])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 1. 准备所有文件片段
        # 在 process_files 函数中：
        fragments = yield from self.prepare_fragments(project_folder, file_paths)
        if not fragments:
            self.chatbot.append(["处理失败", "没有可处理的文件内容"])
            return "没有可处理的文件内容"

        # 2. 批量处理所有文件片段
        self.chatbot.append([f"文件分析", f"共计 {len(fragments)} 个处理单元"])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        try:
            file_summaries = yield from self._process_fragments_batch(fragments)
        except Exception as e:
            self.chatbot.append(["处理错误", f"批处理过程失败：{str(e)}"])
            return "处理过程发生错误"

        # 3. 为每个文件生成整体总结
        self.chatbot.append(["生成总结", "正在汇总文件内容..."])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 处理每个文件的总结
        for rel_path, summaries in file_summaries.items():
            if len(summaries) > 1:  # 多片段文件需要生成整体总结
                sorted_summaries = sorted(summaries, key=lambda x: x['index'])
                if self.plugin_kwargs.get("advanced_arg"):

                    i_say = f'请按照用户要求对文件内容进行处理，用户要求为：{self.plugin_kwargs["advanced_arg"]}：'
                else:
                    i_say = f"请总结文件 {os.path.basename(rel_path)} 的主要内容，不超过500字。"

                try:
                    summary_texts = [s['summary'] for s in sorted_summaries]
                    response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
                        inputs_array=[i_say],
                        inputs_show_user_array=[f"生成 {rel_path} 的处理结果"],
                        llm_kwargs=self.llm_kwargs,
                        chatbot=self.chatbot,
                        history_array=[summary_texts],
                        sys_prompt_array=["你是一个优秀的助手，"],
                    )
                    self.file_summaries_map[rel_path] = response_collection[1]
                except Exception as e:
                    self.chatbot.append(["警告", f"文件 {rel_path} 总结生成失败：{str(e)}"])
                    self.file_summaries_map[rel_path] = "总结生成失败"
            else:  # 单片段文件直接使用其唯一的总结
                self.file_summaries_map[rel_path] = summaries[0]['summary']

        # 4. 生成最终总结
        if total_files == 1:
            return "文件数为1，此时不调用总结模块"
        else:
            try:
                # 收集所有文件的总结用于生成最终总结
                file_summaries_for_final = []
                for rel_path, summary in self.file_summaries_map.items():
                    file_summaries_for_final.append(f"文件 {rel_path} 的总结：\n{summary}")

                if self.plugin_kwargs.get("advanced_arg"):
                    final_summary_prompt = ("根据以下所有文件的总结内容，按要求进行综合处理：" +
                                            self.plugin_kwargs['advanced_arg'])
                else:
                    final_summary_prompt = "请根据以下所有文件的总结内容，生成最终的总结报告。"

                response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
                    inputs_array=[final_summary_prompt],
                    inputs_show_user_array=["生成最终总结报告"],
                    llm_kwargs=self.llm_kwargs,
                    chatbot=self.chatbot,
                    history_array=[file_summaries_for_final],
                    sys_prompt_array=["总结所有文件内容。"],
                    max_workers=1
                )

                return response_collection[1] if len(response_collection) > 1 else "生成总结失败"
            except Exception as e:
                self.chatbot.append(["错误", f"最终总结生成失败：{str(e)}"])
                return "生成总结失败"

    def save_results(self, final_summary: str):
        """保存结果到文件"""
        from toolbox import promote_file_to_downloadzone, write_history_to_file
        from crazy_functions.doc_fns.batch_file_query_doc import MarkdownFormatter, HtmlFormatter, WordFormatter
        import os
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 创建各种格式化器
        md_formatter = MarkdownFormatter(final_summary, self.file_summaries_map, self.failed_files)
        html_formatter = HtmlFormatter(final_summary, self.file_summaries_map, self.failed_files)
        word_formatter = WordFormatter(final_summary, self.file_summaries_map, self.failed_files)

        result_files = []

        # 保存 Markdown
        try:
            md_content = md_formatter.create_document()
            result_file_md = write_history_to_file(
                history=[md_content],  # 直接传入内容列表
                file_basename=f"文档总结_{timestamp}.md"
            )
            result_files.append(result_file_md)
        except:
            pass

        # 保存 HTML
        try:
            html_content = html_formatter.create_document()
            result_file_html = write_history_to_file(
                history=[html_content],
                file_basename=f"文档总结_{timestamp}.html"
            )
            result_files.append(result_file_html)
        except:
            pass

        # 保存 Word
        try:
            doc = word_formatter.create_document()
            # 由于 Word 文档需要用 doc.save()，我们使用与 md 文件相同的目录
            result_file_docx = os.path.join(
                os.path.dirname(result_file_md),
                f"文档总结_{timestamp}.docx"
            )
            doc.save(result_file_docx)
            result_files.append(result_file_docx)
        except:
            pass

        # 添加到下载区
        for file in result_files:
            promote_file_to_downloadzone(file, chatbot=self.chatbot)

        self.chatbot.append(["处理完成", f"结果已保存至: {', '.join(result_files)}"])


@CatchException
def 批量文件询问(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
                 history: List, system_prompt: str, user_request: str):
    """主函数 - 优化版本"""
    # 初始化
    import glob
    import re
    from crazy_functions.rag_fns.rag_file_support import supports_format
    from toolbox import report_exception
    query = plugin_kwargs.get("advanced_arg")
    summarizer = BatchDocumentSummarizer(llm_kwargs, query, chatbot, history, system_prompt)
    chatbot.append(["函数插件功能", f"作者：lbykkkk，批量总结文件。支持格式: {', '.join(supports_format)}等其他文本格式文件，如果长时间卡在文件处理过程，请查看处理进度，然后删除所有处于“pending”状态的文件，然后重新上传处理。"])
    yield from update_ui(chatbot=chatbot, history=history)

    # 验证输入路径
    if not os.path.exists(txt):
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 获取文件列表
    project_folder = txt
    user_name = chatbot.get_user()
    validate_path_safety(project_folder, user_name)
    extract_folder = next((d for d in glob.glob(f'{project_folder}/*')
                           if os.path.isdir(d) and d.endswith('.extract')), project_folder)
    exclude_patterns = r'/[^/]+\.(zip|rar|7z|tar|gz)$'
    file_manifest = [f for f in glob.glob(f'{extract_folder}/**', recursive=True)
                     if os.path.isfile(f) and not re.search(exclude_patterns, f)]

    if not file_manifest:
        report_exception(chatbot, history, a=f"解析项目: {txt}", b="未找到支持的文件类型")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 处理所有文件并生成总结
    final_summary = yield from summarizer.process_files(project_folder, file_manifest)
    yield from update_ui(chatbot=chatbot, history=history)

    # 保存结果
    summarizer.save_results(final_summary)
    yield from update_ui(chatbot=chatbot, history=history)

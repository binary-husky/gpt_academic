import os
import time
import glob
import re
import threading
from typing import Dict, List, Generator, Tuple
from dataclasses import dataclass

from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
from crazy_functions.rag_fns.rag_file_support import extract_text,  convert_to_markdown
from request_llms.bridge_all import model_info
from toolbox import update_ui, CatchException, report_exception, promote_file_to_downloadzone, write_history_to_file
from shared_utils.fastapi_server import validate_path_safety

# 新增：导入结构化论文提取器
from crazy_functions.doc_fns.read_fns.unstructured_all.paper_structure_extractor import PaperStructureExtractor, ExtractorConfig, StructuredPaper

# 导入格式化器
from crazy_functions.paper_fns.file2file_doc import (
    TxtFormatter,
    MarkdownFormatter,
    HtmlFormatter,
    WordFormatter
)

@dataclass
class TextFragment:
    """文本片段数据类，用于组织处理单元"""
    content: str
    fragment_index: int
    total_fragments: int


class DocumentProcessor:
    """文档处理器 - 处理单个文档并输出结果"""

    def __init__(self, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List, history: List, system_prompt: str):
        """初始化处理器"""
        self.llm_kwargs = llm_kwargs.copy()  # 创建原始llm_kwargs的副本
        # 固定使用deepseek-reasoner模型
        self.llm_kwargs['llm_model'] = "deepseek-reasoner"
        self.plugin_kwargs = plugin_kwargs
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.processed_results = []
        self.failed_fragments = []
        # 新增：初始化论文结构提取器
        self.paper_extractor = PaperStructureExtractor()
        # 修改：设置降重次数，默认为1次（原为3次）
        self.reduction_times = int(self.plugin_kwargs.get("reduction_times", 1))

    def _get_token_limit(self) -> int:
        """获取模型token限制，返回更小的值以确保更细粒度的分割"""
        max_token = model_info[self.llm_kwargs['llm_model']]['max_token']
        # 降低token限制，使每个片段更小
        return max_token // 4  # 从3/4降低到1/4

    def _create_batch_inputs(self, fragments: List[TextFragment], current_iteration: int = 1) -> Tuple[List, List, List]:
        """创建批处理输入"""
        inputs_array = []
        inputs_show_user_array = []
        history_array = []

        # 基础指令 - 增强单次调用的效果
        user_instruction = self.plugin_kwargs.get("advanced_arg", """你是一个人类科研工作者，请对以下学术文本进行深度改写，以彻底消除AI生成特征。具体要求如下：

1. 保持学术写作的严谨性和专业性，但加入一些人类写作的不完美元素
2. 维持原文的核心论述和逻辑框架，但打破过于完美的结构
3. 彻底改变句式结构：
   - 灵活运用主动句与被动句，偏好使用主动语态
   - 适当使用不同长度的句子，包括一些较长的复杂句
   - 引入变化多样的句式，打破规律性
   - 完全避免AI常用的模板化句式和套路表达
   - 增加一些学术写作中常见的转折和连接方式
4. 全面改善用词：
   - 使用更多学术语境下的专业词汇和同义词替换
   - 避免过于机械和规律性的连接词，使用更自然的过渡
   - 重构专业术语的表达方式，但保持准确性
   - 增加词汇多样性，减少重复用词
   - 偶尔使用一些不太常见但恰当的词汇
5. 模拟真实学者的写作风格：
   - 注重论证的严密性，但允许存在一些微小的不对称性
   - 保持表达的客观性，同时适度体现个人学术见解
   - 在适当位置表达观点时更加自信和坚定
   - 避免过于完美和机械均衡的论述结构
   - 允许段落长度有所变化，不要过于均匀
6. 引入人类学者常见的写作特点：
   - 段落之间的过渡更加自然流畅
   - 适当使用一些学术界常见的修辞手法，但不过度使用
   - 偶尔使用一些强调和限定性表达
   - 适当使用一些学术界认可的个人化表达
7. 彻底消除AI痕迹：
   - 避免过于规整和均衡的段落结构
   - 避免机械性的句式变化和词汇替换模式
   - 避免过于完美的逻辑推导，适当增加一些转折
   - 减少公式化的表达方式""")

        # 对于单次调用的场景，不需要迭代前缀，直接使用更强力的改写指令
        for frag in fragments:
            # 在单次调用时使用更强力的指令
            if self.reduction_times == 1:
                i_say = (f'请对以下学术文本进行彻底改写，完全消除AI特征，使其像真实人类学者撰写的内容。\n\n{user_instruction}\n\n'
                         f'请记住以下几点：\n'
                         f'1. 避免过于规整和均衡的结构\n'
                         f'2. 引入一些人类写作的微小不完美之处\n'
                         f'3. 使用多样化的句式和词汇\n'
                         f'4. 打破可能的AI规律性表达模式\n'
                         f'5. 适当使用一些专业领域内的表达习惯\n\n'
                         f'请将对文本的处理结果放在<decision>和</decision>标签之间。\n\n'
                         f'文本内容：\n```\n{frag.content}\n```')
            else:
                # 原有的迭代前缀逻辑
                iteration_prefix = ""
                if current_iteration > 1:
                    iteration_prefix = f"这是第{current_iteration}次改写，请在保持学术性的基础上，采用更加人性化、不同的表达方式。"
                    if current_iteration == 2:
                        iteration_prefix += "在保持专业性的同时，进一步优化句式结构和用词，显著降低AI痕迹。"
                    elif current_iteration >= 3:
                        iteration_prefix += "请在确保不损失任何学术内容的前提下，彻底重构表达方式，并适当引入少量人类学者常用的表达技巧，避免过度使用比喻和类比。"

                i_say = (f'请按照以下要求处理文本内容：{iteration_prefix}{user_instruction}\n\n'
                         f'请将对文本的处理结果放在<decision>和</decision>标签之间。\n\n'
                         f'文本内容：\n```\n{frag.content}\n```')

            i_say_show_user = f'正在处理文本片段 {frag.fragment_index + 1}/{frag.total_fragments}'

            inputs_array.append(i_say)
            inputs_show_user_array.append(i_say_show_user)
            history_array.append([])

        return inputs_array, inputs_show_user_array, history_array

    def _extract_decision(self, text: str) -> str:
        """从LLM响应中提取<decision>标签内的内容"""
        import re
        pattern = r'<decision>(.*?)</decision>'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()
        else:
            # 如果没有找到标签，返回原始文本
            return text.strip()

    def process_file(self, file_path: str) -> Generator:
        """处理单个文件"""
        self.chatbot.append(["开始处理文件", f"文件路径: {file_path}"])
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        try:
            # 首先尝试转换为Markdown
            file_path = convert_to_markdown(file_path)

            # 1. 检查文件是否为支持的论文格式
            is_paper_format = any(file_path.lower().endswith(ext) for ext in self.paper_extractor.SUPPORTED_EXTENSIONS)

            if is_paper_format:
                # 使用结构化提取器处理论文
                return (yield from self._process_structured_paper(file_path))
            else:
                # 使用原有方式处理普通文档
                return (yield from self._process_regular_file(file_path))

        except Exception as e:
            self.chatbot.append(["处理错误", f"文件处理失败: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return None

    def _process_structured_paper(self, file_path: str) -> Generator:
        """处理结构化论文文件"""
        # 1. 提取论文结构
        self.chatbot[-1] = ["正在分析论文结构", f"文件路径: {file_path}"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        try:
            paper = self.paper_extractor.extract_paper_structure(file_path)

            if not paper or not paper.sections:
                self.chatbot.append(["无法提取论文结构", "将使用全文内容进行处理"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)

                # 使用全文内容进行段落切分
                if paper and paper.full_text:
                    # 使用增强的分割函数进行更细致的分割
                    fragments = self._breakdown_section_content(paper.full_text)

                    # 创建文本片段对象
                    text_fragments = []
                    for i, frag in enumerate(fragments):
                        if frag.strip():
                            text_fragments.append(TextFragment(
                                content=frag,
                                fragment_index=i,
                                total_fragments=len(fragments)
                            ))

                    # 多次降重处理
                    if text_fragments:
                        current_fragments = text_fragments

                        # 进行多轮降重处理
                        for iteration in range(1, self.reduction_times + 1):
                            # 处理当前片段
                            processed_content = yield from self._process_text_fragments(current_fragments, iteration)

                            # 如果这是最后一次迭代，保存结果
                            if iteration == self.reduction_times:
                                final_content = processed_content
                                break

                            # 否则，准备下一轮迭代的片段
                            # 从处理结果中提取处理后的内容
                            next_fragments = []
                            for idx, item in enumerate(self.processed_results):
                                next_fragments.append(TextFragment(
                                    content=item['content'],
                                    fragment_index=idx,
                                    total_fragments=len(self.processed_results)
                                ))

                            current_fragments = next_fragments

                        # 更新UI显示最终结果
                        self.chatbot[-1] = ["处理完成", f"共完成 {self.reduction_times} 轮降重"]
                        yield from update_ui(chatbot=self.chatbot, history=self.history)

                        return final_content
                    else:
                        self.chatbot.append(["处理失败", "未能提取到有效的文本内容"])
                        yield from update_ui(chatbot=self.chatbot, history=self.history)
                        return None
                else:
                    self.chatbot.append(["处理失败", "未能提取到论文内容"])
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                    return None

            # 2. 准备处理章节内容（不处理标题）
            self.chatbot[-1] = ["已提取论文结构", f"共 {len(paper.sections)} 个主要章节"]
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            # 3. 收集所有需要处理的章节内容并分割为合适大小
            sections_to_process = []
            section_map = {}  # 用于映射处理前后的内容

            def collect_section_contents(sections, parent_path=""):
                """递归收集章节内容，跳过参考文献部分"""
                for i, section in enumerate(sections):
                    current_path = f"{parent_path}/{i}" if parent_path else f"{i}"

                    # 检查是否为参考文献部分，如果是则跳过
                    if section.section_type == 'references' or section.title.lower() in ['references', '参考文献', 'bibliography', '文献']:
                        continue  # 跳过参考文献部分

                    # 只处理内容非空的章节
                    if section.content and section.content.strip():
                        # 使用增强的分割函数进行更细致的分割
                        fragments = self._breakdown_section_content(section.content)

                        for fragment_idx, fragment_content in enumerate(fragments):
                            if fragment_content.strip():
                                fragment_index = len(sections_to_process)
                                sections_to_process.append(TextFragment(
                                    content=fragment_content,
                                    fragment_index=fragment_index,
                                    total_fragments=0  # 临时值，稍后更新
                                ))

                                # 保存映射关系，用于稍后更新章节内容
                                # 为每个片段存储原始章节和片段索引信息
                                section_map[fragment_index] = (current_path, section, fragment_idx, len(fragments))

                    # 递归处理子章节
                    if section.subsections:
                        collect_section_contents(section.subsections, current_path)

            # 收集所有章节内容
            collect_section_contents(paper.sections)

            # 更新总片段数
            total_fragments = len(sections_to_process)
            for frag in sections_to_process:
                frag.total_fragments = total_fragments

            # 4. 如果没有内容需要处理，直接返回
            if not sections_to_process:
                self.chatbot.append(["处理完成", "未找到需要处理的内容"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return None

            # 5. 批量处理章节内容
            self.chatbot[-1] = ["开始处理论文内容", f"共 {len(sections_to_process)} 个内容片段"]
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            # 一次性准备所有输入
            inputs_array, inputs_show_user_array, history_array = self._create_batch_inputs(sections_to_process)

            # 使用系统提示
            instruction = self.plugin_kwargs.get("advanced_arg", """请对以下学术文本进行彻底改写，以显著降低AI生成特征。具体要求如下：

1. 保持学术写作的严谨性和专业性
2. 维持原文的核心论述和逻辑框架
3. 优化句式结构：
   - 灵活运用主动句与被动句
   - 适当拆分复杂句式，提高可读性
   - 注意句式的多样性，避免重复模式
   - 打破AI常用的句式模板
4. 改善用词：
   - 使用更多学术语境下的同义词替换
   - 避免过于机械和规律性的连接词
   - 适当调整专业术语的表达方式
   - 增加词汇多样性，减少重复用词
5. 增强文本的学术特征：
   - 注重论证的严密性
   - 保持表达的客观性
   - 适度体现作者的学术见解
   - 避免过于完美和均衡的论述结构
6. 确保语言风格的一致性
7. 减少AI生成文本常见的套路和模式""")
            sys_prompt_array = [f"""作为一位专业的学术写作顾问，请按照以下要求改写文本：

1. 严格保持学术写作规范
2. 维持原文的核心论述和逻辑框架
3. 通过优化句式结构和用词降低AI生成特征
4. 确保语言风格的一致性和专业性
5. 保持内容的客观性和准确性
6. 避免AI常见的套路化表达和过于完美的结构"""] * len(sections_to_process)

            # 调用LLM一次性处理所有片段
            response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
                inputs_array=inputs_array,
                inputs_show_user_array=inputs_show_user_array,
                llm_kwargs=self.llm_kwargs,
                chatbot=self.chatbot,
                history_array=history_array,
                sys_prompt_array=sys_prompt_array,
            )

            # 处理响应，重组章节内容
            section_contents = {}  # 用于重组各章节的处理后内容

            for j, frag in enumerate(sections_to_process):
                try:
                    llm_response = response_collection[j * 2 + 1]
                    processed_text = self._extract_decision(llm_response)

                    if processed_text and processed_text.strip():
                        # 保存处理结果
                        self.processed_results.append({
                            'index': frag.fragment_index,
                            'content': processed_text
                        })

                        # 存储处理后的文本片段，用于后续重组
                        fragment_index = frag.fragment_index
                        if fragment_index in section_map:
                            path, section, fragment_idx, total_fragments = section_map[fragment_index]

                            # 初始化此章节的内容容器（如果尚未创建）
                            if path not in section_contents:
                                section_contents[path] = [""] * total_fragments

                            # 将处理后的片段放入正确位置
                            section_contents[path][fragment_idx] = processed_text
                    else:
                        self.failed_fragments.append(frag)
                except Exception as e:
                    self.failed_fragments.append(frag)

            # 重组每个章节的内容
            for path, fragments in section_contents.items():
                section = None
                for idx in section_map:
                    if section_map[idx][0] == path:
                        section = section_map[idx][1]
                        break

                if section:
                    # 合并该章节的所有处理后片段
                    section.content = "\n".join(fragments)

            # 6. 更新UI
            success_count = total_fragments - len(self.failed_fragments)
            self.chatbot[-1] = ["处理完成", f"成功处理 {success_count}/{total_fragments} 个内容片段"]
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            # 收集参考文献部分（不进行处理）
            references_sections = []
            def collect_references(sections, parent_path=""):
                """递归收集参考文献部分"""
                for i, section in enumerate(sections):
                    current_path = f"{parent_path}/{i}" if parent_path else f"{i}"

                    # 检查是否为参考文献部分
                    if section.section_type == 'references' or section.title.lower() in ['references', '参考文献', 'bibliography', '文献']:
                        references_sections.append((current_path, section))

                    # 递归检查子章节
                    if section.subsections:
                        collect_references(section.subsections, current_path)

            # 收集参考文献
            collect_references(paper.sections)

            # 7. 将处理后的结构化论文转换为Markdown
            markdown_content = self.paper_extractor.generate_markdown(paper)

            # 8. 返回处理后的内容
            self.chatbot[-1] = ["处理完成", f"成功处理 {success_count}/{total_fragments} 个内容片段，参考文献部分未处理"]
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            return markdown_content

        except Exception as e:
            self.chatbot.append(["结构化处理失败", f"错误: {str(e)}，将尝试作为普通文件处理"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return (yield from self._process_regular_file(file_path))

    def _process_regular_file(self, file_path: str) -> Generator:
        """使用原有方式处理普通文件"""
        # 原有的文件处理逻辑
        self.chatbot[-1] = ["正在读取文件", f"文件路径: {file_path}"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        content = extract_text(file_path)
        if not content or not content.strip():
            self.chatbot.append(["处理失败", "文件内容为空或无法提取内容"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return None

        # 2. 分割文本
        self.chatbot[-1] = ["正在分析文件", "将文件内容分割为适当大小的片段"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 使用增强的分割函数
        fragments = self._breakdown_section_content(content)

        # 3. 创建文本片段对象
        text_fragments = []
        for i, frag in enumerate(fragments):
            if frag.strip():
                text_fragments.append(TextFragment(
                    content=frag,
                    fragment_index=i,
                    total_fragments=len(fragments)
                ))

        # 4. 多轮降重处理
        if not text_fragments:
            self.chatbot.append(["处理失败", "未能提取到有效的文本内容"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)
            return None

        # 批处理大小
        batch_size = 8  # 每批处理的片段数

        # 第一次迭代
        current_batches = []
        for i in range(0, len(text_fragments), batch_size):
            current_batches.append(text_fragments[i:i + batch_size])

        all_processed_fragments = []

        # 进行多轮降重处理
        for iteration in range(1, self.reduction_times + 1):
            self.chatbot[-1] = ["开始处理文本", f"第 {iteration}/{self.reduction_times} 次降重"]
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            next_batches = []
            all_processed_fragments = []

            # 分批处理当前迭代的片段
            for batch in current_batches:
                # 处理当前批次
                _ = yield from self._process_text_fragments(batch, iteration)

                # 收集处理结果
                processed_batch = []
                for item in self.processed_results:
                    processed_batch.append(TextFragment(
                        content=item['content'],
                        fragment_index=len(all_processed_fragments) + len(processed_batch),
                        total_fragments=0  # 临时值，稍后更新
                    ))

                all_processed_fragments.extend(processed_batch)

                # 如果不是最后一轮迭代，准备下一批次
                if iteration < self.reduction_times:
                    for i in range(0, len(processed_batch), batch_size):
                        next_batches.append(processed_batch[i:i + batch_size])

            # 更新总片段数
            for frag in all_processed_fragments:
                frag.total_fragments = len(all_processed_fragments)

            # 为下一轮迭代准备批次
            current_batches = next_batches

        # 合并最终结果
        final_content = "\n\n".join([frag.content for frag in all_processed_fragments])

        # 5. 更新UI显示最终结果
        self.chatbot[-1] = ["处理完成", f"共完成 {self.reduction_times} 轮降重"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        return final_content

    def save_results(self, content: str, original_file_path: str) -> List[str]:
        """保存处理结果为TXT格式"""
        if not content:
            return []

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        original_filename = os.path.basename(original_file_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        base_filename = f"{filename_without_ext}_processed_{timestamp}"

        result_files = []

        # 只保存为TXT
        try:
            txt_formatter = TxtFormatter()
            txt_content = txt_formatter.create_document(content)
            txt_file = write_history_to_file(
                history=[txt_content],
                file_basename=f"{base_filename}.txt"
            )
            result_files.append(txt_file)
        except Exception as e:
            self.chatbot.append(["警告", f"TXT格式保存失败: {str(e)}"])

        # 添加到下载区
        for file in result_files:
            promote_file_to_downloadzone(file, chatbot=self.chatbot)

        return result_files

    def _breakdown_section_content(self, content: str) -> List[str]:
        """对文本内容进行分割与合并

        主要按段落进行组织，只合并较小的段落以减少片段数量
        保留原始段落结构，不对长段落进行强制分割
        针对中英文设置不同的阈值，因为字符密度不同
        """
        # 先按段落分割文本
        paragraphs = content.split('\n\n')

        # 检测语言类型
        chinese_char_count = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
        is_chinese_text = chinese_char_count / max(1, len(content)) > 0.3

        # 根据语言类型设置不同的阈值（只用于合并小段落）
        if is_chinese_text:
            # 中文文本：一个汉字就是一个字符，信息密度高
            min_chunk_size = 300  # 段落合并的最小阈值
            target_size = 800  # 理想的段落大小
        else:
            # 英文文本：一个单词由多个字符组成，信息密度低
            min_chunk_size = 600  # 段落合并的最小阈值
            target_size = 1600  # 理想的段落大小

        # 1. 只合并小段落，不对长段落进行分割
        result_fragments = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            # 如果段落太小且不会超过目标大小，则合并
            if len(para) < min_chunk_size and current_length + len(para) <= target_size:
                current_chunk.append(para)
                current_length += len(para)
            # 否则，创建新段落
            else:
                # 如果当前块非空且与当前段落无关，先保存它
                if current_chunk and current_length > 0:
                    result_fragments.append('\n\n'.join(current_chunk))

                # 当前段落作为新块
                current_chunk = [para]
                current_length = len(para)

            # 如果当前块大小已接近目标大小，保存并开始新块
            if current_length >= target_size:
                result_fragments.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0

        # 保存最后一个块
        if current_chunk:
            result_fragments.append('\n\n'.join(current_chunk))

        # 2. 处理可能过大的片段（确保不超过token限制）
        final_fragments = []
        max_token = self._get_token_limit()

        for fragment in result_fragments:
            # 检查fragment是否可能超出token限制
            # 根据语言类型调整token估算
            if is_chinese_text:
                estimated_tokens = len(fragment) / 1.5  # 中文每个token约1-2个字符
            else:
                estimated_tokens = len(fragment) / 4  # 英文每个token约4个字符

            if estimated_tokens > max_token:
                # 即使可能超出限制，也尽量保持段落的完整性
                # 使用breakdown_text但设置更大的限制来减少分割
                larger_limit = max_token * 0.95  # 使用95%的限制
                sub_fragments = breakdown_text_to_satisfy_token_limit(
                    txt=fragment,
                    limit=larger_limit,
                    llm_model=self.llm_kwargs['llm_model']
                )
                final_fragments.extend(sub_fragments)
            else:
                final_fragments.append(fragment)

        return final_fragments

    def _process_text_fragments(self, text_fragments: List[TextFragment], current_iteration: int = 1) -> str:
        """处理文本片段，支持多次降重

        Args:
            text_fragments: 要处理的文本片段列表
            current_iteration: 当前是第几次降重迭代

        Returns:
            处理后的文本内容
        """
        self.chatbot[-1] = ["开始处理文本", f"第 {current_iteration}/{self.reduction_times} 次降重，共 {len(text_fragments)} 个片段"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 重置处理结果，为当前迭代做准备
        self.processed_results = []
        self.failed_fragments = []

        # 一次性准备所有输入
        inputs_array, inputs_show_user_array, history_array = self._create_batch_inputs(text_fragments, current_iteration)

        # 对于单次调用的特殊处理 - 使用更强力的系统提示词
        if self.reduction_times == 1:
            sys_prompt = f"""你是一个伪装成人类科研学者的AI，能够将各种AI生成内容改写成人类学者常用的表达方式，让人类学者无法分辨。

你的任务是对学术文本进行深度改写，以彻底消除AI特征，使其具有真实人类学者的写作特点：

1. 打破AI常见的规整句式结构和词汇选择模式
2. 引入学术写作中的自然变化和不规则性
3. 使用多样化的句式和段落结构，避免明显的平衡性和规律性
4. 加入人类写作中常见的微小不完美之处，如段落长度变化、论述强调点不均等
5. 在维持核心论点的同时，完全重构表达方式
6. 适当使用学科领域内专家常用的表达习惯和术语
7. 确保文本读起来自然流畅，避免机械感
8. 打破AI生成内容常见的逻辑结构和表达套路
9. 根据文本内容，在保持专业性的基础上增加写作的特色和个性

对于每个文本片段，尽可能彻底地重构，使其无法被识别为AI生成。"""

            sys_prompt_array = [sys_prompt] * len(text_fragments)

        else:
            # 原有的多次迭代处理逻辑
            # 根据迭代次数调整系统提示词强度
            base_instruction = self.plugin_kwargs.get("advanced_arg", """你是一个人类科研工作者，请对以下学术文本进行彻底改写，以显著降低AI生成特征。具体要求如下：

1. 保持学术写作的严谨性和专业性
2. 维持原文的核心论述和逻辑框架
3. 优化句式结构：
   - 灵活运用主动句与被动句
   - 适当拆分复杂句式，提高可读性
   - 注意句式的多样性，避免重复模式
   - 打破AI常用的句式模板
4. 改善用词：
   - 使用更多学术语境下的同义词替换
   - 避免过于机械和规律性的连接词
   - 适当调整专业术语的表达方式
   - 增加词汇多样性，减少重复用词
5. 增强文本的学术特征：
   - 注重论证的严密性
   - 保持表达的客观性
   - 适度体现作者的学术见解
   - 避免过于完美和均衡的论述结构
6. 确保语言风格的一致性
7. 减少AI生成文本常见的套路和模式""")

            # 根据迭代次数增强强度
            if current_iteration == 1:
                # 第一次迭代使用基础强度
                instruction = base_instruction
                sys_prompt = f"""你是一个伪装成人类科研学者的AI，能够将各种AI生成内容改写成人类学者常用的表达方式，让人类学者无法分辨。请进行第{current_iteration}轮深度改写：

1. 严格保持学术写作规范
2. 维持原文的核心论述和逻辑框架
3. 通过优化句式结构和用词降低AI生成特征
4. 确保语言风格的一致性和专业性
5. 保持内容的客观性和准确性
6. 避免AI常见的套路化表达和过于完美的结构"""
            elif current_iteration == 2:
                # 第二次迭代使用中等强度
                instruction = base_instruction + """这是第二次改写，请进一步优化：

1. 更深入地调整句式结构，增加表达多样性
2. 在保持准确性的前提下，替换更多专业术语的表达方式
3. 优化段落结构，增强逻辑连贯性
4. 适当调整学术论证的表达方式
5. 打破AI生成内容的常见模式，如过于均衡的结构和规律性的表达方式"""
                sys_prompt = f"""你是一个伪装成人类科研学者的AI，能够将各种AI生成内容改写成人类学者常用的表达方式，让人类学者无法分辨。请进行第二轮改写：

1. 在保持严谨性的基础上，优化表达方式
2. 改善文本结构，提升学术论述的清晰度
3. 增强专业术语使用的灵活性
4. 确保论证过程的完整性和逻辑性
5. 进一步减少AI生成内容的特征和模式
6. 使文本表现出更自然、更人性化的写作风格"""
            else:
                # 第三次或更多次迭代使用高强度
                instruction = base_instruction + f"""这是第{current_iteration}次改写，需要在保持学术性的前提下彻底重构文本：

1. 全面重构句式，采用不同的表达策略
2. 系统性替换学术用语，保持专业准确性
3. 重组段落结构，优化论证层次
4. 深化学术观点的表达方式
5. 增强文本的逻辑严密性
6. 提升论述的专业深度
7. 确保不遗漏任何学术观点和论证要素
8. 适当使用学术表达技巧（如精准举例、恰当转折等），但不过分依赖比喻和类比
9. 彻底消除AI生成内容的特征，使文本具有真实学者的写作风格"""
                sys_prompt = f"""你是一个伪装成人类科研学者的AI，能够将各种AI生成内容改写成人类学者常用的表达方式，让人类学者无法分辨。请进行第{current_iteration}轮深度改写：

1. 在保持专业水准的前提下，彻底重构表达方式，引入长难句
2. 确保学术论证的严密性和完整性
3. 优化专业术语的运用
4. 提升文本的学术价值
5. 保持论述的逻辑性和连贯性
6. 适当使用少量学术表达技巧，提高文本说服力，但避免过度使用比喻和类比
7. 消除所有明显的AI生成痕迹，使文本更接近真实学者的写作风格"""

            sys_prompt_array = [sys_prompt] * len(text_fragments)

        # 调用LLM一次性处理所有片段
        response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=inputs_array,
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=self.llm_kwargs,
            chatbot=self.chatbot,
            history_array=history_array,
            sys_prompt_array=sys_prompt_array,
        )

        # 处理响应
        for j, frag in enumerate(text_fragments):
            try:
                llm_response = response_collection[j * 2 + 1]
                processed_text = self._extract_decision(llm_response)

                if processed_text and processed_text.strip():
                    self.processed_results.append({
                        'index': frag.fragment_index,
                        'content': processed_text
                    })
                else:
                    self.failed_fragments.append(frag)
                    self.processed_results.append({
                        'index': frag.fragment_index,
                        'content': frag.content
                    })
            except Exception as e:
                self.failed_fragments.append(frag)
                self.processed_results.append({
                    'index': frag.fragment_index,
                    'content': frag.content
                })

        # 按原始顺序合并结果
        self.processed_results.sort(key=lambda x: x['index'])
        final_content = "\n".join([item['content'] for item in self.processed_results])

        # 更新UI
        success_count = len(text_fragments) - len(self.failed_fragments)
        self.chatbot[-1] = ["当前阶段处理完成", f"第 {current_iteration}/{self.reduction_times} 次降重，成功处理 {success_count}/{len(text_fragments)} 个片段"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        return final_content


@CatchException
def 学术降重(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
              history: List, system_prompt: str, user_request: str):
    """主函数 - 文件到文件处理"""
    # 初始化
    # 从高级参数中提取降重次数
    if "advanced_arg" in plugin_kwargs and plugin_kwargs["advanced_arg"]:
        # 检查是否包含降重次数的设置
        match = re.search(r'reduction_times\s*=\s*(\d+)', plugin_kwargs["advanced_arg"])
        if match:
            reduction_times = int(match.group(1))
            # 替换掉高级参数中的reduction_times设置，但保留其他内容
            plugin_kwargs["advanced_arg"] = re.sub(r'reduction_times\s*=\s*\d+', '', plugin_kwargs["advanced_arg"]).strip()
            # 添加到plugin_kwargs中作为单独的参数
            plugin_kwargs["reduction_times"] = reduction_times

    processor = DocumentProcessor(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
    chatbot.append(["函数插件功能", f"文件内容处理：将文档内容进行{processor.reduction_times}次降重处理"])

    # 更新用户提示，提供关于降重策略的详细说明
    if processor.reduction_times == 1:
        chatbot.append(["降重策略", "将使用单次深度降重，这种方式能更有效地降低AI特征，减少查重率。我们采用特殊优化的提示词，通过一次性强力改写来实现降重效果。"])
    elif processor.reduction_times > 1:
        chatbot.append(["降重策略", f"将进行{processor.reduction_times}轮迭代降重，每轮降重都会基于上一轮的结果，并逐渐增加降重强度。请注意，多轮迭代可能会引入新的AI特征，单次强力降重通常效果更好。"])

    yield from update_ui(chatbot=chatbot, history=history)

    # 验证输入路径
    if not os.path.exists(txt):
        report_exception(chatbot, history, a=f"解析路径: {txt}", b=f"找不到路径或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 验证路径安全性
    user_name = chatbot.get_user()
    validate_path_safety(txt, user_name)

    # 获取文件列表
    if os.path.isfile(txt):
        # 单个文件处理
        file_paths = [txt]
    else:
        # 目录处理 - 类似批量文件询问插件
        project_folder = txt
        extract_folder = next((d for d in glob.glob(f'{project_folder}/*')
                           if os.path.isdir(d) and d.endswith('.extract')), project_folder)

        # 排除压缩文件
        exclude_patterns = r'/[^/]+\.(zip|rar|7z|tar|gz)$'
        file_paths = [f for f in glob.glob(f'{extract_folder}/**', recursive=True)
                     if os.path.isfile(f) and not re.search(exclude_patterns, f)]

        # 过滤支持的文件格式
        file_paths = [f for f in file_paths if any(f.lower().endswith(ext) for ext in
                    list(processor.paper_extractor.SUPPORTED_EXTENSIONS) + ['.json', '.csv', '.xlsx', '.xls'])]

    if not file_paths:
        report_exception(chatbot, history, a=f"解析路径: {txt}", b="未找到支持的文件类型")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # 处理文件
    if len(file_paths) > 1:
        chatbot.append(["发现多个文件", f"共找到 {len(file_paths)} 个文件，将处理第一个文件"])
        yield from update_ui(chatbot=chatbot, history=history)

    # 只处理第一个文件
    file_to_process = file_paths[0]
    processed_content = yield from processor.process_file(file_to_process)

    if processed_content:
        # 保存结果
        result_files = processor.save_results(processed_content, file_to_process)

        if result_files:
            chatbot.append(["处理完成", f"已生成 {len(result_files)} 个结果文件"])
        else:
            chatbot.append(["处理完成", "但未能保存任何结果文件"])
    else:
        chatbot.append(["处理失败", "未能生成有效的处理结果"])

    yield from update_ui(chatbot=chatbot, history=history)

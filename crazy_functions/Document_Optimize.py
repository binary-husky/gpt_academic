import os
import time
import glob
import re
import threading
from typing import Dict, List, Generator, Tuple
from dataclasses import dataclass

from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
from crazy_functions.rag_fns.rag_file_support import extract_text, supports_format, convert_to_markdown
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
        self.llm_kwargs = llm_kwargs
        self.plugin_kwargs = plugin_kwargs
        self.chatbot = chatbot
        self.history = history
        self.system_prompt = system_prompt
        self.processed_results = []
        self.failed_fragments = []
        # 新增：初始化论文结构提取器
        self.paper_extractor = PaperStructureExtractor()

    def _get_token_limit(self) -> int:
        """获取模型token限制，返回更小的值以确保更细粒度的分割"""
        max_token = model_info[self.llm_kwargs['llm_model']]['max_token']
        # 降低token限制，使每个片段更小
        return max_token // 4  # 从3/4降低到1/4

    def _create_batch_inputs(self, fragments: List[TextFragment]) -> Tuple[List, List, List]:
        """创建批处理输入"""
        inputs_array = []
        inputs_show_user_array = []
        history_array = []

        user_instruction = self.plugin_kwargs.get("advanced_arg", "请润色以下学术文本，提高其语言表达的准确性、专业性和流畅度，保持学术风格，确保逻辑连贯，但不改变原文的科学内容和核心观点")

        for frag in fragments:
            i_say = (f'请按照以下要求处理文本内容：{user_instruction}\n\n'
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
            from crazy_functions.rag_fns.rag_file_support import convert_to_markdown
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

                    # 批量处理片段
                    if text_fragments:
                        self.chatbot[-1] = ["开始处理文本", f"共 {len(text_fragments)} 个片段"]
                        yield from update_ui(chatbot=self.chatbot, history=self.history)

                        # 一次性准备所有输入
                        inputs_array, inputs_show_user_array, history_array = self._create_batch_inputs(text_fragments)

                        # 使用系统提示
                        instruction = self.plugin_kwargs.get("advanced_arg", "请润色以下学术文本，提高其语言表达的准确性、专业性和流畅度，保持学术风格，确保逻辑连贯，但不改变原文的科学内容和核心观点")
                        sys_prompt_array = [f"你是一个专业的学术文献编辑助手。请按照用户的要求：'{instruction}'处理文本。保持学术风格，增强表达的准确性和专业性。"] * len(text_fragments)

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
                        self.chatbot[-1] = ["处理完成", f"成功处理 {success_count}/{len(text_fragments)} 个片段"]
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
            instruction = self.plugin_kwargs.get("advanced_arg", "请润色以下学术文本，提高其语言表达的准确性、专业性和流畅度，保持学术风格，确保逻辑连贯，但不改变原文的科学内容和核心观点")
            sys_prompt_array = [f"你是一个专业的学术文献编辑助手。请按照用户的要求：'{instruction}'处理文本。保持学术风格，增强表达的准确性和专业性。"] * len(sections_to_process)

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

        # 4. 处理所有片段
        self.chatbot[-1] = ["开始处理文本", f"共 {len(text_fragments)} 个片段"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        # 批量处理片段
        batch_size = 8  # 每批处理的片段数
        for i in range(0, len(text_fragments), batch_size):
            batch = text_fragments[i:i + batch_size]

            inputs_array, inputs_show_user_array, history_array = self._create_batch_inputs(batch)

            # 使用系统提示
            instruction = self.plugin_kwargs.get("advanced_arg", "请润色以下文本")
            sys_prompt_array = [f"你是一个专业的文本处理助手。请按照用户的要求：'{instruction}'处理文本。"] * len(batch)

            # 调用LLM处理
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
                            'content': frag.content  # 如果处理失败，使用原始内容
                        })
                except Exception as e:
                    self.failed_fragments.append(frag)
                    self.processed_results.append({
                        'index': frag.fragment_index,
                        'content': frag.content  # 如果处理失败，使用原始内容
                    })

        # 5. 按原始顺序合并结果
        self.processed_results.sort(key=lambda x: x['index'])
        final_content = "\n".join([item['content'] for item in self.processed_results])

        # 6. 更新UI
        success_count = len(text_fragments) - len(self.failed_fragments)
        self.chatbot[-1] = ["处理完成", f"成功处理 {success_count}/{len(text_fragments)} 个片段"]
        yield from update_ui(chatbot=self.chatbot, history=self.history)

        return final_content

    def save_results(self, content: str, original_file_path: str) -> List[str]:
        """保存处理结果为多种格式"""
        if not content:
            return []

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        original_filename = os.path.basename(original_file_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        base_filename = f"{filename_without_ext}_processed_{timestamp}"

        result_files = []

        # 获取用户指定的处理类型
        processing_type = self.plugin_kwargs.get("advanced_arg", "文本处理")

        # 1. 保存为TXT
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

        # 2. 保存为Markdown
        try:
            md_formatter = MarkdownFormatter()
            md_content = md_formatter.create_document(content, processing_type)
            md_file = write_history_to_file(
                history=[md_content],
                file_basename=f"{base_filename}.md"
            )
            result_files.append(md_file)
        except Exception as e:
            self.chatbot.append(["警告", f"Markdown格式保存失败: {str(e)}"])

        # 3. 保存为HTML
        try:
            html_formatter = HtmlFormatter(processing_type=processing_type)
            html_content = html_formatter.create_document(content)
            html_file = write_history_to_file(
                history=[html_content],
                file_basename=f"{base_filename}.html"
            )
            result_files.append(html_file)
        except Exception as e:
            self.chatbot.append(["警告", f"HTML格式保存失败: {str(e)}"])

        # 4. 保存为Word
        try:
            word_formatter = WordFormatter()
            doc = word_formatter.create_document(content, processing_type)

            # 获取保存路径
            from toolbox import get_log_folder
            word_path = os.path.join(get_log_folder(), f"{base_filename}.docx")
            doc.save(word_path)

            # 5. 保存为PDF（通过Word转换）
            try:
                from crazy_functions.paper_fns.file2file_doc.word2pdf import WordToPdfConverter
                pdf_path = WordToPdfConverter.convert_to_pdf(word_path)
                result_files.append(pdf_path)
            except Exception as e:
                self.chatbot.append(["警告", f"PDF格式保存失败: {str(e)}"])

        except Exception as e:
            self.chatbot.append(["警告", f"Word格式保存失败: {str(e)}"])

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


@CatchException
def 自定义智能文档处理(txt: str, llm_kwargs: Dict, plugin_kwargs: Dict, chatbot: List,
              history: List, system_prompt: str, user_request: str):
    """主函数 - 文件到文件处理"""
    # 初始化
    processor = DocumentProcessor(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)
    chatbot.append(["函数插件功能", "文件内容处理：将文档内容按照指定要求处理后输出为多种格式"])
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

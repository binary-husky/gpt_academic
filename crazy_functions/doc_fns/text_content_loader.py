import os
import re
import glob
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Generator, Tuple, Set, Optional, Dict
from dataclasses import dataclass
from loguru import logger
from toolbox import update_ui
from crazy_functions.rag_fns.rag_file_support import extract_text
from crazy_functions.doc_fns.content_folder import ContentFoldingManager, FileMetadata, FoldingOptions, FoldingStyle, FoldingError
from shared_utils.fastapi_server import validate_path_safety
from datetime import datetime
import mimetypes

@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str  # 完整路径
    rel_path: str  # 相对路径
    size: float  # 文件大小(MB)
    extension: str  # 文件扩展名
    last_modified: str  # 最后修改时间


class TextContentLoader:
    """优化版本的文本内容加载器 - 保持原有接口"""

    # 压缩文件扩展名
    COMPRESSED_EXTENSIONS: Set[str] = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}

    # 系统配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 最大文件大小（100MB）
    MAX_TOTAL_SIZE: int = 100 * 1024 * 1024  # 最大总大小（100MB）
    MAX_FILES: int = 100  # 最大文件数量
    CHUNK_SIZE: int = 1024 * 1024  # 文件读取块大小（1MB）
    MAX_WORKERS: int = min(32, (os.cpu_count() or 1) * 4)  # 最大工作线程数
    BATCH_SIZE: int = 5  # 批处理大小

    def __init__(self, chatbot: List, history: List):
        """初始化加载器"""
        self.chatbot = chatbot
        self.history = history
        self.failed_files: List[Tuple[str, str]] = []
        self.processed_size: int = 0
        self.start_time: float = 0
        self.file_cache: Dict[str, str] = {}
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self.results_queue = queue.Queue()
        self.folding_manager = ContentFoldingManager()

    def _create_file_info(self, entry: os.DirEntry, root_path: str) -> FileInfo:
        """优化的文件信息创建

        Args:
            entry: 目录入口对象
            root_path: 根路径

        Returns:
            FileInfo: 文件信息对象
        """
        try:
            stats = entry.stat()  # 使用缓存的文件状态
            return FileInfo(
                path=entry.path,
                rel_path=os.path.relpath(entry.path, root_path),
                size=stats.st_size / (1024 * 1024),
                extension=os.path.splitext(entry.path)[1].lower(),
                last_modified=time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(stats.st_mtime))
            )
        except (OSError, ValueError) as e:
            return None

    def _process_file_batch(self, file_batch: List[FileInfo]) -> List[Tuple[FileInfo, Optional[str]]]:
        """批量处理文件

        Args:
            file_batch: 要处理的文件信息列表

        Returns:
            List[Tuple[FileInfo, Optional[str]]]: 处理结果列表
        """
        results = []
        futures = {}

        for file_info in file_batch:
            if file_info.path in self.file_cache:
                results.append((file_info, self.file_cache[file_info.path]))
                continue

            if file_info.size * 1024 * 1024 > self.MAX_FILE_SIZE:
                with self._lock:
                    self.failed_files.append(
                        (file_info.rel_path,
                         f"文件过大（{file_info.size:.2f}MB > {self.MAX_FILE_SIZE / (1024 * 1024)}MB）")
                    )
                continue

            future = self.executor.submit(self._read_file_content, file_info)
            futures[future] = file_info

        for future in as_completed(futures):
            file_info = futures[future]
            try:
                content = future.result()
                if content:
                    with self._lock:
                        self.file_cache[file_info.path] = content
                        self.processed_size += file_info.size * 1024 * 1024
                    results.append((file_info, content))
            except Exception as e:
                with self._lock:
                    self.failed_files.append((file_info.rel_path, f"读取失败: {str(e)}"))

        return results

    def _read_file_content(self, file_info: FileInfo) -> Optional[str]:
        """读取单个文件内容

        Args:
            file_info: 文件信息对象

        Returns:
            Optional[str]: 文件内容
        """
        try:
            content = extract_text(file_info.path)
            if not content or not content.strip():
                return None
            return content
        except Exception as e:
            logger.exception(f"读取文件失败: {str(e)}")
            raise Exception(f"读取文件失败: {str(e)}")

    def _is_valid_file(self, file_path: str) -> bool:
        """检查文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否为有效文件
        """
        if not os.path.isfile(file_path):
            return False

        extension = os.path.splitext(file_path)[1].lower()
        if (extension in self.COMPRESSED_EXTENSIONS or
            os.path.basename(file_path).startswith('.') or
            not os.access(file_path, os.R_OK)):
            return False

        # 只要文件可以访问且不在排除列表中就认为是有效的
        return True

    def _collect_files(self, path: str) -> List[FileInfo]:
        """收集文件信息

        Args:
            path: 目标路径

        Returns:
            List[FileInfo]: 有效文件信息列表
        """
        files = []
        total_size = 0

        # 处理单个文件的情况
        if os.path.isfile(path):
            if self._is_valid_file(path):
                file_info = self._create_file_info(os.DirEntry(os.path.dirname(path)), os.path.dirname(path))
                if file_info:
                    return [file_info]
            return []

        # 处理目录的情况
        try:
            # 使用os.walk来递归遍历目录
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if len(files) >= self.MAX_FILES:
                        self.failed_files.append((filename, f"超出最大文件数限制({self.MAX_FILES})"))
                        continue

                    file_path = os.path.join(root, filename)

                    if not self._is_valid_file(file_path):
                        continue

                    try:
                        stats = os.stat(file_path)
                        file_size = stats.st_size / (1024 * 1024)  # 转换为MB

                        if file_size * 1024 * 1024 > self.MAX_FILE_SIZE:
                            self.failed_files.append((file_path,
                                f"文件过大（{file_size:.2f}MB > {self.MAX_FILE_SIZE / (1024 * 1024)}MB）"))
                            continue

                        if total_size + file_size * 1024 * 1024 > self.MAX_TOTAL_SIZE:
                            self.failed_files.append((file_path, "超出总大小限制"))
                            continue

                        file_info = FileInfo(
                            path=file_path,
                            rel_path=os.path.relpath(file_path, path),
                            size=file_size,
                            extension=os.path.splitext(file_path)[1].lower(),
                            last_modified=time.strftime('%Y-%m-%d %H:%M:%S',
                                                      time.localtime(stats.st_mtime))
                        )

                        total_size += file_size * 1024 * 1024
                        files.append(file_info)

                    except Exception as e:
                        self.failed_files.append((file_path, f"处理文件失败: {str(e)}"))
                        continue

        except Exception as e:
            self.failed_files.append(("目录扫描", f"扫描失败: {str(e)}"))
            return []

        return sorted(files, key=lambda x: x.rel_path)

    def _format_content_with_fold(self, file_info, content: str) -> str:
        """使用折叠管理器格式化文件内容"""
        try:
            metadata = FileMetadata(
                rel_path=file_info.rel_path,
                size=file_info.size,
                last_modified=datetime.fromtimestamp(
                    os.path.getmtime(file_info.path)
                ),
                mime_type=mimetypes.guess_type(file_info.path)[0]
            )

            options = FoldingOptions(
                style=FoldingStyle.DETAILED,
                code_language=self.folding_manager._guess_language(
                    os.path.splitext(file_info.path)[1]
                ),
                show_timestamp=True
            )

            return self.folding_manager.format_content(
                content=content,
                formatter_type='file',
                metadata=metadata,
                options=options
            )

        except Exception as e:
            return f"Error formatting content: {str(e)}"

    def _format_content_for_llm(self, file_infos: List[FileInfo], contents: List[str]) -> str:
        """格式化用于LLM的内容

        Args:
            file_infos: 文件信息列表
            contents: 内容列表

        Returns:
            str: 格式化后的内容
        """
        if len(file_infos) != len(contents):
            raise ValueError("文件信息和内容数量不匹配")

        result = [
            "以下是多个文件的内容集合。每个文件的内容都以 '===== 文件 {序号}: {文件名} =====' 开始，",
            "以 '===== 文件 {序号} 结束 =====' 结束。你可以根据这些分隔符来识别不同文件的内容。\n\n"
        ]

        for idx, (file_info, content) in enumerate(zip(file_infos, contents), 1):
            result.extend([
                f"===== 文件 {idx}: {file_info.rel_path} =====",
                "文件内容:",
                content.strip(),
                f"===== 文件 {idx} 结束 =====\n"
            ])

        return "\n".join(result)

    def execute(self, txt: str) -> Generator:
        """执行文本加载和显示 - 保持原有接口

        Args:
            txt: 目标路径

        Yields:
            Generator: UI更新生成器
        """
        try:
            # 首先显示正在处理的提示信息
            self.chatbot.append(["提示", "正在提取文本内容，请稍作等待..."])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            user_name = self.chatbot.get_user()
            validate_path_safety(txt, user_name)
            self.start_time = time.time()
            self.processed_size = 0
            self.failed_files.clear()
            successful_files = []
            successful_contents = []

            # 收集文件
            files = self._collect_files(txt)
            if not files:
                # 移除之前的提示信息
                self.chatbot.pop()
                self.chatbot.append(["提示", "未找到任何有效文件"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return

            # 批量处理文件
            content_blocks = []
            for i in range(0, len(files), self.BATCH_SIZE):
                batch = files[i:i + self.BATCH_SIZE]
                results = self._process_file_batch(batch)

                for file_info, content in results:
                    if content:
                        content_blocks.append(self._format_content_with_fold(file_info, content))
                        successful_files.append(file_info)
                        successful_contents.append(content)

            # 显示文件内容，替换之前的提示信息
            if content_blocks:
                # 移除之前的提示信息
                self.chatbot.pop()
                self.chatbot.append(["文件内容", "\n".join(content_blocks)])
                self.history.extend([
                    self._format_content_for_llm(successful_files, successful_contents),
                    "我已经接收到你上传的文件的内容，请提问"
                ])
                yield from update_ui(chatbot=self.chatbot, history=self.history)

            yield from update_ui(chatbot=self.chatbot, history=self.history)

        except Exception as e:
            # 发生错误时，移除之前的提示信息
            if len(self.chatbot) > 0 and self.chatbot[-1][0] == "提示":
                self.chatbot.pop()
            self.chatbot.append(["错误", f"处理过程中出现错误: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

        finally:
            self.executor.shutdown(wait=False)
            self.file_cache.clear()

    def execute_single_file(self, file_path: str) -> Generator:
        """执行单个文件的加载和显示

        Args:
            file_path: 文件路径

        Yields:
            Generator: UI更新生成器
        """
        try:
            # 首先显示正在处理的提示信息
            self.chatbot.append(["提示", "正在提取文本内容，请稍作等待..."])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

            user_name = self.chatbot.get_user()
            validate_path_safety(file_path, user_name)
            self.start_time = time.time()
            self.processed_size = 0
            self.failed_files.clear()

            # 验证文件是否存在且可读
            if not os.path.isfile(file_path):
                self.chatbot.pop()
                self.chatbot.append(["错误", f"指定路径不是文件: {file_path}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return

            if not self._is_valid_file(file_path):
                self.chatbot.pop()
                self.chatbot.append(["错误", f"无效的文件类型或无法读取: {file_path}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return

            # 创建文件信息
            try:
                stats = os.stat(file_path)
                file_size = stats.st_size / (1024 * 1024)  # 转换为MB

                if file_size * 1024 * 1024 > self.MAX_FILE_SIZE:
                    self.chatbot.pop()
                    self.chatbot.append(["错误", f"文件过大（{file_size:.2f}MB > {self.MAX_FILE_SIZE / (1024 * 1024)}MB）"])
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                    return

                file_info = FileInfo(
                    path=file_path,
                    rel_path=os.path.basename(file_path),
                    size=file_size,
                    extension=os.path.splitext(file_path)[1].lower(),
                    last_modified=time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(stats.st_mtime))
                )
            except Exception as e:
                self.chatbot.pop()
                self.chatbot.append(["错误", f"处理文件失败: {str(e)}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return

            # 读取文件内容
            try:
                content = self._read_file_content(file_info)
                if not content:
                    self.chatbot.pop()
                    self.chatbot.append(["提示", f"文件内容为空或无法提取: {file_path}"])
                    yield from update_ui(chatbot=self.chatbot, history=self.history)
                    return
            except Exception as e:
                self.chatbot.pop()
                self.chatbot.append(["错误", f"读取文件失败: {str(e)}"])
                yield from update_ui(chatbot=self.chatbot, history=self.history)
                return

            # 格式化内容并更新UI
            formatted_content = self._format_content_with_fold(file_info, content)

            # 移除之前的提示信息
            self.chatbot.pop()
            self.chatbot.append(["文件内容", formatted_content])

            # 更新历史记录，便于LLM处理
            llm_content = self._format_content_for_llm([file_info], [content])
            self.history.extend([llm_content, "我已经接收到你上传的文件的内容，请提问"])

            yield from update_ui(chatbot=self.chatbot, history=self.history)

        except Exception as e:
            # 发生错误时，移除之前的提示信息
            if len(self.chatbot) > 0 and self.chatbot[-1][0] == "提示":
                self.chatbot.pop()
            self.chatbot.append(["错误", f"处理过程中出现错误: {str(e)}"])
            yield from update_ui(chatbot=self.chatbot, history=self.history)

    def __del__(self):
        """析构函数 - 确保资源被正确释放"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        if hasattr(self, 'file_cache'):
            self.file_cache.clear()

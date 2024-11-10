from typing import Tuple, Optional, Generator, List
from toolbox import update_ui, update_ui_lastest_msg, get_conf
import os, tarfile, requests, time, re
class ArxivPaperProcessor:
    """Arxiv论文处理器类"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'latin1', 'gbk', 'gb2312', 'ascii']
        self.arxiv_cache_dir = get_conf("ARXIV_CACHE_DIR")

    def download_and_extract(self, txt: str, chatbot, history) -> Generator[Optional[Tuple[str, str]], None, None]:
        """
        Step 1: 下载和提取arxiv论文
        返回: 生成器: (project_folder, arxiv_id)
        """
        try:
            if txt == "":
                chatbot.append(("", "请输入arxiv论文链接或ID"))
                yield from update_ui(chatbot=chatbot, history=history)
                return

            project_folder, arxiv_id = self.arxiv_download(txt, chatbot, history)
            if project_folder is None or arxiv_id is None:
                return

            if not os.path.exists(project_folder):
                chatbot.append((txt, f"找不到项目文件夹: {project_folder}"))
                yield from update_ui(chatbot=chatbot, history=history)
                return

            # 期望的返回值
            yield project_folder, arxiv_id

        except Exception as e:
            print(e)
            # yield from update_ui_lastest_msg(
            #     "下载失败，请手动下载latex源码：请前往arxiv打开此论文下载页面，点other Formats，然后download source。",
            #     chatbot=chatbot, history=history)
            return

    def arxiv_download(self, txt: str, chatbot, history) -> Tuple[str, str]:
        """
        下载arxiv论文并提取
        返回: (project_folder, arxiv_id)
        """
        def is_float(s: str) -> bool:
            try:
                float(s)
                return True
            except ValueError:
                return False

        if txt.startswith('https://arxiv.org/pdf/'):
            arxiv_id = txt.split('/')[-1]  # 2402.14207v2.pdf
            txt = arxiv_id.split('v')[0]  # 2402.14207

        if ('.' in txt) and ('/' not in txt) and is_float(txt):  # is arxiv ID
            txt = 'https://arxiv.org/abs/' + txt.strip()
        if ('.' in txt) and ('/' not in txt) and is_float(txt[:10]):  # is arxiv ID
            txt = 'https://arxiv.org/abs/' + txt[:10]

        if not txt.startswith('https://arxiv.org'):
            chatbot.append((txt, "不是有效的arxiv链接或ID"))
            # yield from update_ui(chatbot=chatbot, history=history)
            return None, None  # 返回两个值，即使其中一个为None

        chatbot.append([f"检测到arxiv文档连接", '尝试下载 ...'])
        # yield from update_ui(chatbot=chatbot, history=history)

        url_ = txt  # https://arxiv.org/abs/1707.06690

        if not txt.startswith('https://arxiv.org/abs/'):
            msg = f"解析arxiv网址失败, 期望格式例如: https://arxiv.org/abs/1707.06690。实际得到格式: {url_}。"
            # yield from update_ui_lastest_msg(msg, chatbot=chatbot, history=history)  # 刷新界面
            return None, None  # 返回两个值，即使其中一个为None

        arxiv_id = url_.split('/')[-1].split('v')[0]

        dst = os.path.join(self.arxiv_cache_dir, arxiv_id, f'{arxiv_id}.tar.gz')
        project_folder = os.path.join(self.arxiv_cache_dir, arxiv_id)

        success = self.download_arxiv_paper(url_, dst, chatbot, history)

        # if os.path.exists(dst) and get_conf('allow_cache'):
        #     # yield from update_ui_lastest_msg(f"调用缓存 {arxiv_id}", chatbot=chatbot, history=history)  # 刷新界面
        #     success = True
        # else:
        #     # yield from update_ui_lastest_msg(f"开始下载 {arxiv_id}", chatbot=chatbot, history=history)  # 刷新界面
        #     success = self.download_arxiv_paper(url_, dst, chatbot, history)
        #     # yield from update_ui_lastest_msg(f"下载完成 {arxiv_id}", chatbot=chatbot, history=history)  # 刷新界面

        if not success:
            # chatbot.append([f"下载失败 {arxiv_id}", ""])
            # yield from update_ui(chatbot=chatbot, history=history)
            raise tarfile.ReadError(f"论文下载失败 {arxiv_id}")

        # yield from update_ui_lastest_msg(f"开始解压 {arxiv_id}", chatbot=chatbot, history=history)  # 刷新界面
        extract_dst = self.extract_tar_file(dst, project_folder, chatbot, history)
        # yield from update_ui_lastest_msg(f"解压完成 {arxiv_id}", chatbot=chatbot, history=history)  # 刷新界面

        return extract_dst, arxiv_id

    def download_arxiv_paper(self, url_: str, dst: str, chatbot, history) -> bool:
        """下载arxiv论文"""
        try:
            proxies = get_conf('proxies')
            for url_tar in [url_.replace('/abs/', '/src/'), url_.replace('/abs/', '/e-print/')]:
                r = requests.get(url_tar, proxies=proxies)
                if r.status_code == 200:
                    with open(dst, 'wb+') as f:
                        f.write(r.content)
                    return True
            return False
        except requests.RequestException as e:
            # chatbot.append((f"下载失败 {url_}", str(e)))
            # yield from update_ui(chatbot=chatbot, history=history)
            return False

    def extract_tar_file(self, file_path: str, dest_dir: str, chatbot, history) -> str:
        """解压arxiv论文"""
        try:
            with tarfile.open(file_path, 'r:gz') as tar:
                tar.extractall(path=dest_dir)
            return dest_dir
        except tarfile.ReadError as e:
            chatbot.append((f"解压失败 {file_path}", str(e)))
            yield from update_ui(chatbot=chatbot, history=history)
            raise e

    def find_main_tex_file(self, tex_files: list) -> str:
        """查找主TEX文件"""
        for tex_file in tex_files:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if r'\documentclass' in content:
                    return tex_file
        return max(tex_files, key=lambda x: os.path.getsize(x))

    def read_file_with_encoding(self, file_path: str) -> Optional[str]:
        """使用多种编码尝试读取文件"""
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return None

    def process_tex_content(self, content: str, base_path: str, processed_files=None) -> str:
        """处理TEX内容，包括递归处理包含的文件"""
        if processed_files is None:
            processed_files = set()

        include_patterns = [
            r'\\input{([^}]+)}',
            r'\\include{([^}]+)}',
            r'\\subfile{([^}]+)}',
            r'\\input\s+([^\s{]+)',
        ]

        for pattern in include_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                include_file = match.group(1)
                if not include_file.endswith('.tex'):
                    include_file += '.tex'
                
                include_path = os.path.join(base_path, include_file)
                include_path = os.path.normpath(include_path)
                
                if include_path in processed_files:
                    continue
                processed_files.add(include_path)

                if os.path.exists(include_path):
                    included_content = self.read_file_with_encoding(include_path)
                    if included_content:
                        included_content = self.process_tex_content(
                            included_content, 
                            os.path.dirname(include_path),
                            processed_files
                        )
                        content = content.replace(match.group(0), included_content)

        return content

    def merge_tex_files(self, folder_path: str, chatbot, history) -> Optional[str]:
        """
        Step 2: 合并TEX文件
        返回: 合并后的内容
        """
        try:
            tex_files = []
            for root, _, files in os.walk(folder_path):
                tex_files.extend([os.path.join(root, f) for f in files if f.endswith('.tex')])

            if not tex_files:
                chatbot.append(("", "未找到任何TEX文件"))
                yield from update_ui(chatbot=chatbot, history=history)
                return None

            main_tex_file = self.find_main_tex_file(tex_files)
            chatbot.append(("", f"找到主TEX文件：{os.path.basename(main_tex_file)}"))
            yield from update_ui(chatbot=chatbot, history=history)

            tex_content = self.read_file_with_encoding(main_tex_file)
            if tex_content is None:
                chatbot.append(("", "无法读取TEX文件，可能是编码问题"))
                yield from update_ui(chatbot=chatbot, history=history)
                return None

            full_content = self.process_tex_content(
                tex_content,
                os.path.dirname(main_tex_file)
            )

            cleaned_content = self.clean_tex_content(full_content)

            chatbot.append(("", 
                f"成功处理所有TEX文件：\n"
                f"- 原始内容大小：{len(full_content)}字符\n"
                f"- 清理后内容大小：{len(cleaned_content)}字符"
            ))
            yield from update_ui(chatbot=chatbot, history=history)

            # 添加标题和摘要提取
            title = ""
            abstract = ""
            if tex_content:
                # 提取标题
                title_match = re.search(r'\\title{([^}]*)}', tex_content)
                if title_match:
                    title = title_match.group(1)
                    
                # 提取摘要
                abstract_match = re.search(r'\\begin{abstract}(.*?)\\end{abstract}', 
                                         tex_content, re.DOTALL)
                if abstract_match:
                    abstract = abstract_match.group(1)
            
            # 按token限制分段
            def split_by_token_limit(text: str, token_limit: int = 1024) -> List[str]:
                segments = []
                current_segment = []
                current_tokens = 0
                
                for line in text.split('\n'):
                    line_tokens = len(line.split())
                    if current_tokens + line_tokens > token_limit:
                        segments.append('\n'.join(current_segment))
                        current_segment = [line]
                        current_tokens = line_tokens
                    else:
                        current_segment.append(line)
                        current_tokens += line_tokens
                        
                if current_segment:
                    segments.append('\n'.join(current_segment))
                    
                return segments
            
            text_segments = split_by_token_limit(cleaned_content)
            
            return {
                'title': title,
                'abstract': abstract,
                'segments': text_segments
            }

        except Exception as e:
            chatbot.append(("", f"处理TEX文件时发生错误：{str(e)}"))
            yield from update_ui(chatbot=chatbot, history=history)
            return None

    @staticmethod
    def clean_tex_content(content: str) -> str:
        """清理TEX内容"""
        content = re.sub(r'(?m)%.*$', '', content)  # 移除注释
        content = re.sub(r'\\cite{[^}]*}', '', content)  # 移除引用
        content = re.sub(r'\\label{[^}]*}', '', content)  # 移除标签
        content = re.sub(r'\s+', ' ', content)  # 规范化空白
        return content.strip()

if __name__ == "__main__":
    # 测试 arxiv_download 函数
    processor = ArxivPaperProcessor()
    chatbot = []
    history = []

    # 测试不同格式的输入
    test_inputs = [
        "https://arxiv.org/abs/2402.14207",           # 标准格式
        "https://arxiv.org/pdf/2402.14207.pdf",       # PDF链接格式
        "2402.14207",                                 # 纯ID格式
        "2402.14207v1",                              # 带版本号的ID格式
        "https://invalid.url",                        # 无效URL测试
    ]

    for input_url in test_inputs:
        print(f"\n测试输入: {input_url}")
        try:
            project_folder, arxiv_id = processor.arxiv_download(input_url, chatbot, history)
            if project_folder and arxiv_id:
                print(f"下载成功:")
                print(f"- 项目文件夹: {project_folder}")
                print(f"- Arxiv ID: {arxiv_id}")
                print(f"- 文件夹是否存在: {os.path.exists(project_folder)}")
            else:
                print("下载失败: 返回值为 None")
        except Exception as e:
            print(f"发生错误: {str(e)}")

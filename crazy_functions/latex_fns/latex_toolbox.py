import os, shutil
import re
import numpy as np
PRESERVE = 0
TRANSFORM = 1

pj = os.path.join

class LinkedListNode():
    """
    Linked List Node
    """
    def __init__(self, string, preserve=True) -> None:
        self.string = string
        self.preserve = preserve
        self.next = None
        self.range = None
        # self.begin_line = 0
        # self.begin_char = 0

def convert_to_linklist(text, mask):
    root = LinkedListNode("", preserve=True)
    current_node = root
    for c, m, i in zip(text, mask, range(len(text))):
        if (m==PRESERVE and current_node.preserve) \
            or (m==TRANSFORM and not current_node.preserve):
            # add
            current_node.string += c
        else:
            current_node.next = LinkedListNode(c, preserve=(m==PRESERVE))
            current_node = current_node.next
    return root

def post_process(root):
    # 修复括号
    node = root
    while True:
        string = node.string
        if node.preserve: 
            node = node.next
            if node is None: break
            continue
        def break_check(string):
            str_stack = [""] # (lv, index)
            for i, c in enumerate(string):
                if c == '{':
                    str_stack.append('{')
                elif c == '}':
                    if len(str_stack) == 1:
                        print('stack fix')
                        return i
                    str_stack.pop(-1)
                else:
                    str_stack[-1] += c
            return -1
        bp = break_check(string)

        if bp == -1:
            pass
        elif bp == 0:
            node.string = string[:1]
            q = LinkedListNode(string[1:], False)
            q.next = node.next
            node.next = q
        else:
            node.string = string[:bp]
            q = LinkedListNode(string[bp:], False)
            q.next = node.next
            node.next = q

        node = node.next
        if node is None: break

    # 屏蔽空行和太短的句子
    node = root
    while True:
        if len(node.string.strip('\n').strip(''))==0: node.preserve = True
        if len(node.string.strip('\n').strip(''))<42: node.preserve = True
        node = node.next
        if node is None: break
    node = root
    while True:
        if node.next and node.preserve and node.next.preserve:
            node.string += node.next.string
            node.next = node.next.next
        node = node.next
        if node is None: break

    # 将前后断行符脱离
    node = root
    prev_node = None
    while True:
        if not node.preserve:
            lstriped_ = node.string.lstrip().lstrip('\n')
            if (prev_node is not None) and (prev_node.preserve) and (len(lstriped_)!=len(node.string)):
                prev_node.string += node.string[:-len(lstriped_)]
                node.string = lstriped_
            rstriped_ = node.string.rstrip().rstrip('\n')
            if (node.next is not None) and (node.next.preserve) and (len(rstriped_)!=len(node.string)):
                node.next.string = node.string[len(rstriped_):] + node.next.string
                node.string = rstriped_
        # =====
        prev_node = node
        node = node.next
        if node is None: break

    # 标注节点的行数范围
    node = root
    n_line = 0
    expansion = 2
    while True:
        n_l = node.string.count('\n')
        node.range = [n_line-expansion, n_line+n_l+expansion]   # 失败时，扭转的范围
        n_line = n_line+n_l
        node = node.next
        if node is None: break
    return root


"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Latex segmentation with a binary mask (PRESERVE=0, TRANSFORM=1)
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
"""


def set_forbidden_text(text, mask, pattern, flags=0):
    """
    Add a preserve text area in this paper
    e.g. with pattern = r"\\begin\{algorithm\}(.*?)\\end\{algorithm\}"
    you can mask out (mask = PRESERVE so that text become untouchable for GPT) 
    everything between "\begin{equation}" and "\end{equation}"
    """
    if isinstance(pattern, list): pattern = '|'.join(pattern)
    pattern_compile = re.compile(pattern, flags)
    for res in pattern_compile.finditer(text):
        mask[res.span()[0]:res.span()[1]] = PRESERVE
    return text, mask

def reverse_forbidden_text(text, mask, pattern, flags=0, forbid_wrapper=True):
    """
    Move area out of preserve area (make text editable for GPT)
    count the number of the braces so as to catch compelete text area. 
    e.g.
    \begin{abstract} blablablablablabla. \end{abstract} 
    """
    if isinstance(pattern, list): pattern = '|'.join(pattern)
    pattern_compile = re.compile(pattern, flags)
    for res in pattern_compile.finditer(text):
        if not forbid_wrapper:
            mask[res.span()[0]:res.span()[1]] = TRANSFORM
        else:
            mask[res.regs[0][0]: res.regs[1][0]] = PRESERVE   # '\\begin{abstract}'
            mask[res.regs[1][0]: res.regs[1][1]] = TRANSFORM   # abstract
            mask[res.regs[1][1]: res.regs[0][1]] = PRESERVE   # abstract
    return text, mask

def set_forbidden_text_careful_brace(text, mask, pattern, flags=0):
    """
    Add a preserve text area in this paper (text become untouchable for GPT).
    count the number of the braces so as to catch compelete text area. 
    e.g.
    \caption{blablablablabla\texbf{blablabla}blablabla.} 
    """
    pattern_compile = re.compile(pattern, flags)
    for res in pattern_compile.finditer(text):
        brace_level = -1
        p = begin = end = res.regs[0][0]
        for _ in range(1024*16):
            if text[p] == '}' and brace_level == 0: break
            elif text[p] == '}':  brace_level -= 1
            elif text[p] == '{':  brace_level += 1
            p += 1
        end = p+1
        mask[begin:end] = PRESERVE
    return text, mask

def reverse_forbidden_text_careful_brace(text, mask, pattern, flags=0, forbid_wrapper=True):
    """
    Move area out of preserve area (make text editable for GPT)
    count the number of the braces so as to catch compelete text area. 
    e.g.
    \caption{blablablablabla\texbf{blablabla}blablabla.} 
    """
    pattern_compile = re.compile(pattern, flags)
    for res in pattern_compile.finditer(text):
        brace_level = 0
        p = begin = end = res.regs[1][0]
        for _ in range(1024*16):
            if text[p] == '}' and brace_level == 0: break
            elif text[p] == '}':  brace_level -= 1
            elif text[p] == '{':  brace_level += 1
            p += 1
        end = p
        mask[begin:end] = TRANSFORM
        if forbid_wrapper:
            mask[res.regs[0][0]:begin] = PRESERVE
            mask[end:res.regs[0][1]] = PRESERVE
    return text, mask

def set_forbidden_text_begin_end(text, mask, pattern, flags=0, limit_n_lines=42):
    """
    Find all \begin{} ... \end{} text block that with less than limit_n_lines lines.
    Add it to preserve area
    """
    pattern_compile = re.compile(pattern, flags)
    def search_with_line_limit(text, mask):
        for res in pattern_compile.finditer(text):
            cmd = res.group(1)  # begin{what}
            this = res.group(2) # content between begin and end
            this_mask = mask[res.regs[2][0]:res.regs[2][1]]
            white_list = ['document', 'abstract', 'lemma', 'definition', 'sproof', 
                          'em', 'emph', 'textit', 'textbf', 'itemize', 'enumerate']
            if (cmd in white_list) or this.count('\n') >= limit_n_lines: # use a magical number 42
                this, this_mask = search_with_line_limit(this, this_mask)
                mask[res.regs[2][0]:res.regs[2][1]] = this_mask
            else:
                mask[res.regs[0][0]:res.regs[0][1]] = PRESERVE
        return text, mask
    return search_with_line_limit(text, mask) 



"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Latex Merge File
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
"""

def find_main_tex_file(file_manifest, mode):
    """
    在多Tex文档中，寻找主文件，必须包含documentclass，返回找到的第一个。
    P.S. 但愿没人把latex模板放在里面传进来 (6.25 加入判定latex模板的代码)
    """
    canidates = []
    for texf in file_manifest:
        if os.path.basename(texf).startswith('merge'):
            continue
        with open(texf, 'r', encoding='utf8', errors='ignore') as f:
            file_content = f.read()
        if r'\documentclass' in file_content:
            canidates.append(texf)
        else:
            continue

    if len(canidates) == 0:
        raise RuntimeError('无法找到一个主Tex文件（包含documentclass关键字）')
    elif len(canidates) == 1:
        return canidates[0]
    else: # if len(canidates) >= 2 通过一些Latex模板中常见（但通常不会出现在正文）的单词，对不同latex源文件扣分，取评分最高者返回
        canidates_score = []
        # 给出一些判定模板文档的词作为扣分项
        unexpected_words = ['\LaTeX', 'manuscript', 'Guidelines', 'font', 'citations', 'rejected', 'blind review', 'reviewers']
        expected_words = ['\input', '\ref', '\cite']
        for texf in canidates:
            canidates_score.append(0)
            with open(texf, 'r', encoding='utf8', errors='ignore') as f:
                file_content = f.read()
                file_content = rm_comments(file_content)
            for uw in unexpected_words:
                if uw in file_content:
                    canidates_score[-1] -= 1
            for uw in expected_words:
                if uw in file_content:
                    canidates_score[-1] += 1
        select = np.argmax(canidates_score) # 取评分最高者返回
        return canidates[select]
    
def rm_comments(main_file):
    new_file_remove_comment_lines = []
    for l in main_file.splitlines():
        # 删除整行的空注释
        if l.lstrip().startswith("%"):
            pass
        else:
            new_file_remove_comment_lines.append(l)
    main_file = '\n'.join(new_file_remove_comment_lines)
    # main_file = re.sub(r"\\include{(.*?)}", r"\\input{\1}", main_file)  # 将 \include 命令转换为 \input 命令
    main_file = re.sub(r'(?<!\\)%.*', '', main_file)  # 使用正则表达式查找半行注释, 并替换为空字符串
    return main_file

def find_tex_file_ignore_case(fp):
    dir_name = os.path.dirname(fp)
    base_name = os.path.basename(fp)
    # 如果输入的文件路径是正确的
    if os.path.exists(pj(dir_name, base_name)): return pj(dir_name, base_name)
    # 如果不正确，试着加上.tex后缀试试
    if not base_name.endswith('.tex'): base_name+='.tex'
    if os.path.exists(pj(dir_name, base_name)): return pj(dir_name, base_name)
    # 如果还找不到，解除大小写限制，再试一次
    import glob
    for f in glob.glob(dir_name+'/*.tex'):
        base_name_s = os.path.basename(fp)
        base_name_f = os.path.basename(f)
        if base_name_s.lower() == base_name_f.lower(): return f
        # 试着加上.tex后缀试试
        if not base_name_s.endswith('.tex'): base_name_s+='.tex'
        if base_name_s.lower() == base_name_f.lower(): return f
    return None

def merge_tex_files_(project_foler, main_file, mode):
    """
    Merge Tex project recrusively
    """
    main_file = rm_comments(main_file)
    for s in reversed([q for q in re.finditer(r"\\input\{(.*?)\}", main_file, re.M)]):
        f = s.group(1)
        fp = os.path.join(project_foler, f)
        fp_ = find_tex_file_ignore_case(fp)
        if fp_:
            with open(fp_, 'r', encoding='utf-8', errors='replace') as fx: c = fx.read()
        else:
            raise RuntimeError(f'找不到{fp}，Tex源文件缺失！')
        c = merge_tex_files_(project_foler, c, mode)
        main_file = main_file[:s.span()[0]] + c + main_file[s.span()[1]:]
    return main_file

def merge_tex_files(project_foler, main_file, mode):
    """
    Merge Tex project recrusively
    P.S. 顺便把CTEX塞进去以支持中文
    P.S. 顺便把Latex的注释去除
    """
    main_file = merge_tex_files_(project_foler, main_file, mode)
    main_file = rm_comments(main_file)

    if mode == 'translate_zh':
        # find paper documentclass
        pattern = re.compile(r'\\documentclass.*\n')
        match = pattern.search(main_file)
        assert match is not None, "Cannot find documentclass statement!"
        position = match.end()
        add_ctex = '\\usepackage{ctex}\n'
        add_url = '\\usepackage{url}\n' if '{url}' not in main_file else ''
        main_file = main_file[:position] + add_ctex + add_url + main_file[position:]
        # fontset=windows
        import platform
        main_file = re.sub(r"\\documentclass\[(.*?)\]{(.*?)}", r"\\documentclass[\1,fontset=windows,UTF8]{\2}",main_file)
        main_file = re.sub(r"\\documentclass{(.*?)}", r"\\documentclass[fontset=windows,UTF8]{\1}",main_file)
        # find paper abstract
        pattern_opt1 = re.compile(r'\\begin\{abstract\}.*\n')
        pattern_opt2 = re.compile(r"\\abstract\{(.*?)\}", flags=re.DOTALL)
        match_opt1 = pattern_opt1.search(main_file)
        match_opt2 = pattern_opt2.search(main_file)
        if (match_opt1 is None) and (match_opt2 is None):
            # "Cannot find paper abstract section!"
            main_file = insert_abstract(main_file)
        match_opt1 = pattern_opt1.search(main_file)
        match_opt2 = pattern_opt2.search(main_file)
        assert (match_opt1 is not None) or (match_opt2 is not None), "Cannot find paper abstract section!"
    return main_file


insert_missing_abs_str = r"""
\begin{abstract}
The GPT-Academic program cannot find abstract section in this paper.
\end{abstract}
"""

def insert_abstract(tex_content):
    if "\\maketitle" in tex_content:
        # find the position of "\maketitle"
        find_index = tex_content.index("\\maketitle")
        # find the nearest ending line
        end_line_index = tex_content.find("\n", find_index)
        # insert "abs_str" on the next line
        modified_tex = tex_content[:end_line_index+1] + '\n\n' + insert_missing_abs_str + '\n\n' + tex_content[end_line_index+1:]
        return modified_tex
    else:
        return tex_content

"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Post process
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
"""
def mod_inbraket(match):
    """
    为啥chatgpt会把cite里面的逗号换成中文逗号呀 
    """
    # get the matched string
    cmd = match.group(1)
    str_to_modify = match.group(2)
    # modify the matched string
    str_to_modify = str_to_modify.replace('：', ':')    # 前面是中文冒号，后面是英文冒号
    str_to_modify = str_to_modify.replace('，', ',')    # 前面是中文逗号，后面是英文逗号
    # str_to_modify = 'BOOM'
    return "\\" + cmd + "{" + str_to_modify + "}"

def fix_content(final_tex, node_string):
    """
    Fix common GPT errors to increase success rate
    """
    final_tex = re.sub(r"(?<!\\)%", "\\%", final_tex)
    final_tex = re.sub(r"\\([a-z]{2,10})\ \{", r"\\\1{", string=final_tex)
    final_tex = re.sub(r"\\\ ([a-z]{2,10})\{", r"\\\1{", string=final_tex)
    final_tex = re.sub(r"\\([a-z]{2,10})\{([^\}]*?)\}", mod_inbraket, string=final_tex)

    if "Traceback" in final_tex and "[Local Message]" in final_tex:
        final_tex = node_string # 出问题了，还原原文
    if node_string.count('\\begin') != final_tex.count('\\begin'):
        final_tex = node_string # 出问题了，还原原文
    if node_string.count('\_') > 0 and node_string.count('\_') > final_tex.count('\_'):
        # walk and replace any _ without \
        final_tex = re.sub(r"(?<!\\)_", "\\_", final_tex)

    def compute_brace_level(string):
        # this function count the number of { and }
        brace_level = 0
        for c in string:
            if c == "{": brace_level += 1
            elif c == "}": brace_level -= 1
        return brace_level
    def join_most(tex_t, tex_o):
        # this function join translated string and original string when something goes wrong
        p_t = 0
        p_o = 0
        def find_next(string, chars, begin):
            p = begin
            while p < len(string):
                if string[p] in chars: return p, string[p]
                p += 1
            return None, None
        while True:
            res1, char = find_next(tex_o, ['{','}'], p_o)
            if res1 is None: break
            res2, char = find_next(tex_t, [char], p_t)
            if res2 is None: break
            p_o = res1 + 1
            p_t = res2 + 1
        return tex_t[:p_t] + tex_o[p_o:]

    if compute_brace_level(final_tex) != compute_brace_level(node_string):
        # 出问题了，还原部分原文，保证括号正确
        final_tex = join_most(final_tex, node_string)
    return final_tex
    
def compile_latex_with_timeout(command, cwd, timeout=60):
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        print("Process timed out!")
        return False
    return True



def merge_pdfs(pdf1_path, pdf2_path, output_path):
    import PyPDF2
    Percent = 0.95
    # Open the first PDF file
    with open(pdf1_path, 'rb') as pdf1_file:
        pdf1_reader = PyPDF2.PdfFileReader(pdf1_file)
        # Open the second PDF file
        with open(pdf2_path, 'rb') as pdf2_file:
            pdf2_reader = PyPDF2.PdfFileReader(pdf2_file)
            # Create a new PDF file to store the merged pages
            output_writer = PyPDF2.PdfFileWriter()
            # Determine the number of pages in each PDF file
            num_pages = max(pdf1_reader.numPages, pdf2_reader.numPages)
            # Merge the pages from the two PDF files
            for page_num in range(num_pages):
                # Add the page from the first PDF file
                if page_num < pdf1_reader.numPages:
                    page1 = pdf1_reader.getPage(page_num)
                else:
                    page1 = PyPDF2.PageObject.createBlankPage(pdf1_reader)
                # Add the page from the second PDF file
                if page_num < pdf2_reader.numPages:
                    page2 = pdf2_reader.getPage(page_num)
                else:
                    page2 = PyPDF2.PageObject.createBlankPage(pdf1_reader)
                # Create a new empty page with double width
                new_page = PyPDF2.PageObject.createBlankPage(
                    width = int(int(page1.mediaBox.getWidth()) + int(page2.mediaBox.getWidth()) * Percent),
                    height = max(page1.mediaBox.getHeight(), page2.mediaBox.getHeight())
                )
                new_page.mergeTranslatedPage(page1, 0, 0)
                new_page.mergeTranslatedPage(page2, int(int(page1.mediaBox.getWidth())-int(page2.mediaBox.getWidth())* (1-Percent)), 0)
                output_writer.addPage(new_page)
            # Save the merged PDF file
            with open(output_path, 'wb') as output_file:
                output_writer.write(output_file)

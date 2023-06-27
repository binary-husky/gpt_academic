from toolbox import update_ui, update_ui_lastest_msg    # 刷新Gradio前端界面
from toolbox import zip_folder, objdump, objload, promote_file_to_downloadzone
import os, shutil
import re
import numpy as np
pj = os.path.join

"""
========================================================================
Part One
Latex segmentation with a binary mask (PRESERVE=0, TRANSFORM=1)
========================================================================
"""
PRESERVE = 0
TRANSFORM = 1

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

class LinkedListNode():
    """
    Linked List Node
    """
    def __init__(self, string, preserve=True) -> None:
        self.string = string
        self.preserve = preserve
        self.next = None
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
"""
========================================================================
Latex Merge File
========================================================================
"""

def 寻找Latex主文件(file_manifest, mode):
    """
    在多Tex文档中，寻找主文件，必须包含documentclass，返回找到的第一个。
    P.S. 但愿没人把latex模板放在里面传进来 (6.25 加入判定latex模板的代码)
    """
    canidates = []
    for texf in file_manifest:
        if os.path.basename(texf).startswith('merge'):
            continue
        with open(texf, 'r', encoding='utf8') as f:
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
            with open(texf, 'r', encoding='utf8') as f:
                file_content = f.read()
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

def merge_tex_files_(project_foler, main_file, mode):
    """
    Merge Tex project recrusively
    """
    main_file = rm_comments(main_file)
    for s in reversed([q for q in re.finditer(r"\\input\{(.*?)\}", main_file, re.M)]):
        f = s.group(1)
        fp = os.path.join(project_foler, f)
        if os.path.exists(fp):  
            # e.g., \input{srcs/07_appendix.tex}
            with open(fp, 'r', encoding='utf-8', errors='replace') as fx:
                c = fx.read()
        else:  
            # e.g., \input{srcs/07_appendix}
            with open(fp+'.tex', 'r', encoding='utf-8', errors='replace') as fx:
                c = fx.read()
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
        assert (match_opt1 is not None) or (match_opt2 is not None), "Cannot find paper abstract section!"
    return main_file



"""
========================================================================
Post process
========================================================================
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

def split_subprocess(txt, project_folder, return_dict, opts):
    """
    break down latex file to a linked list,
    each node use a preserve flag to indicate whether it should
    be proccessed by GPT.
    """
    text = txt
    mask = np.zeros(len(txt), dtype=np.uint8) + TRANSFORM

    # 吸收title与作者以上的部分
    text, mask = set_forbidden_text(text, mask, r"(.*?)\\maketitle", re.DOTALL)
    # 吸收iffalse注释
    text, mask = set_forbidden_text(text, mask, r"\\iffalse(.*?)\\fi", re.DOTALL)
    # 吸收在25行以内的begin-end组合
    text, mask = set_forbidden_text_begin_end(text, mask, r"\\begin\{([a-z\*]*)\}(.*?)\\end\{\1\}", re.DOTALL, limit_n_lines=42)
    # 吸收匿名公式
    text, mask = set_forbidden_text(text, mask, [ r"\$\$(.*?)\$\$",  r"\\\[.*?\\\]" ], re.DOTALL)
    # 吸收其他杂项
    text, mask = set_forbidden_text(text, mask, [ r"\\section\{(.*?)\}", r"\\section\*\{(.*?)\}", r"\\subsection\{(.*?)\}", r"\\subsubsection\{(.*?)\}" ])
    text, mask = set_forbidden_text(text, mask, [ r"\\bibliography\{(.*?)\}", r"\\bibliographystyle\{(.*?)\}" ])
    text, mask = set_forbidden_text(text, mask, r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", re.DOTALL)
    text, mask = set_forbidden_text(text, mask, r"\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}", re.DOTALL)
    text, mask = set_forbidden_text(text, mask, r"\\begin\{wraptable\}(.*?)\\end\{wraptable\}", re.DOTALL)
    text, mask = set_forbidden_text(text, mask, r"\\begin\{algorithm\}(.*?)\\end\{algorithm\}", re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{wrapfigure\}(.*?)\\end\{wrapfigure\}", r"\\begin\{wrapfigure\*\}(.*?)\\end\{wrapfigure\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{figure\}(.*?)\\end\{figure\}", r"\\begin\{figure\*\}(.*?)\\end\{figure\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{multline\}(.*?)\\end\{multline\}", r"\\begin\{multline\*\}(.*?)\\end\{multline\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{table\}(.*?)\\end\{table\}", r"\\begin\{table\*\}(.*?)\\end\{table\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{minipage\}(.*?)\\end\{minipage\}", r"\\begin\{minipage\*\}(.*?)\\end\{minipage\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{align\*\}(.*?)\\end\{align\*\}", r"\\begin\{align\}(.*?)\\end\{align\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\begin\{equation\}(.*?)\\end\{equation\}", r"\\begin\{equation\*\}(.*?)\\end\{equation\*\}"], re.DOTALL)
    text, mask = set_forbidden_text(text, mask, [r"\\includepdf\[(.*?)\]\{(.*?)\}", r"\\clearpage", r"\\newpage", r"\\appendix", r"\\tableofcontents", r"\\include\{(.*?)\}"])
    text, mask = set_forbidden_text(text, mask, [r"\\vspace\{(.*?)\}", r"\\hspace\{(.*?)\}", r"\\label\{(.*?)\}", r"\\begin\{(.*?)\}", r"\\end\{(.*?)\}"])
    text, mask = set_forbidden_text_careful_brace(text, mask, r"\\hl\{(.*?)\}", re.DOTALL)
    # reverse 操作必须放在最后
    text, mask = reverse_forbidden_text_careful_brace(text, mask, r"\\caption\{(.*?)\}", re.DOTALL, forbid_wrapper=True)
    text, mask = reverse_forbidden_text_careful_brace(text, mask, r"\\abstract\{(.*?)\}", re.DOTALL, forbid_wrapper=True)
    root = convert_to_linklist(text, mask)

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
    # 输出html调试文件，用红色标注处保留区（PRESERVE），用黑色标注转换区（TRANSFORM）
    with open(pj(project_folder, 'debug_log.html'), 'w', encoding='utf8') as f:
        segment_parts_for_gpt = []
        nodes = []
        node = root
        while True:
            nodes.append(node)
            show_html = node.string.replace('\n','<br/>')
            if not node.preserve:
                segment_parts_for_gpt.append(node.string)
                f.write(f'<p style="color:black;">#{show_html}#</p>')
            else:
                f.write(f'<p style="color:red;">{show_html}</p>')
            node = node.next
            if node is None: break

    for n in nodes: n.next = None   # break
    return_dict['nodes'] = nodes
    return_dict['segment_parts_for_gpt'] = segment_parts_for_gpt
    return return_dict



class LatexPaperSplit():
    """
    break down latex file to a linked list,
    each node use a preserve flag to indicate whether it should
    be proccessed by GPT.
    """
    def __init__(self) -> None:
        self.nodes = None
        self.msg = "{\\scriptsize\\textbf{警告：该PDF由GPT-Academic开源项目调用大语言模型+Latex翻译插件一键生成，" + \
            "版权归原文作者所有。翻译内容可靠性无保障，请仔细鉴别并以原文为准。" + \
            "项目Github地址 \\url{https://github.com/binary-husky/gpt_academic/}。"
        # 请您不要删除或修改这行警告，除非您是论文的原作者（如果您是论文原作者，欢迎加REAME中的QQ联系开发者）
        self.msg_declare = "为了防止大语言模型的意外谬误产生扩散影响，禁止移除或修改此警告。}}\\\\" 

    def merge_result(self, arr, mode, msg):
        """
        Merge the result after the GPT process completed
        """
        result_string = ""
        p = 0
        for node in self.nodes:
            if node.preserve:
                result_string += node.string
            else:
                result_string += fix_content(arr[p], node.string)
                p += 1
        if mode == 'translate_zh':
            pattern = re.compile(r'\\begin\{abstract\}.*\n')
            match = pattern.search(result_string)
            if not match:
                # match \abstract{xxxx}
                pattern_compile = re.compile(r"\\abstract\{(.*?)\}", flags=re.DOTALL)
                match = pattern_compile.search(result_string)
                position = match.regs[1][0]
            else:
                # match \begin{abstract}xxxx\end{abstract}
                position = match.end()
            result_string = result_string[:position] + self.msg + msg + self.msg_declare + result_string[position:]
        return result_string

    def split(self, txt, project_folder, opts): 
        """
        break down latex file to a linked list,
        each node use a preserve flag to indicate whether it should
        be proccessed by GPT.
        P.S. use multiprocessing to avoid timeout error
        """
        import multiprocessing
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(
            target=split_subprocess, 
            args=(txt, project_folder, return_dict, opts))
        p.start()
        p.join()
        p.close()
        self.nodes = return_dict['nodes']
        self.sp = return_dict['segment_parts_for_gpt']
        return self.sp



class LatexPaperFileGroup():
    """
    use tokenizer to break down text according to max_token_limit
    """
    def __init__(self):
        self.file_paths = []
        self.file_contents = []
        self.sp_file_contents = []
        self.sp_file_index = []
        self.sp_file_tag = []

        # count_token
        from request_llm.bridge_all import model_info
        enc = model_info["gpt-3.5-turbo"]['tokenizer']
        def get_token_num(txt): return len(enc.encode(txt, disallowed_special=()))
        self.get_token_num = get_token_num

    def run_file_split(self, max_token_limit=1900):
        """
        use tokenizer to break down text according to max_token_limit
        """
        for index, file_content in enumerate(self.file_contents):
            if self.get_token_num(file_content) < max_token_limit:
                self.sp_file_contents.append(file_content)
                self.sp_file_index.append(index)
                self.sp_file_tag.append(self.file_paths[index])
            else:
                from .crazy_utils import breakdown_txt_to_satisfy_token_limit_for_pdf
                segments = breakdown_txt_to_satisfy_token_limit_for_pdf(file_content, self.get_token_num, max_token_limit)
                for j, segment in enumerate(segments):
                    self.sp_file_contents.append(segment)
                    self.sp_file_index.append(index)
                    self.sp_file_tag.append(self.file_paths[index] + f".part-{j}.tex")
        print('Segmentation: done')

    def merge_result(self):
        self.file_result = ["" for _ in range(len(self.file_paths))]
        for r, k in zip(self.sp_file_result, self.sp_file_index):
            self.file_result[k] += r

    def write_result(self):
        manifest = []
        for path, res in zip(self.file_paths, self.file_result):
            with open(path + '.polish.tex', 'w', encoding='utf8') as f:
                manifest.append(path + '.polish.tex')
                f.write(res)
        return manifest

def write_html(sp_file_contents, sp_file_result, chatbot):

    # write html
    try:
        import copy
        from .crazy_utils import construct_html
        from toolbox import gen_time_str
        ch = construct_html() 
        orig = ""
        trans = ""
        final = []
        for c,r in zip(sp_file_contents, sp_file_result): 
            final.append(c)
            final.append(r)
        for i, k in enumerate(final): 
            if i%2==0:
                orig = k
            if i%2==1:
                trans = k
                ch.add_row(a=orig, b=trans)
        create_report_file_name = f"{gen_time_str()}.trans.html"
        ch.save_file(create_report_file_name)
        promote_file_to_downloadzone(file=f'./gpt_log/{create_report_file_name}', chatbot=chatbot)
    except:
        from toolbox import trimmed_format_exc
        print('writing html result failed:', trimmed_format_exc())

def Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, mode='proofread', switch_prompt=None, opts=[]):
    import time, os, re
    from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from .latex_utils import LatexPaperFileGroup, merge_tex_files, LatexPaperSplit, 寻找Latex主文件

    #  <-------- 寻找主tex文件 ----------> 
    maintex = 寻找Latex主文件(file_manifest, mode)
    chatbot.append((f"定位主Latex文件", f'[Local Message] 分析结果：该项目的Latex主文件是{maintex}, 如果分析错误, 请立即终止程序, 删除或修改歧义文件, 然后重试。主程序即将开始, 请稍候。'))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    time.sleep(3)

    #  <-------- 读取Latex文件, 将多文件tex工程融合为一个巨型tex ----------> 
    main_tex_basename = os.path.basename(maintex)
    assert main_tex_basename.endswith('.tex')
    main_tex_basename_bare = main_tex_basename[:-4]
    may_exist_bbl = pj(project_folder, f'{main_tex_basename_bare}.bbl')
    if os.path.exists(may_exist_bbl):
        shutil.copyfile(may_exist_bbl, pj(project_folder, f'merge.bbl'))
        shutil.copyfile(may_exist_bbl, pj(project_folder, f'merge_{mode}.bbl'))
        shutil.copyfile(may_exist_bbl, pj(project_folder, f'merge_diff.bbl'))

    with open(maintex, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        merged_content = merge_tex_files(project_folder, content, mode)

    with open(project_folder + '/merge.tex', 'w', encoding='utf-8', errors='replace') as f:
        f.write(merged_content)

    #  <-------- 精细切分latex文件 ----------> 
    chatbot.append((f"Latex文件融合完成", f'[Local Message] 正在精细切分latex文件，这需要一段时间计算，文档越长耗时越长，请耐心等待。'))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    lps = LatexPaperSplit()
    res = lps.split(merged_content, project_folder, opts) # 消耗时间的函数

    #  <-------- 拆分过长的latex片段 ----------> 
    pfg = LatexPaperFileGroup()
    for index, r in enumerate(res):
        pfg.file_paths.append('segment-' + str(index))
        pfg.file_contents.append(r)

    pfg.run_file_split(max_token_limit=1024)
    n_split = len(pfg.sp_file_contents)

    #  <-------- 根据需要切换prompt ----------> 
    inputs_array, sys_prompt_array = switch_prompt(pfg, mode)
    inputs_show_user_array = [f"{mode} {f}" for f in pfg.sp_file_tag]

    if os.path.exists(pj(project_folder,'temp.pkl')):

        #  <-------- 【仅调试】如果存在调试缓存文件，则跳过GPT请求环节 ----------> 
        pfg = objload(file=pj(project_folder,'temp.pkl'))

    else:
        #  <-------- gpt 多线程请求 ----------> 
        gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
            inputs_array=inputs_array,
            inputs_show_user_array=inputs_show_user_array,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[[""] for _ in range(n_split)],
            sys_prompt_array=sys_prompt_array,
            # max_workers=5,  # 并行任务数量限制, 最多同时执行5个, 其他的排队等待
            scroller_max_len = 40
        )

        #  <-------- 文本碎片重组为完整的tex片段 ----------> 
        pfg.sp_file_result = []
        for i_say, gpt_say, orig_content in zip(gpt_response_collection[0::2], gpt_response_collection[1::2], pfg.sp_file_contents):
            pfg.sp_file_result.append(gpt_say)
        pfg.merge_result()

        # <-------- 临时存储用于调试 ----------> 
        pfg.get_token_num = None
        objdump(pfg, file=pj(project_folder,'temp.pkl'))

    write_html(pfg.sp_file_contents, pfg.sp_file_result, chatbot=chatbot)

    #  <-------- 写出文件 ----------> 
    msg = f"当前大语言模型: {llm_kwargs['llm_model']}，当前语言模型温度设定: {llm_kwargs['temperature']}。"
    final_tex = lps.merge_result(pfg.file_result, mode, msg)
    with open(project_folder + f'/merge_{mode}.tex', 'w', encoding='utf-8', errors='replace') as f:
        if mode != 'translate_zh' or "binary" in final_tex: f.write(final_tex)
        

    #  <-------- 整理结果, 退出 ----------> 
    chatbot.append((f"完成了吗？", 'GPT结果已输出, 正在编译PDF'))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    #  <-------- 返回 ----------> 
    return project_folder + f'/merge_{mode}.tex'



def remove_buggy_lines(file_path, log_path, tex_name, tex_name_pure, n_fix, work_folder_modified):
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            log = f.read()
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            file_lines = f.readlines()
        import re
        buggy_lines = re.findall(tex_name+':([0-9]{1,5}):', log)
        buggy_lines = [int(l) for l in buggy_lines]
        buggy_lines = sorted(buggy_lines)
        print("removing lines that has errors", buggy_lines)
        file_lines.pop(buggy_lines[0]-1)
        with open(pj(work_folder_modified, f"{tex_name_pure}_fix_{n_fix}.tex"), 'w', encoding='utf-8', errors='replace') as f:
            f.writelines(file_lines)
        return True, f"{tex_name_pure}_fix_{n_fix}", buggy_lines
    except:
        print("Fatal error occurred, but we cannot identify error, please download zip, read latex log, and compile manually.")
        return False, -1, [-1]
    

def compile_latex_with_timeout(command, timeout=60):
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        print("Process timed out!")
        return False
    return True

def 编译Latex(chatbot, history, main_file_original, main_file_modified, work_folder_original, work_folder_modified, work_folder, mode='default'):
    import os, time
    current_dir = os.getcwd()
    n_fix = 1
    max_try = 32
    chatbot.append([f"正在编译PDF文档", f'编译已经开始。当前工作路径为{work_folder}，如果程序停顿5分钟以上，请直接去该路径下取回翻译结果，或者重启之后再度尝试 ...']); yield from update_ui(chatbot=chatbot, history=history)
    chatbot.append([f"正在编译PDF文档", '...']); yield from update_ui(chatbot=chatbot, history=history); time.sleep(1); chatbot[-1] = list(chatbot[-1]) # 刷新界面
    yield from update_ui_lastest_msg('编译已经开始...', chatbot, history)   # 刷新Gradio前端界面

    while True:
        import os

        # https://stackoverflow.com/questions/738755/dont-make-me-manually-abort-a-latex-compile-when-theres-an-error
        yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 编译原始PDF ...', chatbot, history)   # 刷新Gradio前端界面
        os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)

        yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 编译转化后的PDF ...', chatbot, history)   # 刷新Gradio前端界面
        os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)
        
        if ok and os.path.exists(pj(work_folder_modified, f'{main_file_modified}.pdf')):
            # 只有第二步成功，才能继续下面的步骤
            yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 编译BibTex ...', chatbot, history)    # 刷新Gradio前端界面
            if not os.path.exists(pj(work_folder_original, f'{main_file_original}.bbl')):
                os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'bibtex  {main_file_original}.aux'); os.chdir(current_dir)
            if not os.path.exists(pj(work_folder_modified, f'{main_file_modified}.bbl')):
                os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'bibtex  {main_file_modified}.aux'); os.chdir(current_dir)

            yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 编译文献交叉引用 ...', chatbot, history)  # 刷新Gradio前端界面
            os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)

            if mode!='translate_zh':
                yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 使用latexdiff生成论文转化前后对比 ...', chatbot, history) # 刷新Gradio前端界面
                print(    f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/merge_diff.tex')
                ok = compile_latex_with_timeout(f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/merge_diff.tex')

                yield from update_ui_lastest_msg(f'尝试第 {n_fix}/{max_try} 次编译, 正在编译对比PDF ...', chatbot, history)   # 刷新Gradio前端界面
                os.chdir(work_folder); ok = compile_latex_with_timeout(f'pdflatex  -interaction=batchmode -file-line-error merge_diff.tex'); os.chdir(current_dir)
                os.chdir(work_folder); ok = compile_latex_with_timeout(f'bibtex    merge_diff.aux'); os.chdir(current_dir)
                os.chdir(work_folder); ok = compile_latex_with_timeout(f'pdflatex  -interaction=batchmode -file-line-error merge_diff.tex'); os.chdir(current_dir)
                os.chdir(work_folder); ok = compile_latex_with_timeout(f'pdflatex  -interaction=batchmode -file-line-error merge_diff.tex'); os.chdir(current_dir)

        # <--------------------->
        os.chdir(current_dir)

        # <---------- 检查结果 ----------->
        results_ = ""
        original_pdf_success = os.path.exists(pj(work_folder_original, f'{main_file_original}.pdf'))
        modified_pdf_success = os.path.exists(pj(work_folder_modified, f'{main_file_modified}.pdf'))
        diff_pdf_success     = os.path.exists(pj(work_folder, f'merge_diff.pdf'))
        results_ += f"原始PDF编译是否成功: {original_pdf_success};" 
        results_ += f"转化PDF编译是否成功: {modified_pdf_success};" 
        results_ += f"对比PDF编译是否成功: {diff_pdf_success};" 
        yield from update_ui_lastest_msg(f'第{n_fix}编译结束:<br/>{results_}...', chatbot, history) # 刷新Gradio前端界面

        if modified_pdf_success:
            yield from update_ui_lastest_msg(f'转化PDF编译已经成功, 即将退出 ...', chatbot, history)    # 刷新Gradio前端界面
            os.chdir(current_dir)
            result_pdf = pj(work_folder_modified, f'{main_file_modified}.pdf')
            if os.path.exists(pj(work_folder, '..', 'translation')):
                shutil.copyfile(result_pdf, pj(work_folder, '..', 'translation', 'translate_zh.pdf'))
            promote_file_to_downloadzone(result_pdf, rename_file=None, chatbot=chatbot)
            return True # 成功啦
        else:
            if n_fix>=max_try: break
            n_fix += 1
            can_retry, main_file_modified, buggy_lines = remove_buggy_lines(
                file_path=pj(work_folder_modified, f'{main_file_modified}.tex'), 
                log_path=pj(work_folder_modified, f'{main_file_modified}.log'),
                tex_name=f'{main_file_modified}.tex',
                tex_name_pure=f'{main_file_modified}',
                n_fix=n_fix,
                work_folder_modified=work_folder_modified,
            )
            yield from update_ui_lastest_msg(f'由于最为关键的转化PDF编译失败, 将根据报错信息修正tex源文件并重试, 当前报错的latex代码处于第{buggy_lines}行 ...', chatbot, history)   # 刷新Gradio前端界面
            if not can_retry: break

    os.chdir(current_dir)
    return False # 失败啦




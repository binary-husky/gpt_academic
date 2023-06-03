from toolbox import update_ui, update_ui_lastest_msg    # 刷新Gradio前端界面
from toolbox import zip_folder, objdump, objload
import os
import re
pj = os.path.join

def 寻找Latex主文件(file_manifest, mode):
    """
    在多Tex文档中，寻找主文件，必须包含documentclass，返回找到的第一个。
    P.S. 但愿没人把latex模板放在里面传进来
    """
    for texf in file_manifest:
        if os.path.basename(texf).startswith('merge'):
            continue
        with open(texf, 'r', encoding='utf8') as f:
            file_content = f.read()
        if r'\documentclass' in file_content:
            return texf
        else:
            continue
    raise RuntimeError('无法找到一个主Tex文件（包含documentclass关键字）')

def merge_tex_files_(project_foler, main_file, mode):
    """
    递归地把多Tex工程整合为一个Tex文档
    """
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
    递归地把多Tex工程整合为一个Tex文档（递归外层）
    P.S. 顺便把CTEX塞进去以支持中文
    P.S. 顺便把Latex的注释去除
    """
    main_file = merge_tex_files_(project_foler, main_file, mode)
    if mode == 'translate_zh':
        pattern = re.compile(r'\\documentclass.*\n')
        match = pattern.search(main_file)
        position = match.end()
        main_file = main_file[:position] + '\\usepackage{CTEX}\n\\usepackage{url}\n' + main_file[position:]

    new_file_remove_comment_lines = []
    for l in main_file.splitlines():
        # 删除整行的空注释
        if l.startswith("%") or (l.startswith(" ") and l.lstrip().startswith("%")):
            pass
        else:
            new_file_remove_comment_lines.append(l)
    main_file = '\n'.join(new_file_remove_comment_lines)
    main_file = re.sub(r'(?<!\\)%.*', '', main_file)  # 使用正则表达式查找半行注释, 并替换为空字符串
    return main_file


class LinkedListNode():
    """
    链表单元
    """
    def __init__(self, string, preserve=True) -> None:
        self.string = string
        self.preserve = preserve
        self.next = None


def mod_inbraket(match):
    """
    为啥chatgpt会把cite里面的逗号换成中文逗号呀 艹
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
    final_tex = final_tex.replace('%', r'\%')
    final_tex = final_tex.replace(r'\%', r'\\%')
    final_tex = re.sub(r"\\([a-z]{2,10})\ \{", r"\\\1{", string=final_tex)
    final_tex = re.sub(r"\\\ ([a-z]{2,10})\{", r"\\\1{", string=final_tex)
    final_tex = re.sub(r"\\([a-z]{2,10})\{([^\}]*?)\}", mod_inbraket, string=final_tex)
    return final_tex

class LatexPaperSplit():
    """
    将Latex文档分解到一个链表中，每个链表节点用preserve的标志位提示它是否应当被GPT处理
    """
    def __init__(self) -> None:
        """
        root是链表的根节点
        """
        self.root = None

    def merge_result(self, arr, mode, msg):
        """
        将GPT处理后的结果融合
        """
        result_string = ""
        node = self.root
        p = 0
        while True:
            if node.preserve:
                result_string += node.string
            else:
                result_string += fix_content(arr[p], node.string)
                p += 1
            node = node.next
            if node is None: break
        if mode == 'translate_zh':
            try:
                pattern = re.compile(r'\\begin\{abstract\}.*\n')
                match = pattern.search(result_string)
                position = match.end()
                result_string = result_string[:position] + \
                    "\\textbf{警告：该PDF由GPT-Academic开源项目调用大语言模型+Latex翻译插件一键生成，其内容可靠性没有任何保障，请仔细鉴别并以原文为准。" + \
                    "项目Github地址 \\url{https://github.com/binary-husky/gpt_academic/}。"            + \
                    msg + \
                    "为了防止大语言模型的意外谬误产生扩散影响，禁止移除或修改此警告。}\\\\"    + \
                    result_string[position:]
            except:
                pass
        return result_string

    def split(self, txt):
        """
        将Latex文档分解到一个链表中，每个链表节点用preserve的标志位提示它是否应当被GPT处理
        """
        root = LinkedListNode(txt, False)
        def split_worker(root, pattern, flags=0):
            lt = root
            cnt = 0
            while True:
                if not lt.preserve:
                    while True:
                        res = re.search(pattern, lt.string, flags)
                        if not res: break
                        before = res.string[:res.span()[0]]
                        this = res.group(0)
                        # core = res.group(1)
                        after = res.string[res.span()[1]:]
                        # ======
                        if before.endswith('\n'):
                            this = '\n' + this
                            before = before[:-1]
                        if after.startswith('\n'):
                            # move \n
                            this = this + '\n'
                            after = after[1:]
                        # ======
                        lt.string = before
                        tmp  = lt.next
                        # ======
                        mid = LinkedListNode(this, True)
                        lt.next = mid
                        # ======
                        aft = LinkedListNode(after, False)
                        mid.next = aft
                        aft.next = tmp
                        # ======
                        lt = aft
                lt = lt.next
                cnt += 1
                # print(cnt)
                if lt is None: break

        # root 是链表的头
        print('正在分解Latex源文件，构建链表结构')
        split_worker(root, r"(.*?)\\maketitle", re.DOTALL)
        split_worker(root, r"\\section\{(.*?)\}")
        split_worker(root, r"\\subsection\{(.*?)\}")
        split_worker(root, r"\\subsubsection\{(.*?)\}")
        split_worker(root, r"\\bibliography\{(.*?)\}")
        split_worker(root, r"\\bibliographystyle\{(.*?)\}")
        split_worker(root, r"\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}", re.DOTALL)
        split_worker(root, r"\\begin\{algorithm\}(.*?)\\end\{algorithm\}", re.DOTALL)
        split_worker(root, r"\\begin\{wrapfigure\}(.*?)\\end\{wrapfigure\}", re.DOTALL)
        split_worker(root, r"\\begin\{wrapfigure\*\}(.*?)\\end\{wrapfigure\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{figure\}(.*?)\\end\{figure\}", re.DOTALL)
        split_worker(root, r"\\begin\{figure\*\}(.*?)\\end\{figure\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{table\}(.*?)\\end\{table\}", re.DOTALL)
        split_worker(root, r"\\begin\{table\*\}(.*?)\\end\{table\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{minipage\}(.*?)\\end\{minipage\}", re.DOTALL)
        split_worker(root, r"\\begin\{minipage\*\}(.*?)\\end\{minipage\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{align\*\}(.*?)\\end\{align\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{align\}(.*?)\\end\{align\}", re.DOTALL)
        split_worker(root, r"\\begin\{equation\}(.*?)\\end\{equation\}", re.DOTALL)
        split_worker(root, r"\\begin\{equation\*\}(.*?)\\end\{equation\*\}", re.DOTALL)
        split_worker(root, r"\$\$(.*?)\$\$", re.DOTALL)
        split_worker(root, r"\\item ")
        split_worker(root, r"\\begin\{(.*?)\}")
        split_worker(root, r"\\end\{(.*?)\}")

        res = []
        node = root
        while True:
            res.append((node.string, node.preserve))
            if len(node.string.strip('\n').strip(''))==0: node.preserve = True
            if len(node.string.strip('\n').strip(''))<50: node.preserve = True
            node = node.next
            if node is None: break

        # 将分解结果返回 res_to_t
        with open('debug_log.html', 'w', encoding='utf8') as f:
            res_to_t = []
            node = root
            while True:
                show_html = node.string.replace('\n','<br/>')
                if not node.preserve:
                    res_to_t.append(node.string)
                    f.write(f'<p style="color:black;">{show_html}</p>')
                else:
                    f.write(f'<p style="color:red;">{show_html}</p>')
                node = node.next
                if node is None: break

        self.root = root
        self.sp = res_to_t
        return self.sp

class LatexPaperFileGroup():
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
        将长文本分离开来
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
    
    def zip_result(self):
        import os, time
        folder = os.path.dirname(self.file_paths[0])
        t = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        zip_folder(folder, './gpt_log/', f'{t}-polished.zip')



def Latex精细分解与转化(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, mode='proofread', switch_prompt=None):
    import time, os, re
    from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
    from .latex_utils import LatexPaperFileGroup, merge_tex_files, LatexPaperSplit, 寻找Latex主文件

    #  <-------- 寻找主tex文件 ----------> 
    maintex = 寻找Latex主文件(file_manifest, mode)
    chatbot.append((f"定位主Latex文件", f'[Local Message] 分析结果：该项目的Latex主文件是{maintex}, 如果分析错误, 请立即终止程序, 删除或修改歧义文件, 然后重试。主程序即将开始, 请稍候。'))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    time.sleep(5)

    #  <-------- 读取Latex文件, 将多文件tex工程融合为一个巨型tex ----------> 
    with open(maintex, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        merged_content = merge_tex_files(project_folder, content, mode)

    with open(project_folder + '/merge.tex', 'w', encoding='utf-8', errors='replace') as f:
        f.write(merged_content)

    #  <-------- 精细切分latex文件 ----------> 
    lps = LatexPaperSplit()
    res = lps.split(merged_content)

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


    #  <-------- 写出文件 ----------> 
    msg = f"当前大语言模型: {llm_kwargs['llm_model']}，当前语言模型温度设定: {llm_kwargs['temperature']}。"
    final_tex = lps.merge_result(pfg.file_result, mode, msg)
    with open(project_folder + f'/merge_{mode}.tex', 'w', encoding='utf-8', errors='replace') as f:
        f.write(final_tex)

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
        return False, 0, [0]
    

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
    print(stderr)
    return True

def 编译Latex差别(chatbot, history, main_file_original, main_file_modified, work_folder_original, work_folder_modified, work_folder):
    import os, time
    current_dir = os.getcwd()
    n_fix = 0
    chatbot.append([f"正在编译PDF文档", f'编译已经开始。当前工作路径为{work_folder}，如果程序停顿5分钟以上，则大概率是卡死在Latex里面了。不幸卡死时请直接去该路径下取回翻译结果，或者重启之后再度尝试 ...']); yield from update_ui(chatbot=chatbot, history=history)
    chatbot.append([f"正在编译PDF文档", '...']); yield from update_ui(chatbot=chatbot, history=history); time.sleep(1); chatbot[-1] = list(chatbot[-1]) # 刷新界面
    yield from update_ui_lastest_msg('编译已经开始...', chatbot, history)   # 刷新Gradio前端界面

    while True:
        import os
        # https://stackoverflow.com/questions/738755/dont-make-me-manually-abort-a-latex-compile-when-theres-an-error
        yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 编译原始PDF ...', chatbot, history)   # 刷新Gradio前端界面
        os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)

        yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 编译转化后的PDF ...', chatbot, history)   # 刷新Gradio前端界面
        os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)
        
        if ok:
            # 只有第二步成功，才能继续下面的步骤
            yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 编译BibTex ...', chatbot, history)    # 刷新Gradio前端界面
            os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'bibtex  {main_file_original}.aux'); os.chdir(current_dir)
            os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'bibtex  {main_file_modified}.aux'); os.chdir(current_dir)

            yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 编译文献交叉引用 ...', chatbot, history)  # 刷新Gradio前端界面
            os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_original); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_original}.tex'); os.chdir(current_dir)
            os.chdir(work_folder_modified); ok = compile_latex_with_timeout(f'pdflatex -interaction=batchmode -file-line-error {main_file_modified}.tex'); os.chdir(current_dir)

            yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 使用latexdiff生成论文转化前后对比 ...', chatbot, history) # 刷新Gradio前端界面
            print(    f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/merge_diff.tex')
            ok = compile_latex_with_timeout(f'latexdiff --encoding=utf8 --append-safecmd=subfile {work_folder_original}/{main_file_original}.tex  {work_folder_modified}/{main_file_modified}.tex --flatten > {work_folder}/merge_diff.tex')

            yield from update_ui_lastest_msg(f'尝试第{n_fix}次编译, 正在编译对比PDF ...', chatbot, history)   # 刷新Gradio前端界面
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
            return True # 成功啦
        else:
            if n_fix>=7: break
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




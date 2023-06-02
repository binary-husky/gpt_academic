from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder
import os
import re

def 寻找Latex主文件(file_manifest, mode):
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
    for s in reversed([q for q in re.finditer(r"\\input\{(.*?)\}", main_file, re.M)]):
        f = s.group(1)
        fp = os.path.join(project_foler, f)
        with open(fp, 'r', encoding='utf-8', errors='replace') as fx:
            c = fx.read()
        c = merge_tex_files_(project_foler, c, mode)
        main_file = main_file[:s.span()[0]] + c + main_file[s.span()[1]:]
    return main_file

def merge_tex_files(project_foler, main_file, mode):
    main_file = merge_tex_files_(project_foler, main_file, mode)

    if mode == 'translate_zh':
        pattern = re.compile(r'\\documentclass.*\n')
        match = pattern.search(main_file)
        position = match.end()
        main_file = main_file[:position] + '\\usepackage{CTEX}\n' + main_file[position:]

    return main_file

class LinkTable():
    def __init__(self, string, preserve=True) -> None:
        self.string = string
        self.preserve = preserve
        self.next = None

def mod_inbraket(match):
    # get the matched string
    cmd = match.group(1)
    str_to_modify = match.group(2)

    # modify the matched string
    str_to_modify = str_to_modify.replace('：', ':')
    str_to_modify = str_to_modify.replace('，', ',')
    # str_to_modify = 'BOOM'
    # return the modified string as the replacement
    return "\\" + cmd + "{" + str_to_modify + "}"

def fix_content(final_tex):
    """
        fix common GPT errors to increase success rate
    """
    final_tex = final_tex.replace('%', r'\%')
    final_tex = final_tex.replace(r'\%', r'\\%')
    final_tex = re.sub(r"\\([a-z]{2,10})\ \{", r"\\\1{", string=final_tex)
    final_tex = re.sub(r"\\([a-z]{2,10})\{([^\}]*?)\}", mod_inbraket, string=final_tex)
    return final_tex

class LatexPaperSplit():
    def __init__(self) -> None:
        self.root = None

    def merge_result(self, arr):
        result_string = ""
        node = self.root
        p = 0
        while True:
            if node.preserve:
                result_string += node.string
            else:
                result_string += fix_content(arr[p])
                p += 1
            node = node.next
            if node is None: break

        return result_string

    def split(self, txt):
        # def replace_with_hash()
        root = LinkTable(txt, False)
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
                        mid = LinkTable(this, True)
                        lt.next = mid
                        # ======
                        aft = LinkTable(after, False)
                        mid.next = aft
                        aft.next = tmp
                        # ======
                        lt = aft
                lt = lt.next
                cnt += 1
                print(cnt)
                if lt is None: break

        # root 是链表的头
        print('正在分解Latex源文件')
        split_worker(root, r"(.*?)\\maketitle", re.DOTALL)
        split_worker(root, r"\\section\{(.*?)\}")
        split_worker(root, r"\\subsection\{(.*?)\}")
        split_worker(root, r"\\subsubsection\{(.*?)\}")
        split_worker(root, r"\\begin\{figure\}(.*?)\\end\{figure\}", re.DOTALL)
        split_worker(root, r"\\begin\{figure\*\}(.*?)\\end\{figure\*\}", re.DOTALL)
        split_worker(root, r"\\begin\{table\}(.*?)\\end\{table\}", re.DOTALL)
        split_worker(root, r"\\begin\{table\*\}(.*?)\\end\{table\*\}", re.DOTALL)
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

        with open('debug_log', 'w', encoding='utf8') as f:
            res_to_t = []
            node = root
            while True:
                if not node.preserve:
                    res_to_t.append(node.string)
                    f.write(node.string + '\n ========================= \n')
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

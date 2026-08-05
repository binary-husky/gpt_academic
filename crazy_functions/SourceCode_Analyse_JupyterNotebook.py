from toolbox import update_ui
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
fast_debug = True


class PaperFileGroup():
    def __init__(self):
        self.file_paths = []
        self.file_contents = []
        self.sp_file_contents = []
        self.sp_file_index = []
        self.sp_file_tag = []

        # count_token
        from request_llms.bridge_all import model_info
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
                from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
                segments = breakdown_text_to_satisfy_token_limit(file_content, max_token_limit)
                for j, segment in enumerate(segments):
                    self.sp_file_contents.append(segment)
                    self.sp_file_index.append(index)
                    self.sp_file_tag.append(
                        self.file_paths[index] + f".part-{j}.txt")



def parseNotebook(filename, enable_markdown=1):
    import json

    CodeBlocks = []
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        notebook = json.load(f)
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and cell['source']:
            # remove blank lines
            cell['source'] = [line for line in cell['source'] if line.strip()
                              != '']
            CodeBlocks.append("".join(cell['source']))
        elif enable_markdown and cell['cell_type'] == 'markdown' and cell['source']:
            cell['source'] = [line for line in cell['source'] if line.strip()
                              != '']
            CodeBlocks.append("Markdown:"+"".join(cell['source']))

    Code = ""
    for idx, code in enumerate(CodeBlocks):
        Code += f"This is {idx+1}th code block: \n"
        Code += code+"\n"

    return Code


def ipynb解释(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    from crazy_functions.crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency

    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    enable_markdown = plugin_kwargs.get("advanced_arg", "1")
    try:
        enable_markdown = int(enable_markdown)
    except ValueError:
        enable_markdown = 1

    pfg = PaperFileGroup()

    for fp in file_manifest:
        file_content = parseNotebook(fp, enable_markdown=enable_markdown)
        pfg.file_paths.append(fp)
        pfg.file_contents.append(file_content)

    #  <-------- 拆分过长的IPynb文件 ---------->
    pfg.run_file_split(max_token_limit=1024)
    n_split = len(pfg.sp_file_contents)

    inputs_array = [r"This is a Jupyter Notebook file, tell me about Each Block in Chinese. Focus Just On Code." +
                    r"If a block starts with `Markdown` which means it's a markdown block in ipynbipynb. " +
                    r"Start a new line for a block and block num use Chinese." +
                    f"\n\n{frag}" for frag in pfg.sp_file_contents]
    inputs_show_user_array = [f"{f}的分析如下" for f in pfg.sp_file_tag]
    sys_prompt_array = ["You are a professional programmer."] * n_split

    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(n_split)],
        sys_prompt_array=sys_prompt_array,
        # max_workers=5,  # OpenAI所允许的最大并行过载
        scroller_max_len=80
    )

    #  <-------- 整理结果，退出 ---------->
    block_result = "  \n".join(gpt_response_collection)
    chatbot.append(("解析的结果如下", block_result))
    history.extend(["解析的结果如下", block_result])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    #  <-------- 写入文件，退出 ---------->
    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    chatbot.append(("完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

@CatchException
def 解析ipynb文件(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    chatbot.append([
        "函数插件功能？",
        "对IPynb文件进行解析。Contributor: codycjy."])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    history = []    # 清空历史
    import glob
    import os
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "":
            txt = '空空如也的输入栏'
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return
    if txt.endswith('.ipynb'):
        file_manifest = [txt]
    else:
        file_manifest = [f for f in glob.glob(
            f'{project_folder}/**/*.ipynb', recursive=True)]
    if len(file_manifest) == 0:
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}", b=f"找不到任何.ipynb文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return
    yield from ipynb解释(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, )

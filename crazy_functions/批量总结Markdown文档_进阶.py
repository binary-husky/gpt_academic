import logging, os
from toolbox import update_ui, promote_file_to_downloadzone, gen_time_str, get_log_folder
from toolbox import CatchException, report_exception, trimmed_format_exc
from toolbox import write_history_to_file, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
from .crazy_utils import input_clipping


def 总结Markdown(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    file_write_buffer = []
    SUMMARY_WORD_LIMIT = 800
    meta_inputs_array = []
    meta_inputs_show_user_array = []
    meta_sys_prompt_array = []
    inputs_array = []
    inputs_show_user_array = []
    sys_prompt_array = []
    file_name_array = []
    for idx, file_name in enumerate(file_manifest):
        print('begin analysis on:', file_name)
        file_name_array.append(f'# {idx}.{os.path.basename(file_name)}')

        with open(file_name, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()

        _ = file_content.split('## metadata')
        if len(_) >= 2:
            file_meta = _[-2]
            file_content = _[-1]
        else:
            file_meta = file_name

        meta_inputs_array.append(
            "我需要你从一段文本中识别并提取出这篇文章的1.标题、2.作者、3.作者单位、4.关键词。"
            "其中，1.标题和4.关键词需要给出中文和英文的双语结果，2.作者和3.作者单位按原文语言给出。"
            "以下是需要你识别的文本: " + file_meta
        )
        meta_inputs_show_user_array.append(
            '开始分析元数据：' + file_name
        )
        meta_sys_prompt_array.append("As an academic professional, you need to extract basic informations of the paper from its metadata")

        inputs_array.append(
            "我需要你根据我提供的文本总结一份Markdown文档，分为四个部分：1.研究背景，2.文章主要内容，3.主要创新点，4.结论。"
            + f"各部分的题目采用二级标题前缀(## ),内容可适当的分为若干条，总字数不超过{SUMMARY_WORD_LIMIT}个中文字符."
            + "以下是需要你处理的文本: " + file_content)
        inputs_show_user_array.append('开始总结：' + file_name)
        sys_prompt_array.append(f"As an academic professional, you need to summarize the text with less than {SUMMARY_WORD_LIMIT} Chinese characters")

    gpt_meta_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=meta_inputs_array,
        inputs_show_user_array=meta_inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(len(inputs_array))],
        sys_prompt_array=meta_sys_prompt_array,
        # max_workers=5,  # OpenAI所允许的最大并行过载
        scroller_max_len=80
    )

    gpt_response_collection = yield from request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(len(inputs_array))],
        sys_prompt_array=sys_prompt_array,
        # max_workers=5,  # OpenAI所允许的最大并行过载
        scroller_max_len=80
    )
    try:
        for idx, (gpt_say_meta, gpt_say) in enumerate(zip(gpt_meta_response_collection[1::2], gpt_response_collection[1::2])):
            file_write_buffer.append(file_name_array[idx])
            file_write_buffer.append("## 元数据\n\n" + gpt_say_meta)
            file_write_buffer.append(gpt_say)
    except:
        logging.error(trimmed_format_exc())

    res = write_history_to_file(file_write_buffer, file_basename="result.md", auto_caption=False)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    yield from update_ui(chatbot=chatbot, history=gpt_response_collection) # 刷新界面


@CatchException
def 批量总结Markdown文档_进阶(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结Markdown文档。函数插件贡献者: ValeriaWong，Eralien，Joshua Reed"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_exception(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pymupdf```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.md', recursive=True)]
    
    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a = f"解析项目: {txt}", b = f"找不到任何.md文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 总结Markdown(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

from toolbox import update_ui, promote_file_to_downloadzone, gen_time_str
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import read_and_clean_pdf_text
from .crazy_utils import input_clipping



def pdfAnalyst(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    file_write_buffer = []
    for file_name in file_manifest:
        print('begin analysis on:', file_name)
        file_content, page_one = read_and_clean_pdf_text(file_name) 
        file_content = file_content.encode('utf-8', 'ignore').decode()   
        page_one = str(page_one).encode('utf-8', 'ignore').decode()  
        final_results = []
        iteration_results = []
        last_iteration_result = page_one  
        iteration_results.append(file_content)
        last_iteration_result = ""  
        final_results.extend(iteration_results)
        final_results.append(f'Please response by content above')
        if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
        i_say = plugin_kwargs.get("advanced_arg", "")
        i_say, final_results = input_clipping(i_say, final_results, max_token_limit=32000)
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=file_name, 
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=final_results, 
            sys_prompt= f"[Important]You need response in JSON format, Use NA if information is not found."
        )        
        final_results.append(gpt_say)
        file_write_buffer.append(gpt_say)
        _, final_results = input_clipping("", final_results, max_token_limit=32000)
        yield from update_ui(chatbot=chatbot, history=final_results)
    res = write_history_to_file(file_write_buffer)
    promote_file_to_downloadzone(res, chatbot=chatbot)



@CatchException
def pdfMinerPlus(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "Instruction and citation",
        "https://doi.org/10.3390/fi16050167"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import fitz
    except:
        report_exception(chatbot, history, 
            a = f"Parsing project: {txt}", 
            b = f"Failed to import software dependencies. Using this module requires additional dependencies.")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = 'Empty input field'
        report_exception(chatbot, history,
                         a=f"Parsing project: {txt}", b=f"Cannot find local project or do not have access: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.tex', recursive=True)] + \
                    [f for f in glob.glob(f'{project_folder}/**/*.pdf', recursive=True)] # + \
                    #[f for f in glob.glob(f'{project_folder}/**/*.pdf', recursive=True)]
    
    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history,
                         a=f"Parsing project: {txt}", b=f"Cannot find any .tex or .pdf files: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from pdfAnalyst(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)

#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
import json
import func_box
from crazy_functions import crazy_box
from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder
from crazy_functions import crazy_utils
from request_llm import bridge_all


@CatchException
def Kdocs_轻文档批量操作(link, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    link = str(link).split()
    links = []
    for i in link:
        if i.startswith('http'):
            links.append(i)
    if not links:
        chatbot.append((None, f'输入框空空如也？{link}\n\n'
                              '请在输入框中输入需要解析的轻文档链接，点击插件按钮，链接需要是可访问的，如以下格式，如果有多个文档则用换行或空格隔开'
                             f'\n\n【金山文档】 xxxx https://kdocs.cn/l/xxxxxxxxxx'
                             f'\n\n https://kdocs.cn/l/xxxxxxxxxx'))
        yield from update_ui(chatbot, history)
        return
    docs_file_content = []
    temp_num = 0
    for url in links:
        try:
            temp_num += 1
            chatbot.append([f'爬虫开始工作了！ {url}', None])
            content = crazy_box.get_docs_content(url)
            title = content.splitlines()[0]+f'_{temp_num}'
            docs_file_content.append({title: content})
            yield from update_ui(chatbot, history)
        except:
            chatbot.append([f'啊哦，爬虫歇菜了！ {url}', f'{func_box.html_a_blank(url)} 请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？'])
            yield from update_ui(chatbot, history)
    gpt_response_collection = yield from 需求转Markdown(docs_file_content, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    yield from 需求转测试用例(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)


def 需求转测试用例(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    prompt = """你是一个专业的测试工程师，请阅读以下三个双引号括起来需求文档，自己进行需求分析，编写测试用例\n\"\"\"{v}\""\""\"\n
编写用例时，请遵循以下条件：
划分测试场景：根据功能或模块的不同方面，划分出不同的测试场景,作为表头的功能点。
编写正向测试用例：编写测试用例以验证功能按预期工作的情况。确保输入和参数符合预期，执行操作后的输出正确。
编写负向测试用例：编写测试用例以验证功能处理异常情况的能力。例如，输入无效数据、输入超出范围的值或处理意外错误。
边界测试用例：在编写测试用例时，特别关注边界情况。例如，最大值、最小值、边界条件或临界值，以确保程序在这些情况下能正常工作。
非功能需求的专项测试用例：比如稳定性测试，兼容性测试，易用性测试等
考虑功能交互和集成：对于需要与其他功能或模块进行交互的部分，编写测试用例来验证其正确的集成和协作。
返回格式要求：
Markdown表格返回，表头标题：功能点｜验证点｜前置条件｜操作步骤｜预期结果, 如果没有前置条件，则使用一个空格占位
    """
    if type(file_limit) is list:
        inputs_array = [prompt.replace('{v}', inputs) for inputs in file_limit[1::2]]
        inputs_show_user_array = file_limit[0::2]
    elif type(file_limit) is str:
        inputs_array = [prompt.replace('{v}',file_limit)]
        inputs_show_user_array = [str(file_limit).splitlines()[0]]
    else:
        return
    gpt_response_collection = yield from crazy_utils.request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(len(inputs_array))],
        sys_prompt_array=["" for _ in range(len(inputs_array))],
        # max_workers=5,  # OpenAI所允许的最大并行过载
        scroller_max_len=80
    )
    kwargs_json = crazy_box.json_pars_true(plugin_kwargs['advanced_arg'])
    if kwargs_json:
        if kwargs_json['is_show']:
            for results in list(zip(gpt_response_collection[0::2], gpt_response_collection[1::2])):
                chatbot.append(results)
                history.extend(results)
                yield from update_ui(chatbot, history)
    gpt_response = gpt_response_collection[1::2]
    chat_file_list = ''
    for k in range(len(gpt_response)):
        test_case = []
        for i in gpt_response[k].splitlines():
            test_case.append(i.split('|')[1:])
        file_path = crazy_box.ExcelHandle(ipaddr=llm_kwargs['ipaddr']).lpvoid_lpbuffe(test_case[2:], filename=inputs_show_user_array[k])
        chat_file_list += f'{inputs_show_user_array[k]}生成结果如下:\t {func_box.html_download_blank(__href=file_path, file_name=file_path.split("/")[-1])}\n\n'
    chatbot.append(['Done', chat_file_list])
    yield from update_ui(chatbot, history)


def split_dict_limit(file_limit: list, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    model = llm_kwargs['llm_model']
    max_length = llm_kwargs['max_length']/2  # 考虑到对话+回答会超过tokens,所以/2
    get_token_num = bridge_all.model_info[model]['token_cnt']
    temp_dict_limit = {}
    temp_chat_context = ''
    # 分批次+分词
    prompt = '以上三个双引号内的需求文档请使用Markdown格式进行段落排版，我不需要你的任何建议或提示，你只需要将我提供的文档转换为Markdown格式并返回给我。'
    prompt_us = "Please use Markdown format for paragraph layout for the above three double-quoted requirement documents. I don't need any suggestions or tips from you, you just need to convert the text I provide to Markdown format and return it to me."
    for job_dict in file_limit:
        for k, v in job_dict.items():
            temp_chat_context += f'{func_box.html_tag_color(k)} 开始分词,分好词才能避免对话超出tokens错误...\n\n'
            chatbot[-1] = [chatbot[-1][0], temp_chat_context]
            if get_token_num(v) > max_length:
                temp_chat_context += f'{func_box.html_tag_color(k)} 超过tokens限制...准备拆分后再提交\n\n'
                chatbot[-1] = [chatbot[-1][0], temp_chat_context]
                segments = crazy_utils.breakdown_txt_to_satisfy_token_limit(v, get_token_num, max_length)
                for i in range(len(segments)):
                    temp_dict_limit[k+f'_{i}'] = f'"""{segments[i]}""""\n{prompt}'
            else:
                temp_dict_limit[k] = f'"""\n{v}\n""""\n{prompt}'
                temp_chat_context += f'{func_box.html_tag_color(k)} 准备就绪...\n\n'
                chatbot[-1] = [chatbot[-1][0], temp_chat_context]
    yield from update_ui(chatbot, history)
    inputs_array, inputs_show_user_array = list(temp_dict_limit.values()), list(temp_dict_limit.keys())
    return inputs_array, inputs_show_user_array


def 需求转Markdown(file_limit: list, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # 分词
    inputs_array, inputs_show_user_array = yield from split_dict_limit(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    # 提交多线程任务
    gpt_response_collection = yield from crazy_utils.request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array=inputs_array,
        inputs_show_user_array=inputs_show_user_array,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history_array=[[""] for _ in range(len(inputs_array))],
        sys_prompt_array=["" for _ in range(len(inputs_array))],
        # max_workers=5,  # OpenAI所允许的最大并行过载
        scroller_max_len=80
    )
    # 展示任务结果
    kwargs_json = crazy_box.json_pars_true(plugin_kwargs['advanced_arg'])
    if kwargs_json:
        if kwargs_json['is_show']:
            for results in list(zip(gpt_response_collection[0::2], gpt_response_collection[1::2])):
                chatbot.append(results)
                history.extend(results)
                yield from update_ui(chatbot, history)
    return gpt_response_collection




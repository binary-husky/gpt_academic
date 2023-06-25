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
import prompt_generator


def Kdocs_轻文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    link = str(link_limit).split()
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
            chatbot.append([link_limit, None])
            ovs_data, content, empty_picture_count = crazy_box.get_docs_content(url)
            title = content.splitlines()[0]
            if empty_picture_count > 5:
                chatbot[-1][1] = f'\n\n 需求文档中没有{func_box.html_tag_color("描述")}的图片数量' \
                                  f'有{func_box.html_tag_color(empty_picture_count)}张，生成的测试用例可能存在遗漏点，可以参考以下对图片进行描述补充\n\n' \
                                  f'{func_box.html_local_img("docs/imgs/pic_desc.png")}'
            docs_file_content.append({title: content})
            yield from update_ui(chatbot, history)
        except Exception as e:
            chatbot.append([None, f'{func_box.html_a_blank(url)} \n\n请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？\n\n ```\n{str(e)}\n```'])
            yield from update_ui(chatbot, history)
    return docs_file_content


@CatchException
def KDocs_转测试用例(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    if gpt_response_collection == []:
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    yield from 需求转测试用例(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)


@CatchException
def KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    docs_file_content = yield from Kdocs_轻文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    gpt_response_collection = yield from 需求转Markdown(docs_file_content, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    return gpt_response_collection


@CatchException
def 需求转测试用例(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    kwargs_is_show,  kwargs_prompt = crazy_box.json_args_return(plugin_kwargs['advanced_arg'], ['is_show', 'prompt'])
    if not kwargs_prompt: kwargs_prompt = '文档转测试用例'
    prompt = prompt_generator.SqliteHandle(table=f'prompt_{llm_kwargs["ipaddr"]}').find_prompt_result(kwargs_prompt)
    chatbot.append([f'接下来使用的Prompt是 {func_box.html_tag_color(kwargs_prompt)} ，你可以在Prompt编辑/检索中进行私人定制哦～', None])
    yield from update_ui(chatbot, history)
    if type(file_limit) is list:
        inputs_array = [prompt.replace('{{{v}}}', inputs) for inputs in file_limit[1::2]]
        inputs_show_user_array = file_limit[0::2]
    elif type(file_limit) is str:
        if file_limit: 
            inputs_show_user_array = [str(file_limit).splitlines()[0]]
            inputs_array = [prompt.replace('{v}',file_limit)]
        else:
            chatbot.append((None, f'输入框空空如也？\n\n'
                                '请在输入框中输入你的需求文档，然后再点击需求转测试用例'))
            yield from update_ui(chatbot, history)
            return
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
    if kwargs_is_show:
        for results in list(zip(gpt_response_collection[0::2], gpt_response_collection[1::2])):
            chatbot.append(results)
            history.extend(results)
            yield from update_ui(chatbot, history)
    gpt_response = gpt_response_collection[1::2]
    chat_file_list = ''
    for k in range(len(gpt_response)):
        test_case = []
        for i in gpt_response[k].splitlines():
            test_case.append([func_box.clean_br_string(i) for i in i.split('|')[1:]])
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
    kwargs_prompt = '文档转Markdown'
    prompt = prompt_generator.SqliteHandle(table=f'prompt_{llm_kwargs["ipaddr"]}').find_prompt_result(kwargs_prompt)
    chatbot.append([f'接下来使用的Prompt是 {func_box.html_tag_color(kwargs_prompt)} ，你可以在Prompt编辑/检索中进行私人定制哦～', None])
    yield from update_ui(chatbot, history)
    for job_dict in file_limit:
        for k, v in job_dict.items():
            temp_chat_context += f'{func_box.html_tag_color(k)} 开始分词,分好词才能避免对话超出tokens错误...\n\n'
            chatbot[-1] = [chatbot[-1][0], temp_chat_context]
            if get_token_num(v) > max_length:
                temp_chat_context += f'{func_box.html_tag_color(k)} 超过tokens限制...准备拆分后再提交\n\n'
                chatbot[-1] = [chatbot[-1][0], temp_chat_context]
                segments = crazy_utils.breakdown_txt_to_satisfy_token_limit(v, get_token_num, max_length)
                for i in range(len(segments)):
                    temp_dict_limit[k+f'_{i}'] = prompt.replace('{{{v}}}', segments[i])
            else:
                temp_dict_limit[k] = prompt.replace('{{{v}}}', v)
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
    kwargs_is_show,  = crazy_box.json_args_return(plugin_kwargs['advanced_arg'], ['is_show'])
    if kwargs_is_show:
        for results in list(zip(gpt_response_collection[0::2], gpt_response_collection[1::2])):
            chatbot.append(results)
            history.extend(results)
            yield from update_ui(chatbot, history)
    return gpt_response_collection




#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
import json
import time

import func_box
from crazy_functions import crazy_box
from toolbox import update_ui, trimmed_format_exc
from toolbox import CatchException, report_execption, write_results_to_file, zip_folder
from crazy_functions import crazy_utils
from request_llm import bridge_all
import prompt_generator
import traceback


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
    file_limit = []
    for url in links:
        try:
            chatbot.append([link_limit+"\n\n网页爬虫准备工作中～", None])
            yield from update_ui(chatbot, history)  #增加中间过渡
            ovs_data, content, empty_picture_count, pic_dict = crazy_box.get_docs_content(url)
            title = content.splitlines()[0]
            if empty_picture_count >= 5:
                chatbot.append([None, f'\n\n 需求文档中没有{func_box.html_tag_color("描述")}的图片数量' \
                                  f'有{func_box.html_tag_color(empty_picture_count)}张，生成的测试用例可能存在遗漏点，可以参考以下方法对图片进行描述补充\n\n' \
                                  f'{func_box.html_local_img("docs/imgs/pic_desc.png")}'])
            file_limit.extend([title, content])
            yield from update_ui(chatbot, history)
            time.sleep(1)
        except Exception as e:
            error_str = traceback.format_exc()
            chatbot.append([None, f'{func_box.html_a_blank(url)} \n\n请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？是否是轻文档？下面是什么错误？\n\n ```\n{str(error_str)}\n```'])
            yield from update_ui(chatbot, history)
    return file_limit

def long_name_processing(file_name):
    if len(file_name) > 20:
        if file_name.find('""""') != -1:
            file_name = file_name.split('""""')[1].splitlines()[0]
        else:
            file_name = file_name[:20]
    return file_name


def write_test_cases(gpt_response_collection, inputs_show_user_array, llm_kwargs, chatbot, history):
    gpt_response = gpt_response_collection[1::2]
    chat_file_list = ''
    for k in range(len(gpt_response)):
        file_name = long_name_processing(inputs_show_user_array[k])
        test_case = []
        for i in gpt_response[k].splitlines():
            test_case.append([func_box.clean_br_string(i) for i in i.split('|')[1:]])
        file_path = crazy_box.ExcelHandle(ipaddr=llm_kwargs['ipaddr']).lpvoid_lpbuffe(test_case[2:], filename=file_name)
        chat_file_list += f'{file_name}生成结果如下:\t {func_box.html_download_blank(__href=file_path, file_name=file_path.split("/")[-1])}\n\n'
    chatbot.append(['Done', chat_file_list])
    yield from update_ui(chatbot, history)


def split_content_limit(inputs: str, llm_kwargs, chatbot, history) -> list:
    model = llm_kwargs['llm_model']
    max_length = llm_kwargs['max_length']/2  # 考虑到对话+回答会超过tokens,所以/2
    get_token_num = bridge_all.model_info[model]['token_cnt']
    if get_token_num(inputs) > max_length:
        chatbot.append(None, f'{func_box.html_tag_color(inputs[:10])}...对话预计超出tokens限制, 拆分中...')
        yield from update_ui(chatbot, history)
        segments = crazy_utils.breakdown_txt_to_satisfy_token_limit(inputs, get_token_num, max_length)
    else:
        segments = [inputs]
    return segments


def input_output_processing(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history, default_prompt: str = False, all_chat: bool = True):
    """
    Args:
        gpt_response_collection:  多线程GPT的返回结果
        plugin_kwargs: 对话使用的插件参数
        llm_kwargs:  对话+用户信息
        default_prompt: 默认Prompt, 如果为False，则不添加提示词
    Returns: 下次使用？
        inputs_array， inputs_show_user_array
    """
    inputs_array = []
    inputs_show_user_array = []
    kwargs_prompt, = crazy_box.json_args_return(plugin_kwargs, ['prompt'])
    if default_prompt: kwargs_prompt = default_prompt
    chatbot.append([f'接下来使用的Prompt是 {func_box.html_tag_color(kwargs_prompt)} ，你可以在Prompt编辑/检索中进行私人定制哦～',None])
    prompt = prompt_generator.SqliteHandle(table=f'prompt_{llm_kwargs["ipaddr"]}').find_prompt_result(kwargs_prompt)
    for inputs, you_say in zip(gpt_response_collection[1::2], gpt_response_collection[0::2]):
        content_limit = yield from split_content_limit(inputs, llm_kwargs, chatbot, history)
        for limit in content_limit:
            inputs_array.append(prompt.replace('{{{v}}}', limit))
            inputs_show_user_array.append(you_say)
    yield from update_ui(chatbot, history)
    if all_chat:
        inputs_show_user_array = inputs_array
    else:
        inputs_show_user_array = default_prompt + ': ' + gpt_response_collection[0::2]
    return inputs_array, inputs_show_user_array


def submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs):
    # 提交多线程任务
    if len(inputs_array) == 1:
        yield from bridge_all.predict(inputs_array[0], llm_kwargs, plugin_kwargs, chatbot, history)
        gpt_response_collection = [inputs_show_user_array[0], history[-1]]
        # 下面的方法有内存泄漏?的风险（加载完所有数据后，还在不知道轮询什么东西），暂时屏蔽
        # gpt_say = yield from crazy_utils.request_gpt_model_in_new_thread_with_ui_alive(
        #     inputs=inputs_array[0], inputs_show_user=inputs_array[0],
        #     llm_kwargs=llm_kwargs, chatbot=chatbot, history=[],
        #     sys_prompt="" , refresh_interval=0.1
        # )
        # gpt_response_collection = [inputs_show_user_array[0], gpt_say]
        # history.extend(gpt_response_collection)
    else:
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
        # 是否展示任务结果
        kwargs_is_show,  = crazy_box.json_args_return(plugin_kwargs, ['is_show'])
        if kwargs_is_show:
            for results in list(zip(gpt_response_collection[0::2], gpt_response_collection[1::2])):
                chatbot.append(results)
                history.extend(results)
                yield from update_ui(chatbot, history)
    return gpt_response_collection


def KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_limit = yield from Kdocs_轻文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    if not file_limit:
        yield from update_ui(chatbot=chatbot, history=history, msg='无法获取需求文档内容，暂停运行')
        return
    kwargs_to_mark, = crazy_box.json_args_return(plugin_kwargs, ['to_markdown'])
    if kwargs_to_mark:
        inputs_array, inputs_show_user_array = yield from input_output_processing(file_limit, llm_kwargs, plugin_kwargs,
                                                                           chatbot, history, default_prompt='文档转Markdown')
        gpt_response_collection = yield from submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs)
    else: gpt_response_collection = file_limit
    return gpt_response_collection


@CatchException
def 需求转测试用例(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    if file_limit:
        inputs_show_user_array = [str(file_limit).splitlines()[0]]
        file_limit = [inputs_show_user_array, file_limit]
        inputs_array, inputs_show_user_array = yield from input_output_processing(file_limit, llm_kwargs, plugin_kwargs,
                                                                       chatbot, history)
    else:
        chatbot.append((None, f'输入框空空如也？\n\n'
                            '请在输入框中输入你的需求文档，然后再点击需求转测试用例'))
        yield from update_ui(chatbot, history)
        return
    gpt_response_collection = yield from submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs)
    write_test_cases(gpt_response_collection, inputs_show_user_array, llm_kwargs, chatbot, history)


@CatchException
def KDocs_转测试用例(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    if not gpt_response_collection:
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    inputs_array, inputs_show_user_array = yield from input_output_processing(gpt_response_collection, llm_kwargs, plugin_kwargs,
                                                                   chatbot, history)
    gpt_response_collection = yield from submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs)
    yield from write_test_cases(gpt_response_collection, inputs_show_user_array, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_需求分析问答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    if not gpt_response_collection:
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    inputs_array, inputs_show_user_array = yield from input_output_processing(gpt_response_collection, llm_kwargs, plugin_kwargs,
                                                                   chatbot, history)
    gpt_response_collection = yield from submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs)
    yield from update_ui(chatbot, history, '插件执行成功')

def transfer_flow_chart(gpt_response_collection, llm_kwargs, chatbot, history):
    for inputs, you_say in zip(gpt_response_collection[1::2], gpt_response_collection[0::2]):
        md, html, code = crazy_box.Utils().markdown_to_flow_chart(data=inputs, hosts=llm_kwargs['ipaddr'], file_name=long_name_processing(you_say))
        chatbot.append(("View", func_box.html_view_blank(md), '\n\n View: '+func_box.html_view_blank(html)))
        yield from update_ui(chatbot=chatbot, history=history, msg='成功写入文件！')

@CatchException
def KDocs_文档转流程图(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
    if not gpt_response_collection:
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    yield from transfer_flow_chart(gpt_response_collection, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


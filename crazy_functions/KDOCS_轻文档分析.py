#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
import os.path
import time
from comm_tools import func_box, ocr_tools
from crazy_functions import crazy_box
from comm_tools.toolbox import update_ui, CatchException
from crazy_functions import crazy_utils
import traceback


def Kdocs_轻文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    links = crazy_box.Utils().split_startswith_txt(link_limit)
    files = [file for file in link_limit if os.path.exists(file)]
    if not links and not files:
        chatbot.append((None, f'输入框空空如也？{link_limit}\n\n'
                              '请在输入框中输入需要解析的轻文档链接或Markdown文件目录地址，点击插件按钮，链接需要是可访问的，如以下格式，如果有多个文档则用换行或空格隔开'
                              f'\n\n【金山文档】 xxxx https://kdocs.cn/l/xxxxxxxxxx'
                              f'\n\n https://kdocs.cn/l/xxxxxxxxxx'))
        yield from update_ui(chatbot, history)
        return
    file_limit = []
    img_ocr, = crazy_box.json_args_return(plugin_kwargs, ['img_ocr'])
    for url in links:
        try:
            chatbot.append([link_limit + "\n\n网页爬虫和文件处理准备工作中～", None])
            yield from update_ui(chatbot, history)  # 增加中间过渡
            ovs_data, content, empty_picture_count, pic_dict = crazy_box.get_docs_content(url, image_processing=img_ocr)
            if img_ocr:
                if pic_dict:  # 当有图片文件时，再去提醒
                    ocr_process = f'检测到轻文档中存在{func_box.html_tag_color(empty_picture_count)}张图片，为了产出结果不存在遗漏，正在逐一进行识别\n\n' \
                                  f'> 红框为采用的文案,可信度低于 {func_box.html_tag_color(llm_kwargs["ocr"])} 将不采用, 可在Setting 中进行配置\n\n'
                    chatbot.append([None, ocr_process])
                else:
                    ocr_process = ''
                for i in pic_dict:
                    yield from update_ui(chatbot, history, '正在调用OCR组件，图片多可能会比较慢')
                    img_content, img_result = ocr_tools.Paddle_ocr_select(ipaddr=llm_kwargs['ipaddr'],
                                                                          trust_value=llm_kwargs[
                                                                              'ocr']).img_def_content(
                        img_path=pic_dict[i])
                    content = str(content).replace(f"{i}",
                                                   f"{func_box.html_local_img(img_result)}\n```{img_content}```")
                    ocr_process += f'{i} 识别完成，识别效果如下 {func_box.html_local_img(img_result)} \n\n'
                    chatbot[-1] = [None, ocr_process]
                    yield from update_ui(chatbot, history)
            else:
                if empty_picture_count >= 5:
                    chatbot.append([None, f'\n\n 需求文档中没有{func_box.html_tag_color("描述")}的图片数量' \
                                          f'有{func_box.html_tag_color(empty_picture_count)}张，生成的测试用例可能存在遗漏点，可以参考以下方法对图片进行描述补充，x\n\n' \
                                          f'{func_box.html_local_img("docs/imgs/pic_desc.png")}'])
                yield from update_ui(chatbot, history)
            title = content.splitlines()[0]
            file_limit.extend([title, content])
        except Exception as e:
            error_str = traceback.format_exc()
            chatbot.append([None,
                            f'{func_box.html_a_blank(url)} \n\n请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？是否是轻文档？下面是什么错误？\n\n ```\n\n{str(error_str)}\n```'])
            yield from update_ui(chatbot, history)
    yield from update_ui(chatbot, history)
    return file_limit


def KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_limit = yield from Kdocs_轻文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt,
                                                 web_port)
    if not file_limit:
        chatbot.append([None, f'{func_box.html_tag_color("无法获取需求文档内容，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='无法获取需求文档内容，暂停运行')
        return
    kwargs_to_mark, = crazy_box.json_args_return(plugin_kwargs, ['to_markdown'])
    if kwargs_to_mark:
        split_content_limit = yield from crazy_box.input_output_processing(file_limit, llm_kwargs,
                                                                                            plugin_kwargs,
                                                                                            chatbot, history,
                                                                                            default_prompt=kwargs_to_mark)
        inputs_array, inputs_show_user_array = split_content_limit
        gpt_response_collection = yield from crazy_box.submit_multithreaded_tasks(inputs_array, inputs_show_user_array,
                                                                                  llm_kwargs, chatbot, history,
                                                                                  plugin_kwargs)
    else:
        gpt_response_collection = file_limit
    yield from crazy_box.result_written_to_markdwon(gpt_response_collection, llm_kwargs, chatbot, history)
    return gpt_response_collection


@CatchException
def KDocs_转接口测试用例(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(file_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    split_content_limit = yield from crazy_box.input_output_processing(gpt_response_collection,
                                                                                        llm_kwargs, plugin_kwargs,
                                                                                        chatbot, history)
    inputs_array, inputs_show_user_array = split_content_limit
    gpt_response_collection = yield from crazy_box.submit_multithreaded_tasks(inputs_array, inputs_show_user_array,
                                                                              llm_kwargs, chatbot, history,
                                                                              plugin_kwargs)
    template_file, = crazy_box.json_args_return(plugin_kwargs, ['template_file'])
    yield from crazy_box.write_test_cases(gpt_response_collection, inputs_show_user_array, llm_kwargs, chatbot, history,
                                          is_client=template_file)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_转客户端测试用例(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    split_content_limit = yield from crazy_box.input_output_processing(gpt_response_collection,
                                                                                        llm_kwargs, plugin_kwargs,
                                                                                        chatbot, history)
    inputs_array, inputs_show_user_array = split_content_limit
    gpt_response_collection = yield from crazy_box.submit_multithreaded_tasks(inputs_array, inputs_show_user_array,
                                                                              llm_kwargs, chatbot, history,
                                                                              plugin_kwargs)
    yield from crazy_box.write_test_cases(gpt_response_collection, inputs_show_user_array, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_需求分析问答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    split_content_limit = yield from crazy_box.input_output_processing(gpt_response_collection,
                                                                                        llm_kwargs, plugin_kwargs,
                                                                                        chatbot, history)
    inputs_array, inputs_show_user_array = split_content_limit
    gpt_response_collection = yield from crazy_box.submit_multithreaded_tasks(inputs_array, inputs_show_user_array,
                                                                              llm_kwargs, chatbot, history,
                                                                              plugin_kwargs)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_文档转流程图(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from KDocs_转Markdown(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return
    yield from crazy_box.transfer_flow_chart(gpt_response_collection, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')

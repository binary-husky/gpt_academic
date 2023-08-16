#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
import os.path
import time
from comm_tools import func_box, ocr_tools
from crazy_functions import crazy_box
from comm_tools.toolbox import update_ui, CatchException, trimmed_format_exc, get_conf


def func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types):
    links = crazy_box.Utils().split_startswith_txt(link_limit)
    files = [file for file in link_limit.splitlines() if os.path.exists(file)]
    if not links and not files:
        devs_document, = get_conf('devs_document')
        chatbot.append((None, f'输入框空空如也？{link_limit}\n\n'
                              f'请在输入框中输入需要解析的文档链接或本地文件地址，文档支持类型{func_box.html_tag_color(file_types)}'
                              f'链接需要是可访问的，格式如下，如果有多个文档则用换行或空格隔开，输入后再点击对应的插件'
                              f'\n\n【金山文档】 xxxx https://kdocs.cn/l/xxxxxxxxxx'
                              f'\n\n https://kdocs.cn/l/xxxxxxxxxx'
                              f'\n\n`还是不懂？那就来👺` {devs_document}'))
        yield from update_ui(chatbot, history)
        return
    file_limit = []
    # 爬虫读取
    img_ocr, = crazy_box.json_args_return(plugin_kwargs, ['开启OCR'])
    for url in links:
        try:
            gpt_say = "网页爬虫和文件处理准备工作中...."
            chatbot.append([link_limit, gpt_say])
            yield from update_ui(chatbot, history)  # 增加中间过渡
            if crazy_box.if_kdocs_url_isap(url) and 'ap轻文档' in file_types:
                ovs_data, content, empty_picture_count, pic_dict, kdocs_dict = crazy_box.get_docs_content(url, image_processing=img_ocr)
                if img_ocr:
                    if pic_dict:  # 当有图片文件时，再去提醒
                        ocr_process = f'检测到轻文档中存在{func_box.html_tag_color(empty_picture_count)}张图片，为了产出结果不存在遗漏，正在逐一进行识别\n\n' \
                                      f'> 红框为采用的文案,可信度低于 {func_box.html_tag_color(llm_kwargs["ocr"])} 将不采用, 可在Setting 中进行配置\n\n'
                        chatbot.append([None, ocr_process])
                    else:
                        ocr_process = ''
                    if pic_dict:
                        yield from update_ui(chatbot, history, '正在调用OCR组件，已启用多线程解析，请稍等')
                        ocr_func = ocr_tools.Paddle_ocr_select(ipaddr=llm_kwargs['ipaddr'],trust_value=llm_kwargs['ocr']).img_def_content
                        thread_submission = ocr_tools.submit_threads_ocr(pic_dict, func=ocr_func, max_threads=llm_kwargs.get('worker_num', 5))
                        for t in thread_submission:
                            try:
                                img_content, img_result, error = thread_submission[t].result()
                                content = str(content).replace(f"{t}",
                                                               f"{func_box.html_local_img(img_result)}\n```{img_content}```")
                                if error:
                                    ocr_process += '`tips: 图片右侧说明仅代表图片太大失绘制失败，不影响实际OCR结果`'
                                ocr_process += f'{t} 识别完成，识别效果如下{func_box.html_local_img(img_result)}\n\n'
                                chatbot[-1] = [None, ocr_process]
                                yield from update_ui(chatbot, history)
                            except Exception:
                                ocr_process += f'{t} 识别失败，过滤这个图片\n\n'
                                chatbot[-1] = [None, ocr_process]
                                yield from update_ui(chatbot, history)

                else:
                    if empty_picture_count >= 5:
                        chatbot.append([None, f'\n\n 需求文档中没有{func_box.html_tag_color("描述")}的图片数量' \
                                              f'有{func_box.html_tag_color(empty_picture_count)}张，生成的测试用例可能存在遗漏点，'
                                              f'可以参考以下方法对图片进行描述补充，或在自定义插件参数中开始OCR功能\n\n' \
                                              f'{func_box.html_local_img("docs/imgs/pic_desc.png")}'])
                    yield from update_ui(chatbot, history)
                title = crazy_box.long_name_processing(content)
                file_limit.extend([title, content])
            else:
                gpt_say += f'正在解析文档链接，如果文件类型符合`{file_types}`,将下载并解析...'
                chatbot[-1] = [link_limit, gpt_say]
                yield from update_ui(chatbot, history)
                for t in file_types:
                    success, file_manifest, _ = crazy_box.get_kdocs_from_everything(txt=url, type=t, ipaddr=llm_kwargs['ipaddr'])
                    files.extend(file_manifest)
                    if success:
                        chatbot.append([None, success])
        except Exception as e:
            error_str = trimmed_format_exc()
            chatbot.append([None,
                            f'{func_box.html_a_blank(url)} \n\n请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？是否是轻文档？下面是什么错误？\n\n ```\n\n{str(error_str)}\n```'])
            func_box.通知机器人(f"{link_limit}\n\n```\n{error_str}\n```\n\n```\n{llm_kwargs}\n```")
            yield from update_ui(chatbot, history)
    # 提交文件给file_extraction_intype读取
    yield from crazy_box.file_extraction_intype(files, file_types, file_limit, chatbot, history, llm_kwargs, plugin_kwargs)
    yield from update_ui(chatbot, history)
    if not file_limit:
        chatbot.append([None, f'{func_box.html_tag_color("无法获取需求文档内容，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='无法获取需求文档内容，暂停运行')
    return file_limit


def func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port, to_kdocs=True):
    file_types = ['md', 'txt', 'pdf', 'xmind', 'ap轻文档']
    if to_kdocs:
        file_limit = yield from func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types)
    else:
        file_limit = link_limit
    if not file_limit:
        return
    kwargs_to_mark, = crazy_box.json_args_return(plugin_kwargs, ['格式化文档提示词'])
    if kwargs_to_mark:
        gpt_response = yield from crazy_box.func_拆分与提问(file_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                  args_keys=[kwargs_to_mark, False])
        yield from crazy_box.result_written_to_markdwon(gpt_response, llm_kwargs, plugin_kwargs, chatbot, history)
    else:
        gpt_response = file_limit
    if not gpt_response:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
    return gpt_response


@CatchException
def KDocs_转接口测试用例(file_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(file_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    gpt_response = yield from crazy_box.func_拆分与提问(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot,
                                                        history, args_keys=[False, False])
    yield from crazy_box.write_test_cases(gpt_response, llm_kwargs, plugin_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_转客户端测试用例(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_history = {i: {} for i in range(3)}
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    # < --------------------------- 第一阶段执行 -------------------------------->
    gpt_response = yield from crazy_box.func_拆分与提问(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot,
                                                        history, args_keys=[False, False])
    yield from crazy_box.write_test_cases(gpt_response, llm_kwargs, plugin_kwargs,
                                          chatbot, history, file_history[1])
    yield from update_ui(chatbot, history, '插件执行成功')



func_kwargs = {
    '格式化文档': crazy_box.result_written_to_markdwon,
    '写入测试用例': crazy_box.write_test_cases,
    '补充测试用例': crazy_box.supplementary_test_case
}


@CatchException
def Kdocs_多阶段生成回答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_types = ['md', 'txt', 'pdf', 'xmind', 'ap轻文档']
    file_limit = yield from func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types)
    multi_stage_config, = crazy_box.json_args_return(plugin_kwargs, keys=['阶段性产出'], default={})
    file_count = {}
    for stage in multi_stage_config:
        prompt = multi_stage_config[stage].get('提示词', False)
        func = multi_stage_config[stage].get('调用方法', False)
        knowledge_base = multi_stage_config[stage].get('关联知识库', False)
        file_count[stage] = []
        chatbot.append([f'开始执行{stage}动作，使用`{prompt}`提问后，调用`{func}保存回答`', None])
        yield from update_ui(chatbot=chatbot, history=history)
        if prompt:
            file_limit = yield from crazy_box.func_拆分与提问(file_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                            args_keys=[prompt, knowledge_base], task_tag=stage)
        else:
            yield from update_ui(chatbot=chatbot+[[None, '你没有指定提示词，跳过提问']], history=history)
        if func:
            plugin_kwargs[stage] = yield from func_kwargs[func](file_limit, llm_kwargs, plugin_kwargs,  chatbot, history)
        else:
            yield from update_ui(chatbot=chatbot+[[None, '你没有指定调用方法，跳过生成结果']], history=history)
        file_limit = []
        yield from update_ui(chatbot=chatbot + [[None, '']], history=history)
        yield from crazy_box.file_extraction_intype(plugin_kwargs[stage], [''], file_limit, chatbot, history, llm_kwargs, plugin_kwargs)


@CatchException
def KDocs_需求分析问答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    gpt_response = yield from crazy_box.func_拆分与提问(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot,
                                                      history, args_keys=[False, False],)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_文档转流程图(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    yield from crazy_box.transfer_flow_chart(gpt_response_collection, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_文档提取测试点(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append([None, f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return


@CatchException
def KDocs_测试用例检查优化(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_types = ['xlsx', 'xmind']
    file_limit = yield from func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types)
    if not link_limit:
        return
    gpt_response_collection = yield from crazy_box.func_拆分与提问(file_limit, llm_kwargs, plugin_kwargs, chatbot,
                                                      history, args_keys=[False, False],)
    yield from crazy_box.supplementary_test_case(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')



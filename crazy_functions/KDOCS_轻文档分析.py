#! .\venv\
# encoding: utf-8
# @Time   : 2023/6/15
# @Author : Spike
# @Descr   :
import os.path
from comm_tools import func_box, ocr_tools, Langchain_cn
from crazy_functions.kingsoft_fns import crazy_box, crzay_kingsoft
from comm_tools.toolbox import update_ui, CatchException, trimmed_format_exc, get_conf



def func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types):
    wps_links = crazy_box.Utils().split_startswith_txt(link_limit, domain_name=['kdocs', 'wps'])
    qq_link = crazy_box.Utils().split_startswith_txt(link_limit, domain_name=['docs.qq'])
    files = [file for file in link_limit.splitlines() if os.path.exists(file)]
    if not wps_links and not files and not qq_link:
        devs_document, = get_conf('devs_document')
        chatbot.append((link_limit, f'输入框空空如也？{link_limit}\n\n'
                              f'请在输入框中输入需要解析的文档链接或本地文件地址，然后再点击对应的插件，文档支持类型{func_box.html_tag_color(file_types)}'
                              f'链接需要是可访问的，格式如下，如果有多个文档则用换行或空格隔开，输入后再点击对应的插件'
                              f'\n\n xxxx https://kdocs.cn/l/xxxxxxxxxx'
                              f'\n\n https://kdocs.cn/l/xxxxxxxxxx'
                              f'\n\n`还是不懂？那就来👺` {devs_document}'))
        yield from update_ui(chatbot, history)
        return
    file_limit = []
    # 爬虫读取
    gpt_say = "网页爬虫和文件处理准备工作中...."
    chatbot.append([link_limit, gpt_say])
    for url in wps_links:
        try:
            yield from update_ui(chatbot, history)  # 增加中间过渡
            if crzay_kingsoft.if_kdocs_url_isap(url) and '智能文档' in file_types:
                # TODO 智能文档解析
                yield from crzay_kingsoft.smart_document_extraction(url, llm_kwargs, plugin_kwargs, chatbot, history, files)
            else:
                gpt_say += f'正在解析文档链接，如果文件类型符合`{file_types}`,将下载并解析...'
                chatbot[-1] = [link_limit, gpt_say]
                yield from update_ui(chatbot, history)
                for t in file_types:
                    success, file_manifest, _ = crzay_kingsoft.get_kdocs_from_everything(txt=url, type=t, ipaddr=llm_kwargs['ipaddr'])
                    files.extend(file_manifest)
                    if success:
                        chatbot.append(['进度如何？', success])
        except Exception as e:
            error_str = trimmed_format_exc()
            chatbot.append(['请检查链接是否有效',
                            f'{func_box.html_a_blank(url)} \n\n请检查一下哦，这个链接我们访问不了，是否开启分享？是否设置密码？是否是轻文档？下面是什么错误？\n\n ```\n\n{str(error_str)}\n```'])
            func_box.通知机器人(f"{link_limit}\n\n```\n{error_str}\n```\n\n```\n{llm_kwargs}\n```")
            yield from update_ui(chatbot, history)
    # 提交文件给file_extraction_intype读取
    yield from crazy_box.file_extraction_intype(files, file_types, file_limit, chatbot, history, llm_kwargs, plugin_kwargs)
    yield from update_ui(chatbot, history)
    know_dict, = crazy_box.json_args_return(plugin_kwargs, keys=['自动录入知识库'], default={})
    if not file_limit:
        chatbot.append(['为什么不往下执行？', f'{func_box.html_tag_color("无法获取需求文档内容，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='无法获取需求文档内容，暂停运行')
        return
    if files and know_dict:
        cls_name, = list(know_dict.keys())
        know_id, = list(know_dict.values())
        you_say = f'请将`{str(files).replace(func_box.base_path, "")}`文件录入`cls_name`分类下的`{cls_name}`'
        chatbot.append([you_say, None])
        yield from update_ui(chatbot, history)
        Langchain_cn.single_step_thread_building_knowledge(cls_name=cls_name, know_id=know_id, file_manifest=files, llm_kwargs=llm_kwargs)
        chatbot[-1] = [you_say, 'Done, 已提交线程任务']
        yield from update_ui(chatbot, history)
    return file_limit


def func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port, to_kdocs=True):
    file_types = ['md', 'txt', 'pdf', 'xmind', '智能文档']
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
        chatbot.append(['为什么不继续执行？', f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
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
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    # < --------------------------- 第一阶段执行 -------------------------------->
    gpt_response = yield from crazy_box.func_拆分与提问(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot,
                                                        history, args_keys=[False, False])
    if not gpt_response:
        return
    yield from crazy_box.write_test_cases(gpt_response, llm_kwargs, plugin_kwargs,
                                          chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')



func_kwargs = {
    '结果写入Markdown': crazy_box.result_written_to_markdwon,
    '写入测试用例': crazy_box.write_test_cases,
    '补充测试用例': crazy_box.supplementary_test_case
}


@CatchException
def Kdocs_多阶段生成回答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_types = ['md', 'txt', 'pdf', 'xmind', '智能文档']
    file_limit = yield from func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types)
    if not file_limit:
        return
    multi_stage_config, = crazy_box.json_args_return(plugin_kwargs, keys=['阶段性产出'], default={})
    file_count = {}
    for stage in multi_stage_config:
        prompt = multi_stage_config[stage].get('提示词', False)
        func = multi_stage_config[stage].get('调用方法', False)
        knowledge_base = multi_stage_config[stage].get('关联知识库', False)
        file_count[stage] = []
        chatbot.append([f'开始执行`{stage}`动作，使用`{prompt}`提问后，调用`{func}保存回答`', None])
        yield from update_ui(chatbot=chatbot, history=history)
        if prompt:
            file_limit = yield from crazy_box.func_拆分与提问(file_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                              args_keys=[prompt, knowledge_base], task_tag="_"+stage)
        else:
            chatbot.append(['为什么跳过？', '你没有指定提示词，跳过提问'])
            yield from update_ui(chatbot=chatbot, history=history)
        if func and func_kwargs.get(func, False):
            plugin_kwargs[stage] = yield from func_kwargs[func](file_limit, llm_kwargs, plugin_kwargs,  chatbot, history)
            file_limit = []
        else:
            chatbot.append(['为什么跳过？', '你没有指定调用方法 or 方法错误，跳过生成结果，直接将上次的结果提交给下阶段'])
            content_limit = crazy_box.file_classification_to_dict(file_limit)
            file_limit = [[limit, "".join(content_limit[limit])] for limit in content_limit]
            yield from update_ui(chatbot=chatbot, history=history)
        if stage != [i for i in multi_stage_config][-1]:
            yield from crazy_box.file_extraction_intype(plugin_kwargs[stage], [''], file_limit, chatbot, history, llm_kwargs, plugin_kwargs)

    if not multi_stage_config:
        chatbot.append(['发生了什么事情？', '!!!!! 自定义参数中的Json存在问题，请仔细检查配置是否符合JSON编码格式'])
        yield from update_ui(chatbot=chatbot, history=history)

@CatchException
def KDocs_需求分析问答(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    gpt_response = yield from crazy_box.func_拆分与提问(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot,
                                                        history, args_keys=[False, False], )
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_文档转流程图(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        return
    yield from crazy_box.transfer_flow_chart(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')


@CatchException
def KDocs_文档提取测试点(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    gpt_response_collection = yield from func_格式化文档(link_limit, llm_kwargs, plugin_kwargs, chatbot, history,
                                                          system_prompt, web_port)
    if not gpt_response_collection:
        chatbot.append(['为什么暂停？', f'{func_box.html_tag_color("多线程一个都没有通过，暂停运行!!!!")}'])
        yield from update_ui(chatbot=chatbot, history=history, msg='多线程一个都没有通过，暂停运行')
        return


@CatchException
def KDocs_测试用例检查优化(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    file_types = ['xlsx']
    file_limit = yield from func_文档批量处理(link_limit, llm_kwargs, plugin_kwargs, chatbot, history, file_types)
    if not link_limit:
        return
    gpt_response_collection = yield from crazy_box.func_拆分与提问(file_limit, llm_kwargs, plugin_kwargs, chatbot,
                                                                   history, args_keys=[False, False], )
    yield from crazy_box.supplementary_test_case(gpt_response_collection, llm_kwargs, plugin_kwargs, chatbot, history)
    yield from update_ui(chatbot, history, '插件执行成功')



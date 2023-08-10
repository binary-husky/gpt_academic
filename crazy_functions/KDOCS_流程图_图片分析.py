#! .\venv\
# encoding: utf-8
# @Time   : 2023/7/23
# @Author : Spike
# @Descr   :
from comm_tools import toolbox
from comm_tools import func_box, ocr_tools
from crazy_functions import crazy_box
import os


def ocr_batch_processing(file_manifest, chatbot, history, llm_kwargs):
    ocr_process = f'> 红框为采用的文案,可信度低于 {func_box.html_tag_color(llm_kwargs["ocr"])} 将不采用, 可在Setting 中进行配置\n\n'
    i_say = f'{"  ".join([func_box.html_view_blank(i) for i in file_manifest if os.path.exists(i)])}\n\nORC开始工作'
    chatbot.append([i_say, ocr_process])
    for pic_path in file_manifest:
        yield from toolbox.update_ui(chatbot, history, '正在调用OCR组件，图片多可能会比较慢')
        img_content, img_result = ocr_tools.Paddle_ocr_select(ipaddr=llm_kwargs['ipaddr'],
                                                              trust_value=llm_kwargs['ocr']
                                                              ).img_def_content(img_path=pic_path)
        ocr_process += f'{"/".join(pic_path.split("/")[-2:])} 识别完成，识别效果如下 {func_box.html_local_img(img_result)} \n\n' \
                       f'```\n{img_content}\n```\n\n---\n\n'
        chatbot[-1] = [i_say, ocr_process]
        yield from toolbox.update_ui(chatbot, history)
    ocr_process += f'\n\n---\n\n解析成功，现在我已理解上述内容，有什么不懂得地方你可以问我～'
    yield from toolbox.update_ui(chatbot, history)
    return i_say, ocr_process


@toolbox.CatchException
def 批量分析流程图或图片(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    chatbot_with_cookie = toolbox.ChatBotWithCookies(chatbot)
    chatbot_with_cookie.write_list(chatbot)
    file_handle = crazy_box.Utils()
    task_info, kdocs_manifest_tmp, proj_dir = crazy_box.get_kdocs_from_everything(txt, type='', ipaddr=llm_kwargs['ipaddr'])
    if txt:
        if os.path.exists(txt):
            file_manifest = file_handle.global_search_for_files(txt, matching=file_handle.picture_format)
            yield from ocr_batch_processing(file_manifest, chatbot, history, llm_kwargs=llm_kwargs)
        elif kdocs_manifest_tmp != []:
            for manif in kdocs_manifest_tmp:
                if str(manif).endswith('xmind'):
                    i_say,  process = [func_box.html_view_blank(manif) + "\n\n开始解析", None]
                    chatbot.append([i_say, process])
                    yield from toolbox.update_ui(chatbot, history)
                    content, _ = crazy_box.XmindHandle().xmind_2_md(manif)
                    i_say,  process = [func_box.html_view_blank(manif) + "\n\n开始解析",
                                      f'```{content}```\n\n---\n\nxmind解析成功，现在我已理解上述内容，有什么不懂得地方你可以问我～']
                    chatbot[-1] = [i_say, process]
                    yield from toolbox.update_ui(chatbot, history)
                else:
                    i_say, process = yield from ocr_batch_processing([manif], chatbot, history, llm_kwargs=llm_kwargs)
                chatbot[-1] = [i_say, process]
                history.extend([i_say, process])
        else:
            chatbot.append([None, crazy_box.previously_on_plugins])
            yield from toolbox.update_ui(chatbot, history)
    else:
        chatbot.append([f'空空如也的输入框，{crazy_box.previously_on_plugins}', None])
        yield from toolbox.update_ui(chatbot, history)
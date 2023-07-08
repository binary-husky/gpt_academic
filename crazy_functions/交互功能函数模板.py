from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive


@CatchException
def 交互功能模板函数(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数, 如温度和top_p等, 一般原样传递下去就行
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "交互功能函数模板。在执行完成之后, 可以将自身的状态存储到cookie中, 等待用户的再次调用。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    state = chatbot._cookies.get('plugin_state_0001', None) # 初始化插件状态

    if state is None:
        chatbot._cookies['lock_plugin'] = 'crazy_functions.交互功能函数模板->交互功能模板函数'      # 赋予插件锁定 锁定插件回调路径，当下一次用户提交时，会直接转到该函数
        chatbot._cookies['plugin_state_0001'] = 'wait_user_keyword'                              # 赋予插件状态

        chatbot.append(("第一次调用：", "请输入关键词, 我将为您查找相关壁纸, 建议使用英文单词, 插件锁定中，请直接提交即可。"))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    if state == 'wait_user_keyword':
        chatbot._cookies['lock_plugin'] = None          # 解除插件锁定，避免遗忘导致死锁
        chatbot._cookies['plugin_state_0001'] = None    # 解除插件状态，避免遗忘导致死锁

        # 解除插件锁定
        chatbot.append((f"获取关键词：{txt}", ""))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        page_return = get_image_page_by_keyword(txt)
        inputs=inputs_show_user=f"Extract all image urls in this html page, pick the first 5 images and show them with markdown format: \n\n {page_return}"
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=inputs, inputs_show_user=inputs_show_user,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt="When you want to show an image, use markdown format. e.g. ![image_description](image_url). If there are no image url provided, answer 'no image url provided'"
        )
        chatbot[-1] = [chatbot[-1][0], gpt_say]
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return



# ---------------------------------------------------------------------------------

def get_image_page_by_keyword(keyword):
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(f'https://wallhaven.cc/search?q={keyword}', timeout=2)
    res = "image urls: \n"
    for image_element in BeautifulSoup(response.content, 'html.parser').findAll("img"):
        try:
            res += image_element["data-src"]
            res += "\n"
        except:
            pass
    return res

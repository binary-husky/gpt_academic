# 本源代码中, ⭐ = 关键步骤
"""
测试：
    - show me the solution of $x^2=cos(x)$, solve this problem with figure, and plot and save image to t.jpg

Testing: 
    - Crop the image, keeping the bottom half. 
    - Swap the blue channel and red channel of the image. 
    - Convert the image to grayscale. 
    - Convert the CSV file to an Excel spreadsheet.
"""


from toolbox import CatchException, update_ui, gen_time_str, trimmed_format_exc, ProxyNetworkActivate
from toolbox import get_conf, select_api_key, update_ui_lastest_msg, Singleton
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, get_plugin_arg
from crazy_functions.crazy_utils import input_clipping, try_install_deps
from crazy_functions.agent_fns.persistent import GradioMultiuserManagerForPersistentClasses
from crazy_functions.agent_fns.auto_agent import AutoGenMath
import time


@CatchException
def 多智能体终端(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    # 检查当前的模型是否符合要求
    supported_llms = ['gpt-3.5-turbo-16k', 'gpt-3.5-turbo-1106', 'gpt-4', 'gpt-4-32k', 'gpt-4-1106-preview', 
                      'api2d-gpt-3.5-turbo-16k', 'api2d-gpt-4']
    llm_kwargs['api_key'] = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
    if llm_kwargs['llm_model'] not in supported_llms:
        chatbot.append([f"处理任务: {txt}", f"当前插件只支持{str(supported_llms)}, 当前模型{llm_kwargs['llm_model']}."])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    # 检查当前的模型是否符合要求
    API_URL_REDIRECT, = get_conf('API_URL_REDIRECT')
    if len(API_URL_REDIRECT) > 0:
        chatbot.append([f"处理任务: {txt}", f"暂不支持中转."])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import autogen, docker
    except:
        chatbot.append([ f"处理任务: {txt}", 
            f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade pyautogen docker```。"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import autogen
        import glob, os, time, subprocess
        subprocess.Popen(['docker', '--version'])
    except:
        chatbot.append([f"处理任务: {txt}", f"缺少docker运行环境！"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    # 解锁插件
    chatbot.get_cookies()['lock_plugin'] = None
    persistent_class_multi_user_manager = GradioMultiuserManagerForPersistentClasses()
    user_uuid = chatbot.get_cookies().get('uuid')
    persistent_key = f"{user_uuid}->多智能体终端"
    if persistent_class_multi_user_manager.already_alive(persistent_key):
        # 当已经存在一个正在运行的多智能体终端时，直接将用户输入传递给它，而不是再次启动一个新的多智能体终端
        print('[debug] feed new user input')
        executor = persistent_class_multi_user_manager.get(persistent_key)
        exit_reason = yield from executor.main_process_ui_control(txt, create_or_resume="resume")
    else:
        # 运行多智能体终端 (首次)
        print('[debug] create new executor instance')
        history = []
        chatbot.append(["正在启动: 多智能体终端", "插件动态生成, 执行开始, 作者 Microsoft & Binary-Husky."])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        executor = AutoGenMath(llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port)
        persistent_class_multi_user_manager.set(persistent_key, executor)
        exit_reason = yield from executor.main_process_ui_control(txt, create_or_resume="create")

    if exit_reason == "wait_feedback":
        # 当用户点击了“等待反馈”按钮时，将executor存储到cookie中，等待用户的再次调用
        executor.chatbot.get_cookies()['lock_plugin'] = 'crazy_functions.多智能体->多智能体终端'
    else:
        executor.chatbot.get_cookies()['lock_plugin'] = None
    yield from update_ui(chatbot=executor.chatbot, history=executor.history) # 更新状态

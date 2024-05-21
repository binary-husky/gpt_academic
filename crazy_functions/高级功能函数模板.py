from toolbox import CatchException, update_ui
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime

####################################################################################################################
# Demo 1: 一个非常简单的插件 #########################################################################################
####################################################################################################################

高阶功能模板函数示意图 = f"""
```mermaid
flowchart TD
    %% <gpt_academic_hide_mermaid_code> 一个特殊标记，用于在生成mermaid图表时隐藏代码块
    subgraph 函数调用["函数调用过程"]
        AA["输入栏用户输入的文本(txt)"] --> BB["gpt模型参数(llm_kwargs)"]
        BB --> CC["插件模型参数(plugin_kwargs)"]
        CC --> DD["对话显示框的句柄(chatbot)"]
        DD --> EE["对话历史(history)"]
        EE --> FF["系统提示词(system_prompt)"]
        FF --> GG["当前用户信息(web_port)"]

        A["开始(查询5天历史事件)"]
        A --> B["获取当前月份和日期"]
        B --> C["生成历史事件查询提示词"]
        C --> D["调用大模型"]
        D --> E["更新界面"]
        E --> F["记录历史"]
        F --> |"下一天"| B
    end
```
"""

@CatchException
def 高阶功能模板函数(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request, num_day=5):
    """
    # 高阶功能模板函数示意图：https://mermaid.live/edit#pako:eNptk1tvEkEYhv8KmattQpvlvOyFCcdeeaVXuoYssBwie8gyhCIlqVoLhrbbtAWNUpEGUkyMEDW2Fmn_DDOL_8LZHdOwxrnamX3f7_3mmZk6yKhZCfAgV1KrmYKoQ9fDuKC4yChX0nld1Aou1JzjznQ5fWmejh8LYHW6vG2a47YAnlCLNSIRolnenKBXI_zRIBrcuqRT890u7jZx7zMDt-AaMbnW1--5olGiz2sQjwfoQxsZL0hxplSSU0-rop4vrzmKR6O2JxYjHmwcL2Y_HDatVMkXlf86YzHbGY9bO5j8XE7O8Nsbc3iNB3ukL2SMcH-XIQBgWoVOZzxuOxOJOyc63EPGV6ZQLENVrznViYStTiaJ2vw2M2d9bByRnOXkgCnXylCSU5quyto_IcmkbdvctELmJ-j1ASW3uB3g5xOmKqVTmqr_Na3AtuS_dtBFm8H90XJyHkDDT7S9xXWb4HGmRChx64AOL5HRpUm411rM5uh4H78Z4V7fCZzytjZz2seto9XaNPFue07clLaVZF8UNLygJ-VES8lah_n-O-5Ozc7-77NzJ0-K0yr0ZYrmHdqAk50t2RbA4qq9uNohBASw7YpSgaRkLWCCAtxAlnRZLGbJba9bPwUAC5IsCYAnn1kpJ1ZKUACC0iBSsQLVBzUlA3ioVyQ3qGhZEUrxokiehAz4nFgqk1VNVABfB1uAD_g2_AGPl-W8nMcbCvsDblADfNCz4feyobDPy3rYEMtxwYYbPFNVUoHdCPmDHBv2cP4AMfrCbiBli-Q-3afv0X6WdsIjW2-10fgDy1SAig

    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append((
        "您正在调用插件：历史上的今天",
        "[Local Message] 请注意，您正在调用一个[函数插件]的模板，该函数面向希望实现更多有趣功能的开发者，它可以作为创建新功能函数的模板（该函数只有20多行代码）。此外我们也提供可同步处理大量文件的多线程Demo供您参考。您若希望分享新的功能模组，请不吝PR！" + 高阶功能模板函数示意图))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    for i in range(int(num_day)):
        currentMonth = (datetime.date.today() + datetime.timedelta(days=i)).month
        currentDay = (datetime.date.today() + datetime.timedelta(days=i)).day
        i_say = f'历史中哪些事件发生在{currentMonth}月{currentDay}日？列举两条并发送相关图片。发送图片时，请使用Markdown，将Unsplash API中的PUT_YOUR_QUERY_HERE替换成描述该事件的一个最重要的单词。'
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say, inputs_show_user=i_say,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[],
            sys_prompt="当你想发送一张照片时，请使用Markdown, 并且不要有反斜线, 不要用代码块。使用 Unsplash API (https://source.unsplash.com/1280x720/? < PUT_YOUR_QUERY_HERE >)。"
        )
        chatbot[-1] = (i_say, gpt_say)
        history.append(i_say);history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新







####################################################################################################################
# Demo 2: 一个带二级菜单的插件 #######################################################################################
####################################################################################################################

from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty
class Demo_Wrap(GptAcademicPluginTemplate):
    def __init__(self):
        """
        请注意`execute`会执行在不同的线程中，因此您在定义和使用类变量时，应当慎之又慎！
        """
        pass

    def define_arg_selection_menu(self):
        """
        定义插件的二级选项菜单
        """
        gui_definition = {
            "num_day":
                ArgProperty(title="日期选择", options=["仅今天", "未来3天", "未来5天"], default_value="未来3天", description="无", type="dropdown").model_dump_json(),
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        num_day = plugin_kwargs["num_day"]
        if num_day == "仅今天": num_day = 1
        if num_day == "未来3天": num_day = 3
        if num_day == "未来5天": num_day = 5
        yield from 高阶功能模板函数(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request, num_day=num_day)












####################################################################################################################
# Demo 3: 绘制脑图的Demo ############################################################################################
####################################################################################################################

PROMPT = """
请你给出围绕“{subject}”的逻辑关系图，使用mermaid语法，mermaid语法举例：
```mermaid
graph TD
    P(编程) --> L1(Python)
    P(编程) --> L2(C)
    P(编程) --> L3(C++)
    P(编程) --> L4(Javascipt)
    P(编程) --> L5(PHP)
```
"""
@CatchException
def 测试图表渲染(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "一个测试mermaid绘制图表的功能，您可以在输入框中输入一些关键词，然后使用mermaid+llm绘制图表。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

    if txt == "": txt = "空白的输入栏" # 调皮一下

    i_say_show_user = f'请绘制有关“{txt}”的逻辑关系图。'
    i_say = PROMPT.format(subject=txt)
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say,
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[],
        sys_prompt=""
    )
    history.append(i_say); history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
from toolbox import CatchException, update_ui
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import read_and_clean_pdf_text
import datetime

#暂时只写了这几种的PROMPT
SELECT_PROMPT = """
“{subject}”
=============
以上是从文章中提取的摘要,将会使用这些摘要绘制图表。请你选择一个合适的图表类型:
1 流程图
2 序列图
3 类图
4 饼图
5 甘特图
6 状态图
7 实体关系图
8 象限提示图
不需要解释原因，仅需要输出单个不带任何标点符号的数字。
"""
#流程图
PROMPT_1 = """
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
#序列图
PROMPT_2 = """
请你给出围绕“{subject}”的序列图，使用mermaid语法，mermaid语法举例：
```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统
    A->>B: 登录请求
    B->>A: 登录成功
    A->>B: 获取数据
    B->>A: 返回数据
```
"""
#类图
PROMPT_3 = """
请你给出围绕“{subject}”的类图，使用mermaid语法，mermaid语法举例：
```mermaid
classDiagram
    Class01 <|-- AveryLongClass : Cool
    Class03 *-- Class04
    Class05 o-- Class06
    Class07 .. Class08
    Class09 --> C2 : Where am i?
    Class09 --* C3
    Class09 --|> Class07
    Class07 : equals()
    Class07 : Object[] elementData
    Class01 : size()
    Class01 : int chimp
    Class01 : int gorilla
    Class08 <--> C2: Cool label
```
"""
#饼图
PROMPT_4 = """
请你给出围绕“{subject}”的饼图，使用mermaid语法，mermaid语法举例：
```mermaid
pie title Pets adopted by volunteers
    "狗" : 386
    "猫" : 85
    "兔子" : 15
```
"""
#甘特图
PROMPT_5 = """
请你给出围绕“{subject}”的甘特图，使用mermaid语法，mermaid语法举例：
```mermaid
gantt
    title 项目开发流程
    dateFormat  YYYY-MM-DD
    section 设计
    需求分析 :done, des1, 2024-01-06,2024-01-08
    原型设计 :active, des2, 2024-01-09, 3d
    UI设计 : des3, after des2, 5d
    section 开发
    前端开发 :2024-01-20, 10d
    后端开发 :2024-01-20, 10d
```
"""
#状态图
PROMPT_6 = """
请你给出围绕“{subject}”的状态图，使用mermaid语法，mermaid语法举例：
```mermaid
stateDiagram-v2
   [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```
"""
#实体关系图
PROMPT_7 = """
请你给出围绕“{subject}”的实体关系图，使用mermaid语法，mermaid语法举例：
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string id
    }
    ORDER {
        string orderNumber
        date orderDate
        string customerID
    }
    LINE-ITEM {
        number quantity
        string productID
    }
```
"""
#象限提示图
PROMPT_8 = """
请你给出围绕“{subject}”的象限图，使用mermaid语法，mermaid语法举例：
```mermaid
graph LR
    A[Hard skill] --> B(Programming)
    A[Hard skill] --> C(Design)
    D[Soft skill] --> E(Coordination)
    D[Soft skill] --> F(Communication)
```
"""

def 解析历史输入(history,llm_kwargs,chatbot):
    ############################## <第 0 步，切割输入> ##################################
    # 借用PDF切割中的函数对文本进行切割
    TOKEN_LIMIT_PER_FRAGMENT = 2500
    txt = str(history).encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
    from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
    txt = breakdown_text_to_satisfy_token_limit(txt=txt, limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs['llm_model'])
    ############################## <第 1 步，迭代地历遍整个文章，提取精炼信息> ##################################
    i_say_show_user = f'首先你从历史记录或文件中提取摘要。'; gpt_say = "[Local Message] 收到。"   # 用户提示
    chatbot.append([i_say_show_user, gpt_say]); yield from update_ui(chatbot=chatbot, history=history)    # 更新UI
    results = []
    MAX_WORD_TOTAL = 4096
    n_txt = len(txt)
    last_iteration_result = "从以下文本中提取摘要。"
    if n_txt >= 20: print('文章极长，不能达到预期效果')
    for i in range(n_txt):
        NUM_OF_WORD = MAX_WORD_TOTAL // n_txt
        i_say = f"Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words: {txt[i]}"
        i_say_show_user = f"[{i+1}/{n_txt}] Read this section, recapitulate the content of this section with less than {NUM_OF_WORD} words: {txt[i][:200]} ...."
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(i_say, i_say_show_user,  # i_say=真正给chatgpt的提问， i_say_show_user=给用户看的提问
                                                                           llm_kwargs, chatbot, 
                                                                           history=["The main content of the previous section is?", last_iteration_result], # 迭代上一次的结果
                                                                           sys_prompt="Extracts the main content from the text section where it is located for graphing purposes, answer me with Chinese."  # 提示
                                                                        ) 
        results.append(gpt_say)
        last_iteration_result = gpt_say
    ############################## <第 2 步，根据整理的摘要选择图表类型> ##################################
    i_say_show_user = f'接下来将判断适合的图表类型,如连续3次判断失败将会使用流程图进行绘制'; gpt_say = "[Local Message] 收到。"   # 用户提示
    chatbot.append([i_say_show_user, gpt_say]); yield from update_ui(chatbot=chatbot, history=[])    # 更新UI
    results_txt = '\n'.join(results)
    i_say = SELECT_PROMPT.format(subject=results_txt)
    i_say_show_user = f'请判断适合使用的流程图类型,其中数字对应关系为:1-流程图,2-序列图,3-类图,4-饼图,5-甘特图,6-状态图,7-实体关系图,8-象限提示图'
    for i in range(3):
        gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs=i_say,
            inputs_show_user=i_say_show_user,
            llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
            sys_prompt=""
        )
        if gpt_say in ['1','2','3','4','5','6','7','8']:     #判断返回是否正确
            break
    if gpt_say not in ['1','2','3','4','5','6','7','8']:
        gpt_say = '1'
    ############################## <第 3 步，根据选择的图表类型绘制图表> ##################################
    if gpt_say == '1':
        i_say = PROMPT_1.format(subject=results_txt)
    elif gpt_say == '2':
        i_say = PROMPT_2.format(subject=results_txt)
    elif gpt_say == '3':
        i_say = PROMPT_3.format(subject=results_txt)
    elif gpt_say == '4':
        i_say = PROMPT_4.format(subject=results_txt)
    elif gpt_say == '5':
        i_say = PROMPT_5.format(subject=results_txt)
    elif gpt_say == '6':
        i_say = PROMPT_6.format(subject=results_txt)
    elif gpt_say == '7':
        i_say = PROMPT_7.format(subject=results_txt)
    elif gpt_say == '8':
        i_say = PROMPT_8.format(subject=results_txt)
    i_say_show_user = f'请根据判断结果绘制相应的图表。'
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say,
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=""
    )
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

def 输入区文件处理(txt):
    if txt == "": return False, txt
    success = True
    import glob
    from .crazy_utils import get_files_from_everything
    file_pdf,pdf_manifest,folder_pdf = get_files_from_everything(txt, '.pdf')
    if not file_pdf or len(pdf_manifest) == 0:
        return False, txt   #如不是pdf文件则返回输入区内容
    final_result = ""
    for index, fp in enumerate(pdf_manifest):
        file_content, page_one = read_and_clean_pdf_text(fp) # （尝试）按照章节切割PDF
        file_content = file_content.encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
        final_result += file_content
    return True, final_result
    
@CatchException
def 生成多种Mermaid图表(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    import os
    chatbot.append([
        "函数插件功能？", 
        "根据当前聊天历史或PDF中绘制多种mermaid图表的功能，将会首先判断适合的图表类型，随后绘制图表。函数插件贡献者: Menghuan1918"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    if os.path.exists(txt):     #如输入区无内容则直接解析历史记录
        file_exist, txt = 输入区文件处理(txt)
    history.append(txt)     #将解析后的txt传递加入到历史中
    yield from 解析历史输入(history,llm_kwargs,chatbot)
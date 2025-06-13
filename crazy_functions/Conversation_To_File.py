import re
from toolbox import CatchException, update_ui, promote_file_to_downloadzone, get_log_folder, get_user, update_ui_latest_msg
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty
from loguru import logger

f_prefix = 'GPT-Academic对话存档'

def write_chat_to_file_legacy(chatbot, history=None, file_name=None):
    """
    将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    import os
    import time
    from themes.theme import advanced_css

    if (file_name is not None) and (file_name != "") and (not file_name.endswith('.html')): file_name += '.html'
    else: file_name = None

    if file_name is None:
        file_name = f_prefix + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.html'
    fp = os.path.join(get_log_folder(get_user(chatbot), plugin_name='chat_history'), file_name)

    with open(fp, 'w', encoding='utf8') as f:
        from textwrap import dedent
        form = dedent("""
        <!DOCTYPE html><head><meta charset="utf-8"><title>对话存档</title><style>{CSS}</style></head>
        <body>
        <div class="test_temp1" style="width:10%; height: 500px; float:left;"></div>
        <div class="test_temp2" style="width:80%;padding: 40px;float:left;padding-left: 20px;padding-right: 20px;box-shadow: rgba(0, 0, 0, 0.2) 0px 0px 8px 8px;border-radius: 10px;">
            <div class="chat-body" style="display: flex;justify-content: center;flex-direction: column;align-items: center;flex-wrap: nowrap;">
                {CHAT_PREVIEW}
                <div></div>
                <div></div>
                <div style="text-align: center;width:80%;padding: 0px;float:left;padding-left:20px;padding-right:20px;box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 1px 2px;border-radius: 1px;">对话（原始数据）</div>
                {HISTORY_PREVIEW}
            </div>
        </div>
        <div class="test_temp3" style="width:10%; height: 500px; float:left;"></div>
        </body>
        """)

        qa_from = dedent("""
        <div class="QaBox" style="width:80%;padding: 20px;margin-bottom: 20px;box-shadow: rgb(0 255 159 / 50%) 0px 0px 1px 2px;border-radius: 4px;">
            <div class="Question" style="border-radius: 2px;">{QUESTION}</div>
            <hr color="blue" style="border-top: dotted 2px #ccc;">
            <div class="Answer" style="border-radius: 2px;">{ANSWER}</div>
        </div>
        """)

        history_from = dedent("""
        <div class="historyBox" style="width:80%;padding: 0px;float:left;padding-left:20px;padding-right:20px;box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 1px 2px;border-radius: 1px;">
            <div class="entry" style="border-radius: 2px;">{ENTRY}</div>
        </div>
        """)
        CHAT_PREVIEW_BUF = ""
        for i, contents in enumerate(chatbot):
            question, answer = contents[0], contents[1]
            if question is None: question = ""
            try: question = str(question)
            except: question = ""
            if answer is None: answer = ""
            try: answer = str(answer)
            except: answer = ""
            CHAT_PREVIEW_BUF += qa_from.format(QUESTION=question, ANSWER=answer)

        HISTORY_PREVIEW_BUF = ""
        for h in history:
            HISTORY_PREVIEW_BUF += history_from.format(ENTRY=h)
        html_content = form.format(CHAT_PREVIEW=CHAT_PREVIEW_BUF, HISTORY_PREVIEW=HISTORY_PREVIEW_BUF, CSS=advanced_css)
        f.write(html_content)

    promote_file_to_downloadzone(fp, rename_file=file_name, chatbot=chatbot)
    return '对话历史写入：' + fp

def write_chat_to_file(chatbot, history=None, file_name=None):
    """
    将对话记录history以多种格式（HTML、Word、Markdown）写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    
    Args:
        chatbot: 聊天机器人对象，包含对话内容
        history: 对话历史记录
        file_name: 指定的文件名，如果为None则使用时间戳
        
    Returns:
        str: 提示信息，包含文件保存路径
    """
    import os
    import time
    import asyncio
    import aiofiles
    from toolbox import promote_file_to_downloadzone
    from crazy_functions.doc_fns.conversation_doc.excel_doc import save_chat_tables
    from crazy_functions.doc_fns.conversation_doc.html_doc import HtmlFormatter
    from crazy_functions.doc_fns.conversation_doc.markdown_doc import MarkdownFormatter
    from crazy_functions.doc_fns.conversation_doc.word_doc import WordFormatter
    from crazy_functions.doc_fns.conversation_doc.txt_doc import TxtFormatter
    from crazy_functions.doc_fns.conversation_doc.word2pdf import WordToPdfConverter

    async def save_html():
        try:
            html_formatter = HtmlFormatter(chatbot, history)
            html_content = html_formatter.create_document()
            html_file = os.path.join(save_dir, base_name + '.html')
            async with aiofiles.open(html_file, 'w', encoding='utf8') as f:
                await f.write(html_content)
            return html_file
        except Exception as e:
            print(f"保存HTML格式失败: {str(e)}")
            return None

    async def save_word():
        try:
            word_formatter = WordFormatter()
            doc = word_formatter.create_document(history)
            docx_file = os.path.join(save_dir, base_name + '.docx')
            # 由于python-docx不支持异步，使用线程池执行
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, doc.save, docx_file)
            return docx_file
        except Exception as e:
            print(f"保存Word格式失败: {str(e)}")
            return None
    async def save_pdf(docx_file):
        try:
            if docx_file:
                # 获取文件名和保存路径
                pdf_file = os.path.join(save_dir, base_name + '.pdf')
                
                # 在线程池中执行转换
                loop = asyncio.get_event_loop()
                pdf_file = await loop.run_in_executor(
                    None, 
                    WordToPdfConverter.convert_to_pdf,
                    docx_file
                    # save_dir
                )
                
                return pdf_file
                
        except Exception as e:
            print(f"保存PDF格式失败: {str(e)}")
            return None

    async def save_markdown():
        try:
            md_formatter = MarkdownFormatter()
            md_content = md_formatter.create_document(history)
            md_file = os.path.join(save_dir, base_name + '.md')
            async with aiofiles.open(md_file, 'w', encoding='utf8') as f:
                await f.write(md_content)
            return md_file
        except Exception as e:
            print(f"保存Markdown格式失败: {str(e)}")
            return None

    async def save_txt():
        try:
            txt_formatter = TxtFormatter()
            txt_content = txt_formatter.create_document(history)
            txt_file = os.path.join(save_dir, base_name + '.txt')
            async with aiofiles.open(txt_file, 'w', encoding='utf8') as f:
                await f.write(txt_content)
            return txt_file
        except Exception as e:
            print(f"保存TXT格式失败: {str(e)}")
            return None

    async def main():
        # 并发执行所有保存任务
        html_task = asyncio.create_task(save_html())
        word_task = asyncio.create_task(save_word())
        md_task = asyncio.create_task(save_markdown())
        txt_task = asyncio.create_task(save_txt())
        
        # 等待所有任务完成
        html_file = await html_task
        docx_file = await word_task
        md_file = await md_task
        txt_file = await txt_task
        
        # PDF转换需要等待word文件生成完成
        pdf_file = await save_pdf(docx_file)
        # 收集所有成功生成的文件
        result_files = [f for f in [html_file, docx_file, md_file, txt_file, pdf_file] if f]
        
        # 保存Excel表格
        excel_files = save_chat_tables(history, save_dir, base_name)
        result_files.extend(excel_files)
        
        return result_files

    # 生成时间戳
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    
    # 获取保存目录
    save_dir = get_log_folder(get_user(chatbot), plugin_name='chat_history')
    
    # 处理文件名
    base_name = file_name if file_name else f"聊天记录_{timestamp}"
    
    # 运行异步任务
    result_files = asyncio.run(main())
    
    # 将生成的文件添加到下载区
    for file in result_files:
        promote_file_to_downloadzone(file, rename_file=os.path.basename(file), chatbot=chatbot)
    
    # 如果没有成功保存任何文件，返回错误信息
    if not result_files:
        return "保存对话记录失败，请检查错误日志"
    
    ext_list = [os.path.splitext(f)[1] for f in result_files]
    # 返回成功信息和文件路径
    return f"对话历史已保存至以下格式文件：" + "、".join(ext_list)

def gen_file_preview(file_name):
    try:
        with open(file_name, 'r', encoding='utf8') as f:
            file_content = f.read()
        # pattern to match the text between <head> and </head>
        pattern = re.compile(r'<head>.*?</head>', flags=re.DOTALL)
        file_content = re.sub(pattern, '', file_content)
        html, history = file_content.split('<hr color="blue"> \n\n 对话数据 (无渲染):\n')
        history = history.strip('<code>')
        history = history.strip('</code>')
        history = history.split("\n>>>")
        return list(filter(lambda x:x!="", history))[0][:100]
    except:
        return ""

def read_file_to_chat(chatbot, history, file_name):
    with open(file_name, 'r', encoding='utf8') as f:
        file_content = f.read()
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(file_content, 'lxml')
    # 提取QaBox信息
    chatbot.clear()
    qa_box_list = []
    qa_boxes = soup.find_all("div", class_="QaBox")
    for box in qa_boxes:
        question = box.find("div", class_="Question").get_text(strip=False)
        answer = box.find("div", class_="Answer").get_text(strip=False)
        qa_box_list.append({"Question": question, "Answer": answer})
        chatbot.append([question, answer])
    # 提取historyBox信息
    history_box_list = []
    history_boxes = soup.find_all("div", class_="historyBox")
    for box in history_boxes:
        entry = box.find("div", class_="entry").get_text(strip=False)
        history_box_list.append(entry)
    history = history_box_list
    chatbot.append([None, f"[Local Message] 载入对话{len(qa_box_list)}条，上下文{len(history)}条。"])
    return chatbot, history

@CatchException
def 对话历史存档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    file_name = plugin_kwargs.get("file_name", None)

    chatbot.append((None, f"[Local Message] {write_chat_to_file_legacy(chatbot, history, file_name)}，您可以调用下拉菜单中的“载入对话历史存档”还原当下的对话。"))
    try:
        chatbot.append((None, f"[Local Message] 正在尝试生成pdf以及word格式的对话存档，请稍等..."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求需要一段时间，我们先及时地做一次界面更新
        lastmsg = f"[Local Message] {write_chat_to_file(chatbot, history, file_name)}。" \
              f"您可以调用下拉菜单中的“载入对话历史会话”还原当下的对话，请注意，目前只支持html格式载入历史。" \
              f"当模型回答中存在表格，将提取表格内容存储为Excel的xlsx格式，如果你提供一些数据,然后输入指令要求模型帮你整理为表格" \
              f"（如“请帮我将下面的数据整理为表格：”），再利用此插件就可以获取到Excel表格。"
        yield from update_ui_latest_msg(lastmsg, chatbot, history) # 刷新界面 # 由于请求需要一段时间，我们先及时地做一次界面更新
    except Exception as e:
        logger.exception(f"已完成对话存档（pdf和word格式的对话存档生成未成功）。{str(e)}")
        lastmsg = "已完成对话存档（pdf和word格式的对话存档生成未成功）。"
        yield from update_ui_latest_msg(lastmsg, chatbot, history) # 刷新界面 # 由于请求需要一段时间，我们先及时地做一次界面更新
    return

class Conversation_To_File_Wrap(GptAcademicPluginTemplate):
    def __init__(self):
        """
        请注意`execute`会执行在不同的线程中，因此您在定义和使用类变量时，应当慎之又慎！
        """
        pass

    def define_arg_selection_menu(self):
        """
        定义插件的二级选项菜单

        第一个参数，名称`file_name`，参数`type`声明这是一个文本框，文本框上方显示`title`，文本框内部显示`description`，`default_value`为默认值；
        """
        gui_definition = {
            "file_name": ArgProperty(title="保存文件名", description="输入对话存档文件名，留空则使用时间作为文件名", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        yield from 对话历史存档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)





def hide_cwd(str):
    import os
    current_path = os.getcwd()
    replace_path = "."
    return str.replace(current_path, replace_path)

@CatchException
def 载入对话历史存档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    from crazy_functions.crazy_utils import get_files_from_everything
    success, file_manifest, _ = get_files_from_everything(txt, type='.html')

    if not success:
        if txt == "": txt = '空空如也的输入栏'
        import glob
        local_history = "<br/>".join([
            "`"+hide_cwd(f)+f" ({gen_file_preview(f)})"+"`"
            for f in glob.glob(
                f'{get_log_folder(get_user(chatbot), plugin_name="chat_history")}/**/{f_prefix}*.html',
                recursive=True
            )])
        chatbot.append([f"正在查找对话历史文件（html格式）: {txt}", f"找不到任何html文件: {txt}。但本地存储了以下历史文件，您可以将任意一个文件路径粘贴到输入区，然后重试：<br/>{local_history}"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    try:
        chatbot, history = read_file_to_chat(chatbot, history, file_manifest[0])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    except:
        chatbot.append([f"载入对话历史文件", f"对话历史文件损坏！"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

@CatchException
def 删除所有本地对话历史记录(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """

    import glob, os
    local_history = "<br/>".join([
        "`"+hide_cwd(f)+"`"
        for f in glob.glob(
            f'{get_log_folder(get_user(chatbot), plugin_name="chat_history")}/**/{f_prefix}*.html', recursive=True
        )])
    for f in glob.glob(f'{get_log_folder(get_user(chatbot), plugin_name="chat_history")}/**/{f_prefix}*.html', recursive=True):
        os.remove(f)
    chatbot.append([f"删除所有历史对话文件", f"已删除<br/>{local_history}"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    return
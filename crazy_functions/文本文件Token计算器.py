from toolbox import update_ui
from toolbox import CatchException, report_exception
fast_debug = False

def token计算(file_content):
    # count_token
    from request_llms.bridge_all import model_info
    enc = model_info["gpt-3.5-turbo"]['tokenizer']
    return len(enc.encode(file_content, disallowed_special=()))

def 判断文件并读取(fp):
    try:
        if fp.split(".")[-1] == "docx":
            from docx import Document
            doc = Document(fp)
            return "\n".join([para.text for para in doc.paragraphs])
        elif fp.split(".")[-1] == "doc":
            raise RuntimeError('请先将.doc文档转换为.docx文档。')
        elif fp.split(".")[-1] == "pdf":
            # 读取PDF文件
            from .crazy_utils import read_and_clean_pdf_text
            file_content, _ = read_and_clean_pdf_text(fp)
            return file_content.encode('utf-8', 'ignore').decode()   # avoid reading non-utf8 chars
        else:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    except Exception as e:
        return f"读取文件出错: {str(e)}"

@CatchException
def 文本文件Token计算器(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    chatbot.append([
        "函数插件功能？",
        "对上传的文件进行tokens数量预估。函数插件贡献者: Binary-Husky & zAyRE"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    import glob, os

    if not os.path.exists(txt):
        if txt == "": txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    project_folder = txt
    file_manifest = glob.glob(f'{project_folder}/**/*.*', recursive=True)

    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    for fp in file_manifest:
        file_content = 判断文件并读取(fp)
        if isinstance(file_content, str):
            tokens_count = token计算(file_content)
            chatbot.append((f"文件{os.path.basename(fp)}的Token数量约为：{tokens_count} (仅供参考)", ""))
        else:
            chatbot.append((f"文件{os.path.basename(fp)}处理错误：", file_content))

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


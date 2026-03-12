from toolbox import CatchException, report_exception, update_ui, get_log_folder
from toolbox import promote_file_to_downloadzone, write_history_to_file


@CatchException
def CambAI_Translation(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    """CAMB AI 翻译插件：支持140+语言的高质量翻译。"""
    import os

    chatbot.append(["函数插件功能？", "使用CAMB AI进行高质量翻译，支持140+语言。"])
    yield from update_ui(chatbot=chatbot, history=history)

    # Parse advanced args: source_lang,target_lang (integer codes)
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""):
        plugin_kwargs.pop("advanced_arg")
    advanced_arg = plugin_kwargs.get("advanced_arg", "1,75")  # Default: English->Chinese
    try:
        parts = advanced_arg.split(",")
        source_lang = int(parts[0].strip())
        target_lang = int(parts[1].strip())
    except (ValueError, IndexError):
        report_exception(chatbot, history,
                         a="CAMB AI 翻译",
                         b="高级参数格式错误，请使用 '源语言代码,目标语言代码' 格式，例如 '1,75'（英文->中文）。")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # Collect text to translate
    text_to_translate = ""
    supported_extensions = ['.txt', '.md', '.docx']

    if os.path.exists(txt):
        import glob
        if os.path.isfile(txt):
            file_list = [txt]
        else:
            file_list = []
            for ext in supported_extensions:
                file_list.extend(glob.glob(f'{txt}/**/*{ext}', recursive=True))

        if not file_list:
            report_exception(chatbot, history, a="CAMB AI 翻译", b=f"在路径 {txt} 中未找到支持的文件（.txt, .md, .docx）。")
            yield from update_ui(chatbot=chatbot, history=history)
            return

        for fp in file_list:
            ext = os.path.splitext(fp)[1].lower()
            if ext == '.docx':
                try:
                    import docx
                    doc = docx.Document(fp)
                    text_to_translate += "\n".join([p.text for p in doc.paragraphs]) + "\n"
                except Exception as e:
                    chatbot.append([f"读取 {fp} 失败", str(e)])
                    yield from update_ui(chatbot=chatbot, history=history)
            else:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    text_to_translate += f.read() + "\n"
    else:
        text_to_translate = txt

    if not text_to_translate.strip():
        report_exception(chatbot, history, a="CAMB AI 翻译", b="没有找到要翻译的文本。请在输入框中输入文本或上传文件。")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    chatbot.append(["开始翻译...", f"源语言代码: {source_lang}, 目标语言代码: {target_lang}\n文本长度: {len(text_to_translate)} 字符"])
    yield from update_ui(chatbot=chatbot, history=history)

    # Perform translation
    try:
        from crazy_functions.camb_ai_utils import get_camb_client
        client = get_camb_client()

        result = client.translation.translation_stream(
            text=text_to_translate,
            source_language=source_lang,
            target_language=target_lang,
        )

        # Extract translated text
        if hasattr(result, 'text'):
            translated_text = result.text
        elif hasattr(result, '__iter__'):
            translated_text = ''.join(chunk if isinstance(chunk, str) else chunk.text for chunk in result)
        else:
            translated_text = str(result)

    except Exception as e:
        report_exception(chatbot, history, a="CAMB AI 翻译", b=f"翻译失败: {str(e)}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    # Save result
    os.makedirs(get_log_folder(plugin_name='camb_translation'), exist_ok=True)
    output_path = os.path.join(get_log_folder(plugin_name='camb_translation'), 'translation_result.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    promote_file_to_downloadzone(output_path, chatbot=chatbot)
    chatbot.append(["翻译完成", translated_text[:2000] + ("..." if len(translated_text) > 2000 else "")])
    history.extend(["翻译完成", translated_text])

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    yield from update_ui(chatbot=chatbot, history=history)

from toolbox import CatchException, report_exception, update_ui, get_log_folder
from toolbox import promote_file_to_downloadzone, write_history_to_file


@CatchException
def CambAI_VoiceClone(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    """CAMB AI 声音克隆插件：从音频样本创建自定义语音。"""
    import os

    chatbot.append(["函数插件功能？", "使用CAMB AI从音频样本克隆声音，生成可用于TTS的自定义voice_id。推荐使用10-30秒的清晰语音样本。"])
    yield from update_ui(chatbot=chatbot, history=history)

    # Parse advanced args: voice_name,gender_code
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""):
        plugin_kwargs.pop("advanced_arg")
    advanced_arg = plugin_kwargs.get("advanced_arg", "MyVoice,2")
    try:
        parts = advanced_arg.split(",")
        voice_name = parts[0].strip()
        gender = int(parts[1].strip()) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        voice_name = "MyVoice"
        gender = 0  # Not Specified

    # Find audio file
    if not os.path.exists(txt):
        if txt == "":
            txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"CAMB AI 声音克隆: {txt}", b=f"找不到本地文件或无权访问: {txt}。请上传一个10-30秒的音频文件。")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
    if not txt.endswith(tuple(extensions)):
        report_exception(chatbot, history,
                         a=f"CAMB AI 声音克隆: {txt}",
                         b=f"不支持的文件格式。请上传以下格式的音频文件: {', '.join(extensions)}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    chatbot.append([f"开始克隆声音: {os.path.basename(txt)}", f"声音名称: {voice_name}, 性别代码: {gender}\n处理中..."])
    yield from update_ui(chatbot=chatbot, history=history)

    try:
        from crazy_functions.camb_ai_utils import get_camb_client
        client = get_camb_client()

        with open(txt, 'rb') as f:
            result = client.voice_cloning.create_custom_voice(
                voice_name=voice_name,
                gender=gender,
                file=f,
            )

        voice_id = result.voice_id
        result_msg = (
            f"声音克隆成功！\n\n"
            f"Voice ID: **{voice_id}**\n"
            f"Voice Name: {voice_name}\n\n"
            f"使用方法：将 `CAMB_TTS_VOICE_ID = {voice_id}` 添加到 config_private.py 中即可使用此声音进行TTS。"
        )
        chatbot[-1] = (chatbot[-1][0], result_msg)
        history.extend(["声音克隆结果", result_msg])

    except Exception as e:
        report_exception(chatbot, history, a="CAMB AI 声音克隆", b=f"克隆失败: {str(e)}")

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    yield from update_ui(chatbot=chatbot, history=history)

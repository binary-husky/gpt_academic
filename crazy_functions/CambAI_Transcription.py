from toolbox import CatchException, report_exception, update_ui, get_log_folder
from toolbox import promote_file_to_downloadzone, write_history_to_file


@CatchException
def CambAI_Transcription(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    """CAMB AI 语音转文字插件：支持多种音频/视频格式，带说话人识别。"""
    import os
    import glob

    chatbot.append(["函数插件功能？", "使用CAMB AI进行语音转文字，支持说话人识别和时间戳。"])
    yield from update_ui(chatbot=chatbot, history=history)

    # Parse advanced args: language code (optional)
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""):
        plugin_kwargs.pop("advanced_arg")
    language_code = plugin_kwargs.get("advanced_arg", "1")  # Default: English
    try:
        language_code = int(language_code.strip())
    except ValueError:
        language_code = 1

    # Find audio/video files
    if not os.path.exists(txt):
        if txt == "":
            txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"CAMB AI 转录: {txt}", b=f"找不到本地文件或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    extensions = ['.mp4', '.m4a', '.wav', '.mp3', '.flac', '.aac']
    if txt.endswith(tuple(extensions)):
        file_manifest = [txt]
    else:
        file_manifest = []
        for ext in extensions:
            file_manifest.extend(glob.glob(f'{txt}/**/*{ext}', recursive=True))

    if not file_manifest:
        report_exception(chatbot, history, a=f"CAMB AI 转录: {txt}", b=f"找不到任何音频或视频文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    from crazy_functions.camb_ai_utils import get_camb_client, poll_task
    client = get_camb_client()
    os.makedirs(get_log_folder(plugin_name='camb_transcription'), exist_ok=True)

    history = []
    for index, fp in enumerate(file_manifest):
        chatbot.append([f"正在转录第 {index + 1}/{len(file_manifest)} 个文件: {os.path.basename(fp)}", "处理中..."])
        yield from update_ui(chatbot=chatbot, history=history)

        try:
            with open(fp, 'rb') as f:
                result = client.transcription.create_transcription(
                    language=language_code,
                    media_file=f,
                )

            task_id = result.task_id
            chatbot[-1] = (chatbot[-1][0], f"任务已提交 (task_id: {task_id})，等待处理...")
            yield from update_ui(chatbot=chatbot, history=history)

            status = poll_task(client.transcription.get_transcription_task_status, task_id)

            transcription = client.transcription.get_transcription_result(status.run_id)

            # Format output with speaker labels and timestamps
            output_lines = []
            if hasattr(transcription, 'segments') and transcription.segments:
                for seg in transcription.segments:
                    speaker = getattr(seg, 'speaker', 'Unknown')
                    start = getattr(seg, 'start', 0)
                    end = getattr(seg, 'end', 0)
                    text = getattr(seg, 'text', '')
                    output_lines.append(f"[{start:.1f}s - {end:.1f}s] Speaker {speaker}: {text}")
                transcript_text = "\n".join(output_lines)
            elif hasattr(transcription, 'text'):
                transcript_text = transcription.text
            else:
                transcript_text = str(transcription)

            # Save transcript
            output_path = os.path.join(
                get_log_folder(plugin_name='camb_transcription'),
                f'transcript_{index}.txt'
            )
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            promote_file_to_downloadzone(output_path, chatbot=chatbot)
            chatbot[-1] = (chatbot[-1][0], transcript_text[:3000] + ("..." if len(transcript_text) > 3000 else ""))
            history.extend([f"文件 {os.path.basename(fp)} 转录结果", transcript_text])
            yield from update_ui(chatbot=chatbot, history=history)

        except Exception as e:
            chatbot[-1] = (chatbot[-1][0], f"转录失败: {str(e)}")
            yield from update_ui(chatbot=chatbot, history=history)

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    chatbot.append(["所有文件转录完成", res])
    yield from update_ui(chatbot=chatbot, history=history)

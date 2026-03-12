from toolbox import CatchException, report_exception, update_ui, get_log_folder
from toolbox import promote_file_to_downloadzone, write_history_to_file


@CatchException
def CambAI_AudioSeparation(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    """CAMB AI 音频分离插件：将音频分离为人声和背景音。"""
    import os
    import glob
    import requests

    chatbot.append(["函数插件功能？", "使用CAMB AI将音频分离为人声和背景音轨。"])
    yield from update_ui(chatbot=chatbot, history=history)

    # Find audio files
    if not os.path.exists(txt):
        if txt == "":
            txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"CAMB AI 音频分离: {txt}", b=f"找不到本地文件或无权访问: {txt}")
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
        report_exception(chatbot, history, a=f"CAMB AI 音频分离: {txt}", b=f"找不到任何音频文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)
        return

    from crazy_functions.camb_ai_utils import get_camb_client, poll_task
    client = get_camb_client()
    output_dir = get_log_folder(plugin_name='camb_audio_separation')
    os.makedirs(output_dir, exist_ok=True)

    history = []
    for index, fp in enumerate(file_manifest):
        basename = os.path.splitext(os.path.basename(fp))[0]
        chatbot.append([f"正在分离第 {index + 1}/{len(file_manifest)} 个文件: {os.path.basename(fp)}", "处理中..."])
        yield from update_ui(chatbot=chatbot, history=history)

        try:
            with open(fp, 'rb') as f:
                result = client.audio_separation.create_audio_separation(media_file=f)

            task_id = result.task_id
            chatbot[-1] = (chatbot[-1][0], f"任务已提交 (task_id: {task_id})，等待处理...")
            yield from update_ui(chatbot=chatbot, history=history)

            status = poll_task(client.audio_separation.get_audio_separation_status, task_id)
            sep_info = client.audio_separation.get_audio_separation_run_info(status.run_id)

            # Download vocals and background
            saved_files = []
            for attr_name, label in [('vocals_url', 'vocals'), ('background_url', 'background')]:
                url = getattr(sep_info, attr_name, None)
                if url:
                    resp = requests.get(url)
                    resp.raise_for_status()
                    out_path = os.path.join(output_dir, f'{basename}_{label}.wav')
                    with open(out_path, 'wb') as f:
                        f.write(resp.content)
                    promote_file_to_downloadzone(out_path, chatbot=chatbot)
                    saved_files.append(out_path)

            result_msg = f"分离完成！已保存 {len(saved_files)} 个文件:\n" + "\n".join(saved_files)
            chatbot[-1] = (chatbot[-1][0], result_msg)
            history.extend([f"文件 {os.path.basename(fp)} 分离结果", result_msg])
            yield from update_ui(chatbot=chatbot, history=history)

        except Exception as e:
            chatbot[-1] = (chatbot[-1][0], f"音频分离失败: {str(e)}")
            yield from update_ui(chatbot=chatbot, history=history)

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    chatbot.append(["所有文件分离完成", res])
    yield from update_ui(chatbot=chatbot, history=history)

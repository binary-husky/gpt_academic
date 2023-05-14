from toolbox import CatchException, report_execption, select_api_key, update_ui, write_results_to_file
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, split_audio_file


def AnalyAudio(file_manifest, llm_kwargs, chatbot, history):
    import os, requests
    from moviepy.editor import AudioFileClip
    from request_llm.bridge_all import model_info

    # 设置OpenAI密钥和模型
    api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
    chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']

    whisper_endpoint = chat_endpoint.replace('chat/completions', 'audio/transcriptions')
    url = whisper_endpoint
    headers = {
        'Authorization': f"Bearer {api_key}"
    }

    os.makedirs('gpt_log/mp3/', exist_ok=True)
    for index, fp in enumerate(file_manifest):
        audio_history = []
        # 提取文件扩展名
        ext = os.path.splitext(fp)[1]
        # 提取视频中的音频
        if ext not in [".mp3", ".wav", ".m4a", ".mpga"]:
            audio_clip = AudioFileClip(fp)
            audio_clip.write_audiofile(f'gpt_log/mp3/output{index}.mp3')
            fp = f'gpt_log/mp3/output{index}.mp3'
        # 调用whisper模型音频转文字
        voice = split_audio_file(fp)
        for j, i in enumerate(voice):
            with open(i, 'rb') as f:
                file_content = f.read()  # 读取文件内容到内存
                files = {
                    'file': (os.path.basename(i), file_content),
                }
                data = {
                    "model": "whisper-1",
                    'response_format': "text"
                }
            response = requests.post(url, headers=headers, files=files, data=data).text

            i_say = f'请对下面的文章片段做概述，文章内容是 ```{response}```'
            i_say_show_user = f'第{index + 1}段音频的第{j + 1} / {len(voice)}片段。'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=[],
                sys_prompt="总结文章。"
            )

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.extend([i_say_show_user, gpt_say])
            audio_history.extend([i_say_show_user, gpt_say])

        # 已经对该文章的所有片段总结完毕，如果文章被切分了，
        result = "".join(audio_history)
        if len(audio_history) > 1:
            i_say = f"根据以上的对话，使用中文总结文章{result}的主要内容。"
            i_say_show_user = f'第{index + 1}段音频的主要内容：'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=audio_history,
                sys_prompt="总结文章。"
            )

            history.extend([i_say, gpt_say])
            audio_history.extend([i_say, gpt_say])

        res = write_results_to_file(history)
        chatbot.append((f"第{index + 1}段音频完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    # 删除中间文件夹
    import shutil
    shutil.rmtree('gpt_log/mp3')
    res = write_results_to_file(history)
    chatbot.append(("所有音频都总结完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history)


@CatchException
def 总结音视频(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "总结音视频内容，函数插件贡献者: dalvqw"])
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

    try:
        from moviepy.editor import AudioFileClip
    except:
        report_execption(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade moviepy```。")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return

    # 搜索需要处理的文件清单
    extensions = ['.mp4', '.m4a', '.wav', '.mpga', '.mpeg', '.mp3', '.avi', '.mkv', '.flac', '.aac']

    if txt.endswith(tuple(extensions)):
        file_manifest = [txt]
    else:
        file_manifest = []
        for extension in extensions:
            file_manifest.extend(glob.glob(f'{project_folder}/**/*{extension}', recursive=True))

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何音频或视频文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return

    # 开始正式执行任务
    yield from AnalyAudio(file_manifest, llm_kwargs, chatbot, history)

    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

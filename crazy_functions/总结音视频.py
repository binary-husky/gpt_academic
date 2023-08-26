from comm_tools.toolbox import CatchException, report_execption, select_api_key, update_ui, write_results_to_file, get_conf
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, get_files_from_everything
import glob, os
from comm_tools import func_box

from crazy_functions import KDOCS_轻文档分析, crazy_box


def split_audio_file(filename, split_duration=1000):
    """
    根据给定的切割时长将音频文件切割成多个片段。

    Args:
        filename (str): 需要被切割的音频文件名。
        split_duration (int, optional): 每个切割音频片段的时长（以秒为单位）。默认值为1000。

    Returns:
        filelist (list): 一个包含所有切割音频片段文件路径的列表。

    """
    from moviepy.editor import AudioFileClip
    import os
    os.makedirs('gpt_log/mp3/cut/', exist_ok=True)  # 创建存储切割音频的文件夹

    # 读取音频文件
    audio = AudioFileClip(filename)

    # 计算文件总时长和切割点
    total_duration = audio.duration
    split_points = list(range(0, int(total_duration), split_duration))
    split_points.append(int(total_duration))
    filelist = []

    # 切割音频文件
    for i in range(len(split_points) - 1):
        start_time = split_points[i]
        end_time = split_points[i + 1]
        split_audio = audio.subclip(start_time, end_time)
        split_audio.write_audiofile(f"gpt_log/mp3/cut/{filename[0]}_{i}.mp3")
        filelist.append(f"gpt_log/mp3/cut/{filename[0]}_{i}.mp3")

    audio.close()
    return filelist

def AnalyAudio(parse_prompt, file_manifest, llm_kwargs, chatbot, history):
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
                    "prompt": parse_prompt,
                    'response_format': "text"
                }

            chatbot.append([f"将 {i} 发送到openai音频解析终端 (whisper)，当前参数：{parse_prompt}", "正在处理 ..."])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
            proxies, = get_conf('proxies')
            response = requests.post(url, headers=headers, files=files, data=data, proxies=proxies).text

            chatbot.append(["音频解析结果", response])
            history.extend(["音频解析结果", response])
            yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面

            i_say = f'请对下面的音频片段做概述，音频内容是 ```{response}```'
            i_say_show_user = f'第{index + 1}段音频的第{j + 1} / {len(voice)}片段。'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=[],
                sys_prompt=f"总结音频。音频文件名{fp}"
            )

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.extend([i_say_show_user, gpt_say])
            audio_history.extend([i_say_show_user, gpt_say])

        # 已经对该文章的所有片段总结完毕，如果文章被切分了
        result = "".join(audio_history)
        if len(audio_history) > 1:
            i_say = f"根据以上的对话，总结音频“{result}”的主要内容。"
            i_say_show_user = f'第{index + 1}段音频的主要内容：'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=audio_history,
                sys_prompt=""
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
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "总结音视频内容，函数插件贡献者: dalvqw & BinaryHusky"])
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
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    parse_prompt = plugin_kwargs.get("advanced_arg", '将音频解析为简体中文')
    yield from AnalyAudio(parse_prompt, file_manifest, llm_kwargs, chatbot, history)
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面


def audio_extraction_text(file):
    import speech_recognition as sr
    # 打开音频文件
    r = sr.Recognizer()
    with sr.AudioFile(file) as source:
        # 读取音频文件的内容
        audio_content = r.record(source)
        # 使用Google的文字转话服务将音频转换为文字
        text = r.recognize_google(audio_content, language='zh-CN')
    return text


def audio_comparison_of_video_converters(files, chatbot, history):
    from moviepy.editor import AudioFileClip
    temp_chat = ''
    chatbot.append(['可以开始了么', temp_chat])
    temp_list = []
    for file in files:
        temp_chat += f'正在将{func_box.html_view_blank(file)}文件转换为可提取的音频文件.\n\n'
        chatbot[-1] = ['可以开始了么', temp_chat]
        yield from update_ui(chatbot=chatbot, history=history)
        temp_path = os.path.join(os.path.dirname(file), f"{os.path.basename(file)}.wav")
        videoclip = AudioFileClip(file)
        videoclip.write_audiofile(temp_path)
        temp_list.extend((temp_path, audio_extraction_text(temp_path)))
    return temp_list


@CatchException
def Kdocs音频提取总结(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, WEB_PORT):
    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt) or txt.find('http') != -1:
        project_folder = txt
    else:
        report_execption(chatbot, history, a=None, b=f"{crazy_box.previously_on_plugins}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return
    # 搜索需要处理的文件清单
    extensions = ['.mp4', '.m4a', '.wav', '.mpga', '.mpeg', '.mp3', '.avi', '.mkv', '.flac', '.aac']
    if txt.endswith(tuple(extensions)):
        file_manifest = [txt]
    else:
        file_manifest = []
        for ed in extensions:
            _, file_manifest_tmp, _ = get_files_from_everything(txt, ed, ipaddr=llm_kwargs['ipaddr'])
            _, kdocs_manifest_tmp, _ = crazy_box.get_kdocs_from_everything(txt, ed, ipaddr=llm_kwargs['ipaddr'])
            file_manifest += kdocs_manifest_tmp
            file_manifest += file_manifest_tmp

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_execption(chatbot, history, a=f"解析项目: {txt}", b=f"{crazy_box.previously_on_plugins}")
        yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
        return
    # 将音频转换为文字
    txt_manifest = yield from audio_comparison_of_video_converters(file_manifest, chatbot, history)
    inputs_array, inputs_show_user_array = yield from crazy_box.input_output_processing(txt_manifest, llm_kwargs, plugin_kwargs, chatbot, history)
    gpt_response_collection = yield from crazy_box.submit_multithreaded_tasks(inputs_array, inputs_show_user_array, llm_kwargs, chatbot, history, plugin_kwargs)
    yield from update_ui(chatbot, history, '插件执行成功')

if __name__ == '__main__':
    # 创建一个音频识别对象w
    import speech_recognition as sr
    from pydub import AudioSegment


    def extract_audio(file_path):
        audio = AudioSegment.from_file(file_path)
        return audio


    def recognize_speech(audio):
        r = sr.Recognizer()
        audio_data = sr.AudioData(audio.raw_data,
                                  sample_rate=audio.frame_rate,
                                  sample_width=audio.sample_width)

        # 文字识别
        text = r.recognize_google(audio_data, language='en')

        # 返回文字和时间段
        time_markers = []
        for i, segment in enumerate(audio[::10000]):  # 根据需要调整分割时间间隔
            start_time = i * 10
            end_time = (i + 1) * 10
            time_markers.append({
                'text': text,
                'start_time': start_time,
                'end_time': end_time
            })

        return time_markers


    file_path = '/Users/kilig/Desktop/土木三班陈同学-离人.mp3'  # 替换成你的音视频文件路径
    audio = extract_audio(file_path)
    time_markers = recognize_speech(audio)

    for marker in time_markers:
        print(f"Text: {marker['text']}")
        print(f"Start Time: {marker['start_time']}s")
        print(f"End Time: {marker['end_time']}s")
        print('---')

import requests
import random
import time
import re
import json
from bs4 import BeautifulSoup
from functools import lru_cache
from itertools import zip_longest
from check_proxy import check_proxy
from toolbox import CatchException, update_ui, get_conf, promote_file_to_downloadzone, update_ui_lastest_msg, generate_file_link
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, input_clipping
from request_llms.bridge_all import model_info
from request_llms.bridge_all import predict_no_ui_long_connection
from crazy_functions.prompts.internet import SearchOptimizerPrompt, SearchAcademicOptimizerPrompt
from crazy_functions.json_fns.pydantic_io import GptJsonIO, JsonStringError
from textwrap import dedent
from loguru import logger
from pydantic import BaseModel, Field

class Query(BaseModel):
    search_keyword: str = Field(description="search query for video resource")

# {'title': '【麦笛奈Martine】天文馆的猫 | Diffsinger Lynxnet版本中文试听【Cover 泠鸢·折纸信笺】', 'author': '灰条纹的灰猫君', 'author_id': 2083633, 'bvid': 'BV1LSSHYXEtv', '播放量': 75, '弹幕': 0, '评论': 7, '点赞': 5, '发布时间': '2024-10-31 22:10:08', '视频时长': '4:40', 'tag': '虚拟歌姬,鸟蛋,冷鸟,女声翻唱,泠鸢yousa,虚拟主播,虚拟UP主,VTuber,Diffsinger,虚拟歌手分享官,虚拟之声创作计划·2024第三期', 'description': '翻唱：麦笛奈Martine\n调混：灰条纹的灰猫君\nQ版曲绘：西柚Kanno\n原曲：Av847726911\n原唱：泠鸢\n\n滑铲——月更！\n万圣节快乐！今天是和喵星发电报的可爱猫猫~'}

class VideoResource(BaseModel):
    thought: str = Field(description="analysis of the search results based on the user's query")
    title: str = Field(description="title of the video")
    author: str = Field(description="author/uploader of the video") 
    bvid: str = Field(description="unique ID of the video")


def get_video_resource(search_keyword):
    from crazy_functions.media_fns.get_media import search_videos

    # Search for videos and return the first result
    videos = search_videos(
        search_keyword
    )

    # Return the first video if results exist, otherwise return None
    return videos

def download_video(bvid, user_name, chatbot, history):
    # from experimental_mods.get_bilibili_resource import download_bilibili
    from crazy_functions.media_fns.get_media import download_video
    # pause a while
    tic_time = 8
    for i in range(tic_time):
        yield from update_ui_lastest_msg(
            lastmsg=f"即将下载音频。等待{tic_time-i}秒后自动继续, 点击“停止”键取消此操作。", 
            chatbot=chatbot, history=[], delay=1)

    # download audio
    chatbot.append((None, "下载音频, 请稍等...")); yield from update_ui(chatbot=chatbot, history=history)
    downloaded_files = yield from download_video(bvid, only_audio=True, user_name=user_name, chatbot=chatbot, history=history)

    # preview
    preview_list = [promote_file_to_downloadzone(fp) for fp in downloaded_files]
    file_links = generate_file_link(preview_list)
    yield from update_ui_lastest_msg(f"已完成的文件: <br/>" + file_links, chatbot=chatbot, history=history, delay=0)
    chatbot.append((None, f"即将下载视频。"))

    # pause a while
    tic_time = 16
    for i in range(tic_time):
        yield from update_ui_lastest_msg(
            lastmsg=f"即将下载视频。等待{tic_time-i}秒后自动继续, 点击“停止”键取消此操作。", 
            chatbot=chatbot, history=[], delay=1)

    # download video
    chatbot.append((None, "下载视频, 请稍等...")); yield from update_ui(chatbot=chatbot, history=history)
    downloaded_files_part2 = yield from download_video(bvid, only_audio=False, user_name=user_name, chatbot=chatbot, history=history)

    # preview
    preview_list = [promote_file_to_downloadzone(fp) for fp in downloaded_files_part2]
    file_links = generate_file_link(preview_list)
    yield from update_ui_lastest_msg(f"已完成的文件: <br/>" + file_links, chatbot=chatbot, history=history, delay=0)

    # return
    return downloaded_files + downloaded_files_part2

@CatchException
def 多媒体任务(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    user_wish: str = txt

    # 搜索
    chatbot.append((txt, "检索中, 请稍等..."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    # 结构化生成
    rf_req = dedent(f"""
    The user wish to get the following resource:
        {user_wish}
    Generate reseach keywords (less than 5 keywords) accordingly.
    """)
    gpt_json_io = GptJsonIO(Query)
    inputs = rf_req + gpt_json_io.format_instructions
    run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
    analyze_res = run_gpt_fn(inputs, "")
    logger.info(analyze_res)
    query: Query = gpt_json_io.generate_output_auto_repair(analyze_res, run_gpt_fn)
    # 关键词展示
    chatbot.append((None, f"检索关键词已确认: {query.search_keyword}。筛选中, 请稍等..."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 获取候选资源
    candadate_dictionary: dict =  get_video_resource(query.search_keyword)
    candadate_dictionary_as_str = json.dumps(candadate_dictionary, ensure_ascii=False, indent=4)

    # 展示候选资源
    candadate_display = "\n".join([f"{i+1}. {it['title']}" for i, it in enumerate(candadate_dictionary)])
    chatbot.append((None, f"候选:\n\n{candadate_display}"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 结构化生成
    rf_req_2 = dedent(f"""
    The user wish to get the following resource:
        {user_wish}

    Select the most relevant and suitable video resource from the following search results:
        {candadate_dictionary_as_str}

    Note:
        1. The first several search video results are more likely to satisfy the user's wish.
        2. The time duration of the video should be less than 10 minutes.
        3. You should analyze the search results first, before giving your answer.
        4. Use Chinese if possible.
    """)
    gpt_json_io = GptJsonIO(VideoResource)
    inputs = rf_req_2 + gpt_json_io.format_instructions
    run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
    analyze_res = run_gpt_fn(inputs, "")
    logger.info(analyze_res)
    video_resource: VideoResource = gpt_json_io.generate_output_auto_repair(analyze_res, run_gpt_fn)

    # Display
    chatbot.append(
        (None, 
            f"分析：{video_resource.thought}" "<br/>"
            f"选择: `{video_resource.title}`。" "<br/>" 
            f"作者：{video_resource.author}"
        )
    )
    chatbot.append((None, f"下载中, 请稍等..."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    if video_resource and video_resource.bvid:
        logger.info(video_resource)
        yield from download_video(video_resource.bvid, chatbot.get_user(), chatbot, history)
"""
对项目中的各个插件进行测试。运行方法：直接运行 python tests/test_plugins.py
"""

import init_test
import os, sys

if __name__ == "__main__":
    from experimental_mods.get_bilibili_resource import download_bilibili
    download_bilibili("BV1LSSHYXEtv", only_audio=True, user_name="test")

# if __name__ == "__main__":
#     from test_utils import plugin_test

#     plugin_test(plugin='crazy_functions.VideoResource_GPT->视频任务', main_input="帮我找到《天文馆的猫》，歌手泠鸢")

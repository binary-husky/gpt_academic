"""
对项目中的各个插件进行测试。运行方法：直接运行 python tests/test_plugins.py
"""


import os, sys


def validate_path():
    dir_name = os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(dir_name + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # 返回项目根路径

if __name__ == "__main__":
    from tests.test_utils import plugin_test

    plugin_test(plugin="crazy_functions.知识库问答->知识库文件注入", main_input="./README.md")

    plugin_test(
        plugin="crazy_functions.知识库问答->读取知识库作答",
        main_input="What is the installation method？",
    )

    plugin_test(plugin="crazy_functions.知识库问答->读取知识库作答", main_input="远程云服务器部署？")

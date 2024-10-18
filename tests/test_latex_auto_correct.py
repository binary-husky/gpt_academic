"""
对项目中的各个插件进行测试。运行方法：直接运行 python tests/test_plugins.py
"""


import os, sys, importlib


def validate_path():
    dir_name = os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(dir_name + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # 返回项目根路径

if __name__ == "__main__":
    plugin_test = importlib.import_module('test_utils').plugin_test


    # plugin_test(plugin='crazy_functions.Latex_Function->Latex翻译中文并重新编译PDF', main_input="2203.01927")
    # plugin_test(plugin='crazy_functions.Latex_Function->Latex翻译中文并重新编译PDF', main_input="gpt_log/arxiv_cache/2203.01927/workfolder")
    # plugin_test(plugin='crazy_functions.Latex_Function->Latex翻译中文并重新编译PDF', main_input="2410.05779")
    plugin_test(plugin='crazy_functions.Latex_Function->Latex翻译中文并重新编译PDF', main_input="gpt_log/default_user/workfolder")


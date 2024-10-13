"""
对项目中的各个插件进行测试。运行方法：直接运行 python tests/test_plugins.py
"""

import init_test
import os, sys


if __name__ == "__main__":
    from test_utils import plugin_test

    plugin_test(plugin='crazy_functions.数学动画生成manim->动画生成', main_input="A point moving along function culve y=sin(x), starting from x=0 and stop at x=4*\pi.")

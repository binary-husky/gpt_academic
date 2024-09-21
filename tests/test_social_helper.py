"""
对项目中的各个插件进行测试。运行方法：直接运行 python tests/test_plugins.py
"""

import init_test
import os, sys


if __name__ == "__main__":
    from test_utils import plugin_test
    plugin_test(
        plugin='crazy_functions.Social_Helper->I人助手', 
        main_input="""
添加联系人：
艾德·史塔克：我的养父，他是临冬城的公爵。
凯特琳·史塔克：我的养母，她对我态度冷淡，因为我是私生子。
罗柏·史塔克：我的哥哥，他是北境的继承人。
艾莉亚·史塔克：我的妹妹，她和我关系亲密，性格独立坚强。
珊莎·史塔克：我的妹妹，她梦想成为一位淑女。
布兰·史塔克：我的弟弟，他有预知未来的能力。
瑞肯·史塔克：我的弟弟，他是个天真无邪的小孩。
山姆威尔·塔利：我的朋友，他在守夜人军团中与我并肩作战。
伊格瑞特：我的恋人，她是野人中的一员。
        """)

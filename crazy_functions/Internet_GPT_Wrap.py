import random
from toolbox import get_conf
from crazy_functions.Internet_GPT import 连接网络回答问题
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty


class NetworkGPT_Wrap(GptAcademicPluginTemplate):
    def __init__(self):
        """
        请注意`execute`会执行在不同的线程中，因此您在定义和使用类变量时，应当慎之又慎！
        """
        pass

    def define_arg_selection_menu(self):
        """
        定义插件的二级选项菜单

        第一个参数，名称`main_input`，参数`type`声明这是一个文本框，文本框上方显示`title`，文本框内部显示`description`，`default_value`为默认值；
        第二个参数，名称`advanced_arg`，参数`type`声明这是一个文本框，文本框上方显示`title`，文本框内部显示`description`，`default_value`为默认值；
        第三个参数，名称`allow_cache`，参数`type`声明这是一个下拉菜单，下拉菜单上方显示`title`+`description`，下拉菜单的选项为`options`，`default_value`为下拉菜单默认值；

        """
        urls = get_conf("SEARXNG_URLS")
        url = random.choice(urls)

        gui_definition = {
            "main_input":
                ArgProperty(title="输入问题", description="待通过互联网检索的问题，会自动读取输入框内容", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "categories":
                ArgProperty(title="搜索分类", options=["网页", "学术论文"], default_value="网页", description="无", type="dropdown").model_dump_json(),
            "engine":
                ArgProperty(title="选择搜索引擎", options=["Mixed", "bing", "google", "duckduckgo"], default_value="google", description="无", type="dropdown").model_dump_json(),
            "optimizer":
                ArgProperty(title="搜索优化", options=["关闭", "开启", "开启(增强)"], default_value="关闭", description="是否使用搜索增强。注意这可能会消耗较多token", type="dropdown").model_dump_json(),
            "searxng_url":
                ArgProperty(title="Searxng服务地址", description="输入Searxng的地址", default_value=url, type="string").model_dump_json(), # 主输入，自动从输入框同步

        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        if plugin_kwargs["categories"] == "网页": plugin_kwargs["categories"] = "general"
        if plugin_kwargs["categories"] == "学术论文": plugin_kwargs["categories"] = "science"
        yield from 连接网络回答问题(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)


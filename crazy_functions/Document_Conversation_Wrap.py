import random
from toolbox import get_conf
from crazy_functions.Document_Conversation import 批量文件询问
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty


class Document_Conversation_Wrap(GptAcademicPluginTemplate):
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
        gui_definition = {
            "main_input":
                ArgProperty(title="已上传的文件", description="上传文件后自动填充", default_value="", type="string").model_dump_json(),
            "searxng_url":
                ArgProperty(title="对材料提问", description="提问", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs:dict, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        yield from 批量文件询问(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)

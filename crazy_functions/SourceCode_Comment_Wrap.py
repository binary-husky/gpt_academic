
from toolbox import get_conf, update_ui
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty
from crazy_functions.SourceCode_Comment import 注释Python项目

class SourceCodeComment_Wrap(GptAcademicPluginTemplate):
    def __init__(self):
        """
        请注意`execute`会执行在不同的线程中，因此您在定义和使用类变量时，应当慎之又慎！
        """
        pass

    def define_arg_selection_menu(self):
        """
        定义插件的二级选项菜单
        """
        gui_definition = {
            "main_input":
                ArgProperty(title="路径", description="程序路径（上传文件后自动填写）", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "use_chinese":
                ArgProperty(title="注释语言", options=["英文", "中文"], default_value="英文", description="无", type="dropdown").model_dump_json(),
            # "use_emoji":
                # ArgProperty(title="在注释中使用emoji", options=["禁止", "允许"], default_value="禁止", description="无", type="dropdown").model_dump_json(),
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        if plugin_kwargs["use_chinese"] == "中文": 
            plugin_kwargs["use_chinese"] = True
        else: 
            plugin_kwargs["use_chinese"] = False

        yield from 注释Python项目(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)

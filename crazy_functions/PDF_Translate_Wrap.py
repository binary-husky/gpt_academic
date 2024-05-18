from .PDF_Translate import 批量翻译PDF文档
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty

class PDF_Tran(GptAcademicPluginTemplate):
    def __init__(self):
        pass

    def define_arg_selection_menu(self):
        gui_definition = {
            "main_input":
                ArgProperty(title="PDF文件路径", description="上传文件后，会自动生成路径", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "advanced_arg":
                ArgProperty(title="高级参数输入区", description="无", default_value="", type="string").model_dump_json(), # 高级参数输入区，自动同步
            "additional_01":
                ArgProperty(title="附属参数", description="无", default_value="没有附属参数", type="string").model_dump_json(), # 高级参数输入区，自动同步
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        print(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
        yield from 批量翻译PDF文档(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
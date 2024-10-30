
from crazy_functions.Latex_Function import Latex翻译中文并重新编译PDF, PDF翻译中文并重新编译PDF
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty


class Arxiv_Localize(GptAcademicPluginTemplate):
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
                ArgProperty(title="ArxivID", description="输入Arxiv的ID或者网址", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "advanced_arg":
                ArgProperty(title="额外的翻译提示词",
                            description=r"如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 "
                                        r"例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: "
                                        r'If the term "agent" is used in this section, it should be translated to "智能体". ',
                            default_value="", type="string").model_dump_json(), # 高级参数输入区，自动同步
            "allow_cache":
                ArgProperty(title="是否允许从缓存中调取结果", options=["允许缓存", "从头执行"], default_value="允许缓存", description="无", type="dropdown").model_dump_json(),
            "allow_cloudio":
                ArgProperty(title="是否允许从GPTAC学术云下载(或者上传)翻译结果(仅针对Arxiv论文)", options=["允许", "禁止"], default_value="禁止", description="共享文献，互助互利", type="dropdown").model_dump_json(),
        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        allow_cache = plugin_kwargs["allow_cache"]
        allow_cloudio = plugin_kwargs["allow_cloudio"]
        advanced_arg = plugin_kwargs["advanced_arg"]

        if allow_cache == "从头执行": plugin_kwargs["advanced_arg"] = "--no-cache " + plugin_kwargs["advanced_arg"]

        # 从云端下载翻译结果，以及上传翻译结果到云端；人人为我，我为人人。
        if allow_cloudio == "允许": plugin_kwargs["advanced_arg"] = "--allow-cloudio " + plugin_kwargs["advanced_arg"]

        yield from Latex翻译中文并重新编译PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)



class PDF_Localize(GptAcademicPluginTemplate):
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
                ArgProperty(title="PDF文件路径", description="未指定路径，请上传文件后，再点击该插件", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "advanced_arg":
                ArgProperty(title="额外的翻译提示词",
                            description=r"如果有必要, 请在此处给出自定义翻译命令, 解决部分词汇翻译不准确的问题。 "
                                        r"例如当单词'agent'翻译不准确时, 请尝试把以下指令复制到高级参数区: "
                                        r'If the term "agent" is used in this section, it should be translated to "智能体". ',
                            default_value="", type="string").model_dump_json(), # 高级参数输入区，自动同步
            "method":
                ArgProperty(title="采用哪种方法执行转换", options=["MATHPIX", "DOC2X"], default_value="DOC2X", description="无", type="dropdown").model_dump_json(),

        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        yield from PDF翻译中文并重新编译PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
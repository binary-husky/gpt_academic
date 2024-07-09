
from toolbox import get_conf, update_ui
from crazy_functions.Image_Generate import 图片生成_DALLE2, 图片生成_DALLE3, 图片修改_DALLE2
from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate, ArgProperty


class ImageGen_Wrap(GptAcademicPluginTemplate):
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

        """
        gui_definition = {
            "main_input":
                ArgProperty(title="输入图片描述", description="需要生成图像的文本描述，尽量使用英文", default_value="", type="string").model_dump_json(), # 主输入，自动从输入框同步
            "model_name":
                ArgProperty(title="模型", options=["DALLE2", "DALLE3"], default_value="DALLE3", description="无", type="dropdown").model_dump_json(),
            "resolution":
                ArgProperty(title="分辨率", options=["256x256(限DALLE2)", "512x512(限DALLE2)", "1024x1024", "1792x1024(限DALLE3)", "1024x1792(限DALLE3)"], default_value="1024x1024", description="无", type="dropdown").model_dump_json(),
            "quality (仅DALLE3生效)":
                ArgProperty(title="质量", options=["standard", "hd"], default_value="standard", description="无", type="dropdown").model_dump_json(),
            "style (仅DALLE3生效)":
                ArgProperty(title="风格", options=["vivid", "natural"], default_value="vivid", description="无", type="dropdown").model_dump_json(),

        }
        return gui_definition

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        """
        执行插件
        """
        # 分辨率
        resolution = plugin_kwargs["resolution"].replace("(限DALLE2)", "").replace("(限DALLE3)", "")

        if plugin_kwargs["model_name"] == "DALLE2":
            plugin_kwargs["advanced_arg"] = resolution
            yield from 图片生成_DALLE2(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)

        elif plugin_kwargs["model_name"] == "DALLE3":
            quality = plugin_kwargs["quality (仅DALLE3生效)"]
            style = plugin_kwargs["style (仅DALLE3生效)"]
            plugin_kwargs["advanced_arg"] = f"{resolution}-{quality}-{style}"
            yield from 图片生成_DALLE3(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)

        else:
            chatbot.append([None, "抱歉，找不到该模型"])
            yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

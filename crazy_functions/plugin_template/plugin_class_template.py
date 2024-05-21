import os, json, base64
from pydantic import BaseModel, Field
from textwrap import dedent
from typing import List

class ArgProperty(BaseModel): # PLUGIN_ARG_MENU
    title: str = Field(description="The title", default="")
    description: str = Field(description="The description", default="")
    default_value: str = Field(description="The default value", default="")
    type: str = Field(description="The type", default="")   # currently we support ['string', 'dropdown']
    options: List[str] = Field(default=[], description="List of options available for the argument") # only used when type is 'dropdown'

class GptAcademicPluginTemplate():
    def __init__(self):
        # please note that `execute` method may run in different threads,
        # thus you should not store any state in the plugin instance,
        # which may be accessed by multiple threads
        pass


    def define_arg_selection_menu(self):
        """
        An example as below:
            ```
            def define_arg_selection_menu(self):
                gui_definition = {
                    "main_input":
                        ArgProperty(title="main input", description="description", default_value="default_value", type="string").model_dump_json(),
                    "advanced_arg":
                        ArgProperty(title="advanced arguments", description="description", default_value="default_value", type="string").model_dump_json(),
                    "additional_arg_01":
                        ArgProperty(title="additional", description="description", default_value="default_value", type="string").model_dump_json(),
                }
                return gui_definition
            ```
        """
        raise NotImplementedError("You need to implement this method in your plugin class")


    def get_js_code_for_generating_menu(self, btnName):
        define_arg_selection = self.define_arg_selection_menu()

        if len(define_arg_selection.keys()) > 8:
            raise ValueError("You can only have up to 8 arguments in the define_arg_selection")
        # if "main_input" not in define_arg_selection:
        #     raise ValueError("You must have a 'main_input' in the define_arg_selection")

        DEFINE_ARG_INPUT_INTERFACE = json.dumps(define_arg_selection)
        return base64.b64encode(DEFINE_ARG_INPUT_INTERFACE.encode('utf-8')).decode('utf-8')

    def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        raise NotImplementedError("You need to implement this method in your plugin class")
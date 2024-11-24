from toolbox import CatchException, update_ui, get_conf, select_api_key, get_log_folder
from crazy_functions.multi_stage.multi_stage_utils import GptAcademicState


@CatchException
def AntFinTest(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    chatbot.append(("AntFin Test", "AntFin Test"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 界面更新


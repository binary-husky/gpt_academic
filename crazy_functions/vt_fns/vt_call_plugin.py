from pydantic import BaseModel, Field
from typing import List
from comm_tools.toolbox import update_ui_lastest_msg, get_conf
from request_llm.bridge_all import predict_no_ui_long_connection
from crazy_functions.json_fns.pydantic_io import GptJsonIO
import copy, json, pickle, os, sys


def read_avail_plugin_enum():
    from comm_tools.crazy_functional import get_crazy_functions
    plugin_arr = get_crazy_functions()
    # remove plugins with out explaination
    plugin_arr = {k:v for k, v in plugin_arr.items() if 'Info' in v}
    plugin_arr_info = {"F{:04d}".format(i):v["Info"] for i, v in enumerate(plugin_arr.values(), start=1)}
    plugin_arr_dict = {"F{:04d}".format(i):v for i, v in enumerate(plugin_arr.values(), start=1)}
    prompt = json.dumps(plugin_arr_info, ensure_ascii=False, indent=2)
    prompt = "\n\nThe defination of PluginEnum:\nPluginEnum=" + prompt
    return prompt, plugin_arr_dict


def execute_plugin(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_intention):
    plugin_arr_enum_prompt, plugin_arr_dict = read_avail_plugin_enum()
    class Plugin(BaseModel):
        plugin_selection: str = Field(description="The most related plugin from one of the PluginEnum.", default="F0000000000000")
        plugin_arg: str = Field(description="The argument of the plugin. A path or url or empty.", default="")

    # ⭐ ⭐ ⭐ 选择插件
    yield from update_ui_lastest_msg(lastmsg=f"正在执行任务: {txt}\n\n查找可用插件中...", chatbot=chatbot, history=history, delay=0)
    gpt_json_io = GptJsonIO(Plugin)
    gpt_json_io.format_instructions += plugin_arr_enum_prompt
    inputs = "Choose the correct plugin and extract plugin_arg, the user requirement is: \n\n" + \
             ">> " + txt.rstrip('\n').replace('\n','\n>> ') + '\n\n' + \
             gpt_json_io.format_instructions 
    run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(
        inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
    plugin_sel = gpt_json_io.generate_output_auto_repair(run_gpt_fn(inputs, ""), run_gpt_fn)

    if plugin_sel.plugin_selection not in plugin_arr_dict:
        msg = f'找不到合适插件执行该任务'
        yield from update_ui_lastest_msg(lastmsg=msg, chatbot=chatbot, history=history, delay=2)
        return
    
    # ⭐ ⭐ ⭐ 确认插件参数
    plugin = plugin_arr_dict[plugin_sel.plugin_selection]
    yield from update_ui_lastest_msg(lastmsg=f"正在执行任务: {txt}\n\n提取插件参数...", chatbot=chatbot, history=history, delay=0)
    class PluginExplicit(BaseModel):
        plugin_selection: str = plugin_sel.plugin_selection
        plugin_arg: str = Field(description="The argument of the plugin.", default="")
    gpt_json_io = GptJsonIO(PluginExplicit)
    gpt_json_io.format_instructions += "The information about this plugin is:" + plugin["Info"]
    inputs = f"A plugin named {plugin_sel.plugin_selection} is selected, " + \
             "you should extract plugin_arg from the user requirement, the user requirement is: \n\n" + \
             ">> " + txt.rstrip('\n').replace('\n','\n>> ') + '\n\n' + \
             gpt_json_io.format_instructions 
    run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(
        inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
    plugin_sel = gpt_json_io.generate_output_auto_repair(run_gpt_fn(inputs, ""), run_gpt_fn)


    # ⭐ ⭐ ⭐ 执行插件
    fn = plugin['Function']
    fn_name = fn.__name__
    msg = f'正在调用插件: {fn_name}\n\n插件说明：{plugin["Info"]}\n\n插件参数：{plugin_sel.plugin_arg}'
    yield from update_ui_lastest_msg(lastmsg=msg, chatbot=chatbot, history=history, delay=2)
    yield from fn(plugin_sel.plugin_arg, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, -1)
    return
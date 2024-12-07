import json
import base64
from typing import Callable

def load_web_cookie_cache__fn_builder(customize_btns, cookies, predefined_btns)->Callable:
    def load_web_cookie_cache(persistent_cookie_, cookies_):
        import gradio as gr
        from themes.theme import load_dynamic_theme, to_cookie_str, from_cookie_str, assign_user_uuid

        ret = {}
        for k in customize_btns:
            ret.update({customize_btns[k]: gr.update(visible=False, value="")})

        try: persistent_cookie_ = from_cookie_str(persistent_cookie_)    # persistent cookie to dict
        except: return ret

        customize_fn_overwrite_ = persistent_cookie_.get("custom_bnt", {})
        cookies_['customize_fn_overwrite'] = customize_fn_overwrite_
        ret.update({cookies: cookies_})

        for k,v in persistent_cookie_["custom_bnt"].items():
            if v['Title'] == "": continue
            if k in customize_btns: ret.update({customize_btns[k]: gr.update(visible=True, value=v['Title'])})
            else: ret.update({predefined_btns[k]: gr.update(visible=True, value=v['Title'])})
        return ret
    return load_web_cookie_cache

def assign_btn__fn_builder(customize_btns, predefined_btns, cookies, web_cookie_cache)->Callable:
    def assign_btn(persistent_cookie_, cookies_, basic_btn_dropdown_, basic_fn_title, basic_fn_prefix, basic_fn_suffix, clean_up=False):
        import gradio as gr
        from themes.theme import load_dynamic_theme, to_cookie_str, from_cookie_str, assign_user_uuid
        ret = {}
        # 读取之前的自定义按钮
        customize_fn_overwrite_ = cookies_['customize_fn_overwrite']
        # 更新新的自定义按钮
        customize_fn_overwrite_.update({
            basic_btn_dropdown_:
                {
                    "Title":basic_fn_title,
                    "Prefix":basic_fn_prefix,
                    "Suffix":basic_fn_suffix,
                }
            }
        )
        if clean_up:
            customize_fn_overwrite_ = {}
        cookies_.update(customize_fn_overwrite_)    # 更新cookie
        visible = (not clean_up) and (basic_fn_title != "")
        if basic_btn_dropdown_ in customize_btns:
            # 是自定义按钮，不是预定义按钮
            ret.update({customize_btns[basic_btn_dropdown_]: gr.update(visible=visible, value=basic_fn_title)})
        else:
            # 是预定义按钮
            ret.update({predefined_btns[basic_btn_dropdown_]: gr.update(visible=visible, value=basic_fn_title)})
        ret.update({cookies: cookies_})
        try: persistent_cookie_ = from_cookie_str(persistent_cookie_)   # persistent cookie to dict
        except: persistent_cookie_ = {}
        persistent_cookie_["custom_bnt"] = customize_fn_overwrite_      # dict update new value
        persistent_cookie_ = to_cookie_str(persistent_cookie_)          # persistent cookie to dict
        ret.update({web_cookie_cache: persistent_cookie_})             # write persistent cookie
        return ret
    return assign_btn

# cookies, web_cookie_cache = make_cookie_cache()
def make_cookie_cache():
    # 定义 后端state（cookies）、前端（web_cookie_cache）两兄弟
    import gradio as gr
    from toolbox import load_chat_cookies
    # 定义cookies的后端state
    cookies = gr.State(load_chat_cookies())
    # 定义cookies的一个孪生的前端存储区（隐藏）
    web_cookie_cache = gr.Textbox(visible=False, elem_id="web_cookie_cache")
    return cookies, web_cookie_cache

# history, history_cache, history_cache_update = make_history_cache()
def make_history_cache():
    # 定义 后端state（history）、前端（history_cache）、后端setter（history_cache_update）三兄弟
    import gradio as gr
    # 定义history的后端state
    # history = gr.State([])
    history = gr.Textbox(visible=False, elem_id="history-ng")
    # # 定义history的一个孪生的前端存储区（隐藏）
    # history_cache = gr.Textbox(visible=False, elem_id="history_cache")
    # # 定义history_cache->history的更新方法（隐藏）。在触发这个按钮时，会先执行js代码更新history_cache，然后再执行python代码更新history
    # def process_history_cache(history_cache):
    #     return json.loads(history_cache)
    # # 另一种更简单的setter方法
    # history_cache_update = gr.Button("", elem_id="elem_update_history", visible=False).click(
    #     process_history_cache, inputs=[history_cache], outputs=[history])
    # # save history to history_cache
    # def process_history_cache(history_cache):
    #     return json.dumps(history_cache)
    # # 定义history->history_cache的更新方法（隐藏）
    # def sync_history_cache(history):
    #     print("sync_history_cache", history)
    #     return json.dumps(history)
    # # history.change(sync_history_cache, inputs=[history], outputs=[history_cache])

    # # history_cache_sync = gr.Button("", elem_id="elem_sync_history", visible=False).click(
    # #     lambda history: (json.dumps(history)), inputs=[history_cache], outputs=[history])
    return history, None, None



def create_button_with_javascript_callback(btn_value, elem_id, variant, js_callback, input_list, output_list, function, input_name_list, output_name_list):
    import gradio as gr
    middle_ware_component = gr.Textbox(visible=False, elem_id=elem_id+'_buffer')
    def get_fn_wrap():
        def fn_wrap(*args):
            summary_dict = {}
            for name, value in zip(input_name_list, args):
                summary_dict.update({name: value})

            res = function(*args)

            for name, value in zip(output_name_list, res):
                summary_dict.update({name: value})

            summary = base64.b64encode(json.dumps(summary_dict).encode('utf8')).decode("utf-8")
            return (*res, summary)
        return fn_wrap

    btn = gr.Button(btn_value, elem_id=elem_id, variant=variant)
    call_args = ""
    for name in output_name_list:
        call_args += f"""Data["{name}"],"""
    call_args = call_args.rstrip(",")
    _js_callback = """
        (base64MiddleString)=>{
            console.log('hello')
            const stringData = atob(base64MiddleString);
            let Data = JSON.parse(stringData);
            call = JS_CALLBACK_GEN;
            call(CALL_ARGS);
        }
    """.replace("JS_CALLBACK_GEN", js_callback).replace("CALL_ARGS", call_args)

    btn.click(get_fn_wrap(), input_list, output_list+[middle_ware_component]).then(None, [middle_ware_component], None, _js=_js_callback)
    return btn
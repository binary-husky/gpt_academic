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


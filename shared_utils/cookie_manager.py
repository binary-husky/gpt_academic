
def cookie_buffer_loader(gradio_comp_customize_btns, gradio_comp_predefined_btns, gradio_comp_cookies):
    def fn(persistent_cookie_, cookies_):
        import gradio as gr
        from themes.theme import load_dynamic_theme, to_cookie_str, from_cookie_str, assign_user_uuid
        ret = {}
        for k in gradio_comp_customize_btns:
            ret.update({gradio_comp_customize_btns[k]: gr.update(visible=False, value="")})

        try: persistent_cookie_ = from_cookie_str(persistent_cookie_)    # persistent cookie to dict
        except: return ret

        customize_fn_overwrite_ = persistent_cookie_.get("custom_bnt", {})
        cookies_['customize_fn_overwrite'] = customize_fn_overwrite_
        ret.update({gradio_comp_cookies: cookies_})

        for k,v in persistent_cookie_["custom_bnt"].items():
            if v['Title'] == "": continue
            if k in gradio_comp_customize_btns: ret.update({gradio_comp_customize_btns[k]: gr.update(visible=True, value=v['Title'])})
            else: ret.update({gradio_comp_predefined_btns[k]: gr.update(visible=True, value=v['Title'])})
        return ret
    return fn
function remove_legacy_cookie() {
    setCookie("web_cookie_cache", "", -1);
    setCookie("js_previous_chat_cookie", "", -1);
    setCookie("js_previous_history_cookie", "", -1);
}


async function GptAcademicJavaScriptInit(dark, prompt, live2d, layout, tts) {
    // 第一部分，布局初始化
    remove_legacy_cookie();
    audio_fn_init();
    minor_ui_adjustment();
    ButtonWithDropdown_init();
    update_conversation_metadata();
    window.addEventListener("gptac_restore_chat_from_local_storage", restore_chat_from_local_storage);
    
    // 加载欢迎页面
    const welcomeMessage = new WelcomeMessage();
    welcomeMessage.begin_render();
    chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
    var chatbotObserver = new MutationObserver(() => {
        chatbotContentChanged(1);
        welcomeMessage.update();
    });
    chatbotObserver.observe(chatbotIndicator, { attributes: true, childList: true, subtree: true });
    
    if (layout === "LEFT-RIGHT") { chatbotAutoHeight(); }
    if (layout === "LEFT-RIGHT") { limit_scroll_position(); }

    // 第二部分，读取Cookie，初始话界面
    let searchString = "";
    let bool_value = "";
    //  darkmode 深色模式
    if (getCookie("js_darkmode_cookie")) {
        dark = getCookie("js_darkmode_cookie")
    }
    dark = dark == "True";
    if (document.querySelectorAll('.dark').length) {
        if (!dark) {
            document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
        }
    } else {
        if (dark) {
            document.querySelector('body').classList.add('dark');
        }
    }

    //  自动朗读
    if (tts != "DISABLE"){
        enable_tts = true;
        if (getCookie("js_auto_read_cookie")) {
            auto_read_tts = getCookie("js_auto_read_cookie")
            auto_read_tts = auto_read_tts == "True";
            if (auto_read_tts) {
                allow_auto_read_tts_flag = true;
            }
        }
    }

    // SysPrompt 系统静默提示词
    gpt_academic_gradio_saveload("load", "elem_prompt", "js_system_prompt_cookie", null, "str");
    // Temperature 大模型温度参数
    gpt_academic_gradio_saveload("load", "elem_temperature", "js_temperature_cookie", null, "float");
    // md_dropdown 大模型类型选择
    if (getCookie("js_md_dropdown_cookie")) {
        const cached_model = getCookie("js_md_dropdown_cookie");
        var model_sel = await get_gradio_component("elem_model_sel");
        // determine whether the cached model is in the choices
        if (model_sel.props.choices.includes(cached_model)){
            // change dropdown
            gpt_academic_gradio_saveload("load", "elem_model_sel", "js_md_dropdown_cookie", null, "str");
            // 连锁修改chatbot的label
            push_data_to_gradio_component({
                label: '当前模型：' + getCookie("js_md_dropdown_cookie"),
                __type__: 'update'
            }, "gpt-chatbot", "obj")
        }
    }



    // clearButton 自动清除按钮
    if (getCookie("js_clearbtn_show_cookie")) {
        // have cookie
        bool_value = getCookie("js_clearbtn_show_cookie")
        bool_value = bool_value == "True";
        searchString = "输入清除键";

        if (bool_value) {
            // make btns appear
            let clearButton = document.getElementById("elem_clear"); clearButton.style.display = "block";
            let clearButton2 = document.getElementById("elem_clear2"); clearButton2.style.display = "block";
            // deal with checkboxes
            let arr_with_clear_btn = update_array(
                await get_data_from_gradio_component('cbs'), "输入清除键", "add"
            )
            push_data_to_gradio_component(arr_with_clear_btn, "cbs", "no_conversion");
        } else {
            // make btns disappear
            let clearButton = document.getElementById("elem_clear"); clearButton.style.display = "none";
            let clearButton2 = document.getElementById("elem_clear2"); clearButton2.style.display = "none";
            // deal with checkboxes
            let arr_without_clear_btn = update_array(
                await get_data_from_gradio_component('cbs'), "输入清除键", "remove"
            )
            push_data_to_gradio_component(arr_without_clear_btn, "cbs", "no_conversion");
        }
    }

    // live2d 显示
    if (getCookie("js_live2d_show_cookie")) {
        // have cookie
        searchString = "添加Live2D形象";
        bool_value = getCookie("js_live2d_show_cookie");
        bool_value = bool_value == "True";
        if (bool_value) {
            loadLive2D();
            let arr_with_live2d = update_array(
                await get_data_from_gradio_component('cbsc'), "添加Live2D形象", "add"
            )
            push_data_to_gradio_component(arr_with_live2d, "cbsc", "no_conversion");
        } else {
            try {
                $('.waifu').hide();
                let arr_without_live2d = update_array(
                    await get_data_from_gradio_component('cbsc'), "添加Live2D形象", "remove"
                )
                push_data_to_gradio_component(arr_without_live2d, "cbsc", "no_conversion");
            } catch (error) {
            }
        }
    } else {
        // do not have cookie
        if (live2d) {
            loadLive2D();
        } else {
        }
    }

    // 主题加载（恢复到上次）
    change_theme("", "")

}

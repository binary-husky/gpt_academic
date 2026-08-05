function remove_legacy_cookie() {
    setCookie("web_cookie_cache", "", -1);
    setCookie("js_previous_chat_cookie", "", -1);
    setCookie("js_previous_history_cookie", "", -1);
}


function processFontFamily(fontfamily) {
    // 检查是否包含括号
    if (fontfamily.includes('(')) {
        // 分割字符串
        const parts = fontfamily.split('(');
        const fontNamePart = parts[1].split(')')[0].trim(); // 获取括号内的部分

        // 检查是否包含 @
        if (fontNamePart.includes('@')) {
            const [fontName, fontUrl] = fontNamePart.split('@').map(part => part.trim());
            return { fontName, fontUrl };
        } else {
            return { fontName: fontNamePart, fontUrl: null };
        }
    } else {
        return { fontName: fontfamily, fontUrl: null };
    }
}

// 检查字体是否存在
function checkFontAvailability(fontfamily) {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        // 设置两个不同的字体进行比较
        const testText = 'abcdefghijklmnopqrstuvwxyz0123456789';
        context.font = `16px ${fontfamily}, sans-serif`;
        const widthWithFont = context.measureText(testText).width;

        context.font = '16px sans-serif';
        const widthWithFallback = context.measureText(testText).width;

        // 如果宽度相同，说明字体不存在
        resolve(widthWithFont !== widthWithFallback);
    });
}
async function checkFontAvailabilityV2(fontfamily) {
    fontName = fontfamily;
    console.log('Checking font availability:', fontName);
    if ('queryLocalFonts' in window) {
        try {
            const fonts = await window.queryLocalFonts();
            const fontExists = fonts.some(font => font.family === fontName);
            console.log(`Local Font "${fontName}" exists:`, fontExists);
            return fontExists;
        } catch (error) {
            console.error('Error querying local fonts:', error);
            return false;
        }
    } else {
        console.error('queryLocalFonts is not supported in this browser.');
        return false;
    }
}
// 动态加载字体
function loadFont(fontfamily, fontUrl) {
    return new Promise((resolve, reject) => {
        // 使用 Google Fonts 或其他字体来源
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = fontUrl;
        link.onload = () => {
            toast_push(`字体 "${fontfamily}" 已成功加载`, 3000);
            resolve();
        };
        link.onerror = (error) => {
            reject(error);
        };
        document.head.appendChild(link);
    });
}
function gpt_academic_change_chatbot_font(fontfamily, fontsize, fontcolor) {
    const chatbot = document.querySelector('#gpt-chatbot');
    // 检查元素是否存在
    if (chatbot) {
        if (fontfamily != null) {
            // 更改字体
            const result = processFontFamily(fontfamily);
            if (result.fontName == "Theme-Default-Font") {
                chatbot.style.fontFamily = result.fontName;
                return;
            }
            // 检查字体是否存在
            checkFontAvailability(result.fontName).then((isAvailable) => {
                if (isAvailable) {
                    // 如果字体存在，直接应用
                    chatbot.style.fontFamily = result.fontName;
                } else {
                    if (result.fontUrl == null) {
                        // toast_push('无法加载字体，本地字体不存在，且URL未提供', 3000);
                        // 直接把失效的字体放上去，让系统自动fallback
                        chatbot.style.fontFamily = result.fontName;
                        return;
                    } else {
                        toast_push('正在下载字体', 3000);
                        // 如果字体不存在，尝试加载字体
                        loadFont(result.fontName, result.fontUrl).then(() => {
                            chatbot.style.fontFamily = result.fontName;
                        }).catch((error) => {
                            console.error(`无法加载字体 "${result.fontName}":`, error);
                        });
                    }
                }
            });

        }
        if (fontsize != null) {
            // 修改字体大小
            document.documentElement.style.setProperty(
                '--gpt-academic-message-font-size',
                `${fontsize}px`
            );
        }
        if (fontcolor != null) {
            // 更改字体颜色
            chatbot.style.color = fontcolor;
        }
    } else {
        console.error('#gpt-chatbot is missing');
    }
}

function footer_show_hide(show) {
    if (show) {
        document.querySelector('footer').style.display = '';
    } else {
        document.querySelector('footer').style.display = 'none';
    }
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
    if (tts != "DISABLE") {
        enable_tts = true;
        if (getCookie("js_auto_read_cookie")) {
            auto_read_tts = getCookie("js_auto_read_cookie")
            auto_read_tts = auto_read_tts == "True";
            if (auto_read_tts) {
                allow_auto_read_tts_flag = true;
            }
        }
    }

    // 字体
    gpt_academic_gradio_saveload("load", "elem_fontfamily", "js_fontfamily", null, "str");
    gpt_academic_change_chatbot_font(getCookie("js_fontfamily"), null, null);
    gpt_academic_gradio_saveload("load", "elem_fontsize", "js_fontsize", null, "str");
    gpt_academic_change_chatbot_font(null, getCookie("js_fontsize"), null);
    // SysPrompt 系统静默提示词
    gpt_academic_gradio_saveload("load", "elem_prompt", "js_system_prompt_cookie", null, "str");
    // Temperature 大模型温度参数
    gpt_academic_gradio_saveload("load", "elem_temperature", "js_temperature_cookie", null, "float");
    // md_dropdown 大模型类型选择
    if (getCookie("js_md_dropdown_cookie")) {
        const cached_model = getCookie("js_md_dropdown_cookie");
        var model_sel = await get_gradio_component("elem_model_sel");
        // determine whether the cached model is in the choices
        if (model_sel.props.choices.includes(cached_model)) {
            // change dropdown
            gpt_academic_gradio_saveload("load", "elem_model_sel", "js_md_dropdown_cookie", null, "str");
            // 连锁修改chatbot的label
            push_data_to_gradio_component({
                label: '当前模型：' + getCookie("js_md_dropdown_cookie"),
                __type__: 'update'
            }, "gpt-chatbot", "obj")
        }
    }


    if (getCookie("js_show_title")) {
        // have cookie
        bool_value = getCookie("js_show_title")
        bool_value = bool_value == "True";
        searchString = "主标题";
        tool_bar_group = "cbsc";
        const true_function = function () {
            document.querySelector('.prose.svelte-1ybaih5 h1').style.display = '';
        }
        const false_function = function () {
            document.querySelector('.prose.svelte-1ybaih5 h1').style.display = 'none';
        }
        if (bool_value) {
            // make btns appear
            true_function();
            // deal with checkboxes
            let arr_with_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "add"
            )
            push_data_to_gradio_component(arr_with_clear_btn, tool_bar_group, "no_conversion");
        } else {
            false_function();
            // deal with checkboxes
            let arr_without_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "remove"
            )
            push_data_to_gradio_component(arr_without_clear_btn, tool_bar_group, "no_conversion");
        }
    }
    if (getCookie("js_show_subtitle")) {
        // have cookie
        bool_value = getCookie("js_show_subtitle")
        bool_value = bool_value == "True";
        searchString = "副标题";
        tool_bar_group = "cbsc";
        const true_function = function () {
            element = document.querySelector('.prose.svelte-1ybaih5 h2');
            if (element) element.style.display = '';
            element = document.querySelector('.prose.svelte-1ybaih5 h6');
            if (element) element.style.display = '';
        }
        const false_function = function () {
            element = document.querySelector('.prose.svelte-1ybaih5 h2');
            if (element) element.style.display = 'none';
            element = document.querySelector('.prose.svelte-1ybaih5 h6');
            if (element) element.style.display = 'none';
        }
        if (bool_value) {
            // make btns appear
            true_function();
            // deal with checkboxes
            let arr_with_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "add"
            )
            push_data_to_gradio_component(arr_with_clear_btn, tool_bar_group, "no_conversion");
        } else {
            false_function();
            // deal with checkboxes
            let arr_without_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "remove"
            )
            push_data_to_gradio_component(arr_without_clear_btn, tool_bar_group, "no_conversion");
        }
    }
    if (getCookie("js_show_footer")) {
        // have cookie
        bool_value = getCookie("js_show_footer")
        searchString = "显示logo";
        tool_bar_group = "cbsc";
        bool_value = bool_value == "True";
        if (bool_value) {
            // make btns appear
            footer_show_hide(true);
            // deal with checkboxes
            let arr_with_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "add"
            )
            push_data_to_gradio_component(arr_with_clear_btn, tool_bar_group, "no_conversion");
        } else {
            footer_show_hide(false);
            // deal with checkboxes
            let arr_without_clear_btn = update_array(
                await get_data_from_gradio_component(tool_bar_group), searchString, "remove"
            )
            push_data_to_gradio_component(arr_without_clear_btn, tool_bar_group, "no_conversion");
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
                await get_data_from_gradio_component("cbs"), "输入清除键", "add"
            )
            push_data_to_gradio_component(arr_with_clear_btn, "cbs", "no_conversion");
        } else {
            // make btns disappear
            let clearButton = document.getElementById("elem_clear"); clearButton.style.display = "none";
            let clearButton2 = document.getElementById("elem_clear2"); clearButton2.style.display = "none";
            // deal with checkboxes
            let arr_without_clear_btn = update_array(
                await get_data_from_gradio_component("cbs"), "输入清除键", "remove"
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



function apply_checkbox_change_for_group2(display_panel_arr) {
    setTimeout(() => {
        display_panel_arr = get_checkbox_selected_items("cbsc");

        let searchString = "添加Live2D形象";
        if (display_panel_arr.includes(searchString)) {
            setCookie("js_live2d_show_cookie", "True", 365);
            loadLive2D();
        } else {
            try {
                setCookie("js_live2d_show_cookie", "False", 365);
                $('.waifu').hide();
            } catch (e) {
            }
        }


        function handleDisplay(searchString, key, displayElement, showFn, hideFn) {
            if (display_panel_arr.includes(searchString)) {
                setCookie(key, "True", 365);
                if (showFn) showFn();
                if (displayElement) displayElement.style.display = '';
            } else {
                setCookie(key, "False", 365);
                if (hideFn) hideFn();
                if (displayElement) displayElement.style.display = 'none';
            }
        }

        // 主标题
        const mainTitle = document.querySelector('.prose.svelte-1ybaih5 h1');
        handleDisplay("主标题", "js_show_title", mainTitle, null, null);

        // 副标题
        const subTitle = document.querySelector('.prose.svelte-1ybaih5 h2');
        handleDisplay("副标题", "js_show_subtitle", subTitle, null, null);

        // 显示logo
        handleDisplay("显示logo", "js_show_footer", null, () => footer_show_hide(true), () => footer_show_hide(false));
    }, 50);
}

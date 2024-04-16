// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 1 部分: 工具函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function push_data_to_gradio_component(DAT, ELEM_ID, TYPE) {
    // type,               // type==="str" / type==="float"
    if (TYPE == "str") {
        // convert dat to string: do nothing
    }
    else if (TYPE == "obj") {
        // convert dat to string: do nothing
    }
    else if (TYPE == "no_conversion") {
        // no nothing
    }
    else if (TYPE == "float") {
        // convert dat to float
        DAT = parseFloat(DAT);
    }
    const myEvent = new CustomEvent('gpt_academic_update_gradio_component', {
        detail: {
            data: DAT,
            elem_id: ELEM_ID,
        }
    });
    window.dispatchEvent(myEvent);
}


async function get_gradio_component(ELEM_ID) {
    function waitFor(ELEM_ID) {
        return new Promise((resolve) => {
            const myEvent = new CustomEvent('gpt_academic_get_gradio_component_value', {
                detail: {
                    elem_id: ELEM_ID,
                    resolve,
                }
            });
            window.dispatchEvent(myEvent);
        });
    }
    result = await waitFor(ELEM_ID);
    return result;
}


async function get_data_from_gradio_component(ELEM_ID) {
    let comp = await get_gradio_component(ELEM_ID);
    return comp.props.value;
}


function update_array(arr, item, mode) {
    //   // Remove "输入清除键"
    //   p = updateArray(p, "输入清除键", "remove");
    //   console.log(p); // Should log: ["基础功能区", "函数插件区"]

    //   // Add "输入清除键"
    //   p = updateArray(p, "输入清除键", "add");
    //   console.log(p); // Should log: ["基础功能区", "函数插件区", "输入清除键"]

    const index = arr.indexOf(item);
    if (mode === "remove") {
        if (index !== -1) {
            // Item found, remove it
            arr.splice(index, 1);
        }
    } else if (mode === "add") {
        if (index === -1) {
            // Item not found, add it
            arr.push(item);
        }
    }
    return arr;
}


function gradioApp() {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];
    if (elem !== document) {
        elem.getElementById = function (id) {
            return document.getElementById(id);
        };
    }
    return elem.shadowRoot ? elem.shadowRoot : elem;
}


function setCookie(name, value, days) {
    var expires = "";

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }

    document.cookie = name + "=" + value + expires + "; path=/";
}


function getCookie(name) {
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookies = decodedCookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();

        if (cookie.indexOf(name + "=") === 0) {
            return cookie.substring(name.length + 1, cookie.length);
        }
    }

    return null;
}


let toastCount = 0;
function toast_push(msg, duration) {
    duration = isNaN(duration) ? 3000 : duration;
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => {
        toast.style.top = `${parseInt(toast.style.top, 10) - 70}px`;
    });
    const m = document.createElement('div');
    m.innerHTML = msg;
    m.classList.add('toast');
    m.style.cssText = `font-size: var(--text-md) !important; color: rgb(255, 255, 255); background-color: rgba(0, 0, 0, 0.6); padding: 10px 15px; border-radius: 4px; position: fixed; top: ${50 + toastCount * 70}%; left: 50%; transform: translateX(-50%); width: auto; text-align: center; transition: top 0.3s;`;
    document.body.appendChild(m);
    setTimeout(function () {
        m.style.opacity = '0';
        setTimeout(function () {
            document.body.removeChild(m);
            toastCount--;
        }, 500);
    }, duration);
    toastCount++;
}


function toast_up(msg) {
    var m = document.getElementById('toast_up');
    if (m) {
        document.body.removeChild(m); // remove the loader from the body
    }
    m = document.createElement('div');
    m.id = 'toast_up';
    m.innerHTML = msg;
    m.style.cssText = "font-size: var(--text-md) !important; color: rgb(255, 255, 255); background-color: rgba(0, 0, 100, 0.6); padding: 10px 15px; margin: 0 0 0 -60px; border-radius: 4px; position: fixed; top: 50%; left: 50%; width: auto; text-align: center;";
    document.body.appendChild(m);
}


function toast_down() {
    var m = document.getElementById('toast_up');
    if (m) {
        document.body.removeChild(m); // remove the loader from the body
    }
}


function begin_loading_status() {
    // Create the loader div and add styling
    var loader = document.createElement('div');
    loader.id = 'Js_File_Loading';
    var C1 = document.createElement('div');
    var C2 = document.createElement('div');
    // var C3 = document.createElement('span');
    // C3.textContent = '上传中...'
    // C3.style.position = "fixed";
    // C3.style.top = "50%";
    // C3.style.left = "50%";
    // C3.style.width = "80px";
    // C3.style.height = "80px";
    // C3.style.margin = "-40px 0 0 -40px";

    C1.style.position = "fixed";
    C1.style.top = "50%";
    C1.style.left = "50%";
    C1.style.width = "80px";
    C1.style.height = "80px";
    C1.style.borderLeft = "12px solid #00f3f300";
    C1.style.borderRight = "12px solid #00f3f300";
    C1.style.borderTop = "12px solid #82aaff";
    C1.style.borderBottom = "12px solid #82aaff"; // Added for effect
    C1.style.borderRadius = "50%";
    C1.style.margin = "-40px 0 0 -40px";
    C1.style.animation = "spinAndPulse 2s linear infinite";

    C2.style.position = "fixed";
    C2.style.top = "50%";
    C2.style.left = "50%";
    C2.style.width = "40px";
    C2.style.height = "40px";
    C2.style.borderLeft = "12px solid #00f3f300";
    C2.style.borderRight = "12px solid #00f3f300";
    C2.style.borderTop = "12px solid #33c9db";
    C2.style.borderBottom = "12px solid #33c9db"; // Added for effect
    C2.style.borderRadius = "50%";
    C2.style.margin = "-20px 0 0 -20px";
    C2.style.animation = "spinAndPulse2 2s linear infinite";

    loader.appendChild(C1);
    loader.appendChild(C2);
    // loader.appendChild(C3);
    document.body.appendChild(loader); // Add the loader to the body

    // Set the CSS animation keyframes for spin and pulse to be synchronized
    var styleSheet = document.createElement('style');
    styleSheet.id = 'Js_File_Loading_Style';
    styleSheet.textContent = `
    @keyframes spinAndPulse {
        0% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(90deg) scale(1.1); }
        50% { transform: rotate(180deg) scale(1); }
        75% { transform: rotate(270deg) scale(0.9); }
        100% { transform: rotate(360deg) scale(1); }
    }

    @keyframes spinAndPulse2 {
        0% { transform: rotate(-90deg);}
        25% { transform: rotate(-180deg);}
        50% { transform: rotate(-270deg);}
        75% { transform: rotate(-360deg);}
        100% { transform: rotate(-450deg);}
    }
    `;
    document.head.appendChild(styleSheet);
}


function cancel_loading_status() {
    // remove the loader from the body
    var loadingElement = document.getElementById('Js_File_Loading');
    if (loadingElement) {
        document.body.removeChild(loadingElement);
    }
    var loadingStyle = document.getElementById('Js_File_Loading_Style');
    if (loadingStyle) {
        document.head.removeChild(loadingStyle);
    }
    // create new listen event
    let clearButton = document.querySelectorAll('div[id*="elem_upload"] button[aria-label="Clear"]');
    for (let button of clearButton) {
        button.addEventListener('click', function () {
            setTimeout(function () {
                register_upload_event();
            }, 50);
        });
    }
}


// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 2 部分: 复制按钮
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function addCopyButton(botElement) {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    // Copy bot button
    const copiedIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
    const copyIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';

    const messageBtnColumnElement = botElement.querySelector('.message-btn-row');
    if (messageBtnColumnElement) {
        // if .message-btn-column exists
        return;
    }

    var copyButton = document.createElement('button');
    copyButton.classList.add('copy-bot-btn');
    copyButton.setAttribute('aria-label', 'Copy');
    copyButton.innerHTML = copyIcon;
    copyButton.addEventListener('click', async () => {
        const textToCopy = botElement.innerText;
        try {
            if ("clipboard" in navigator) {
                await navigator.clipboard.writeText(textToCopy);
                copyButton.innerHTML = copiedIcon;
                setTimeout(() => {
                    copyButton.innerHTML = copyIcon;
                }, 1500);
            } else {
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    copyButton.innerHTML = copiedIcon;
                    setTimeout(() => {
                        copyButton.innerHTML = copyIcon;
                    }, 1500);
                } catch (error) {
                    console.error("Copy failed: ", error);
                }
                document.body.removeChild(textArea);
            }
        } catch (error) {
            console.error("Copy failed: ", error);
        }
    });
    var messageBtnColumn = document.createElement('div');
    messageBtnColumn.classList.add('message-btn-row');
    messageBtnColumn.appendChild(copyButton);
    botElement.appendChild(messageBtnColumn);
}


let timeoutID = null;
let lastInvocationTime = 0;
let lastArgs = null;
function do_something_but_not_too_frequently(min_interval, func) {
    return function (...args) {
        lastArgs = args;
        const now = Date.now();
        if (!lastInvocationTime || (now - lastInvocationTime) >= min_interval) {
            lastInvocationTime = now;
            // 现在就执行
            setTimeout(() => {
                func.apply(this, lastArgs);
            }, 0);
        } else if (!timeoutID) {
            // 等一会执行
            timeoutID = setTimeout(() => {
                timeoutID = null;
                lastInvocationTime = Date.now();
                func.apply(this, lastArgs);
            }, min_interval - (now - lastInvocationTime));
        } else {
            // 压根不执行
        }
    }
}


function chatbotContentChanged(attempt = 1, force = false) {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    for (var i = 0; i < attempt; i++) {
        setTimeout(() => {
            gradioApp().querySelectorAll('#gpt-chatbot .message-wrap .message.bot').forEach(addCopyButton);
        }, i === 0 ? 0 : 200);
    }
    // we have moved mermaid-related code to gradio-fix repository: binary-husky/gradio-fix@32150d0

}



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 3 部分: chatbot动态高度调整
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function chatbotAutoHeight() {
    // 自动调整高度：立即
    function update_height() {
        var { height_target, chatbot_height, chatbot } = get_elements(true);
        if (height_target != chatbot_height) {
            var pixelString = height_target.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }

    // 自动调整高度：缓慢
    function update_height_slow() {
        var { height_target, chatbot_height, chatbot } = get_elements();
        if (height_target != chatbot_height) {
            // sign = (height_target - chatbot_height)/Math.abs(height_target - chatbot_height);
            // speed = Math.max(Math.abs(height_target - chatbot_height), 1);
            new_panel_height = (height_target - chatbot_height) * 0.5 + chatbot_height;
            if (Math.abs(new_panel_height - height_target) < 10) {
                new_panel_height = height_target;
            }
            var pixelString = new_panel_height.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }
    monitoring_input_box()
    update_height();
    window.addEventListener('resize', function () { update_height(); });
    window.addEventListener('scroll', function () { update_height_slow(); });
    setInterval(function () { update_height_slow() }, 50); // 每50毫秒执行一次
}


swapped = false;
function swap_input_area() {
    // Get the elements to be swapped
    var element1 = document.querySelector("#input-panel");
    var element2 = document.querySelector("#basic-panel");

    // Get the parent of the elements
    var parent = element1.parentNode;

    // Get the next sibling of element2
    var nextSibling = element2.nextSibling;

    // Swap the elements
    parent.insertBefore(element2, element1);
    parent.insertBefore(element1, nextSibling);
    if (swapped) { swapped = false; }
    else { swapped = true; }
}


function get_elements(consider_state_panel = false) {
    var chatbot = document.querySelector('#gpt-chatbot > div.wrap.svelte-18telvq');
    if (!chatbot) {
        chatbot = document.querySelector('#gpt-chatbot');
    }
    const panel1 = document.querySelector('#input-panel').getBoundingClientRect();
    const panel2 = document.querySelector('#basic-panel').getBoundingClientRect()
    const panel3 = document.querySelector('#plugin-panel').getBoundingClientRect();
    // const panel4 = document.querySelector('#interact-panel').getBoundingClientRect();
    const panel_active = document.querySelector('#state-panel').getBoundingClientRect();
    if (consider_state_panel || panel_active.height < 25) {
        document.state_panel_height = panel_active.height;
    }
    // 25 是chatbot的label高度, 16 是右侧的gap
    var height_target = panel1.height + panel2.height + panel3.height + 0 + 0 - 25 + 16 * 2;
    // 禁止动态的state-panel高度影响
    height_target = height_target + (document.state_panel_height - panel_active.height)
    var height_target = parseInt(height_target);
    var chatbot_height = chatbot.style.height;
    // 交换输入区位置，使得输入区始终可用
    if (!swapped) {
        if (panel1.top != 0 && (0.9 * panel1.bottom + 0.1 * panel1.top) < 0) { swap_input_area(); }
    }
    else if (swapped) {
        if (panel2.top != 0 && panel2.top > 0) { swap_input_area(); }
    }
    // 调整高度
    const err_tor = 5;
    if (Math.abs(panel1.left - chatbot.getBoundingClientRect().left) < err_tor) {
        // 是否处于窄屏模式
        height_target = window.innerHeight * 0.6;
    } else {
        // 调整高度
        const chatbot_height_exceed = 15;
        const chatbot_height_exceed_m = 10;
        b_panel = Math.max(panel1.bottom, panel2.bottom, panel3.bottom)
        if (b_panel >= window.innerHeight - chatbot_height_exceed) {
            height_target = window.innerHeight - chatbot.getBoundingClientRect().top - chatbot_height_exceed_m;
        }
        else if (b_panel < window.innerHeight * 0.75) {
            height_target = window.innerHeight * 0.8;
        }
    }
    var chatbot_height = parseInt(chatbot_height);
    return { height_target, chatbot_height, chatbot };
}



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 4 部分: 粘贴、拖拽文件上传
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

var elem_upload = null;
var elem_upload_float = null;
var elem_input_main = null;
var elem_input_float = null;
var elem_chatbot = null;
var elem_upload_component_float = null;
var elem_upload_component = null;
var exist_file_msg = '⚠️请先删除上传区（左上方）中的历史文件，再尝试上传。'

function locate_upload_elems() {
    elem_upload = document.getElementById('elem_upload')
    elem_upload_float = document.getElementById('elem_upload_float')
    elem_input_main = document.getElementById('user_input_main')
    elem_input_float = document.getElementById('user_input_float')
    elem_chatbot = document.getElementById('gpt-chatbot')
    elem_upload_component_float = elem_upload_float.querySelector("input[type=file]");
    elem_upload_component = elem_upload.querySelector("input[type=file]");
}

async function upload_files(files) {
    let totalSizeMb = 0
    elem_upload_component_float = elem_upload_float.querySelector("input[type=file]");
    if (files && files.length > 0) {
        // 执行具体的上传逻辑
        if (elem_upload_component_float) {
            for (let i = 0; i < files.length; i++) {
                // 将从文件数组中获取的文件大小(单位为字节)转换为MB，
                totalSizeMb += files[i].size / 1024 / 1024;
            }
            // 检查文件总大小是否超过20MB
            if (totalSizeMb > 20) {
                toast_push('⚠️文件夹大于 20MB 🚀上传文件中', 3000);
            }
            let event = new Event("change");
            Object.defineProperty(event, "target", { value: elem_upload_component_float, enumerable: true });
            Object.defineProperty(event, "currentTarget", { value: elem_upload_component_float, enumerable: true });
            Object.defineProperty(elem_upload_component_float, "files", { value: files, enumerable: true });
            elem_upload_component_float.dispatchEvent(event);
        } else {
            toast_push(exist_file_msg, 3000);
        }
    }
}


function register_func_paste(input) {
    let paste_files = [];
    if (input) {
        input.addEventListener("paste", async function (e) {
            const clipboardData = e.clipboardData || window.clipboardData;
            const items = clipboardData.items;
            if (items) {
                for (i = 0; i < items.length; i++) {
                    if (items[i].kind === "file") { // 确保是文件类型
                        const file = items[i].getAsFile();
                        // 将每一个粘贴的文件添加到files数组中
                        paste_files.push(file);
                        e.preventDefault();  // 避免粘贴文件名到输入框
                    }
                }
                if (paste_files.length > 0) {
                    // 按照文件列表执行批量上传逻辑
                    await upload_files(paste_files);
                    paste_files = []

                }
            }
        });
    }
}


function register_func_drag(elem) {
    if (elem) {
        const dragEvents = ["dragover"];
        const leaveEvents = ["dragleave", "dragend", "drop"];

        const onDrag = function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (elem_upload_float.querySelector("input[type=file]")) {
                toast_up('⚠️释放以上传文件')
            } else {
                toast_up(exist_file_msg)
            }
        };

        const onLeave = function (e) {
            toast_down();
            e.preventDefault();
            e.stopPropagation();
        };

        dragEvents.forEach(event => {
            elem.addEventListener(event, onDrag);
        });

        leaveEvents.forEach(event => {
            elem.addEventListener(event, onLeave);
        });

        elem.addEventListener("drop", async function (e) {
            const files = e.dataTransfer.files;
            await upload_files(files);
        });
    }
}


function elem_upload_component_pop_message(elem) {
    if (elem) {
        const dragEvents = ["dragover"];
        const leaveEvents = ["dragleave", "dragend", "drop"];
        dragEvents.forEach(event => {
            elem.addEventListener(event, function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (elem_upload_float.querySelector("input[type=file]")) {
                    toast_up('⚠️释放以上传文件')
                } else {
                    toast_up(exist_file_msg)
                }
            });
        });
        leaveEvents.forEach(event => {
            elem.addEventListener(event, function (e) {
                toast_down();
                e.preventDefault();
                e.stopPropagation();
            });
        });
        elem.addEventListener("drop", async function (e) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    }
}


function register_upload_event() {
    locate_upload_elems();
    if (elem_upload_float) {
        _upload = document.querySelector("#elem_upload_float div.center.boundedheight.flex")
        elem_upload_component_pop_message(_upload);
    }
    if (elem_upload_component_float) {
        elem_upload_component_float.addEventListener('change', function (event) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    }
    if (elem_upload_component) {
        elem_upload_component.addEventListener('change', function (event) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    } else {
        toast_push("oppps", 3000);
    }
}


function monitoring_input_box() {
    register_upload_event();

    if (elem_input_main) {
        if (elem_input_main.querySelector("textarea")) {
            register_func_paste(elem_input_main.querySelector("textarea"))
        }
    }
    if (elem_input_float) {
        if (elem_input_float.querySelector("textarea")) {
            register_func_paste(elem_input_float.querySelector("textarea"))
        }
    }
    if (elem_chatbot) {
        register_func_drag(elem_chatbot)
    }

}


// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    // const ga = document.getElementsByTagName("gradio-app");
    gradioApp().addEventListener("render", monitoring_input_box);
});





// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 5 部分: 音频按钮样式变化
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function audio_fn_init() {
    let audio_component = document.getElementById('elem_audio');
    if (audio_component) {
        let buttonElement = audio_component.querySelector('button');
        let specificElement = audio_component.querySelector('.hide.sr-only');
        specificElement.remove();

        buttonElement.childNodes[1].nodeValue = '启动麦克风';
        buttonElement.addEventListener('click', function (event) {
            event.stopPropagation();
            toast_push('您启动了麦克风!下一步请点击“实时语音对话”启动语音对话。');
        });

        // 查找语音插件按钮
        let buttons = document.querySelectorAll('button');
        let audio_button = null;
        for (let button of buttons) {
            if (button.textContent.includes('语音')) {
                audio_button = button;
                break;
            }
        }
        if (audio_button) {
            audio_button.addEventListener('click', function () {
                toast_push('您点击了“实时语音对话”启动语音对话。');
            });
            let parent_element = audio_component.parentElement; // 将buttonElement移动到audio_button的内部
            audio_button.appendChild(audio_component);
            buttonElement.style.cssText = 'border-color: #00ffe0;border-width: 2px; height: 25px;'
            parent_element.remove();
            audio_component.style.cssText = 'width: 250px;right: 0px;display: inline-flex;flex-flow: row-reverse wrap;place-content: stretch space-between;align-items: center;background-color: #ffffff00;';
        }

    }
}


function minor_ui_adjustment() {
    let cbsc_area = document.getElementById('cbsc');
    cbsc_area.style.paddingTop = '15px';
    var bar_btn_width = [];
    // 自动隐藏超出范围的toolbar按钮
    function auto_hide_toolbar() {
        var qq = document.getElementById('tooltip');
        var tab_nav = qq.getElementsByClassName('tab-nav');
        if (tab_nav.length == 0) { return; }
        var btn_list = tab_nav[0].getElementsByTagName('button')
        if (btn_list.length == 0) { return; }
        // 获取页面宽度
        var page_width = document.documentElement.clientWidth;
        // 总是保留的按钮数量
        const always_preserve = 2;
        // 获取最后一个按钮的右侧位置
        var cur_right = btn_list[always_preserve - 1].getBoundingClientRect().right;
        if (bar_btn_width.length == 0) {
            // 首次运行，记录每个按钮的宽度
            for (var i = 0; i < btn_list.length; i++) {
                bar_btn_width.push(btn_list[i].getBoundingClientRect().width);
            }
        }
        // 处理每一个按钮
        for (var i = always_preserve; i < btn_list.length; i++) {
            var element = btn_list[i];
            var element_right = element.getBoundingClientRect().right;
            if (element_right != 0) { cur_right = element_right; }
            if (element.style.display === 'none') {
                if ((cur_right + bar_btn_width[i]) < (page_width * 0.37)) {
                    // 恢复显示当前按钮
                    element.style.display = 'block';
                    return;
                } else {
                    return;
                }
            } else {
                if (cur_right > (page_width * 0.38)) {
                    // 隐藏当前按钮以及右侧所有按钮
                    for (var j = i; j < btn_list.length; j++) {
                        if (btn_list[j].style.display !== 'none') {
                            btn_list[j].style.display = 'none';
                        }
                    }
                    return;
                }
            }
        }
    }

    setInterval(function () {
        auto_hide_toolbar()
    }, 200); // 每50毫秒执行一次
}


// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 6 部分: 避免滑动
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
let prevented_offset = 0;
function limit_scroll_position() {
    let scrollableDiv = document.querySelector('#gpt-chatbot > div.wrap');
    scrollableDiv.addEventListener('wheel', function (e) {
        let preventScroll = false;
        if (e.deltaX != 0) { prevented_offset = 0; return; }
        if (this.scrollHeight == this.clientHeight) { prevented_offset = 0; return; }
        if (e.deltaY < 0) { prevented_offset = 0; return; }
        if (e.deltaY > 0 && this.scrollHeight - this.clientHeight - this.scrollTop <= 1) { preventScroll = true; }

        if (preventScroll) {
            prevented_offset += e.deltaY;
            if (Math.abs(prevented_offset) > 499) {
                if (prevented_offset > 500) { prevented_offset = 500; }
                if (prevented_offset < -500) { prevented_offset = -500; }
                preventScroll = false;
            }
        } else {
            prevented_offset = 0;
        }
        if (preventScroll) {
            e.preventDefault();
            return;
        }
    }, { passive: false }); // Passive event listener option should be false
}



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 7 部分: JS初始化函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function loadLive2D() {
    try {
        $("<link>").attr({ href: "file=themes/waifu_plugin/waifu.css", rel: "stylesheet", type: "text/css" }).appendTo('head');
        $('body').append('<div class="waifu"><div class="waifu-tips"></div><canvas id="live2d" class="live2d"></canvas><div class="waifu-tool"><span class="fui-home"></span> <span class="fui-chat"></span> <span class="fui-eye"></span> <span class="fui-user"></span> <span class="fui-photo"></span> <span class="fui-info-circle"></span> <span class="fui-cross"></span></div></div>');
        $.ajax({
            url: "file=themes/waifu_plugin/waifu-tips.js", dataType: "script", cache: true, success: function () {
                $.ajax({
                    url: "file=themes/waifu_plugin/live2d.js", dataType: "script", cache: true, success: function () {
                        /* 可直接修改部分参数 */
                        live2d_settings['hitokotoAPI'] = "hitokoto.cn";  // 一言 API
                        live2d_settings['modelId'] = 3;                  // 默认模型 ID
                        live2d_settings['modelTexturesId'] = 44;          // 默认材质 ID
                        live2d_settings['modelStorage'] = false;         // 不储存模型 ID
                        live2d_settings['waifuSize'] = '210x187';
                        live2d_settings['waifuTipsSize'] = '187x52';
                        live2d_settings['canSwitchModel'] = true;
                        live2d_settings['canSwitchTextures'] = true;
                        live2d_settings['canSwitchHitokoto'] = false;
                        live2d_settings['canTakeScreenshot'] = false;
                        live2d_settings['canTurnToHomePage'] = false;
                        live2d_settings['canTurnToAboutPage'] = false;
                        live2d_settings['showHitokoto'] = false;          // 显示一言
                        live2d_settings['showF12Status'] = false;         // 显示加载状态
                        live2d_settings['showF12Message'] = false;        // 显示看板娘消息
                        live2d_settings['showF12OpenMsg'] = false;        // 显示控制台打开提示
                        live2d_settings['showCopyMessage'] = false;       // 显示 复制内容 提示
                        live2d_settings['showWelcomeMessage'] = true;     // 显示进入面页欢迎词
                        /* 在 initModel 前添加 */
                        initModel("file=themes/waifu_plugin/waifu-tips.json");
                    }
                });
            }
        });
    } catch (err) { console.log("[Error] JQuery is not defined.") }
}


function get_checkbox_selected_items(elem_id) {
    display_panel_arr = [];
    document.getElementById(elem_id).querySelector('[data-testid="checkbox-group"]').querySelectorAll('label').forEach(label => {
        // Get the span text
        const spanText = label.querySelector('span').textContent;
        // Get the input value
        const checked = label.querySelector('input').checked;
        if (checked) {
            display_panel_arr.push(spanText)
        }
    });
    return display_panel_arr;
}


function gpt_academic_gradio_saveload(
    save_or_load,       // save_or_load==="save" / save_or_load==="load"
    elem_id,            // element id
    cookie_key,         // cookie key
    save_value = "",      // save value
    load_type = "str",  // type==="str" / type==="float"
    load_default = false, // load default value
    load_default_value = ""
) {
    if (save_or_load === "load") {
        let value = getCookie(cookie_key);
        if (value) {
            console.log('加载cookie', elem_id, value)
            push_data_to_gradio_component(value, elem_id, load_type);
        }
        else {
            if (load_default) {
                console.log('加载cookie的默认值', elem_id, load_default_value)
                push_data_to_gradio_component(load_default_value, elem_id, load_type);
            }
        }
    }
    if (save_or_load === "save") {
        setCookie(cookie_key, save_value, 365);
    }
}


async function GptAcademicJavaScriptInit(dark, prompt, live2d, layout) {
    // 第一部分，布局初始化
    audio_fn_init();
    minor_ui_adjustment();
    chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
    var chatbotObserver = new MutationObserver(() => {
        chatbotContentChanged(1);
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

    // SysPrompt 系统静默提示词
    gpt_academic_gradio_saveload("load", "elem_prompt", "js_system_prompt_cookie", null, "str");

    // Temperature 大模型温度参数
    gpt_academic_gradio_saveload("load", "elem_temperature", "js_temperature_cookie", null, "float");

    if (getCookie("js_md_dropdown_cookie")){
        // md_dropdown 大模型类型选择
        gpt_academic_gradio_saveload("load", "elem_model_sel", "js_md_dropdown_cookie", null, "str");
        // 连锁修改chatbot的label
        push_data_to_gradio_component({
            label: '当前模型：' + getCookie("js_md_dropdown_cookie"),
            __type__: 'update'
        }, "gpt-chatbot", "obj")
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

}


function reset_conversation(a, b) {
    console.log("js_code_reset");
    a = btoa(unescape(encodeURIComponent(JSON.stringify(a))));
    setCookie("js_previous_chat_cookie", a, 1);
    gen_restore_btn();
    return [[], [], "已重置"];
}

// clear -> 将 history 缓存至 history_cache -> 点击复原 -> restore_previous_chat() -> 触发elem_update_history -> 读取 history_cache
function restore_previous_chat(){
    console.log("restore_previous_chat");
    let chat = getCookie("js_previous_chat_cookie");
    chat = JSON.parse(decodeURIComponent(escape(atob(chat))));
    push_data_to_gradio_component(chat, "gpt-chatbot", "obj");
    document.querySelector("#elem_update_history").click(); // in order to call set_history_gr_state, and send history state to server
}

function gen_restore_btn(){
    // 创建按钮元素
    const button = document.createElement('div');

    let initial_text = '+';

    // 设置按钮的样式和属性
    button.id = 'floatingButton';
    button.className = 'glow';
    button.style.position = 'fixed';
    button.style.bottom = '10px';
    button.style.left = '10px';
    button.style.width = '50px';
    button.style.height = '50px';
    button.style.borderRadius = '50%';
    button.style.backgroundColor = '#007bff';
    button.style.color = 'white';
    button.style.display = 'flex';
    button.style.alignItems = 'center';
    button.style.justifyContent = 'center';
    button.style.cursor = 'pointer';
    button.style.transition = 'all 0.3s ease';
    button.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
    button.textContent = initial_text;

    // 添加发光动画的关键帧
    const styleSheet = document.createElement('style');
    styleSheet.type = 'text/css';
    styleSheet.innerText = `
    @keyframes glow {
        from {
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }
        to {
        box-shadow: 0 0 20px rgba(0,0,0,0.4);
        }
    }
    #floatingButton.glow {
        animation: glow 1s infinite alternate;
    }
    #floatingButton:hover {
        transform: scale(1.2);
        box-shadow: 0 0 20px rgba(0,0,0,0.4);
    }
    #floatingButton.disappearing {
        animation: shrinkAndDisappear 0.5s forwards;
    }
    `;
    document.head.appendChild(styleSheet);

    // 鼠标悬停和移开的事件监听器
    button.addEventListener('mouseover', function() {
        this.textContent = "还原对话";
    });

    button.addEventListener('mouseout', function() {
        this.textContent = initial_text;
    });

    // 点击事件监听器
    button.addEventListener('click', function() {
        // 添加一个类来触发缩小和消失的动画
        restore_previous_chat();
        this.classList.add('disappearing');
        // 在动画结束后移除按钮
        document.body.removeChild(this);
    });

    // 将按钮添加到页面中
    document.body.appendChild(button);
}

async function on_plugin_exe_complete(fn_name)
{
    console.log(fn_name);
    if (fn_name === "保存当前的对话")
    {
        // get chat profile path
        let chatbot = await get_data_from_gradio_component('gpt-chatbot');
        let may_have_chat_profile_info = chatbot[chatbot.length-1][1];

        function get_href(htmlString){
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlString, 'text/html');
            const anchor = doc.querySelector('a');

            if (anchor) {
                return anchor.getAttribute('href');
            } else {
                return null;
            }
        }
        let href = get_href(may_have_chat_profile_info);
        if (href){
            const cleanedHref = href.replace('file=', ''); // /home/fuqingxu/chatgpt_academic/gpt_log/default_user/chat_history/GPT-Academic对话存档2024-04-12-00-35-06.html
            console.log(cleanedHref);
        }

    }
}
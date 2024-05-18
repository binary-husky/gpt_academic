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


var allow_auto_read_continously = true;
var allow_auto_read_tts_flag = false;
function addCopyButton(botElement, index, is_last_in_arr) {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    // Copy bot button
    const copiedIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
    const copyIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';
    // const audioIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';
    const audioIcon = '<span><svg t="1713628577799" fill="currentColor" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4587" width=".9em" height=".9em"><path d="M113.7664 540.4672c0-219.9552 178.2784-398.2336 398.2336-398.2336S910.2336 320.512 910.2336 540.4672v284.4672c0 31.4368-25.4976 56.9344-56.9344 56.9344h-56.9344c-31.4368 0-56.9344-25.4976-56.9344-56.9344V597.2992c0-31.4368 25.4976-56.9344 56.9344-56.9344h56.9344c0-188.5184-152.7808-341.2992-341.2992-341.2992S170.7008 351.9488 170.7008 540.4672h56.9344c31.4368 0 56.9344 25.4976 56.9344 56.9344v227.5328c0 31.4368-25.4976 56.9344-56.9344 56.9344h-56.9344c-31.4368 0-56.9344-25.4976-56.9344-56.9344V540.4672z" p-id="4588"></path></svg></span>';
    // const cancelAudioIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';

    // 此功能没准备好
    if (allow_auto_read_continously && is_last_in_arr && allow_auto_read_tts_flag) {
        process_latest_text_output(botElement.innerText, index);
    }

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
            // push_text_to_audio(textToCopy).catch(console.error);
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

    if (enable_tts){
        var audioButton = document.createElement('button');
        audioButton.classList.add('audio-toggle-btn');
        audioButton.innerHTML = audioIcon;
        audioButton.addEventListener('click', async () => {
            if (audioPlayer.isPlaying) {
                allow_auto_read_tts_flag = false;
                toast_push('自动朗读已禁用。', 3000);
                audioPlayer.stop();
                setCookie("js_auto_read_cookie", "False", 365);

            } else {
                allow_auto_read_tts_flag = true;
                toast_push('正在合成语音 & 自动朗读已开启 (再次点击此按钮可禁用自动朗读)。', 3000);
                // toast_push('正在合成语音', 3000);
                const readText = botElement.innerText;
                prev_chatbot_index = index;
                prev_text = readText;
                prev_text_already_pushed = readText;
                push_text_to_audio(readText);
                setCookie("js_auto_read_cookie", "True", 365);
            }
        });
    }

    var messageBtnColumn = document.createElement('div');
    messageBtnColumn.classList.add('message-btn-row');
    messageBtnColumn.appendChild(copyButton);
    if (enable_tts){
        messageBtnColumn.appendChild(audioButton);
    }
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
            const messages = gradioApp().querySelectorAll('#gpt-chatbot .message-wrap .message.bot');
            messages.forEach((message, index, arr) => {
                // Check if the current message is the last in the array
                const is_last_in_arr = index === arr.length - 1;

                // Now pass both the message element and the is_last_in_arr boolean to addCopyButton
                addCopyButton(message, index, is_last_in_arr);
            });
            // gradioApp().querySelectorAll('#gpt-chatbot .message-wrap .message.bot').forEach(addCopyButton);
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
            register_func_paste(elem_input_main.querySelector("textarea"));
        }
    }
    if (elem_input_float) {
        if (elem_input_float.querySelector("textarea")) {
            register_func_paste(elem_input_float.querySelector("textarea"));
        }
    }
    if (elem_chatbot) {
        register_func_drag(elem_chatbot);
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
        auto_hide_toolbar();
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

enable_tts = false;
async function GptAcademicJavaScriptInit(dark, prompt, live2d, layout, tts) {
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
        // deterine whether the cached model is in the choices
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

}


function reset_conversation(a, b) {
    // console.log("js_code_reset");
    a = btoa(unescape(encodeURIComponent(JSON.stringify(a))));
    setCookie("js_previous_chat_cookie", a, 1);
    gen_restore_btn();
    return [[], [], "已重置"];
}

// clear -> 将 history 缓存至 history_cache -> 点击复原 -> restore_previous_chat() -> 触发elem_update_history -> 读取 history_cache
function restore_previous_chat() {
    console.log("restore_previous_chat");
    let chat = getCookie("js_previous_chat_cookie");
    chat = JSON.parse(decodeURIComponent(escape(atob(chat))));
    push_data_to_gradio_component(chat, "gpt-chatbot", "obj");
    document.querySelector("#elem_update_history").click(); // in order to call set_history_gr_state, and send history state to server
}

function gen_restore_btn() {


    // 创建按钮元素
    const button = document.createElement('div');
    // const recvIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
    const rec_svg = '<svg t="1714361184567" style="transform:translate(1px, 2.5px)" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4389" width="35" height="35"><path d="M320 512h384v64H320zM320 384h384v64H320zM320 640h192v64H320z" p-id="4390" fill="#ffffff"></path><path d="M863.7 544c-1.9 44-11.4 86.8-28.5 127.2-18.5 43.8-45.1 83.2-78.9 117-33.8 33.8-73.2 60.4-117 78.9C593.9 886.3 545.7 896 496 896s-97.9-9.7-143.2-28.9c-43.8-18.5-83.2-45.1-117-78.9-33.8-33.8-60.4-73.2-78.9-117C137.7 625.9 128 577.7 128 528s9.7-97.9 28.9-143.2c18.5-43.8 45.1-83.2 78.9-117s73.2-60.4 117-78.9C398.1 169.7 446.3 160 496 160s97.9 9.7 143.2 28.9c23.5 9.9 45.8 22.2 66.5 36.7l-119.7 20 9.9 59.4 161.6-27 59.4-9.9-9.9-59.4-27-161.5-59.4 9.9 19 114.2C670.3 123.8 586.4 96 496 96 257.4 96 64 289.4 64 528s193.4 432 432 432c233.2 0 423.3-184.8 431.7-416h-64z" p-id="4391" fill="#ffffff"></path></svg>'
    const recvIcon = '<span>' + rec_svg + '</span>';

    // 设置按钮的样式和属性
    button.id = 'floatingButton';
    button.className = 'glow';
    button.style.textAlign = 'center';
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

    button.innerHTML = recvIcon;

    // 添加发光动画的关键帧
    const styleSheet = document.createElement('style');
    styleSheet.id = 'floatingButtonStyle';
    styleSheet.innerText = `
    @keyframes glow {
        from {
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }
        to {
        box-shadow: 0 0 13px rgba(0,0,0,0.5);
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

    // only add when not exist
    if (!document.getElementById('recvButtonStyle'))
    {
        document.head.appendChild(styleSheet);
    }

    // 鼠标悬停和移开的事件监听器
    button.addEventListener('mouseover', function () {
        this.textContent = "还原\n对话";
    });

    button.addEventListener('mouseout', function () {
        this.innerHTML = recvIcon;
    });

    // 点击事件监听器
    button.addEventListener('click', function () {
        // 添加一个类来触发缩小和消失的动画
        restore_previous_chat();
        this.classList.add('disappearing');
        // 在动画结束后移除按钮
        document.body.removeChild(this);
    });
    // only add when not exist
    if (!document.getElementById('recvButton'))
    {
        document.body.appendChild(button);
    }

    // 将按钮添加到页面中

}

async function on_plugin_exe_complete(fn_name) {
    console.log(fn_name);
    if (fn_name === "保存当前的对话") {
        // get chat profile path
        let chatbot = await get_data_from_gradio_component('gpt-chatbot');
        let may_have_chat_profile_info = chatbot[chatbot.length - 1][1];

        function get_href(htmlString) {
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
        if (href) {
            const cleanedHref = href.replace('file=', ''); // /home/fuqingxu/chatgpt_academic/gpt_log/default_user/chat_history/GPT-Academic对话存档2024-04-12-00-35-06.html
            console.log(cleanedHref);
        }

    }
}








// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 8 部分: TTS语音生成函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
audio_debug = false;
class AudioPlayer {
    constructor() {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        this.queue = [];
        this.isPlaying = false;
        this.currentSource = null; // 添加属性来保存当前播放的源
    }

    // Base64 编码的字符串转换为 ArrayBuffer
    base64ToArrayBuffer(base64) {
        const binaryString = window.atob(base64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }

    // 检查音频播放队列并播放音频
    checkQueue() {
        if (!this.isPlaying && this.queue.length > 0) {
            this.isPlaying = true;
            const nextAudio = this.queue.shift();
            this.play_wave(nextAudio);
        }
    }

    // 将音频添加到播放队列
    enqueueAudio(audio_buf_wave) {
        if (allow_auto_read_tts_flag) {
            this.queue.push(audio_buf_wave);
            this.checkQueue();
        }
    }

    // 播放音频
    async play_wave(encodedAudio) {
        //const audioData = this.base64ToArrayBuffer(encodedAudio);
        const audioData = encodedAudio;
        try {
            const buffer = await this.audioCtx.decodeAudioData(audioData);
            const source = this.audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(this.audioCtx.destination);
            source.onended = () => {
                if (allow_auto_read_tts_flag) {
                    this.isPlaying = false;
                    this.currentSource = null; // 播放结束后清空当前源
                    this.checkQueue();
                }
            };
            this.currentSource = source; // 保存当前播放的源
            source.start();
        } catch (e) {
            console.log("Audio error!", e);
            this.isPlaying = false;
            this.currentSource = null; // 出错时也应清空当前源
            this.checkQueue();
        }
    }

    // 新增：立即停止播放音频的方法
    stop() {
        if (this.currentSource) {
            this.queue = []; // 清空队列
            this.currentSource.stop(); // 停止当前源
            this.currentSource = null; // 清空当前源
            this.isPlaying = false; // 更新播放状态
            // 关闭音频上下文可能会导致无法再次播放音频，因此仅停止当前源
            // this.audioCtx.close(); // 可选：如果需要可以关闭音频上下文
        }
    }
}

const audioPlayer = new AudioPlayer();

class FIFOLock {
    constructor() {
        this.queue = [];
        this.currentTaskExecuting = false;
    }

    lock() {
        let resolveLock;
        const lock = new Promise(resolve => {
            resolveLock = resolve;
        });

        this.queue.push(resolveLock);

        if (!this.currentTaskExecuting) {
            this._dequeueNext();
        }

        return lock;
    }

    _dequeueNext() {
        if (this.queue.length === 0) {
            this.currentTaskExecuting = false;
            return;
        }
        this.currentTaskExecuting = true;
        const resolveLock = this.queue.shift();
        resolveLock();
    }

    unlock() {
        this.currentTaskExecuting = false;
        this._dequeueNext();
    }
}








function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Define the trigger function with delay parameter T in milliseconds
function trigger(T, fire) {
    // Variable to keep track of the timer ID
    let timeoutID = null;
    // Variable to store the latest arguments
    let lastArgs = null;

    return function (...args) {
        // Update lastArgs with the latest arguments
        lastArgs = args;
        // Clear the existing timer if the function is called again
        if (timeoutID !== null) {
            clearTimeout(timeoutID);
        }
        // Set a new timer that calls the `fire` function with the latest arguments after T milliseconds
        timeoutID = setTimeout(() => {
            fire(...lastArgs);
        }, T);
    };
}


prev_text = ""; // previous text, this is used to check chat changes
prev_text_already_pushed = ""; // previous text already pushed to audio, this is used to check where we should continue to play audio
prev_chatbot_index = -1;
const delay_live_text_update = trigger(3000, on_live_stream_terminate);

function on_live_stream_terminate(latest_text) {
    // remove `prev_text_already_pushed` from `latest_text`
    if (audio_debug) console.log("on_live_stream_terminate", latest_text);
    remaining_text = latest_text.slice(prev_text_already_pushed.length);
    if ((!isEmptyOrWhitespaceOnly(remaining_text)) && remaining_text.length != 0) {
        prev_text_already_pushed = latest_text;
        push_text_to_audio(remaining_text);
    }
}
function is_continue_from_prev(text, prev_text) {
    abl = 5
    if (text.length < prev_text.length - abl) {
        return false;
    }
    if (prev_text.length > 10) {
        return text.startsWith(prev_text.slice(0, Math.min(prev_text.length - abl, 100)));
    } else {
        return text.startsWith(prev_text);
    }
}
function isEmptyOrWhitespaceOnly(remaining_text) {
    // Replace \n and 。 with empty strings
    let textWithoutSpecifiedCharacters = remaining_text.replace(/[\n。]/g, '');
    // Check if the remaining string is empty
    return textWithoutSpecifiedCharacters.trim().length === 0;
}
function process_increased_text(remaining_text) {
    // console.log('[is continue], remaining_text: ', remaining_text)
    // remaining_text starts with \n or 。, then move these chars into prev_text_already_pushed
    while (remaining_text.startsWith('\n') || remaining_text.startsWith('。')) {
        prev_text_already_pushed = prev_text_already_pushed + remaining_text[0];
        remaining_text = remaining_text.slice(1);
    }
    if (remaining_text.includes('\n') || remaining_text.includes('。')) { // determine remaining_text contain \n or 。
        // new message begin!
        index_of_last_sep = Math.max(remaining_text.lastIndexOf('\n'), remaining_text.lastIndexOf('。'));
        // break the text into two parts
        tobe_pushed = remaining_text.slice(0, index_of_last_sep + 1);
        prev_text_already_pushed = prev_text_already_pushed + tobe_pushed;
        // console.log('[is continue], push: ', tobe_pushed)
        // console.log('[is continue], update prev_text_already_pushed: ', prev_text_already_pushed)
        if (!isEmptyOrWhitespaceOnly(tobe_pushed)) {
            // console.log('[is continue], remaining_text is empty')
            push_text_to_audio(tobe_pushed);
        }
    }
}
function process_latest_text_output(text, chatbot_index) {
    if (text.length == 0) {
        prev_text = text;
        prev_text_mask = text;
        // console.log('empty text')
        return;
    }
    if (text == prev_text) {
        // console.log('[nothing changed]')
        return;
    }

    var is_continue = is_continue_from_prev(text, prev_text_already_pushed);
    if (chatbot_index == prev_chatbot_index && is_continue) {
        // on_text_continue_grow
        remaining_text = text.slice(prev_text_already_pushed.length);
        process_increased_text(remaining_text);
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    else if (chatbot_index == prev_chatbot_index && !is_continue) {
        if (audio_debug) console.log('---------------------');
        if (audio_debug) console.log('text twisting!');
        if (audio_debug) console.log('[new message begin]', 'text', text, 'prev_text_already_pushed', prev_text_already_pushed);
        if (audio_debug) console.log('---------------------');
        prev_text_already_pushed = "";
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    else {
        // on_new_message_begin, we have to clear `prev_text_already_pushed`
        if (audio_debug) console.log('---------------------');
        if (audio_debug) console.log('new message begin!');
        if (audio_debug) console.log('[new message begin]', 'text', text, 'prev_text_already_pushed', prev_text_already_pushed);
        if (audio_debug) console.log('---------------------');
        prev_text_already_pushed = "";
        process_increased_text(text);
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    prev_text = text;
    prev_chatbot_index = chatbot_index;
}

const audio_push_lock = new FIFOLock();
async function push_text_to_audio(text) {
    if (!allow_auto_read_tts_flag) {
        return;
    }
    await audio_push_lock.lock();
    var lines = text.split(/[\n。]/);
    for (const audio_buf_text of lines) {
        if (audio_buf_text) {
            // Append '/vits' to the current URL to form the target endpoint
            const url = `${window.location.href}vits`;
            // Define the payload to be sent in the POST request
            const payload = {
                text: audio_buf_text, // Ensure 'audio_buf_text' is defined with valid data
                text_language: "zh"
            };
            // Call the async postData function and log the response
            post_text(url, payload, send_index);
            send_index = send_index + 1;
            if (audio_debug) console.log(send_index, audio_buf_text);
            // sleep 2 seconds
            if (allow_auto_read_tts_flag) {
                await delay(3000);
            }
        }
    }
    audio_push_lock.unlock();
}


send_index = 0;
recv_index = 0;
to_be_processed = [];
async function UpdatePlayQueue(cnt, audio_buf_wave) {
    if (cnt != recv_index) {
        to_be_processed.push([cnt, audio_buf_wave]);
        if (audio_debug) console.log('cache', cnt);
    }
    else {
        if (audio_debug) console.log('processing', cnt);
        recv_index = recv_index + 1;
        if (audio_buf_wave) {
            audioPlayer.enqueueAudio(audio_buf_wave);
        }
        // deal with other cached audio
        while (true) {
            find_any = false;
            for (i = to_be_processed.length - 1; i >= 0; i--) {
                if (to_be_processed[i][0] == recv_index) {
                    if (audio_debug) console.log('processing cached', recv_index);
                    if (to_be_processed[i][1]) {
                        audioPlayer.enqueueAudio(to_be_processed[i][1]);
                    }
                    to_be_processed.pop(i);
                    find_any = true;
                    recv_index = recv_index + 1;
                }
            }
            if (!find_any) { break; }
        }
    }
}

function post_text(url, payload, cnt) {
    if (allow_auto_read_tts_flag) {
        postData(url, payload, cnt)
        .then(data => {
            UpdatePlayQueue(cnt, data);
            return;
        });
    } else {
        UpdatePlayQueue(cnt, null);
        return;
    }
}

notify_user_error = false
// Create an async function to perform the POST request
async function postData(url = '', data = {}) {
    try {
        // Use the Fetch API with await
        const response = await fetch(url, {
            method: 'POST', // Specify the request method
            body: JSON.stringify(data), // Convert the JavaScript object to a JSON string
        });
        // Check if the response is ok (status in the range 200-299)
        if (!response.ok) {
            // If not OK, throw an error
            console.info('There was a problem during audio generation requests:', response.status);
            // if (!notify_user_error){
            //     notify_user_error = true;
            //     alert('There was a problem during audio generation requests:', response.status);
            // }
            return null;
        }
        // If OK, parse and return the JSON response
        return await response.arrayBuffer();
    } catch (error) {
        // Log any errors that occur during the fetch operation
        console.info('There was a problem during audio generation requests:', error);
        // if (!notify_user_error){
        //     notify_user_error = true;
        //     alert('There was a problem during audio generation requests:', error);
        // }
        return null;
    }
}

async function generate_menu(guiBase64String, btnName){
    // assign the button and menu data
    push_data_to_gradio_component(guiBase64String, "invisible_current_pop_up_plugin_arg", "string");
    push_data_to_gradio_component(btnName, "invisible_callback_btn_for_plugin_exe", "string");

    // Base64 to dict
    const stringData = atob(guiBase64String);
    let guiJsonData = JSON.parse(stringData);
    let menu = document.getElementById("plugin_arg_menu");
    gui_args = {}
    for (const key in guiJsonData) {
        if (guiJsonData.hasOwnProperty(key)) {
            const innerJSONString = guiJsonData[key];
            const decodedObject = JSON.parse(innerJSONString);
            gui_args[key] = decodedObject;
        }
    }

    // 使参数菜单显现
    push_data_to_gradio_component({
        visible: true,
        __type__: 'update'
    }, "plugin_arg_menu", "obj");
    hide_all_elem();
    // 根据 gui_args, 使得对应参数项显现
    let text_cnt = 0;
    for (const key in gui_args) {
        if (gui_args.hasOwnProperty(key)) {
            const component_name = "plugin_arg_txt_" + text_cnt;
            if (gui_args[key].type=='string'){
                push_data_to_gradio_component({
                    visible: true,
                    label: gui_args[key].title + "(" + gui_args[key].description +  ")",
                    // label: gui_args[key].title,
                    placeholder: gui_args[key].description,
                    __type__: 'update'
                }, component_name, "obj");
                if (key === "main_input"){
                    // 为了与旧插件兼容，生成菜单时，自动加载输入栏的值
                    let current_main_input = await get_data_from_gradio_component('user_input_main');
                    let current_main_input_2 = await get_data_from_gradio_component('user_input_float');
                    push_data_to_gradio_component(current_main_input + current_main_input_2, component_name, "obj");
                }
                else if (key === "advanced_arg"){
                    // 为了与旧插件兼容，生成菜单时，自动加载旧高级参数输入区的值
                    let advance_arg_input_legacy = await get_data_from_gradio_component('advance_arg_input_legacy');
                    push_data_to_gradio_component(advance_arg_input_legacy, component_name, "obj");
                }
                else {
                    push_data_to_gradio_component(gui_args[key].default_value, component_name, "obj");
                }
                document.getElementById(component_name).parentNode.parentNode.style.display = '';
                text_cnt += 1;
            }
        }
    }
}

async function execute_current_pop_up_plugin(){
    let guiBase64String = await get_data_from_gradio_component('invisible_current_pop_up_plugin_arg');
    const stringData = atob(guiBase64String);
    let guiJsonData = JSON.parse(stringData);
    gui_args = {}
    for (const key in guiJsonData) {
        if (guiJsonData.hasOwnProperty(key)) {
            const innerJSONString = guiJsonData[key];
            const decodedObject = JSON.parse(innerJSONString);
            gui_args[key] = decodedObject;
        }
    }
    // read user confirmed value
    let text_cnt = 0;
    for (const key in gui_args) {
        if (gui_args.hasOwnProperty(key)) {
            if (gui_args[key].type=='string'){
                corrisponding_elem_id = "plugin_arg_txt_"+text_cnt
                gui_args[key].user_confirmed_value = await get_data_from_gradio_component(corrisponding_elem_id);
                text_cnt += 1;
            }
        }
    }

    // close menu
    push_data_to_gradio_component({
        visible: false,
        __type__: 'update'
    }, "plugin_arg_menu", "obj");
    hide_all_elem();

    // execute the plugin
    push_data_to_gradio_component(JSON.stringify(gui_args), "invisible_current_pop_up_plugin_arg_final", "string");
    document.getElementById("invisible_callback_btn_for_plugin_exe").click();

}

function hide_all_elem(){
    for (text_cnt = 0; text_cnt < 8; text_cnt++){
        push_data_to_gradio_component({
            visible: false,
            label: "",
            __type__: 'update'
        }, "plugin_arg_txt_"+text_cnt, "obj");
        document.getElementById("plugin_arg_txt_"+text_cnt).parentNode.parentNode.style.display = 'none';
    }
}

function close_current_pop_up_plugin(){
    push_data_to_gradio_component({
        visible: false,
        __type__: 'update'
    }, "plugin_arg_menu", "obj");
    hide_all_elem();
}

advanced_plugin_init_code_lib = {}
function register_advanced_plugin_init_code(key, code){
    advanced_plugin_init_code_lib[key] = code;
}
function run_advanced_plugin_launch_code(key){
    // convert js code string to function
    generate_menu(advanced_plugin_init_code_lib[key], key);
}
function on_flex_button_click(key){
    run_advanced_plugin_launch_code(key);
}






// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 1 部分: 工具函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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
        // Do something if .message-btn-column exists, for example, remove it
        // messageBtnColumnElement.remove();
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

function chatbotContentChanged(attempt = 1, force = false) {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    for (var i = 0; i < attempt; i++) {
        setTimeout(() => {
            gradioApp().querySelectorAll('#gpt-chatbot .message-wrap .message.bot').forEach(addCopyButton);
        }, i === 0 ? 0 : 200);
    }
}



// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 3 部分: chatbot动态高度调整
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function chatbotAutoHeight() {
    // 自动调整高度
    function update_height() {
        var { height_target, chatbot_height, chatbot } = get_elements(true);
        if (height_target != chatbot_height) {
            var pixelString = height_target.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }

    function update_height_slow() {
        var { height_target, chatbot_height, chatbot } = get_elements();
        if (height_target != chatbot_height) {
            new_panel_height = (height_target - chatbot_height) * 0.5 + chatbot_height;
            if (Math.abs(new_panel_height - height_target) < 10) {
                new_panel_height = height_target;
            }
            // console.log(chatbot_height, height_target, new_panel_height);
            var pixelString = new_panel_height.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString;
        }
    }
    monitoring_input_box()
    update_height();
    setInterval(function () {
        update_height_slow()
    }, 50); // 每50毫秒执行一次
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
    if (swapped) {swapped = false;} 
    else {swapped = true;}
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
    if (!swapped){
        if (panel1.top!=0 && panel1.top < 0){ swap_input_area(); }
    }
    else if (swapped){
        if (panel2.top!=0 && panel2.top > 0){ swap_input_area(); }
    }
    // 调整高度
    const err_tor = 5;
    if (Math.abs(panel1.left - chatbot.getBoundingClientRect().left) < err_tor){
        // 是否处于窄屏模式
        height_target = window.innerHeight * 0.6;
    }else{
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
var exist_file_msg = '⚠️请先删除上传区（左上方）中的历史文件，再尝试上传。'

function add_func_paste(input) {
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

function add_func_drag(elem) {
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

async function upload_files(files) {
    const uploadInputElement = elem_upload_float.querySelector("input[type=file]");
    let totalSizeMb = 0
    if (files && files.length > 0) {
        // 执行具体的上传逻辑
        if (uploadInputElement) {
            for (let i = 0; i < files.length; i++) {
                // 将从文件数组中获取的文件大小(单位为字节)转换为MB，
                totalSizeMb += files[i].size / 1024 / 1024;
            }
            // 检查文件总大小是否超过20MB
            if (totalSizeMb > 20) {
                toast_push('⚠️文件夹大于 20MB 🚀上传文件中', 3000)
                // return;  // 如果超过了指定大小, 可以不进行后续上传操作
            }
            // 监听change事件， 原生Gradio可以实现
            // uploadInputElement.addEventListener('change', function(){replace_input_string()});
            let event = new Event("change");
            Object.defineProperty(event, "target", { value: uploadInputElement, enumerable: true });
            Object.defineProperty(event, "currentTarget", { value: uploadInputElement, enumerable: true });
            Object.defineProperty(uploadInputElement, "files", { value: files, enumerable: true });
            uploadInputElement.dispatchEvent(event);
        } else {
            toast_push(exist_file_msg, 3000)
        }
    }
}

function begin_loading_status() {
    // Create the loader div and add styling
    var loader = document.createElement('div');
    loader.id = 'Js_File_Loading';
    loader.style.position = "absolute";
    loader.style.top = "50%";
    loader.style.left = "50%";
    loader.style.width = "60px";
    loader.style.height = "60px";
    loader.style.border = "16px solid #f3f3f3";
    loader.style.borderTop = "16px solid #3498db";
    loader.style.borderRadius = "50%";
    loader.style.animation = "spin 2s linear infinite";
    loader.style.transform = "translate(-50%, -50%)";
    document.body.appendChild(loader); // Add the loader to the body
    // Set the CSS animation keyframes
    var styleSheet = document.createElement('style');
    // styleSheet.type = 'text/css';
    styleSheet.id = 'Js_File_Loading_Style'
    styleSheet.innerText = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }`;
    document.head.appendChild(styleSheet);
}

function cancel_loading_status() {
    var loadingElement = document.getElementById('Js_File_Loading');
    if (loadingElement) {
        document.body.removeChild(loadingElement); // remove the loader from the body
    }
    var loadingStyle = document.getElementById('Js_File_Loading_Style');
    if (loadingStyle) {
        document.head.removeChild(loadingStyle);
    }
    let clearButton = document.querySelectorAll('div[id*="elem_upload"] button[aria-label="Clear"]');
    for (let button of clearButton) {
        button.addEventListener('click', function () {
            setTimeout(function () {
                register_upload_event();
            }, 50);
        });
    }
}

function register_upload_event() {
    elem_upload_float = document.getElementById('elem_upload_float')
    const upload_component = elem_upload_float.querySelector("input[type=file]");
    if (upload_component) {
        upload_component.addEventListener('change', function (event) {
            toast_push('正在上传中，请稍等。', 2000);
            begin_loading_status();
        });
    }
}

function monitoring_input_box() {
    register_upload_event();

    elem_upload = document.getElementById('elem_upload')
    elem_upload_float = document.getElementById('elem_upload_float')
    elem_input_main = document.getElementById('user_input_main')
    elem_input_float = document.getElementById('user_input_float')
    elem_chatbot = document.getElementById('gpt-chatbot')

    if (elem_input_main) {
        if (elem_input_main.querySelector("textarea")) {
            add_func_paste(elem_input_main.querySelector("textarea"))
        }
    }
    if (elem_input_float) {
        if (elem_input_float.querySelector("textarea")) {
            add_func_paste(elem_input_float.querySelector("textarea"))
        }
    }
    if (elem_chatbot) {
        add_func_drag(elem_chatbot)
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
}

// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  第 6 部分: JS初始化函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function GptAcademicJavaScriptInit(LAYOUT = "LEFT-RIGHT") {
    audio_fn_init();
    minor_ui_adjustment();
    chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
    var chatbotObserver = new MutationObserver(() => {
        chatbotContentChanged(1);
    });
    chatbotObserver.observe(chatbotIndicator, { attributes: true, childList: true, subtree: true });
    if (LAYOUT === "LEFT-RIGHT") { chatbotAutoHeight(); }
}
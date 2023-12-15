function gradioApp() {
    // https://github.com/GaiZhenbiao/ChuanhuChatGPT/tree/main/web_assets/javascript
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];
    if (elem !== document) {
        elem.getElementById = function(id) {
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

function chatbotAutoHeight(){
    // 自动调整高度
    function update_height(){
        var { panel_height_target, chatbot_height, chatbot } = get_elements(true);
        if (panel_height_target!=chatbot_height)
        {
            var pixelString = panel_height_target.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString; 
        }
    }

    function update_height_slow(){
        var { panel_height_target, chatbot_height, chatbot } = get_elements();
        if (panel_height_target!=chatbot_height)
        {
            new_panel_height = (panel_height_target - chatbot_height)*0.5 + chatbot_height;
            if (Math.abs(new_panel_height - panel_height_target) < 10){
                new_panel_height = panel_height_target;
            }
            // console.log(chatbot_height, panel_height_target, new_panel_height);
            var pixelString = new_panel_height.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString; 
        }
    }
    monitoring_input_box()
    update_height();
    setInterval(function() {
        update_height_slow()
    }, 50); // 每100毫秒执行一次
}



function get_elements(consider_state_panel=false) {
    var chatbot = document.querySelector('#gpt-chatbot > div.wrap.svelte-18telvq');
    if (!chatbot) {
        chatbot = document.querySelector('#gpt-chatbot');
    }
    const panel1 = document.querySelector('#input-panel').getBoundingClientRect();
    const panel2 = document.querySelector('#basic-panel').getBoundingClientRect()
    const panel3 = document.querySelector('#plugin-panel').getBoundingClientRect();
    // const panel4 = document.querySelector('#interact-panel').getBoundingClientRect();
    const panel5 = document.querySelector('#input-panel2').getBoundingClientRect();
    const panel_active = document.querySelector('#state-panel').getBoundingClientRect();
    if (consider_state_panel || panel_active.height < 25){
        document.state_panel_height = panel_active.height;
    }
    // 25 是chatbot的label高度, 16 是右侧的gap
    var panel_height_target = panel1.height + panel2.height + panel3.height + 0 + 0 - 25 + 16*2;
    // 禁止动态的state-panel高度影响
    panel_height_target = panel_height_target + (document.state_panel_height-panel_active.height)
    var panel_height_target = parseInt(panel_height_target);
    var chatbot_height = chatbot.style.height;
    var chatbot_height = parseInt(chatbot_height);
    return { panel_height_target, chatbot_height, chatbot };
}


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
                    await paste_upload_files(paste_files);
                    paste_files = []

                }
            }
        });
    }
}


async function paste_upload_files(files) {
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
                toast_push('⚠️文件夹大于20MB 🚀上传文件中', 2000)
                // return;  // 如果超过了指定大小, 可以不进行后续上传操作
            }
             // 监听change事件， 原生Gradio可以实现
            // uploadInputElement.addEventListener('change', function(){replace_input_string()});
            let event = new Event("change");
            Object.defineProperty(event, "target", {value: uploadInputElement, enumerable: true});
            Object.defineProperty(event, "currentTarget", {value: uploadInputElement, enumerable: true});
            Object.defineProperty(uploadInputElement, "files", {value: files, enumerable: true});
            uploadInputElement.dispatchEvent(event);
            // toast_push('🎉上传文件成功', 2000)
        } else {
            toast_push('⚠️请先删除上传区中的历史文件，再尝试粘贴。', 2000)
        }
    }
}
//提示信息 封装
function toast_push(msg, duration) {
    duration = isNaN(duration) ? 3000 : duration;
    const m = document.createElement('div');
    m.innerHTML = msg;
    m.style.cssText = "font-size:  var(--text-md) !important; color: rgb(255, 255, 255);background-color: rgba(0, 0, 0, 0.6);padding: 10px 15px;margin: 0 0 0 -60px;border-radius: 4px;position: fixed;    top: 50%;left: 50%;width: auto; text-align: center;";
    document.body.appendChild(m);
    setTimeout(function () {
        var d = 0.5;
        m.style.opacity = '0';
        setTimeout(function () {
            document.body.removeChild(m)
        }, d * 1000);
    }, duration);
}

var elem_upload = null;
var elem_upload_float = null;
var elem_input_main = null;
var elem_input_float = null;


function monitoring_input_box() {
    elem_upload = document.getElementById('elem_upload')
    elem_upload_float = document.getElementById('elem_upload_float')
    elem_input_main = document.getElementById('user_input_main')
    elem_input_float = document.getElementById('user_input_float')
    if (elem_input_main) {
        if (elem_input_main.querySelector("textarea")) {
            add_func_paste(elem_input_main.querySelector("textarea"))
        }
    }
    if (elem_input_float) {
        if (elem_input_float.querySelector("textarea")){
            add_func_paste(elem_input_float.querySelector("textarea"))
        }
    }
}


// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    // const ga = document.getElementsByTagName("gradio-app");
    gradioApp().addEventListener("render", monitoring_input_box);
});

function audio_fn_init() {
    let audio_component = document.getElementById('elem_audio');
    if (audio_component){
        let buttonElement = audio_component.querySelector('button');
        let specificElement = audio_component.querySelector('.hide.sr-only');
        specificElement.remove();

        buttonElement.childNodes[1].nodeValue = '启动麦克风';
        buttonElement.addEventListener('click', function(event) {
            event.stopPropagation();
            toast_push('您启动了麦克风!下一步请点击“实时语音对话”启动语音对话。');
        });

        // 查找语音插件按钮
        let buttons = document.querySelectorAll('button');
        let audio_button = null;
        for(let button of buttons){
            if (button.textContent.includes('语音')){
                audio_button = button;
                break;
            }
        }
        if (audio_button){
            audio_button.addEventListener('click', function() {
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

function GptAcademicJavaScriptInit(LAYOUT = "LEFT-RIGHT") {
    audio_fn_init();
    chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
    var chatbotObserver = new MutationObserver(() => {
        chatbotContentChanged(1);
    });
    chatbotObserver.observe(chatbotIndicator, { attributes: true, childList: true, subtree: true });
    if (LAYOUT === "LEFT-RIGHT") {chatbotAutoHeight();}
}
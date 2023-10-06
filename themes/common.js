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

    update_height();
    setInterval(function() {
        update_height_slow()
    }, 50); // 每100毫秒执行一次
}

function GptAcademicJavaScriptInit(LAYOUT = "LEFT-RIGHT") {
    chatbotIndicator = gradioApp().querySelector('#gpt-chatbot > div.wrap');
    var chatbotObserver = new MutationObserver(() => {
        chatbotContentChanged(1);
    });
    chatbotObserver.observe(chatbotIndicator, { attributes: true, childList: true, subtree: true });
    if (LAYOUT === "LEFT-RIGHT") {chatbotAutoHeight();}
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
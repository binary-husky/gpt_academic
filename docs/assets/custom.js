// custom javascript here
var gradioContainer = null;
var chatbot = null;
var chatbotWrap = null;
var apSwitch = null;
var loginUserForm = null;
var chatbotIndicator = null;
var initialized = false;
var isInIframe = (window.self !== window.top);
var statusDisplay = null;


// gradio 页面加载好了么??? 我能动你的元素了么??
function gradioLoaded(mutations) {
    for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].addedNodes.length) {
            if (initialized) {
                observer.disconnect(); // 停止监听
                return;
            }
            initialize();
        }
        chatbot = document.querySelector('#main_chatbot');
        chatbotWrap = document.querySelector('#main_chatbot > .wrapper > .wrap');

        if (gradioContainer && apSwitch) {  // gradioCainter 加载出来了没?
            adjustDarkMode();
        }
    }
}

function initialize() {
    var needInit = {gradioContainer, apSwitch, chatbot, chatbotIndicator, chatbotWrap};
    initialized = true;

    loginUserForm = gradioApp().querySelector(".gradio-container > .main > .wrap > .panel > .form")
    gradioContainer = gradioApp().querySelector(".gradio-container");
    chatbot = gradioApp().querySelector('#main_chatbot');
    chatbotIndicator = gradioApp().querySelector('#main_chatbot>div.wrap');
    chatbotWrap = gradioApp().querySelector('#main_chatbot > .wrapper > .wrap');
    apSwitch = gradioApp().querySelector('.apSwitch input[type="checkbox"]');

    for (let elem in needInit) {
        if (needInit[elem] == null) {
            initialized = false;
            return;
        }
    }
    if (initialized) {
        adjustDarkMode();
        chatbotObserver.observe(chatbotIndicator, {attributes: true});
    }
}

var username = null;
function toggleDarkMode(isEnabled) {
    if (isEnabled) {
        document.body.classList.add("dark");
        document.body.style.setProperty("background-color", "var(--neutral-950)", "important");
    } else {
        document.body.classList.remove("dark");
        document.body.style.backgroundColor = "";
    }
}
function adjustDarkMode() {
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");

    // 获取保存在localStorage中的状态，如果没有则使用系统偏好
    const storedState = localStorage.getItem('darkModeEnabled');
    const initialState = storedState === null ? darkModeQuery.matches : (storedState === "true");

    // 根据当前颜色模式设置初始状态
    apSwitch.checked = initialState;
    toggleDarkMode(initialState);

    // 监听颜色模式变化
    darkModeQuery.addEventListener("change", (e) => {
        const newState = e.matches;
        apSwitch.checked = newState;
        toggleDarkMode(newState);
        // 保存新状态到localStorage
        localStorage.setItem('darkModeEnabled', newState);
    });

    apSwitch.addEventListener("change", (e) => {
        const newState = e.target.checked;
        toggleDarkMode(newState);
        // 保存新状态到localStorage
        localStorage.setItem('darkModeEnabled', newState);
    });
}
// button svg code
const copyIcon   = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';
const copiedIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
const mdIcon     = '<span><svg stroke="currentColor" fill="none" stroke-width="1" viewBox="0 0 14 18" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><path d="M1.5,0 L12.5,0 C13.3284271,-1.52179594e-16 14,0.671572875 14,1.5 L14,16.5 C14,17.3284271 13.3284271,18 12.5,18 L1.5,18 C0.671572875,18 1.01453063e-16,17.3284271 0,16.5 L0,1.5 C-1.01453063e-16,0.671572875 0.671572875,1.52179594e-16 1.5,0 Z" stroke-width="1.8"></path><line x1="3.5" y1="3.5" x2="10.5" y2="3.5"></line><line x1="3.5" y1="6.5" x2="8" y2="6.5"></line></g><path d="M4,9 L10,9 C10.5522847,9 11,9.44771525 11,10 L11,13.5 C11,14.0522847 10.5522847,14.5 10,14.5 L4,14.5 C3.44771525,14.5 3,14.0522847 3,13.5 L3,10 C3,9.44771525 3.44771525,9 4,9 Z" stroke="none" fill="currentColor"></path></svg></span>';
const rawIcon    = '<span><svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 18 14" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><polyline points="4 3 0 7 4 11"></polyline><polyline points="14 3 18 7 14 11"></polyline><line x1="12" y1="0" x2="6" y2="14"></line></g></svg></span>';


function addChuanhuButton(botElement){
    var rawMessage = botElement.querySelector('.raw-message');
    var mdMessage = botElement.querySelector('.md-message');

    if (!rawMessage) { // 如果没有 raw message，说明是早期历史记录，去除按钮
        var buttons = botElement.querySelectorAll('button.chuanhu-btn');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].parentNode.removeChild(buttons[i]);
        }
        return;
    }
    botElement.querySelectorAll('button.copy-bot-btn, button.toggle-md-btn').forEach(btn => btn.remove()); // 就算原先有了，也必须重新添加，而不是跳过

    // Copy bot button
    var copyButton = document.createElement('button');
    copyButton.classList.add('chuanhu-btn');
    copyButton.classList.add('copy-bot-btn');
    copyButton.setAttribute('aria-label', 'Copy');
    copyButton.innerHTML = copyIcon;

    copyButton.addEventListener('click', async () => {
        const textToCopy = rawMessage.innerText;
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
    botElement.appendChild(copyButton);

    // Toggle button
    var toggleButton = document.createElement('button');
    toggleButton.classList.add('chuanhu-btn');
    toggleButton.classList.add('toggle-md-btn');
    toggleButton.setAttribute('aria-label', 'Toggle');
    var renderMarkdown = mdMessage.classList.contains('hideM');
    toggleButton.innerHTML = renderMarkdown ? mdIcon : rawIcon;
    toggleButton.addEventListener('click', () => {
        renderMarkdown = mdMessage.classList.contains('hideM');
        if (renderMarkdown) {
            renderMarkdownText(botElement);
            toggleButton.innerHTML=rawIcon;
        } else {
            removeMarkdownText(botElement);
            toggleButton.innerHTML=mdIcon;
        }
        chatbotContentChanged(1); // to set md or raw in read-only history html
    });
    botElement.insertBefore(toggleButton, copyButton);

    function renderMarkdownText(message) {
        var mdDiv = message.querySelector('.md-message');
        if (mdDiv) mdDiv.classList.remove('hideM');
        var rawDiv = message.querySelector('.raw-message');
        if (rawDiv) rawDiv.classList.add('hideM');
    }
    function removeMarkdownText(message) {
        var rawDiv = message.querySelector('.raw-message');
        if (rawDiv) {
            rawDiv.innerHTML = rawDiv.querySelector('pre')?.innerHTML || rawDiv.innerHTML;
            rawDiv.classList.remove('hideM');
        }
        var mdDiv = message.querySelector('.md-message');
        if (mdDiv) mdDiv.classList.add('hideM');
    }
    // CSS样式
    toggleButton.classList.add('toggle-button-hide'); // 添加初始隐藏样式
    // 鼠标悬浮时显示按钮
    toggleButton.addEventListener('mouseover', () => {
        toggleButton.classList.remove('toggle-button-hide');
    });
    // 鼠标离开时隐藏按钮
    toggleButton.addEventListener('mouseout', () => {
        toggleButton.classList.add('toggle-button-hide');
    });
}

function gradioApp() {
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];

    if (elem !== document) {
        elem.getElementById = function(id) {
            return document.getElementById(id);
        };
    }
    return elem.shadowRoot ? elem.shadowRoot : elem;
}

function chatbotContentChanged(attempt = 1) {
    for (var i = 0; i < attempt; i++) {
        setTimeout(() => {
            gradioApp().querySelectorAll('#main_chatbot .message-wrap .message.bot, #main_chatbot .message-wrap .message.user').forEach(addChuanhuButton);
          // 添加以下代码
          const messageElems = gradioApp().querySelectorAll('#main_chatbot .message-wrap .message');
          messageElems.forEach(messageElem => {
            if (messageElem.classList.contains('hide')) {
              messageElem.parentNode.classList.add('hide-important');
            } else {
              messageElem.parentNode.classList.remove('hide-important');
            }
          });
            }, i === 0 ? 0 : 500);
    }
    // 理论上是不需要多次尝试执行的，可惜gradio的bug导致message可能没有渲染完毕，所以尝试500ms后再次执行
}

var chatbotObserver = new MutationObserver(() => {
    if (chatbotIndicator.classList.contains('hide')) {
        chatbotContentChanged(2);
    }
});

// 监视页面内部 DOM 变动
var observer = new MutationObserver(function (mutations) {
    gradioLoaded(mutations);
});
// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    const ga = document.getElementsByTagName("gradio-app");
    observer.observe(ga[0], { childList: true, subtree: true });
    isInIframe = (window.self !== window.top);
});
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", adjustDarkMode);
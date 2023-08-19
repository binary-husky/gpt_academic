// custom javascript here
var gradioContainer = null;
var user_input_tb = null;
var userInfoDiv = null;
var appTitleDiv = null;
var chatbot = null;
var chatbotWrap = null;
var apSwitch = null;
var loginUserForm = null;

// gradio 页面加载好了么??? 我能动你的元素了么??
function gradioLoaded(mutations) {
    for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].addedNodes.length) {
            loginUserForm = document.querySelector(".gradio-container > .main > .wrap > .panel > .form")
            gradioContainer = document.querySelector(".gradio-container");
            user_input_tb = document.getElementById('user_input_tb');
            userInfoDiv = document.getElementById("user_info");
            appTitleDiv = document.getElementById("app_title");
            chatbot = document.querySelector('#main_chatbot');
            chatbotWrap = document.querySelector('#main_chatbot > .wrapper > .wrap');
            apSwitch = document.querySelector('.apSwitch input[type="checkbox"]');
            if (gradioContainer && apSwitch) {  // gradioCainter 加载出来了没?
                adjustDarkMode();
            }
        }
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
    var rawMessage = null;
    var mdMessage = null;
    rawMessage = botElement.querySelector('.raw-message');
    mdMessage = botElement.querySelector('.md-message');
    if (!rawMessage) {
        var buttons = botElement.querySelectorAll('button.chuanhu-btn');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].parentNode.removeChild(buttons[i]);
        }
        return;
    }
    var oldCopyButton = null;
    var oldToggleButton = null;
    oldCopyButton = botElement.querySelector('button.copy-bot-btn');
    oldToggleButton = botElement.querySelector('button.toggle-md-btn');
    if (oldCopyButton) oldCopyButton.remove();
    if (oldToggleButton) oldToggleButton.remove();

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
        if (renderMarkdown){
            renderMarkdownText(botElement);
            toggleButton.innerHTML=rawIcon;
        } else {
            removeMarkdownText(botElement);
            toggleButton.innerHTML=mdIcon;
        }
    });
    botElement.insertBefore(toggleButton, copyButton);

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

function renderMarkdownText(message) {
    var mdDiv = message.querySelector('.md-message');
    if (mdDiv) mdDiv.classList.remove('hideM');
    var rawDiv = message.querySelector('.raw-message');
    if (rawDiv) rawDiv.classList.add('hideM');
}
function removeMarkdownText(message) {
    var rawDiv = message.querySelector('.raw-message');
    if (rawDiv) rawDiv.classList.remove('hideM');
    var mdDiv = message.querySelector('.md-message');
    if (mdDiv) mdDiv.classList.add('hideM');
}

let timeoutId;
let isThrottled = false;
var mmutation
// 监听所有元素中 bot message 的变化，为 bot 消息添加复制按钮。
var mObserver = new MutationObserver(function (mutationsList) {
    for (mmutation of mutationsList) {
        if (mmutation.type === 'childList') {
            for (var node of mmutation.addedNodes) {
                if (node.nodeType === 1 && node.classList.contains('message')) {
                    document.querySelectorAll('#main_chatbot .message-wrap .message.bot, #main_chatbot .message-wrap .message.user').forEach(addChuanhuButton);
                }
            }
            for (var node of mmutation.removedNodes) {
                if (node.nodeType === 1 && node.classList.contains('message')) {
                    document.querySelectorAll('#main_chatbot .message-wrap .message.bot, #main_chatbot .message-wrap .message.user').forEach(addChuanhuButton);
                }
            }
        } else if (mmutation.type === 'attributes') {
            if (isThrottled) break; // 为了防止重复不断疯狂渲染，加上等待_(:з」∠)_
            isThrottled = true;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                isThrottled = false;
                document.querySelectorAll('#main_chatbot .message-wrap .message.bot, #main_chatbot .message-wrap .message.user').forEach(addChuanhuButton);
                }, 1500);
        }
    }
});

var submitObserver = new MutationObserver(function (mutationsList) {
    document.querySelectorAll('#chuanhu-chatbot .message-wrap .message.bot').forEach(addChuanhuButton);
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
    historyLoaded = false;
});
mObserver.observe(document.documentElement, { attributes: true, childList: true, subtree: true });
window.addEventListener('resize', setChatbotHeight);
window.addEventListener('scroll', function(){setChatbotHeight(); setUpdateWindowHeight();});
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", adjustDarkMode);
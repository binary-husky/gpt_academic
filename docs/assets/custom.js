
// custom javascript here

const MAX_HISTORY_LENGTH = 32;

var key_down_history = [];
var currentIndex = -1;
var user_input_ta;

var gradioContainer = null;
var user_input_ta = null;
var chat_txt = null;
var userInfoDiv = null;
var appTitleDiv = null;
var chatbot = null;
var chatbotWrap = null;
var apSwitch = null;
var messageBotDivs = null;
var loginUserForm = null;
var logginUser = null;

var userLogged = false;
var usernameGotten = false;
var historyLoaded = false;

var ga = document.getElementsByTagName("gradio-app");
var targetNode = ga[0];
var isInIframe = (window.self !== window.top);
var language = navigator.language.slice(0,2);

var forView_i18n = {
    'zh': "仅供查看",
    'en': "For viewing only",
    'ja': "閲覧専用",
    'fr': "Pour consultation seulement",
    'es': "Solo para visualización",
};

var deleteConfirm_i18n_pref = {
    'zh': "你真的要删除 ",
    'en': "Are you sure you want to delete ",
    'ja': "本当に ",
};
var deleteConfirm_i18n_suff = {
    'zh': " 吗？",
    'en': " ?",
    'ja': " を削除してもよろしいですか？",
};
var deleteConfirm_msg_pref = "Are you sure you want to delete ";
var deleteConfirm_msg_suff = " ?";

// gradio 页面加载好了么??? 我能动你的元素了么??
function gradioLoaded(mutations) {
    for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].addedNodes.length) {
            loginUserForm = document.querySelector(".gradio-container > .main > .wrap > .panel > .form")
            gradioContainer = document.querySelector(".gradio-container");
            chat_txt = document.getElementById('chat_txt');
            userInfoDiv = document.getElementById("user_info");
            appTitleDiv = document.getElementById("app_title");
            chatbot = document.querySelector('#废弃');
            chatbotWrap = document.querySelector('#废弃 > .wrap');
            apSwitch = document.querySelector('.apSwitch input[type="checkbox"]');

            if (loginUserForm) {
                localStorage.setItem("userLogged", true);
                userLogged = true;
            }

            if (gradioContainer && apSwitch) {  // gradioCainter 加载出来了没?
                adjustDarkMode();
            }
            if (chat_txt) {  // chat_txt 加载出来了没?
                selectHistory();
            }
            if (userInfoDiv && appTitleDiv) {  // userInfoDiv 和 appTitleDiv 加载出来了没?
                if (!usernameGotten) {
                    getUserInfo();
                }
                setTimeout(showOrHideUserInfo(), 2000);
            }
            if (chatbot) {  // chatbot 加载出来了没?
                setChatbotHeight();
            }
            if (chatbotWrap) {
                if (!historyLoaded) {
                    loadHistoryHtml();
                }
                setChatbotScroll();
            }
        }
    }
}

function webLocale() {
    // console.log("webLocale", language);
    if (forView_i18n.hasOwnProperty(language)) {
        var forView = forView_i18n[language];
        var forViewStyle = document.createElement('style');
        forViewStyle.innerHTML = '.wrap>.history-message>:last-child::after { content: "' + forView + '"!important; }';
        document.head.appendChild(forViewStyle);
    }
    if (deleteConfirm_i18n_pref.hasOwnProperty(language)) {
        deleteConfirm_msg_pref = deleteConfirm_i18n_pref[language];
        deleteConfirm_msg_suff = deleteConfirm_i18n_suff[language];
    }
}

function showConfirmationDialog(a, file, c) {
    if (file != "") {
        var result = confirm(deleteConfirm_msg_pref + file + deleteConfirm_msg_suff);
        if (result) {
            return [a, file, c];
        }
    }
    return [a, "CANCELED", c];
}

function selectHistory() {
    user_input_ta = chat_txt.querySelector("textarea");
    if (user_input_ta) {
        observer.disconnect(); // 停止监听
        // 在 textarea 上监听 keydown 事件
        user_input_ta.addEventListener("keydown", function (event) {
            var value = user_input_ta.value.trim();
            // 判断按下的是否为方向键
            if (event.code === 'ArrowUp' || event.code === 'ArrowDown') {
                // 如果按下的是方向键，且输入框中有内容，且历史记录中没有该内容，则不执行操作
                if (value && key_down_history.indexOf(value) === -1)
                    return;
                // 对于需要响应的动作，阻止默认行为。
                event.preventDefault();
                var length = key_down_history.length;
                if (length === 0) {
                    currentIndex = -1; // 如果历史记录为空，直接将当前选中的记录重置
                    return;
                }
                if (currentIndex === -1) {
                    currentIndex = length;
                }
                if (event.code === 'ArrowUp' && currentIndex > 0) {
                    currentIndex--;
                    user_input_ta.value = key_down_history[currentIndex];
                } else if (event.code === 'ArrowDown' && currentIndex < length - 1) {
                    currentIndex++;
                    user_input_ta.value = key_down_history[currentIndex];
                }
                user_input_ta.selectionStart = user_input_ta.value.length;
                user_input_ta.selectionEnd = user_input_ta.value.length;
                const input_event = new InputEvent("input", { bubbles: true, cancelable: true });
                user_input_ta.dispatchEvent(input_event);
            } else if (event.code === "Enter") {
                if (value) {
                    currentIndex = -1;
                    if (key_down_history.indexOf(value) === -1) {
                        key_down_history.push(value);
                        if (key_down_history.length > MAX_HISTORY_LENGTH) {
                            key_down_history.shift();
                        }
                    }
                }
            }
        });
    }
}

var username = null;
function getUserInfo() {
    if (usernameGotten) {
        return;
    }
    userLogged = localStorage.getItem('userLogged');
    if (userLogged) {
        username = userInfoDiv.innerText;
        if (username) {
            if (username.includes("getting user info…")) {
                setTimeout(getUserInfo, 500);
                return;
            } else if (username === " ") {
                localStorage.removeItem("username");
                localStorage.removeItem("userLogged")
                userLogged = false;
                usernameGotten = true;
                return;
            } else {
                username = username.match(/User:\s*(.*)/)[1] || username;
                localStorage.setItem("username", username);
                usernameGotten = true;
                clearHistoryHtml();
            }
        }
    }
}

function toggleUserInfoVisibility(shouldHide) {
    if (userInfoDiv) {
        if (shouldHide) {
            userInfoDiv.classList.add("hideK");
        } else {
            userInfoDiv.classList.remove("hideK");
        }
    }
}
function showOrHideUserInfo() {
    var sendBtn = document.getElementById("submit_btn");

    // Bind mouse/touch events to show/hide user info
    appTitleDiv.addEventListener("mouseenter", function () {
        toggleUserInfoVisibility(false);
    });
    userInfoDiv.addEventListener("mouseenter", function () {
        toggleUserInfoVisibility(false);
    });
    sendBtn.addEventListener("mouseenter", function () {
        toggleUserInfoVisibility(false);
    });

    appTitleDiv.addEventListener("mouseleave", function () {
        toggleUserInfoVisibility(true);
    });
    userInfoDiv.addEventListener("mouseleave", function () {
        toggleUserInfoVisibility(true);
    });
    sendBtn.addEventListener("mouseleave", function () {
        toggleUserInfoVisibility(true);
    });

    appTitleDiv.ontouchstart = function () {
        toggleUserInfoVisibility(false);
    };
    userInfoDiv.ontouchstart = function () {
        toggleUserInfoVisibility(false);
    };
    sendBtn.ontouchstart = function () {
        toggleUserInfoVisibility(false);
    };

    appTitleDiv.ontouchend = function () {
        setTimeout(function () {
            toggleUserInfoVisibility(true);
        }, 3000);
    };
    userInfoDiv.ontouchend = function () {
        setTimeout(function () {
            toggleUserInfoVisibility(true);
        }, 3000);
    };
    sendBtn.ontouchend = function () {
        setTimeout(function () {
            toggleUserInfoVisibility(true);
        }, 3000); // Delay 1 second to hide user info
    };

    // Hide user info after 2 second
    setTimeout(function () {
        toggleUserInfoVisibility(true);
    }, 2000);
}

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

    // 根据当前颜色模式设置初始状态
    apSwitch.checked = darkModeQuery.matches;
    toggleDarkMode(darkModeQuery.matches);
    // 监听颜色模式变化
    darkModeQuery.addEventListener("change", (e) => {
        apSwitch.checked = e.matches;
        toggleDarkMode(e.matches);
    });
    // apSwitch = document.querySelector('.apSwitch input[type="checkbox"]');
    apSwitch.addEventListener("change", (e) => {
        toggleDarkMode(e.target.checked);
    });
}

function setChatbotHeight() {
    const screenWidth = window.innerWidth;
    const statusDisplay = document.querySelector('#status_display');
    const statusDisplayHeight = statusDisplay ? statusDisplay.offsetHeight : 0;
    const wrap = chatbot.querySelector('.wrap');
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    if (isInIframe) {
        chatbot.style.height = `700px`;
        wrap.style.maxHeight = `calc(700px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`
    } else {
        if (screenWidth <= 320) {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 150}px)`;
            wrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 150}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        } else if (screenWidth <= 499) {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 100}px)`;
            wrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 100}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        } else {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 160}px)`;
            wrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 160}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        }
    }
}
function setChatbotScroll() {
    var scrollHeight = chatbotWrap.scrollHeight;
    chatbotWrap.scrollTo(0,scrollHeight)
}
var rangeInputs = null;
var numberInputs = null;
function setSlider() {
    rangeInputs = document.querySelectorAll('input[type="range"]');
    numberInputs = document.querySelectorAll('input[type="number"]')
    setSliderRange();
    rangeInputs.forEach(rangeInput => {
        rangeInput.addEventListener('input', setSliderRange);
    });
    numberInputs.forEach(numberInput => {
        numberInput.addEventListener('input', setSliderRange);
    })
}
function setSliderRange() {
    var range = document.querySelectorAll('input[type="range"]');
    range.forEach(range => {
        range.style.backgroundSize = (range.value - range.min) / (range.max - range.min) * 100 + '% 100%';
    });
}

function addChuanhuButton(botElement) {
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
    var copyButton = null;
    var toggleButton = null;
    copyButton = botElement.querySelector('button.copy-bot-btn');
    toggleButton = botElement.querySelector('button.toggle-md-btn');
    if (copyButton) copyButton.remove();
    if (toggleButton) toggleButton.remove();

    // Copy bot button
    var copyButton = document.createElement('button');
    copyButton.classList.add('chuanhu-btn');
    copyButton.classList.add('copy-bot-btn');
    copyButton.setAttribute('aria-label', 'Copy');
    copyButton.innerHTML = copyIcon;
    copyButton.addEventListener('click', () => {
        const textToCopy = rawMessage.innerText;
        navigator.clipboard
            .writeText(textToCopy)
            .then(() => {
                copyButton.innerHTML = copiedIcon;
                setTimeout(() => {
                    copyButton.innerHTML = copyIcon;
                }, 1500);
            })
            .catch(() => {
                console.error("copy failed");
            });
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
                if (node.nodeType === 1 && node.classList.contains('message') && node.getAttribute('data-testid') === 'bot') {
                    saveHistoryHtml();
                    document.querySelectorAll('#废弃>.wrap>.message-wrap .message.bot').forEach(addChuanhuButton);
                }
                if (node.tagName === 'INPUT' && node.getAttribute('type') === 'range') {
                    setSlider();
                }
            }
            for (var node of mmutation.removedNodes) {
                if (node.nodeType === 1 && node.classList.contains('message') && node.getAttribute('data-testid') === 'bot') {
                    saveHistoryHtml();
                    document.querySelectorAll('#废弃>.wrap>.message-wrap .message.bot').forEach(addChuanhuButton);
                }
            }
        } else if (mmutation.type === 'attributes') {
            if (mmutation.target.nodeType === 1 && mmutation.target.classList.contains('message') && mmutation.target.getAttribute('data-testid') === 'bot') {
                if (isThrottled) break; // 为了防止重复不断疯狂渲染，加上等待_(:з」∠)_
                isThrottled = true;
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    isThrottled = false;
                    document.querySelectorAll('#废弃>.wrap>.message-wrap .message.bot').forEach(addChuanhuButton);
                    saveHistoryHtml();
                }, 500);
            }
        }
    }
});
mObserver.observe(document.documentElement, { attributes: true, childList: true, subtree: true });


// 监视页面内部 DOM 变动
var observer = new MutationObserver(function (mutations) {
    gradioLoaded(mutations);
});
observer.observe(targetNode, { childList: true, subtree: true });

// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    isInIframe = (window.self !== window.top);
    historyLoaded = false;
});
window.addEventListener('resize', setChatbotHeight);
window.addEventListener('scroll', setChatbotHeight);
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", adjustDarkMode);

// button svg code
const copyIcon   = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';
const copiedIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
const mdIcon     = '<span><svg stroke="currentColor" fill="none" stroke-width="1" viewBox="0 0 14 18" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><path d="M1.5,0 L12.5,0 C13.3284271,-1.52179594e-16 14,0.671572875 14,1.5 L14,16.5 C14,17.3284271 13.3284271,18 12.5,18 L1.5,18 C0.671572875,18 1.01453063e-16,17.3284271 0,16.5 L0,1.5 C-1.01453063e-16,0.671572875 0.671572875,1.52179594e-16 1.5,0 Z" stroke-width="1.8"></path><line x1="3.5" y1="3.5" x2="10.5" y2="3.5"></line><line x1="3.5" y1="6.5" x2="8" y2="6.5"></line></g><path d="M4,9 L10,9 C10.5522847,9 11,9.44771525 11,10 L11,13.5 C11,14.0522847 10.5522847,14.5 10,14.5 L4,14.5 C3.44771525,14.5 3,14.0522847 3,13.5 L3,10 C3,9.44771525 3.44771525,9 4,9 Z" stroke="none" fill="currentColor"></path></svg></span>';
const rawIcon    = '<span><svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 18 14" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><polyline points="4 3 0 7 4 11"></polyline><polyline points="14 3 18 7 14 11"></polyline><line x1="12" y1="0" x2="6" y2="14"></line></g></svg></span>';

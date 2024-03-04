const MAX_HISTORY_LENGTH = 32;

var key_down_history = [];
var currentIndex = -1;

var gradioContainer = null;
var user_input_ta = null;
var user_input_tb = null;
var userInfoDiv = null;
var appTitleDiv = null;
var chatbotArea = null;
var chatbot = null;
var chatbotIndicator = null;
var uploaderIndicator = null;
var chatListIndicator = null;
var chatbotWrap = null;
var apSwitch = null;
var messageBotDivs = null;
var loginUserForm = null;
var logginUser = null;
var chuanhuBody = null;
var chatbotMsg = null;
var updateToast = null;
var sendBtn = null;
var cancelBtn = null;
var sliders = null;
var updateChuanhuBtn = null;
var statusDisplay = null;
var historySelector = null;
var chuanhuPopup = null;
var waifuStatus = null;
var searchBox = null;
var settingBox = null;
var promptBox = null;
var popupWrapper = null;
var chuanhuHeader = null;
var menu = null;
var toolbox = null;
// var trainBody = null;

var isInIframe = (window.self !== window.top);
var currentTime = new Date().getTime();

let windowWidth = window.innerWidth; // 初始窗口宽度

var uploadedFilesCountElement = null
var uploadIndexFileElement = null
var uploadIndexFileHeight = null
var uploadIndexLinkElement = null
const validImgExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'svg', 'webp', 'ico', 'tif', 'tiff', 'raw', 'eps', 'gif'];
const validDocsExtensions = ['html', 'htm', 'xhtml', 'css', 'js', 'pdf', 'txt', 'json', 'xml', 'md'];
const validAudioExtensions = ['mp3', 'wav', 'aac'];
const validVideoExtensions = ['mp4', 'm4a', 'wav', 'mpeg', 'avi', 'mkv', 'flac', 'aac']
var input_storage_mapping = {}

function addInit() {
    var needInit = {chatbotIndicator, uploaderIndicator};

    chatbotIndicator = gradioApp().querySelector('#chuanhu-chatbot > div.wrap');
    uploaderIndicator = gradioApp().querySelector('#upload-index-file > div.wrap');
    chatListIndicator = gradioApp().querySelector('#history-select-dropdown > div.wrap');
    if (uploaderIndicator) {
        setUploader();
    }
    for (let elem in needInit) {
        if (needInit[elem] == null) {
            // addInited = false;
            return false;
        }
    }
    chatbotObserver.observe(chatbotIndicator, { attributes: true, childList: true, subtree: true });
    chatListObserver.observe(chatListIndicator, { attributes: true });
    chatbotObserverMsg.observe(chatbotWrap, { attributes: true, childList: true, subtree: true });
    chatbotObserverMsgBot.observe(chatbotWrap, { attributes: true, childList: true, subtree: true });
    setDragUploader();
    return true;
}

function initialize() {
    gradioObserver.observe(gradioApp(), { childList: true, subtree: true });

    loginUserForm = gradioApp().querySelector(".gradio-container > .main > .wrap > .panel > .form")
    gradioContainer = gradioApp().querySelector(".gradio-container");
    user_input_tb = gradioApp().getElementById('user-input-tb');

    userInfoDiv = gradioApp().getElementById("user-info");
    appTitleDiv = gradioApp().getElementById("app-title");
    chatbotArea = gradioApp().querySelector('#chatbot-area');
    chatbot = gradioApp().querySelector('#chuanhu-chatbot');
    chatbotWrap = gradioApp().querySelector('#chuanhu-chatbot > .wrapper > .wrap');
    chuanhuBody = gradioApp().querySelector('#chuanhu-body');
    chatbotMsg = chatbotWrap.querySelector('.message-wrap');
    apSwitch = gradioApp().querySelector('.apSwitch input[type="checkbox"]');
    updateToast = gradioApp().querySelector("#toast-update");
    sendBtn = gradioApp().getElementById("submit-btn");
    cancelBtn = gradioApp().getElementById("cancel-btn");
    sliders = gradioApp().querySelectorAll('input[type="range"]');
    updateChuanhuBtn = gradioApp().getElementById("update-chuanhu-btn");
    statusDisplay = gradioApp().querySelector('#status-display');
    waifuStatus = document.querySelector('.waifu')
    historySelector = gradioApp().querySelector('#history-select-dropdown');
    chuanhuPopup = gradioApp().querySelector('#chuanhu-popup');
    settingBox = gradioApp().querySelector('#chuanhu-setting');
    searchBox = gradioApp().querySelector('#spike-search');
    promptBox = gradioApp().querySelector('#spike-prompt');
    popupWrapper = gradioApp().querySelector('#popup-wrapper');
    chuanhuHeader = gradioApp().querySelector('#chuanhu-header');
    menu = gradioApp().querySelector('#menu-area');
    toolbox = gradioApp().querySelector('#toolbox-area');
    uploadedFilesCountElement = gradioApp().querySelector('#uploaded-files-count');
    uploadIndexFileElement = gradioApp().querySelector('#upload-index-file');
    uploadIndexLinkElement = uploadedFilesCountElement.querySelector('a');
    uploadIndexFileHeight = uploadIndexFileElement.offsetHeight;
    input_storage_mapping = {
    "apiKeys": gradioApp().querySelector('#api-keys-input input'),
    "wpsCookies": gradioApp().querySelector('#wps-cookies-input textarea'),
    "qqCookies": gradioApp().querySelector('#qq-cookies-input textarea'),
    "feishuCookies": gradioApp().querySelector('#feishu-cookies-input textarea')
    }
    // trainBody = gradioApp().querySelector('#train-body');

    // if (loginUserForm) {
    // localStorage.setItem("userLogged", true);
    // userLogged = true;
    // }
    addInputListeners()
    adjustDarkMode();
    adjustSide();
    setChatList();
    setChatListHeader();
    setLoclize();
    selectHistory();
    // setChatbotHeight();
    setPopupBoxPosition();
    setSlider();
    setCheckboxes();
    checkModel();

    settingBox.classList.add('hideBox');

    if (!historyLoaded) loadHistoryHtml();
    if (!usernameGotten) getUserInfo();

    // setUpdater();

    setChatbotScroll();
    setTimeout(showOrHideUserInfo(), 2000);

    // setHistroyPanel();
    // trainBody.classList.add('hide-body');

    // 提示词点击后，光标重定向到输入框
    move_cursor();
    //
    toast_move_main()
    check_move_list();
    btn_move_to_tab();
    add_func_event();
    sm_move_more_label();
    addHistoryBtn();
    return true;
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

function showConfirmationDialog(a, file, c) {
    if (file != "") {
        var result = confirm(i18n(deleteConfirm_i18n_pref) + c + ` "${file}"` + i18n(deleteConfirm_i18n_suff));
        if (result) {
            return [a, file, c];
        }
    }
    return [a, "CANCELED", c];
}

function selectHistory() {
    user_input_ta = user_input_tb.querySelector("textarea");
    add_func_paste(user_input_ta)
    if (user_input_ta) {
        disableSendBtn();
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

function disableSendBtn() {
    sendBtn.disabled = user_input_ta.value.trim() === '';
    user_input_ta.addEventListener('input', () => {
        sendBtn.disabled = user_input_ta.value.trim() === '';
    });
}

function checkModel() {
    const model = gradioApp().querySelector('#model-select-dropdown input');
    var modelValue = model.value;
    checkGPT();
    checkXMChat();
    function checkGPT() {
        modelValue = model.value;
        if (modelValue.includes('gpt')) {
            gradioApp().querySelector('#header-btn-groups').classList.add('is-gpt');
        } else {
            gradioApp().querySelector('#header-btn-groups').classList.remove('is-gpt');
        }
        // console.log('gpt model checked')
    }
    function checkXMChat() {
        modelValue = model.value;
        if (modelValue.includes('xmchat')) {
            chatbotArea.classList.add('is-xmchat');
        } else {
            chatbotArea.classList.remove('is-xmchat');
        }
    }

    model.addEventListener('blur', ()=>{
        setTimeout(()=>{
            checkGPT();
            checkXMChat();
        }, 100);
    });
}

function toggleDarkMode(isEnabled) {
    if (isEnabled) {
        mermaidConfig.theme = 'dark'
        document.body.classList.add("dark");
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#171717');
        document.body.style.setProperty("background-color", "var(--neutral-950)", "important");
    } else {
        mermaidConfig.theme = 'default'
        document.body.classList.remove("dark");
        document.querySelector('meta[name="theme-color"]').setAttribute('content', '#ffffff');
        document.body.style.backgroundColor = "";
    }
}
function adjustDarkMode() {
    const savedPreference = localStorage.getItem('darkMode');
    const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const useDarkMode = savedPreference === 'true' || (savedPreference === null && darkModeQuery.matches);

    apSwitch.checked = useDarkMode;

    toggleDarkMode(useDarkMode);
    darkModeQuery.addEventListener("change", (e) => {
        apSwitch.checked = e.matches;
        toggleDarkMode(e.matches);
    });
    apSwitch.addEventListener("change", (e) => {
        toggleDarkMode(e.target.checked);
    });
}
function btnToggleDarkMode() {
    apSwitch.checked = !apSwitch.checked;
    toggleDarkMode(apSwitch.checked);
    localStorage.setItem('darkMode', apSwitch.checked);
    if (chatbotMsg) {
        chatbotMsg.querySelectorAll('.bot .language-mermaid').forEach(mermaidCodeAdd)
    }
}

function setScrollShadow() {
    const toolboxScroll = toolbox.querySelector('#toolbox-area > .gradio-box > .gradio-tabs > div.tab-nav');
    const toolboxTabs = toolboxScroll.querySelectorAll('button');
    let toolboxScrollWidth = 0;
    toolboxTabs.forEach((tab) => {
        toolboxScrollWidth += tab.offsetWidth; // 获取按钮宽度并累加
    });
    function adjustScrollShadow() {
        if (toolboxScroll.scrollLeft > 0) {
            toolboxScroll.classList.add('scroll-shadow-left');
        } else {
            toolboxScroll.classList.remove('scroll-shadow-left');
        }

        if (toolboxScroll.scrollLeft + toolboxScroll.clientWidth < toolboxScrollWidth) {
            toolboxScroll.classList.add('scroll-shadow-right');
        } else {
            toolboxScroll.classList.remove('scroll-shadow-right');
        }
    }
    toolboxScroll.addEventListener('scroll', () => {
        adjustScrollShadow();
    });
    // no, I failed to make shadow appear on the top layer...
}

function setPopupBoxPosition() {
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    if (popupWrapper) {
        popupWrapper.style.height = `${screenHeight}px`;
        popupWrapper.style.width = `${screenWidth}px`;
    }
    // const popupBoxWidth = 680;
    // const popupBoxHeight = 400;
    // chuanhuPopup.style.left = `${(screenWidth - popupBoxWidth) / 2}px`;
    // chuanhuPopup.style.top = `${(screenHeight - popupBoxHeight) / 2}px`;
}

function updateVH() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

function setChatbotHeight() {
    return;
    const screenWidth = window.innerWidth;
    const statusDisplay = document.querySelector('#status-display');
    const statusDisplayHeight = statusDisplay ? statusDisplay.offsetHeight : 0;
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    if (isInIframe) {
        chatbot.style.height = `700px`;
        chatbotWrap.style.maxHeight = `calc(700px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`
    } else {
        if (screenWidth <= 320) {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 150}px)`;
            chatbotWrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 150}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        } else if (screenWidth <= 499) {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 100}px)`;
            chatbotWrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 100}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        } else {
            chatbot.style.height = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 160}px)`;
            chatbotWrap.style.maxHeight = `calc(var(--vh, 1vh) * 100 - ${statusDisplayHeight + 160}px - var(--line-sm) * 1rem - 2 * var(--block-label-margin))`;
        }
    }
}
function setChatbotScroll() {
    var scrollHeight = chatbotWrap.scrollHeight;
    chatbotWrap.scrollTo(0,scrollHeight)
}

function clearChatbot() {
    clearHistoryHtml();
    // clearMessageRows();
}

function chatbotContentChanged(attempt = 1, force = false) {
    for (var i = 0; i < attempt; i++) {

        setTimeout(() => {
            // clearMessageRows();
            saveHistoryHtml();
            disableSendBtn();
            //
            addShowAllButton();
            gradioApp().querySelectorAll('#chuanhu-chatbot .message-wrap .message.bot, #chuanhu-chatbot .message-wrap .message.user').forEach(addChuanhuButton);
            gradioApp().querySelectorAll('#chuanhu-chatbot .message-wrap .message.bot .language-mermaid').forEach(mermaidEditAdd)
            gradioApp().querySelectorAll('#chuanhu-chatbot .message-wrap .message.bot .md-message .fold-panel').forEach(foldPanelAdd)
            if (chatbotIndicator.classList.contains('hide')) { // generation finished
                setLatestMessage();
                setChatList();
            }

            if (!chatbotIndicator.classList.contains('translucent')) { // message deleted
                var checkLatestAdded = setInterval(() => {
                    var latestMessageNow = gradioApp().querySelector('#chuanhu-chatbot > .wrapper > .wrap > .message-wrap .message.bot.latest');
                    if (latestMessageNow && latestMessageNow.querySelector('.message-btn-row')) {
                        clearInterval(checkLatestAdded);
                    } else {
                        setLatestMessage();
                    }
                }, 200);
            }
        }, i === 0 ? 0 : 200);
    }
    // 理论上是不需要多次尝试执行的，可惜gradio的bug导致message可能没有渲染完毕，所以尝试500ms后再次执行
}
var chatbotObserver = new MutationObserver(() => {
    chatbotContentChanged(1);
    if (chatbotIndicator.classList.contains('hide')) {
        // setLatestMessage();
        chatbotContentChanged(2);
    }
    if (!chatbotIndicator.classList.contains('translucent')) {
        chatbotContentChanged(2);
    }

});

var chatListObserver = new MutationObserver(() => {
    setChatList();
});

// 监视页面内部 DOM 变动
var gradioObserver = new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].addedNodes.length) {
            if (addInit()) {
                gradioObserver.disconnect();
                return;
            }
        }
    }
});

// 监视页面变化
window.addEventListener("DOMContentLoaded", function () {
    // const ga = document.getElementsByTagName("gradio-app");
    updateVH();
    windowWidth = window.innerWidth;
    gradioApp().addEventListener("render", initialize);
    isInIframe = (window.self !== window.top);
    historyLoaded = false;
});

window.addEventListener('resize', ()=>{
    // setChatbotHeight();
    updateVH();
    windowWidth = window.innerWidth;
    setPopupBoxPosition();
    adjustSide(); 
});
window.addEventListener('orientationchange', (event) => {
    updateVH();
    windowWidth = window.innerWidth;
    setPopupBoxPosition();
    adjustSide();
});
window.addEventListener('scroll', ()=>{setPopupBoxPosition();});
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", adjustDarkMode);

// console suprise
var styleTitle1 = `
font-size: 16px;
font-family: ui-monospace, monospace;
color: #06AE56;
`
var styleDesc1 = `
font-size: 12px;
font-family: ui-monospace, monospace;
`
function makeML(str) {
    let l = new String(str)
    l = l.substring(l.indexOf("/*") + 3, l.lastIndexOf("*/"))
    return l
}
let ChuanhuInfo = function () {
    /* 
   ________                      __             ________          __ 
  / ____/ /_  __  ______ _____  / /_  __  __   / ____/ /_  ____ _/ /_
 / /   / __ \/ / / / __ `/ __ \/ __ \/ / / /  / /   / __ \/ __ `/ __/
/ /___/ / / / /_/ / /_/ / / / / / / / /_/ /  / /___/ / / / /_/ / /_  
\____/_/ /_/\__,_/\__,_/_/ /_/_/ /_/\__,_/   \____/_/ /_/\__,_/\__/  
                                                                     
   川虎Chat (Chuanhu Chat) - GUI for ChatGPT API and many LLMs
 */
}
let description = `
© 2023 Chuanhu, MZhao, Keldos
GitHub repository: [https://github.com/GaiZhenbiao/ChuanhuChatGPT]\n
Enjoy our project!\n
`
console.log(`%c${makeML(ChuanhuInfo)}`,styleTitle1);
console.log(`%c${description}`, styleDesc1);

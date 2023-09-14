
var historyLoaded = false;
var loadhistorytime = 0; // for debugging


function saveHistoryHtml() {
    var historyHtml = document.querySelector('#chuanhu-chatbot>.wrapper>.wrap');
    if (!historyHtml) return;   // no history, do nothing
    localStorage.setItem('chatHistory', historyHtml.innerHTML);
    // console.log("History Saved")
    historyLoaded = false;
}

function loadHistoryHtml() {
    var historyHtml = localStorage.getItem('chatHistory');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = historyHtml;
    if (!historyHtml || tempDiv.innerText.trim() === "") {
        historyLoaded = true;
        return; // no history, do nothing
    }
    userLogged = localStorage.getItem('userLogged');
    hideHistoryWhenNotLoggedIn = gradioApp().querySelector('#hideHistoryWhenNotLoggedIn_config').innerText === "True";
    if (userLogged || (!userLogged && !hideHistoryWhenNotLoggedIn)){
        historyLoaded = true;
        return; // logged in, do nothing. OR, not logged in but not hide history list, do nothing.
    }

    // 只有用户未登录，还隐藏历史记录列表时，才选用只读历史记录
    if (!historyLoaded) {
        // preprocess, gradio buttons in history lost their event listeners
        var gradioCopyButtons = tempDiv.querySelectorAll('button.copy_code_button');
        for (var i = 0; i < gradioCopyButtons.length; i++) {
            gradioCopyButtons[i].parentNode.removeChild(gradioCopyButtons[i]);
        }
        var messageBtnRows = tempDiv.querySelectorAll('.message-btn-row');
        for (var i = 0; i < messageBtnRows.length; i++) {
            messageBtnRows[i].parentNode.removeChild(messageBtnRows[i]);
        }
        var latestMessages = tempDiv.querySelectorAll('.message.latest');
        for (var i = 0; i < latestMessages.length; i++) {
            latestMessages[i].classList.remove('latest');
        }

        var fakeHistory = document.createElement('div');
        fakeHistory.classList.add('history-message');
        fakeHistory.innerHTML = tempDiv.innerHTML;
        const forViewStyle = document.createElement('style');
        forViewStyle.innerHTML = '.wrapper>.wrap>.history-message>:last-child::after { content: "' + i18n(forView_i18n) + '"!important; }';
        document.head.appendChild(forViewStyle);
        chatbotWrap.insertBefore(fakeHistory, chatbotWrap.firstChild);
        // var fakeHistory = document.createElement('div');
        // fakeHistory.classList.add('history-message');
        // fakeHistory.innerHTML = historyHtml;
        // chatbotWrap.insertBefore(fakeHistory, chatbotWrap.firstChild);
        historyLoaded = true;
        // console.log("History Loaded");
        loadhistorytime += 1; // for debugging
    } else {
        historyLoaded = false;
    }
}

function clearHistoryHtml() {
    localStorage.removeItem("chatHistory");
    historyMessages = chatbotWrap.querySelector('.history-message');
    if (historyMessages) {
        chatbotWrap.removeChild(historyMessages);
        console.log("History Cleared");
    }
}

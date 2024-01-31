
var currentChatName = null;

function setChatListHeader() {
    var grHistoryRefreshBtn = gradioApp().querySelector('button#gr-history-refresh-btn');
    var grHistoryUploadBtn = gradioApp().querySelector('button#gr-history-upload-btn');
    var grCodeBtn = gradioApp().querySelector('button#sm_code_btn');
    var grMyFileBtn = gradioApp().querySelector('button#sm_file_btn');
    var grHistoryBtn = gradioApp().querySelector('button#sm_history_btn')

    // 去掉Gr的样式类
    grHistoryRefreshBtn.className = "";
    grHistoryUploadBtn.className = "";
    grCodeBtn.className = '';
    grMyFileBtn.className = '';
    grHistoryBtn.className = '';

    // 自定义按钮样式捏
    grHistoryRefreshBtn.innerHTML = HistoryRefreshIcon;
    grHistoryUploadBtn.innerHTML = HistoryUploadIcon;
    grCodeBtn.innerHTML = CodeIcon
    grMyFileBtn.innerHTML  = MyFileIcon
    grHistoryBtn.innerHTML = HistoryCO
}

function setChatList() {
    var selectedChat = null;
    var chatList = gradioApp().querySelector('fieldset#history-select-dropdown');
    selectedChat = chatList.querySelector(".wrap label.selected")
    if (!selectedChat) {
        currentChatName = null;
        return;
    }

    // if (userLogged) {
    //     currentChatName = username + "/" + selectedChat.querySelector('span').innerText;
    // } else {
        currentChatName = selectedChat.querySelector('span').innerText;
    // }

    if (selectedChat.classList.contains('added-chat-btns')) {
        return;
    }

    chatList.querySelector('.chat-selected-btns')?.remove(); // remove old buttons
    chatList.querySelectorAll('.added-chat-btns').forEach(chat => chat.classList.remove('added-chat-btns'));

    var ChatSelectedBtns = document.createElement('div');
    ChatSelectedBtns.classList.add('chat-selected-btns');
    selectedChat.classList.add('added-chat-btns');
    ChatSelectedBtns.innerHTML = selectedChatBtns;

    var renameBtn = ChatSelectedBtns.querySelector('#history-rename-btn');
    renameBtn.addEventListener('click', function () {
        gradioApp().querySelector('#gr-history-save-btn').click();
    });

    var deleteBtn = ChatSelectedBtns.querySelector('#history-delete-btn');
    deleteBtn.addEventListener('click', function () {
        gradioApp().querySelector('#gr-history-delete-btn').click();
    });
    selectedChat.appendChild(ChatSelectedBtns);

    return;
}


function saveChatHistory(a, b, c, d) {
    var fileName = b;

    while (true) {
        var result = prompt(renameChat_i18n, fileName);

        if (result === null) {
            throw new Error("rename operation cancelled");
            // 不返回原文件名，而是使用 throw new Error() 打断程序，避免 gradio 进行保存操作
            // break;
        } else if (isValidFileName(result)) {
            return [a, result, c, d];
        } else {
            alert(validFileName_i18n + "!@#$%^&*()<>?/\\|}{~:");
        }
    }
    return [a, b, c, d]; // 兜底保障
}

function isValidFileName(fileName) {
    // 使用正则表达式来检查文件名是否包含不合格字符
    var regex = /[!@#$%^&*()<>?/\\|}{~:]/;
    return !regex.test(fileName) && fileName.trim() !== "";
}

const selectedChatBtns = `
<button id="history-rename-btn"><svg class="icon-need-hover" stroke="currentColor" fill="none" stroke-width="2" height="18px" width="18px" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg></button>
<button id="history-delete-btn"><svg class="icon-need-hover" stroke="currentColor" fill="none" stroke-width="2" height="18px" width="18px" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></button>
`
const HistoryRefreshIcon = '<svg class="icon-need-hover" width="18px" height="18px" viewBox="0 0 16.3594 21.9258 " version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path d="M0 11.6367C0 16.1836 3.65625 19.8398 8.17969 19.8398C12.7031 19.8398 16.3594 16.1836 16.3594 11.6367C16.3594 11.1328 16.0078 10.7695 15.4805 10.7695C14.9883 10.7695 14.6719 11.1328 14.6719 11.6367C14.6719 15.2461 11.7773 18.1406 8.17969 18.1406C4.59376 18.1406 1.6875 15.2461 1.6875 11.6367C1.6875 8.03906 4.59376 5.14452 8.17969 5.14452C8.80079 5.14452 9.33985 5.17968 9.83202 5.28516L7.35937 7.72265C7.19531 7.88671 7.11328 8.09765 7.11328 8.30858C7.11328 8.78906 7.47657 9.15235 7.94531 9.15235C8.20312 9.15235 8.40234 9.07032 8.54296 8.91797L12.2578 5.21484C12.4219 5.05078 12.4922 4.85155 12.4922 4.60546C12.4922 4.38281 12.4102 4.16016 12.2578 4.00781L8.54296 0.257808C8.40234 0.093744 8.19141 0 7.9336 0C7.47657 0 7.11328 0.386712 7.11328 0.867192C7.11328 1.08984 7.19531 1.30078 7.34766 1.46484L9.49218 3.57422C9.07031 3.49219 8.62499 3.45703 8.17969 3.45703C3.65625 3.45703 0 7.10155 0 11.6367Z" fill="currentColor"/></g></svg>';
const HistoryUploadIcon  = '<svg class="icon-need-hover" width="18px" height="18px" viewBox="0 0 21.0234 19.5352" version="1.1" xmlns="http://www.w3.org/2000/svg"><g fill="currentColor"><path d="M4.03125 19.5352C5.34375 19.5352 8.01562 18.1758 9.90234 16.7812C16.4531 16.8281 21.0234 13.1016 21.0234 8.40234C21.0234 3.75 16.3477 0 10.5117 0C4.6875 0 0 3.75 0 8.40234C0 11.4258 1.93359 14.1211 4.83984 15.4336C4.41797 16.2539 3.62109 17.4141 3.19922 17.9766C2.69531 18.6445 3.01172 19.5352 4.03125 19.5352ZM5.17969 17.7891C5.10938 17.8242 5.08594 17.7656 5.13281 17.707C5.67188 17.0391 6.38672 16.0547 6.69141 15.5156C6.98438 14.9883 6.91406 14.4961 6.23438 14.1797C3.35156 12.8438 1.73438 10.7695 1.73438 8.40234C1.73438 4.73438 5.625 1.73438 10.5117 1.73438C15.4102 1.73438 19.2891 4.73438 19.2891 8.40234C19.2891 12.0586 15.4102 15.0586 10.5117 15.0586C10.3945 15.0586 10.1602 15.0586 9.82031 15.0586C9.38672 15.0586 9.05859 15.1992 8.67188 15.5156C7.65234 16.3125 6.03516 17.3789 5.17969 17.7891Z"/><path d="M10.5234 13.1133C10.9805 13.1133 11.3086 12.7969 11.3086 12.3398L11.3086 8.20312L11.2266 6.10547L12.0938 7.19531L13.0312 8.15625C13.1719 8.30859 13.3594 8.37891 13.5938 8.37891C14.0156 8.37891 14.3555 8.05078 14.3555 7.62891C14.3555 7.41797 14.2734 7.21875 14.1445 7.08984L11.1445 4.10156C10.9453 3.90234 10.7578 3.79688 10.5234 3.79688C10.3008 3.79688 10.125 3.89062 9.91406 4.10156L6.91406 7.08984C6.77344 7.21875 6.70312 7.41797 6.70312 7.62891C6.70312 8.05078 7.03125 8.37891 7.46484 8.37891C7.6875 8.37891 7.875 8.29688 8.01562 8.15625L8.96484 7.19531L9.82031 6.11719L9.75 8.20312L9.75 12.3398C9.75 12.7969 10.0781 13.1133 10.5234 13.1133Z"/></g></svg>';
const CodeIcon = '<svg t="1694887807893" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1474" width="18px" height="18px"><path d="M153.770667 517.558857l200.387047-197.241905L302.86019 268.190476 48.761905 518.290286l254.439619 243.614476 50.590476-52.833524-200.021333-191.512381zM658.285714 320.316952L709.583238 268.190476l254.098286 250.09981L709.241905 761.904762l-50.590476-52.833524 200.021333-191.512381L658.285714 320.316952z m-112.981333-86.186666L393.99619 785.554286l70.534096 19.358476 151.30819-551.399619-70.534095-19.358476z" p-id="1475" fill="currentColor"></path></svg>'
const MyFileIcon = '<svg t="1694941997827" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1523" width="18" height="18"><path d="M912 208H428l-50.4-94.4c-11.2-20.8-32.8-33.6-56.8-33.6H112c-35.2 0-64 28.8-64 64v736c0 35.2 28.8 64 64 64h800c35.2 0 64-28.8 64-64V272c0-35.2-28.8-64-64-64zM112 144h208.8l68.8 128H912v97.6H112V144z m0 736V784l1.6-350.4 798.4 1.6V880H112z" p-id="1524" fill="currentColor"></path><path d="M680 767.2c-4 0-8-0.8-12-2.4-4-1.6-7.2-4-9.6-6.4-2.4-2.4-4.8-5.6-6.4-9.6-1.6-4-2.4-8-2.4-12s0.8-8 2.4-12c1.6-4 4-7.2 6.4-9.6s5.6-4.8 9.6-6.4 8-2.4 12-2.4h4.8l42.4-51.2c-0.8-1.6-0.8-3.2-1.6-4.8v-5.6c0-4 0.8-8 2.4-12s4-7.2 6.4-9.6c2.4-2.4 5.6-4.8 9.6-6.4 4-1.6 8-2.4 12-2.4s8 0.8 12 2.4 7.2 4 9.6 6.4 4.8 5.6 6.4 9.6c1.6 4 2.4 8 2.4 12 0 3.2-0.8 6.4-1.6 9.6-0.8 3.2-2.4 6.4-4.8 8.8l36.8 81.6 20.8-37.6c-1.6-2.4-3.2-4.8-4-8-0.8-3.2-1.6-6.4-1.6-9.6 0-4 0.8-8 2.4-12 1.6-4 4-7.2 6.4-9.6 2.4-2.4 5.6-4.8 9.6-6.4s8-2.4 12-2.4 8 0.8 12 2.4c4 1.6 7.2 4 9.6 6.4 3.2 2.4 4.8 5.6 6.4 9.6 1.6 4 2.4 8 2.4 12s-0.8 8-2.4 12c-1.6 4-4 7.2-6.4 9.6-3.2 3.2-6.4 4.8-9.6 6.4-4 1.6-8 2.4-12 2.4h-4.8l-20.8 37.6c3.2 3.2 5.6 6.4 7.2 10.4 1.6 4 3.2 8 3.2 12.8 0 4-0.8 8-2.4 12-1.6 4-4 7.2-6.4 9.6-3.2 3.2-6.4 4.8-9.6 6.4-4 1.6-8 2.4-12 2.4s-8-0.8-12-2.4c-4-1.6-7.2-4-9.6-6.4-2.4-3.2-4.8-6.4-6.4-9.6-1.6-4-2.4-8-2.4-12 0-4.8 0.8-8.8 2.4-12.8 1.6-4 4-7.2 7.2-10.4l-36.8-83.2c-1.6 0-2.4 0.8-3.2 0.8-2.4 0-4.8 0-6.4-0.8-2.4-0.8-4-1.6-5.6-2.4l-37.6 48c1.6 2.4 2.4 4.8 3.2 8 0.8 3.2 1.6 5.6 1.6 8.8 0 4-0.8 8-2.4 12-1.6 4-4 7.2-6.4 9.6-3.2 2.4-6.4 4.8-9.6 6.4-4 1.6-8 2.4-12.8 2.4z m-30.4 60.8h243.2v29.6H649.6v-29.6z" p-id="1525" fill="currentColor"></path></svg>'
const HistoryCO = `<svg t="1706709024358" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="13358" width="18" height="18"><path d="M640 320H288c-17.6 0-32-14.4-32-32s14.4-32 32-32h352c17.6 0 32 14.4 32 32s-14.4 32-32 32zM448 512H288c-17.6 0-32-14.4-32-32s14.4-32 32-32h160c17.6 0 32 14.4 32 32s-14.4 32-32 32zM704 512c51.285 0 99.5 19.971 135.765 56.235C876.029 604.5 896 652.715 896 704s-19.971 99.5-56.235 135.765C803.5 876.029 755.285 896 704 896s-99.5-19.971-135.765-56.235C531.971 803.5 512 755.285 512 704s19.971-99.5 56.235-135.765C604.5 531.971 652.715 512 704 512m0-64c-141.385 0-256 114.615-256 256s114.615 256 256 256 256-114.615 256-256-114.615-256-256-256z" fill="currentColor" p-id="13359"></path><path d="M800 672h-64v-96c0-17.6-14.4-32-32-32s-32 14.4-32 32v128c0 17.6 14.4 32 32 32h96c17.6 0 32-14.4 32-32s-14.4-32-32-32z" fill="currentColor" p-id="13360"></path><path d="M426.821 864H224c-35.2 0-64-28.8-64-64V192c0-35.2 28.8-64 64-64h480c35.2 0 64 28.8 64 64v198.407a317.482 317.482 0 0 1 64 20.246V192c0-70.4-57.6-128-128-128H224c-70.4 0-128 57.6-128 128v608c0 70.4 57.6 128 128 128h251.505c-18.773-19.148-35.168-40.635-48.684-64z" fill="currentColor" p-id="13361"></path></svg>`
var closeHistoryIcon = `
    <svg t="1706697116707" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
        p-id="10463" width="24" height="32">
        <path
            d="M376.726737 511.554289L779.385807 108.89522a63.564419 63.564419 0 1 0-89.901868-89.901868L242.507047 467.236467a63.311174 63.311174 0 0 0 0 89.901868l448.243115 448.243115a63.564419 63.564419 0 1 0 89.901868-89.901868z"
            fill="currentColor" p-id="10464"></path>
    </svg>
`
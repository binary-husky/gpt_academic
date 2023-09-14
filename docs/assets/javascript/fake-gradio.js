
// Fake gradio components!

// buttons
function newChatClick() {
    gradioApp().querySelector('#empty-btn').click();
}
function jsonDownloadClick() {
    gradioApp().querySelector('#gr-history-download-btn').click();
}
function mdDownloadClick() {
    gradioApp().querySelector('#gr-markdown-export-btn').click();
    gradioApp().querySelector('#gr-history-mardown-download-btn').click();

    // downloadHistory(username, currentChatName, ".md");
}

// index files
function setUploader() {
    transUpload();
    var uploaderObserver = new MutationObserver(function (mutations) {
        var fileInput = null;
        var fileCount = 0;
        fileInput = gradioApp().querySelector("#upload-index-file table.file-preview");
        var fileCountSpan = gradioApp().querySelector("#uploaded-files-count");
        if (fileInput) {
            chatbotArea.classList.add('with-file');
            fileCount = fileInput.querySelectorAll('tbody > tr.file').length;
            fileCountSpan.innerText = fileCount;
        } else {
            chatbotArea.classList.remove('with-file');
            fileCount = 0;
            transUpload();
        }
    });
    uploaderObserver.observe(uploaderIndicator, {attributes: true})
}
var grUploader;
var chatbotUploader;
var handleClick = function() {
    grUploader.click();

};
function transUpload() {
    chatbotUploader = gradioApp().querySelector("#upload-files-btn");
    chatbotUploader.removeEventListener('click', handleClick);
    grUploader = gradioApp().querySelector("#upload-index-file > .center.flex");

    // let uploaderEvents = ["click", "drag", "dragend", "dragenter", "dragleave", "dragover", "dragstart", "drop"];
    // transEventListeners(chatbotUploader, grUploader, uploaderEvents);

    chatbotUploader.addEventListener('click', handleClick);
}

// checkbox
var grSingleSessionCB;
var grOnlineSearchCB;
var chatbotSingleSessionCB;
var chatbotOnlineSearchCB;
function setCheckboxes() {
    chatbotSingleSessionCB = gradioApp().querySelector('input[name="single-session-cb"]');
    chatbotOnlineSearchCB = gradioApp().querySelector('input[name="online-search-cb"]');
    grSingleSessionCB = gradioApp().querySelector("#gr-single-session-cb > label > input");
    grOnlineSearchCB = gradioApp().querySelector("#gr-websearch-cb > label> input");

    chatbotSingleSessionCB.addEventListener('change', (e) => {
        grSingleSessionCB.checked = chatbotSingleSessionCB.checked;
        gradioApp().querySelector('#change-single-session-btn').click();
    });
    chatbotOnlineSearchCB.addEventListener('change', (e) => {
        grOnlineSearchCB.checked = chatbotOnlineSearchCB.checked;
        gradioApp().querySelector('#change-online-search-btn').click();
    });
    grSingleSessionCB.addEventListener('change', (e) => {
        chatbotSingleSessionCB.checked = grSingleSessionCB.checked;
    });
    grOnlineSearchCB.addEventListener('change', (e) => {
        chatbotOnlineSearchCB.checked = grOnlineSearchCB.checked;
    });
}

function bgChangeSingleSession() {
    // const grSingleSessionCB = gradioApp().querySelector("#gr-single-session-cb > label > input");
    let a = chatbotSingleSessionCB.checked;
    return [a];
}
function bgChangeOnlineSearch() {
    // const grOnlineSearchCB = gradioApp().querySelector("#gr-websearch-cb > label> input");
    let a = chatbotOnlineSearchCB.checked;
    return [a];
}

// UTILS
function transEventListeners(target, source, events) {
    events.forEach((sourceEvent) => {
        target.addEventListener(sourceEvent, function (targetEvent) {
            if(targetEvent.preventDefault) targetEvent.preventDefault();
            if(targetEvent.stopPropagation) targetEvent.stopPropagation();

            source.dispatchEvent(new Event(sourceEvent, {detail: targetEvent.detail}));
            // console.log(targetEvent.detail);
        });
    });
    /* 事实上，我发现这样写的大多数gradio组件并不适用。。所以。。。生气 */
}

function bgSelectHistory(a,b){
    const historySelectorInput = gradioApp().querySelector('#history-select-dropdown input');
    let file = historySelectorInput.value;
    return [a,file]
}

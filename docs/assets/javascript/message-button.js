
// 为 bot 消息添加复制与切换显示按钮 以及最新消息加上重新生成，删除最新消息，嗯。

function addChuanhuButton(botElement) {

    // botElement = botRow.querySelector('.message.bot');
    var isLatestMessage = botElement.classList.contains('latest');

    var rawMessage = botElement.querySelector('.raw-message');
    var mdMessage = botElement.querySelector('.md-message');
    
    if (!rawMessage) { // 如果没有 raw message，说明是早期历史记录，去除按钮
        // var buttons = botElement.querySelectorAll('button.chuanhu-btn');
        // for (var i = 0; i < buttons.length; i++) {
        //     buttons[i].parentNode.removeChild(buttons[i]);
        // }
        botElement.querySelector('.message-btn-row')?.remove();
        botElement.querySelector('.message-btn-column')?.remove();
        return;
    }
    // botElement.querySelectorAll('button.copy-bot-btn, button.toggle-md-btn').forEach(btn => btn.remove()); // 就算原先有了，也必须重新添加，而不是跳过
    if (!isLatestMessage) botElement.querySelector('.message-btn-row')?.remove();
    botElement.querySelector('.message-btn-column')?.remove();

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
    // botElement.appendChild(copyButton);

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
    // botElement.insertBefore(toggleButton, copyButton);
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
    var messageBtnColumn = document.createElement('div');
    messageBtnColumn.classList.add('message-btn-column');
    messageBtnColumn.appendChild(toggleButton);
    messageBtnColumn.appendChild(copyButton);
    botElement.appendChild(messageBtnColumn);

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
}

function setLatestMessage() {
    var latestMessage = gradioApp().querySelector('#chuanhu-chatbot > .wrapper > .wrap > .message-wrap .message.bot.latest');
    if (latestMessage) addLatestMessageButtons(latestMessage);
}

function addLatestMessageButtons(botElement) {
    botElement.querySelector('.message-btn-row')?.remove();

    var messageBtnRow = document.createElement('div');
    messageBtnRow.classList.add('message-btn-row');
    var messageBtnRowLeading = document.createElement('div');
    messageBtnRowLeading.classList.add('message-btn-row-leading');
    var messageBtnRowTrailing = document.createElement('div');
    messageBtnRowTrailing.classList.add('message-btn-row-trailing');

    messageBtnRow.appendChild(messageBtnRowLeading);
    messageBtnRow.appendChild(messageBtnRowTrailing);

    botElement.appendChild(messageBtnRow);

    //leading
    var regenerateButton = document.createElement('button');
    regenerateButton.classList.add('chuanhu-btn');
    regenerateButton.classList.add('regenerate-btn');
    regenerateButton.setAttribute('aria-label', 'Regenerate');
    regenerateButton.innerHTML = regenIcon + `<span>${i18n(regenerate_i18n)}</span>`;

    var gradioRetryBtn = gradioApp().querySelector('#gr-retry-btn');
    regenerateButton.addEventListener('click', () => {
        gradioRetryBtn.click();
    });

    var deleteButton = document.createElement('button');
    deleteButton.classList.add('chuanhu-btn');
    deleteButton.classList.add('delete-latest-btn');
    deleteButton.setAttribute('aria-label', 'Delete');
    deleteButton.innerHTML = deleteIcon + `<span>${i18n(deleteRound_i18n)}</span>`;

    var gradioDelLastBtn = gradioApp().querySelector('#gr-dellast-btn');
    deleteButton.addEventListener('click', () => {
        gradioDelLastBtn.click();
    });

    messageBtnRowLeading.appendChild(regenerateButton);
    messageBtnRowLeading.appendChild(deleteButton);

    // trailing
    var likeButton = document.createElement('button');
    likeButton.classList.add('chuanhu-btn');
    likeButton.classList.add('like-latest-btn');
    likeButton.setAttribute('aria-label', 'Like');
    likeButton.innerHTML = likeIcon;

    var gradioLikeBtn = gradioApp().querySelector('#gr-like-btn');
    likeButton.addEventListener('click', () => {
        gradioLikeBtn.click();
    });

    var dislikeButton = document.createElement('button');
    dislikeButton.classList.add('chuanhu-btn');
    dislikeButton.classList.add('dislike-latest-btn');
    dislikeButton.setAttribute('aria-label', 'Dislike');
    dislikeButton.innerHTML = dislikeIcon;

    var gradioDislikeBtn = gradioApp().querySelector('#gr-dislike-btn');
    dislikeButton.addEventListener('click', () => {
        gradioDislikeBtn.click();
    });

    messageBtnRowTrailing.appendChild(likeButton);
    messageBtnRowTrailing.appendChild(dislikeButton);
}


// button svg code
const copyIcon   = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg></span>';
const copiedIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12"></polyline></svg></span>';
const mdIcon     = '<span><svg stroke="currentColor" fill="none" stroke-width="1" viewBox="0 0 14 18" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><path d="M1.5,0 L12.5,0 C13.3284271,-1.52179594e-16 14,0.671572875 14,1.5 L14,16.5 C14,17.3284271 13.3284271,18 12.5,18 L1.5,18 C0.671572875,18 1.01453063e-16,17.3284271 0,16.5 L0,1.5 C-1.01453063e-16,0.671572875 0.671572875,1.52179594e-16 1.5,0 Z" stroke-width="1.8"></path><line x1="3.5" y1="3.5" x2="10.5" y2="3.5"></line><line x1="3.5" y1="6.5" x2="8" y2="6.5"></line></g><path d="M4,9 L10,9 C10.5522847,9 11,9.44771525 11,10 L11,13.5 C11,14.0522847 10.5522847,14.5 10,14.5 L4,14.5 C3.44771525,14.5 3,14.0522847 3,13.5 L3,10 C3,9.44771525 3.44771525,9 4,9 Z" stroke="none" fill="currentColor"></path></svg></span>';
const rawIcon    = '<span><svg stroke="currentColor" fill="none" stroke-width="1.8" viewBox="0 0 18 14" stroke-linecap="round" stroke-linejoin="round" height=".8em" width=".8em" xmlns="http://www.w3.org/2000/svg"><g transform-origin="center" transform="scale(0.85)"><polyline points="4 3 0 7 4 11"></polyline><polyline points="14 3 18 7 14 11"></polyline><line x1="12" y1="0" x2="6" y2="14"></line></g></svg></span>';

const regenIcon  = '<span><svg viewBox="0 0 15.6737 14.3099" height="11px" width="10px" xmlns="http://www.w3.org/2000/svg"><g fill="currentColor"><path d="M8.52344 14.3043C12.4453 14.3043 15.6737 11.0704 15.6737 7.15396C15.6737 3.23385 12.4453 0 8.52344 0C4.61357 0 1.39193 3.20969 1.37314 7.11614L2.77012 7.11614C2.78891 3.94173 5.34391 1.40431 8.52344 1.40431C11.7096 1.40431 14.2785 3.96418 14.2785 7.15396C14.2785 10.3401 11.7096 12.9163 8.52344 12.9073C6.6559 12.9036 5.0325 12.0192 3.98219 10.6317C3.70247 10.3165 3.29141 10.2174 2.96431 10.4686C2.65796 10.6988 2.60863 11.1321 2.91325 11.5028C4.17573 13.1677 6.28972 14.3043 8.52344 14.3043ZM0.520576 5.73631C-0.0035439 5.73631-0.140743 6.14811 0.149274 6.53993L1.86425 8.89772C2.08543 9.20509 2.4372 9.20143 2.65301 8.89772L4.36628 6.53626C4.64726 6.14981 4.51544 5.73631 3.99839 5.73631Z"/></g></svg></span>';
const deleteIcon = '<span><svg viewBox="0 0 17.0644 12.9388" height="11px" width="11px" xmlns="http://www.w3.org/2000/svg"><g fill="currentColor"><path d="M4.85464 12.9388L12.2098 12.9388C13.6299 12.9388 14.26 12.2074 14.4792 10.7927L15.6069 3.38561L14.2702 3.42907L13.1479 10.686C13.049 11.3506 12.7252 11.6268 12.12 11.6268L4.94444 11.6268C4.32818 11.6268 4.01711 11.3506 3.91652 10.686L2.79421 3.42907L1.45752 3.38561L2.5852 10.7927C2.80443 12.2147 3.43453 12.9388 4.85464 12.9388ZM1.5018 4.10325L15.5643 4.10325C16.5061 4.10325 17.0644 3.49076 17.0644 2.55799L17.0644 1.55796C17.0644 0.623227 16.5061 0.0144053 15.5643 0.0144053L1.5018 0.0144053C0.588798 0.0144053 0 0.623227 0 1.55796L0 2.55799C0 3.49076 0.561696 4.10325 1.5018 4.10325ZM1.72372 2.88176C1.41559 2.88176 1.26666 2.7255 1.26666 2.412L1.26666 1.70028C1.26666 1.39215 1.41559 1.23589 1.72372 1.23589L15.3444 1.23589C15.6542 1.23589 15.7978 1.39215 15.7978 1.70028L15.7978 2.412C15.7978 2.7255 15.6542 2.88176 15.3444 2.88176Z"/><path d="M6.62087 10.2995C6.77686 10.2995 6.90282 10.2353 7.01438 10.1274L8.53038 8.60625L10.0517 10.1274C10.1633 10.2316 10.2876 10.2995 10.4526 10.2995C10.7594 10.2995 11.0131 10.0368 11.0131 9.72824C11.0131 9.56151 10.9542 9.44092 10.8427 9.32936L9.33033 7.81679L10.8463 6.29151C10.965 6.17458 11.0184 6.0557 11.0184 5.90166C11.0184 5.58407 10.7685 5.33044 10.4526 5.33044C10.302 5.33044 10.1814 5.38928 10.0608 5.5062L8.53038 7.03269L7.01072 5.50987C6.89379 5.39831 6.77686 5.33947 6.62087 5.33947C6.31036 5.33947 6.05307 5.59311 6.05307 5.90166C6.05307 6.05936 6.11019 6.18899 6.22346 6.29688L7.73579 7.81679L6.22346 9.33303C6.1119 9.44092 6.05307 9.56688 6.05307 9.72824C6.05307 10.0405 6.3067 10.2995 6.62087 10.2995Z"/></g></svg></span>';
    // const deleteIcon = '<span><svg stroke="currentColor" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" height="11px" width="11px" viewBox="0 0 216 163" version="1.1" xmlns="http://www.w3.org/2000/svg"><rect x="0.5" y="0.5" width="215" height="39" rx="9"/><path d="M197.485,39.535 L181.664,145.870 C180.953,150.648 178.547,154.805 175.110,157.768 C171.674,160.731 167.207,162.500 162.376,162.500 L53.558,162.500 C48.737,162.500 44.278,160.738 40.843,157.785 C37.409,154.831 34.999,150.686 34.278,145.919 L18.173,39.535 L197.485,39.535 Z" /><line x1="79.5" y1="71.5" x2="135.5" y2="127.5"/><line x1="79.5" y1="127.5" x2="135.5" y2="71.5"/></svg></span>'

const likeIcon   = '<span><svg viewBox="0 0 14.4675 15.7462" height="11px" width="11px" xmlns="http://www.w3.org/2000/svg"><g fill="currentColor"><path d="M0 10.371C0 12.7447 1.51703 14.6758 3.48611 14.6758L5.667 14.6758C6.55809 15.123 7.61471 15.3774 8.77071 15.3774L9.69842 15.3774C10.58 15.3774 11.3136 15.3276 11.7943 15.2026C12.7703 14.9639 13.3931 14.2618 13.3931 13.3949C13.3931 13.2345 13.3677 13.0941 13.3208 12.9537C13.7842 12.5939 14.042 12.0763 14.042 11.4997C14.042 11.2309 13.9917 10.9655 13.8908 10.7507C14.206 10.4318 14.3799 9.96358 14.3799 9.46848C14.3799 9.14304 14.3027 8.81345 14.1645 8.57078C14.3581 8.2876 14.4675 7.90016 14.4675 7.47879C14.4675 6.42124 13.6602 5.60147 12.6063 5.60147L10.1642 5.60147C10.0006 5.60147 9.8919 5.52528 9.89873 5.37707C9.94826 4.69467 11.0035 3.06283 11.0035 1.72154C11.0035 0.72357 10.3014 0 9.33735 0C8.63623 0 8.15116 0.370089 7.70051 1.23942C6.86069 2.86536 5.8793 4.19561 4.39803 6.0414L3.23221 6.0414C1.38812 6.0414 0 7.9527 0 10.371ZM4.16181 10.3188C4.16181 8.90914 4.47725 8.01363 5.3808 6.80246C6.38763 5.45238 7.78384 3.82937 8.78871 1.82159C8.99528 1.42114 9.12909 1.3181 9.34054 1.3181C9.5974 1.3181 9.76222 1.50416 9.76222 1.81548C9.76222 2.78038 8.64211 4.4305 8.64211 5.51371C8.64211 6.3203 9.28051 6.84271 10.1713 6.84271L12.5653 6.84271C12.9408 6.84271 13.2246 7.12839 13.2246 7.50612C13.2246 7.76811 13.1415 7.94147 12.9377 8.15218C12.7334 8.34524 12.7053 8.65131 12.8901 8.84536C13.0595 9.07976 13.1352 9.25141 13.1352 9.47018C13.1352 9.73072 13.007 9.95486 12.7653 10.139C12.5131 10.3172 12.4299 10.6154 12.5712 10.9049C12.7031 11.1466 12.77 11.2853 12.77 11.4877C12.77 11.7944 12.5751 12.0361 12.1869 12.2381C11.9475 12.3752 11.8772 12.6425 11.9851 12.8802C12.1062 13.1749 12.1242 13.2435 12.1225 13.3864C12.1225 13.6664 11.9184 13.8921 11.4792 14.0019C11.0907 14.1006 10.4594 14.1416 9.60644 14.1399L8.82296 14.1382C6.03316 14.1313 4.16181 12.5581 4.16181 10.3188ZM1.21733 10.371C1.21733 8.67034 2.08408 7.32534 3.09216 7.26898C3.26992 7.26556 3.44573 7.26386 3.62349 7.26215C3.13079 8.20088 2.91716 9.15693 2.91716 10.3266C2.91716 11.5559 3.35395 12.646 4.14963 13.4907C3.90227 13.4907 3.64466 13.489 3.39046 13.4872C2.20833 13.4275 1.21733 12.0649 1.21733 10.371Z"/></g></svg></span>';
const dislikeIcon= '<span><svg viewBox="0 0 14.4675 15.5664" height="11px" width="11px" xmlns="http://www.w3.org/2000/svg"><g fill="currentColor"><path d="M14.4675 5.19535C14.4675 2.82169 12.9488 0.890613 10.9814 0.890613L8.7988 0.890613C7.90771 0.443351 6.85109 0.188955 5.70046 0.188955L4.76908 0.188955C3.88948 0.188955 3.15391 0.238755 2.6715 0.363751C1.6972 0.602507 1.07444 1.30459 1.07444 2.17147C1.07444 2.33189 1.09984 2.47228 1.14501 2.61267C0.683343 2.97251 0.423822 3.49007 0.423822 4.06671C0.423822 4.33551 0.47778 4.60089 0.574954 4.81574C0.265139 5.13456 0.0859375 5.60282 0.0859375 6.09792C0.0859375 6.42336 0.168459 6.75295 0.302984 6.99562C0.11304 7.2788 0 7.66624 0 8.0859C0 9.14516 0.807327 9.96493 1.8595 9.96493L4.30164 9.96493C4.46695 9.96493 4.57561 10.0411 4.56707 10.1893C4.51754 10.8717 3.46404 12.5036 3.46404 13.8449C3.46404 14.8428 4.16442 15.5664 5.12845 15.5664C5.83128 15.5664 6.31634 15.1963 6.76895 14.327C7.60878 12.701 8.5882 11.3708 10.0695 9.525L11.2353 9.525C13.0794 9.525 14.4675 7.6137 14.4675 5.19535ZM10.3057 5.24758C10.3057 6.65726 9.98855 7.55277 9.09036 8.76394C8.07817 10.114 6.68196 11.737 5.67709 13.7448C5.47418 14.1453 5.33671 14.2483 5.12697 14.2483C4.87376 14.2483 4.70528 14.0622 4.70528 13.7509C4.70528 12.786 5.82539 11.1359 5.82539 10.0527C5.82539 9.2461 5.187 8.72369 4.29816 8.72369L1.90049 8.72369C1.52497 8.72369 1.24124 8.43801 1.24124 8.06028C1.24124 7.79829 1.32426 7.62493 1.52984 7.41422C1.7361 7.22116 1.76051 6.91509 1.5811 6.72104C1.41166 6.48664 1.3323 6.31499 1.3323 6.09622C1.3323 5.83398 1.46049 5.61154 1.70587 5.42744C1.95436 5.24925 2.03956 4.95098 1.89627 4.66148C1.76271 4.41976 1.69581 4.28108 1.69581 4.07866C1.69581 3.77199 1.89065 3.53027 2.28058 3.32835C2.52003 3.19117 2.59033 2.92392 2.4861 2.68447C2.35962 2.39146 2.34155 2.32115 2.34497 2.17831C2.34497 1.89995 2.54909 1.67434 2.99028 1.56447C3.38042 1.46584 4.01005 1.42116 4.85936 1.42653L5.64284 1.42824C8.43435 1.4424 10.3057 3.00833 10.3057 5.24758ZM13.2502 5.19535C13.2502 6.89606 12.3834 8.24106 11.3736 8.29742C11.2013 8.30084 11.0218 8.30254 10.844 8.30425C11.3367 7.36552 11.5486 6.40947 11.5486 5.23978C11.5486 4.01052 11.1136 2.92044 10.3162 2.07574C10.5689 2.07574 10.8228 2.07745 11.077 2.07915C12.2575 2.13893 13.2502 3.50151 13.2502 5.19535Z"/></g></svg></span>'

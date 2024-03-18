function addHideBoxClassExcept(element) {
    chuanhuPopup.classList.add('showBox');
    popupWrapper.classList.add('showBox');
    let boxes = [settingBox, searchBox, promptBox]
    for (let box of boxes) {
        if (box !== element) {
            box.classList.add('hideBox');
        } else {
            box.classList.remove('hideBox');
        }
    }
    showMask("box");
}


function openSettingBox() {
    addHideBoxClassExcept(settingBox)
    fillInputsFromCache()
}


function openSearch() {
    addHideBoxClassExcept(searchBox)
}

function open_treasure_chest() {
    addHideBoxClassExcept(promptBox)
    remove_red_dot()
}

function openChatMore() {
    chatbotArea.classList.add('show-chat-more');
    showMask("chat-more");
}


function closeChatMore() {
    chatbotArea.classList.remove('show-chat-more');
    chatbotArea.querySelector('.chuanhu-mask')?.remove();
}


function showMask(obj) {
    const mask = document.createElement('div');
    mask.classList.add('chuanhu-mask');
    if (obj == "box") {
        mask.classList.add('mask-blur');
        document.body.classList.add('popup-open');
        popupWrapper.appendChild(mask);
    } else if (obj == "chat-more") {
        mask.classList.add('transparent-mask');
        chatbotArea.querySelector('#chatbot-input-more-area').parentNode.appendChild(mask);
    } else if (obj == "update-toast") {
        mask.classList.add('chuanhu-top-mask');
        document.body.appendChild(mask);
        // mask.classList.add('transparent-mask');
    }

    mask.addEventListener('click', () => {
        if (obj == "box") {
            closeBox();
        } else if (obj == "chat-more") {
            closeChatMore();
        } else if (obj == "update-toast") {
            closeUpdateToast();
        }
    });
}

function chatMoreBtnClick() {
    if (chatbotArea.classList.contains('show-chat-more')) {
        closeChatMore();
    } else {
        openChatMore();
    }
}

function closeBtnClick(obj = "box") {
    if (obj == "box") {
        closeBox();
    } else if (obj == "toolbox") {
        closeSide(toolbox);
        wantOpenToolbox = false;
    }
}

function closeBox() {
    chuanhuPopup.classList.remove('showBox');
    popupWrapper.classList.remove('showBox');
    settingBox.classList.add('hideBox');
    document.querySelector('.chuanhu-mask')?.remove();
    document.body.classList.remove('popup-open');
    red_dot_detection()
}

function closeSide(sideArea) {
    document.body.classList.remove('popup-open');
    if (sideArea) {
        sideArea.classList.remove('showSide');
    }
    if (sideArea === toolbox) {
        chuanhuHeader.classList.remove('under-box');
        chatbotArea.classList.remove('toolbox-open')
        toolboxOpening = false;
    } else if (sideArea === menu) {
        chatbotArea.classList.remove('menu-open')
        menuOpening = false;
        if (waifuStatus) {
            waifuStatus.style.display = 'none'
        }
    }
    adjustMask();
}

function openSide(sideArea) {
    if (sideArea) {
        sideArea.classList.add('showSide');
        if (sideArea === toolbox) {
            chuanhuHeader.classList.add('under-box');
            chatbotArea.classList.add('toolbox-open')
            toolboxOpening = true;
        } else if (sideArea === menu) {
            chatbotArea.classList.add('menu-open')
            menuOpening = true;
            if (waifuStatus) {
                waifuStatus.style.display = 'flex'
            }
        }
    }
    // document.body.classList.add('popup-open');
}

function menuClick() {
    shouldAutoClose = false;
    if (menuOpening) {
        closeSide(menu);
        wantOpenMenu = false;
    } else {
        if (windowWidth < 1024 && toolboxOpening) {
            closeSide(toolbox);
            wantOpenToolbox = false;
        }
        openSide(menu);
        wantOpenMenu = true;
    }
    click_toggle_move(tog_history_btn, wantOpenMenu);
    adjustSide();
}

function toolboxClick() {
    shouldAutoClose = false;
    if (toolboxOpening) {
        closeSide(toolbox);
        wantOpenToolbox = false;
    } else {
        if (windowWidth < 1024 && menuOpening) {
            closeSide(menu);
            wantOpenMenu = false;
        }
        openSide(toolbox);
        wantOpenToolbox = true;
    }
    adjustSide();
}

var menuOpening = false;
var toolboxOpening = false;
var shouldAutoClose = true;
var wantOpenMenu = windowWidth > 768;
var wantOpenToolbox = windowWidth >= 1024;
var wantCloseToolbox = windowWidth < 1400;

function adjustSide() {
    if (windowWidth >= 1024) {
        shouldAutoClose = true;
        if (wantOpenMenu) {
            openSide(menu);
            if (wantCloseToolbox) {
                closeSide(toolbox);
            } else if (wantOpenToolbox) {
                openSide(toolbox);
            }
        } else if (wantOpenToolbox) {
            openSide(toolbox);
        } else {
            closeSide(menu);
            closeSide(toolbox);
        }
    } else if (windowWidth > 768 && windowWidth < 1024) {
        shouldAutoClose = true;
        if (wantOpenToolbox) {
            if (wantOpenMenu) {
                closeSide(toolbox);
                openSide(menu);
            } else {
                closeSide(menu);
                openSide(toolbox);
            }
        } else if (wantOpenMenu) {
            if (wantOpenToolbox) {
                closeSide(menu);
                openSide(toolbox);
            } else {
                closeSide(toolbox);
                openSide(menu);
            }
        } else if (!wantOpenMenu && !wantOpenToolbox) {
            closeSide(menu);
            closeSide(toolbox);
        }
    } else { // windowWidth <= 768
        if (shouldAutoClose) {
            closeSide(menu);
            // closeSide(toolbox);
        }
    }
    checkChatbotWidth();
    adjustMask();
}

function add_tooltip_toggle(elem, text) {
    if (elem) {
        elem.setAttribute('aria-label', text);
        elem.classList.add('tooltip-toggle')
        elem.classList.add('hover-background')
    }
}

function click_toggle_move(elem, open) {
    if (elem) {
        if (!open) {
            add_tooltip_toggle(elem, 'Open sidebar');
            elem.style.left = '30px';
            elem.querySelector('svg').style.transform = 'scaleX(-1)';
        } else {
            add_tooltip_toggle(elem, 'Close sidebar');
            elem.style.left = '290px';
            elem.querySelector('svg').style.transform = 'scaleY(-1)';
        }
    }
}

var tog_history_btn;
var historyToggleButtonStyle = {
    display: 'flex',
    position: 'fixed',
    left: '290px',
    top: '50%',
    zIndex: 4,
    minWidth: 'min(25px, 100%)',
    borderRadius: '7px',
    boxShadow: 'rgba(0, 0, 0, 0.19) 0 10px 20px, rgba(0, 0, 0, 0.23) 0 5px 5px'
};

function addHistoryBtn() {
    tog_history_btn = chuanhuBody.querySelector('#history-toggle-button');
    if (!tog_history_btn) {
        let tog_btn = document.createElement('button');
        tog_btn.id = 'history-toggle-button'
        tog_btn.innerHTML = HistoryStateIcon;
        click_toggle_move(tog_btn, wantOpenMenu)
        Object.assign(tog_btn.style, historyToggleButtonStyle);
        tog_btn.addEventListener('click', () => {
            menuClick();
        });
        chuanhuBody.appendChild(tog_btn);
        tog_history_btn = chuanhuBody.querySelector('#history-toggle-button');
    }
}


function adjustMask() {
    var sideMask = null;
    if (!gradioApp().querySelector('.chuanhu-side-mask')) {
        sideMask = document.createElement('div');
        sideMask.classList.add('chuanhu-side-mask');
        gradioApp().appendChild(sideMask);
        sideMask.addEventListener('click', () => {
            closeSide(menu);
            closeSide(toolbox);
        });
    }
    sideMask = gradioApp().querySelector('.chuanhu-side-mask');

    if (windowWidth > 768) {
        sideMask.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        setTimeout(() => {
            sideMask.style.display = 'none';
        }, 100);
        return;
    }
    // if (windowWidth <= 768)
    if (menuOpening || toolboxOpening) {
        document.body.classList.add('popup-open');
        sideMask.style.display = 'block';
        setTimeout(() => {
            sideMask.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        }, 200);
        sideMask.classList.add('mask-blur');
    } else if (!menuOpening && !toolboxOpening) {
        sideMask.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        setTimeout(() => {
            sideMask.style.display = 'none';
        }, 100);
    }
}

function checkChatbotWidth() {
    // let chatbotWidth = chatbotArea.clientWidth;
    // if (chatbotWidth > 488) {
    if (windowWidth > 768) {
        chatbotArea.classList.add('chatbot-full-width');
        if (tog_history_btn) {
            tog_history_btn.style.display = 'flex'
        } else {
            historyToggleButtonStyle.display = 'flex'
        }
    } else {
        chatbotArea.classList.remove('chatbot-full-width');
        if (chatbot) {
            monitorSwipeEvent()
        }
        if (tog_history_btn) {
            tog_history_btn.style.display = 'none'
        } else {
            historyToggleButtonStyle.display = 'none'
        }
    }

    if (windowWidth > 768) {
        chatbotArea.classList.remove('no-toolbox');
        chatbotArea.classList.remove('no-menu');

        if (!chatbotArea.classList.contains('toolbox-open') && chatbotArea.classList.contains('menu-open')) {
            chatbotArea.classList.add('no-toolbox');
        } else if (!chatbotArea.classList.contains('menu-open') && chatbotArea.classList.contains('toolbox-open')) {
            chatbotArea.classList.add('no-menu');
        } else if (!chatbotArea.classList.contains('menu-open') && !chatbotArea.classList.contains('toolbox-open')) {
            chatbotArea.classList.add('no-toolbox');
            chatbotArea.classList.add('no-menu');
        }
    }

    checkChatMoreMask();
}

function checkChatMoreMask() {
    if (!chatbotArea.classList.contains('chatbot-full-width')) {
        chatbotArea.querySelector('.chuanhu-mask')?.remove();
        chatbotArea.classList.remove('show-chat-more');
    }
}

function setThemeClass(css) {
    var existingStyles = document.querySelectorAll("style[data-loaded-css]");
    for (var i = 0; i < existingStyles.length; i++) {
        var style = existingStyles[i];
        style.parentNode.removeChild(style);
    }
    var styleElement = document.createElement('style');
    styleElement.setAttribute('data-loaded-css', css);
    styleElement.innerHTML = css;
    document.head.appendChild(styleElement);
}

/*
function setHistroyPanel() {
    const historySelectorInput = gradioApp().querySelector('#history-select-dropdown input');
    const historyPanel = document.createElement('div');
    historyPanel.classList.add('chuanhu-history-panel');
    historySelector.parentNode.insertBefore(historyPanel, historySelector);
    var historyList=null;

    historySelectorInput.addEventListener('click', (e) => {
        e.stopPropagation();
        historyList = gradioApp().querySelector('#history-select-dropdown ul.options');

        if (historyList) {
            // gradioApp().querySelector('.chuanhu-history-panel')?.remove();
            historyPanel.innerHTML = '';
            let historyListClone = historyList.cloneNode(true);
            historyListClone.removeAttribute('style');
            // historyList.classList.add('hidden');
            historyList.classList.add('hideK');
            historyPanel.appendChild(historyListClone);
            addHistoryPanelListener(historyPanel);
            // historySelector.parentNode.insertBefore(historyPanel, historySelector);
        }
    });
}
*/

// function addHistoryPanelListener(historyPanel){
//     historyPanel.querySelectorAll('ul.options > li').forEach((historyItem) => {
//         historyItem.addEventListener('click', (e) => {
//             const historySelectorInput = gradioApp().querySelector('#history-select-dropdown input');
//             const historySelectBtn = gradioApp().querySelector('#history-select-btn');
//             historySelectorInput.value = historyItem.innerText;
//             historySelectBtn.click();
//         });
//     });
// }


// function testTrain() {

//     trainBody.classList.toggle('hide-body');
//     trainingBox.classList.remove('hideBox');

//     var chuanhuBody = document.querySelector('#chuanhu-body');
//     chuanhuBody.classList.toggle('hide-body');
// }
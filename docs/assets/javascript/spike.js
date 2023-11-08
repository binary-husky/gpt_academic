function move_cursor() {
    const buttonsParent = gradioApp().getElementById('prompt_list');
    const inputElement = gradioApp().getElementById('user-input-tb');
    const textarea = inputElement.querySelector('[data-testid=textbox]');
    if (buttonsParent && inputElement && textarea) {
        buttonsParent.querySelectorAll('button').forEach((button) => {
            button.addEventListener('click', () => {
                textarea.focus();
            });
        });
    }
}

function check_move_list() {
    const promptList = document.getElementById('prompt_list');
    const pm_check = document.getElementById('pm_check');
    if (!promptList.querySelector('.label #pm_check')) {
        promptList.querySelector('.label').appendChild(pm_check);
    }
}

function btn_move_to_tab() {
    const mk_tabs = document.getElementById('mask_tabs');
    const mk_del = document.getElementById('mk_del');
    const mk_clear = document.getElementById('mk_clear');
    const mk_btn_wrap = mk_tabs.querySelector('.controls-wrap')
    if (!mk_btn_wrap.contains(mk_del)) {
        mk_btn_wrap.appendChild(mk_del)
    }
    if (!mk_btn_wrap.contains(mk_clear)) {
        mk_btn_wrap.appendChild(mk_clear)
    }
}

function red_dot_detection() {
    const langchainTab = document.getElementById('langchain_tab');
    const hasGeneratingAttr = langchainTab.querySelector('[generating]');
    if (hasGeneratingAttr) {
        const btn = document.getElementById("prompt-mask-btn")
        const dot = document.createElement('span');
        dot.className = 'red-dot';
        btn.appendChild(dot);
    }
}

function remove_red_dot() {
    const btn = document.getElementById("prompt-mask-btn");
    const redDot = btn.querySelector('.red-dot');
    if (redDot) {
        btn.removeChild(redDot);
    }
}

function reuse_or_edit(check, b, c, d, e, f) {
    if (check === false) {
        openPrompt()
    }
    return [check, b, c, d, e, f]
}


function addShowAllButton() {
    var codeWraps = document.getElementsByClassName('code_wrap');
    for (var i = 0; i < codeWraps.length; i++) {
        if (codeWraps[i].getElementsByClassName('language-folded').length > 0) {
            // 检查button是否已经存在
            var existingButton = codeWraps[i].querySelector("#show-all-btn");
            // 如果按钮不存在，则创建
            if (!existingButton) {
                // 创建外层button元素
                var show_button = document.createElement("button");
                show_button.id = "show-all-btn";
                show_button.title = "show all";
                // 创建内部span包裹svg图标
                var span_show_svg = document.createElement("span");
                span_show_svg.innerHTML = `
                        <svg t="1699438091661" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
                            p-id="6097" width="17" height="17">
                            <path
                                d="M193.349046 210.094207v130.995519c0.084979 23.530755-6.042025 43.024996-29.555785 43.105726h-0.195452c-23.649726-0.025494-33.940714-19.53673-34.004448-43.207701v-169.916017a41.580349 41.580349 0 0 1 41.784299-41.809792h170.328166c23.641228 0.029743 42.795552 10.707386 42.825294 34.36561 0.029743 23.535004-19.009859 29.445311-42.523618 29.475054H210.344896a16.995851 16.995851 0 0 0-16.99585 16.99585z m620.306058-16.99585H681.992498c-23.513759-0.025494-42.549112-5.935801-42.523618-29.470805 0.029743-23.662473 19.184066-34.335867 42.825294-34.369859H852.78805a41.580349 41.580349 0 0 1 41.618589 41.809792v169.920266c-0.063734 23.666722-10.354722 43.182207-34.000199 43.21195h-0.199701c-23.513759-0.084979-29.636515-19.57922-29.555785-43.109975v-130.995519a16.995851 16.995851 0 0 0-16.99585-16.99585zM210.344896 830.09434H342.007502c23.513759 0.025494 42.553361 5.94005 42.523618 29.470805-0.029743 23.662473-19.184066 34.335867-42.825294 34.369859H171.21195a41.580349 41.580349 0 0 1-41.618589-41.809792v-169.916017c0.063734-23.670971 10.354722-43.186456 34.004448-43.21195h0.195452c23.513759 0.084979 29.636515 19.574971 29.555785 43.105726v130.995519a16.995851 16.995851 0 0 0 16.99585 16.99585z m620.306058-16.859884v-130.991269c-0.084979-23.535004 6.042025-43.024996 29.555785-43.109975h0.199701c23.645477 0.029743 33.936465 19.545228 34.000199 43.21195v169.916016a41.580349 41.580349 0 0 1-41.784299 41.809793h-170.328166c-23.641228-0.029743-42.795552-10.707386-42.825294-34.36561-0.025494-23.535004 19.009859-29.445311 42.523618-29.475054H813.655104a16.995851 16.995851 0 0 0 16.99585-16.995851z"
                                fill="currentColor" p-id="6098"></path>
                        </svg>
                `
                // 将span添加到button，并将button添加到父节点
                show_button.appendChild(span_show_svg);
                codeWraps[i].appendChild(show_button);
                // 给button添加监听事件
                show_button.addEventListener('click', handleShowAllButtonClick);
            }
        }
    }
}

function handleShowAllButtonClick(event) {
    if (!event.target.closest('#show-all-btn')) return; // 如果事件来源不在 Show All 按钮内执行退出

    var codeWrap = event.target.closest('.code_wrap');

    if(!codeWrap) { // 找不到外围code_wrap则退出运行
        console.warn("Can't find the parent .code_wrap element.");
        return;
    }
    var languageFoldedElement = codeWrap.querySelector('.language-folded');

    if(languageFoldedElement){
       if (languageFoldedElement.classList.contains('unclamp')) {
           languageFoldedElement.classList.remove('unclamp');
       } else {
           languageFoldedElement.classList.add('unclamp');
       }
    }
}
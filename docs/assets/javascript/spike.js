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

function check_move_list(){
    const promptList = document.getElementById('prompt_list');
    const pm_check =  document.getElementById('pm_check');
    if (!promptList.querySelector('.label #pm_check')) {
        promptList.querySelector('.label').appendChild(pm_check);
    }
}

function btn_move_to_tab() {
    const mk_tabs = document.getElementById('mask_tabs');
    const mk_del = document.getElementById('mk_del');
    const mk_clear = document.getElementById('mk_clear');
    const mk_btn_wrap =  mk_tabs.querySelector('.controls-wrap')
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
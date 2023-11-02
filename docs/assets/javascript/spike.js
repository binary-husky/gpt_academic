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
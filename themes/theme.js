async function try_load_previous_theme(){
    if (getCookie("js_theme_selection_cookie")) {
        theme_selection = getCookie("js_theme_selection_cookie");
        let css = localStorage.getItem('theme-' + theme_selection);
        if (css) {
            change_theme(theme_selection, css);
        }
    }
}

async function change_theme(theme_selection, css) {
    if (theme_selection.length==0) {
        try_load_previous_theme();
        return;
    }

    var existingStyles = document.querySelectorAll("body > gradio-app > div > style")
    for (var i = 0; i < existingStyles.length; i++) {
        var style = existingStyles[i];
        style.parentNode.removeChild(style);
    }
    var existingStyles = document.querySelectorAll("style[data-loaded-css]");
    for (var i = 0; i < existingStyles.length; i++) {
        var style = existingStyles[i];
        style.parentNode.removeChild(style);
    }

    setCookie("js_theme_selection_cookie", theme_selection, 3);
    localStorage.setItem('theme-' + theme_selection, css);

    var styleElement = document.createElement('style');
    styleElement.setAttribute('data-loaded-css', 'placeholder');
    styleElement.innerHTML = css;
    document.body.appendChild(styleElement);
}


// // 记录本次的主题切换
// async function change_theme_prepare(theme_selection, secret_css) {
//     setCookie("js_theme_selection_cookie", theme_selection, 3);
// }
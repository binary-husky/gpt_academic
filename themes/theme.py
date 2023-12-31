import pickle
import base64
import uuid
from toolbox import get_conf

"""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第 1 部分
加载主题相关的工具函数
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""


def load_dynamic_theme(THEME):
    adjust_dynamic_theme = None
    if THEME == "Chuanhu-Small-and-Beautiful":
        from .green import adjust_theme, advanced_css

        theme_declaration = (
            '<h2 align="center"  class="small">[Chuanhu-Small-and-Beautiful主题]</h2>'
        )
    elif THEME == "High-Contrast":
        from .contrast import adjust_theme, advanced_css

        theme_declaration = ""
    elif "/" in THEME:
        from .gradios import adjust_theme, advanced_css
        from .gradios import dynamic_set_theme

        adjust_dynamic_theme = dynamic_set_theme(THEME)
        theme_declaration = ""
    else:
        from .default import adjust_theme, advanced_css

        theme_declaration = ""
    return adjust_theme, advanced_css, theme_declaration, adjust_dynamic_theme


adjust_theme, advanced_css, theme_declaration, _ = load_dynamic_theme(get_conf("THEME"))


"""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第 2 部分
cookie相关工具函数
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""


def init_cookie(cookies, chatbot):
    # 为每一位访问的用户赋予一个独一无二的uuid编码
    cookies.update({"uuid": uuid.uuid4()})
    return cookies


def to_cookie_str(d):
    # Pickle the dictionary and encode it as a string
    pickled_dict = pickle.dumps(d)
    cookie_value = base64.b64encode(pickled_dict).decode("utf-8")
    return cookie_value


def from_cookie_str(c):
    # Decode the base64-encoded string and unpickle it into a dictionary
    pickled_dict = base64.b64decode(c.encode("utf-8"))
    return pickle.loads(pickled_dict)


"""
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
第 3 部分
内嵌的javascript代码
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""

js_code_for_css_changing = """(css) => {
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
    var styleElement = document.createElement('style');
    styleElement.setAttribute('data-loaded-css', 'placeholder');
    styleElement.innerHTML = css;
    document.body.appendChild(styleElement);
}
"""

js_code_for_darkmode_init = """(dark) => {
    dark = dark == "True";
    if (document.querySelectorAll('.dark').length) {
        if (!dark){
            document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
        }
    } else {
        if (dark){
            document.querySelector('body').classList.add('dark');
        }
    }
}
"""

js_code_for_toggle_darkmode = """() => {
    if (document.querySelectorAll('.dark').length) {
        document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
    } else {
        document.querySelector('body').classList.add('dark');
    }
}"""


js_code_for_persistent_cookie_init = """(persistent_cookie) => {
    return getCookie("persistent_cookie");
}
"""

from toolbox import get_conf
CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT")

def get_common_html_javascript_code():
    js = "\n"
    for jsf in [
        "file=themes/common.js",
        "file=themes/mermaid.min.js",
        "file=themes/mermaid_loader.js",
    ]:
        js += f"""<script src="{jsf}"></script>\n"""

    # 添加Live2D
    if ADD_WAIFU:
        for jsf in [
            "file=docs/waifu_plugin/jquery.min.js",
            "file=docs/waifu_plugin/jquery-ui.min.js",
            "file=docs/waifu_plugin/autoload.js",
        ]:
            js += f"""<script src="{jsf}"></script>\n"""
    return js
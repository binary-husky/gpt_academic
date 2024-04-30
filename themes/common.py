from toolbox import get_conf
CODE_HIGHLIGHT, ADD_WAIFU, LAYOUT = get_conf("CODE_HIGHLIGHT", "ADD_WAIFU", "LAYOUT")

def minimize_js(common_js_path):
    try:
        import rjsmin, hashlib, glob, os
        # clean up old minimized js files, matching `common_js_path + '.min.*'`
        for old_min_js in glob.glob(common_js_path + '.min.*.js'):
            os.remove(old_min_js)
        # use rjsmin to minimize `common_js_path`
        c_jsmin = rjsmin.jsmin
        with open(common_js_path, "r") as f:
            js_content = f.read()
        minimized_js_content = c_jsmin(js_content)
        # compute sha256 hash of minimized js content
        sha_hash = hashlib.sha256(minimized_js_content.encode()).hexdigest()[:8]
        minimized_js_path = common_js_path + '.min.' + sha_hash + '.js'
        # save to minimized js file
        with open(minimized_js_path, "w") as f:
            f.write(minimized_js_content)
        # return minimized js file path
        return minimized_js_path
    except:
        return common_js_path

def get_common_html_javascript_code():
    js = "\n"
    common_js_path = "themes/common.js"
    minimized_js_path = minimize_js(common_js_path)
    for jsf in [
        f"file={minimized_js_path}",
    ]:
        js += f"""<script src="{jsf}"></script>\n"""

    # 添加Live2D
    if ADD_WAIFU:
        for jsf in [
            "file=themes/waifu_plugin/jquery.min.js",
            "file=themes/waifu_plugin/jquery-ui.min.js",
        ]:
            js += f"""<script src="{jsf}"></script>\n"""
    else:
        js += """<script>window.loadLive2D = function(){};</script>\n"""
    return js

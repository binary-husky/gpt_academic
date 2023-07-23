from toolbox import CatchException, update_ui, gen_time_str
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from .crazy_utils import input_clipping

def inspect_dependency(chatbot, history):
    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        from VISUALIZE.mcom import mcom
        return True
    except:
        chatbot.append(["导入依赖失败", "使用该模块需要额外依赖，安装方法:```pip install vhmap```"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return False

def get_code_block(reply):
    try:
        import json
        json.loads(reply)
        return reply
    except:
        pass

    import re
    pattern = r"```([\s\S]*?)```" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    res = ""
    for match in matches:
        if 'import ' not in match:
            res = match.strip('python').strip('json')
            break
    if len(res) == 0:
        print(reply)
        raise RuntimeError("GPT is not generating proper Json.")
    return res  #  code block

def get_json_blocks(reply):
    import re, json
    pattern = r"{([\s\S]*?)}" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    res = []
    for match in matches:
        if '"name"' in match:
            try:
                res.append(json.loads("{" + f'{match}' + "}"))
            except:
                pass
    return res  #  code block

def read_json(code):
    import json
    return json.loads(code)
     
def parse_partial(vi, gpt_say):
    # 解析Json
    js = get_json_blocks(gpt_say)
    vi.update(js)


@CatchException
def 三维生成(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    from .vhmap_interact.vhmap import vhmp_interface
    vi = vhmp_interface()
    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "生成3D, 此插件处于开发阶段, 建议暂时不要使用, 作者: binary-husky, 插件初始化中 ..."
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖, 如果缺少依赖, 则给出安装建议
    dep_ok = yield from inspect_dependency(chatbot=chatbot, history=history) # 刷新界面
    if not dep_ok: return
    
    # 输入
    i_say = prompt(txt)
    # 开始
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=i_say, inputs_show_user=i_say, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=r"You are a Json generator",
        on_reply_update=lambda t:parse_partial(vi, t)
    )
    chatbot.append(["开始生成执行", "..."])
    history.extend([i_say, gpt_say])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新
    
    # 解析Json
    code = get_code_block(gpt_say)
    js = read_json(code)
    vi.update(js)
    return


def prompt(text):
    return r"""
> Requirements:
    1. You can only use square Boxes to build cubes and walls.
    2. The space you can work in is a sphere with origin (0,0,0) and radius 100.
    3. The ground is z=0.
    4. You can only use 100 boxes.
    5. Format of each box is json, e.g.
    {
        "name": "Box-1",
        "geometry": "box", // choose from "box", "octahedron", "sphere", "cylinder"
        "size": 1.0,
        "color": "rgb(255,165,0)",
        "location_x": 1.0,
        "location_y": 0.0,
        "location_z": 0.0
    },
    6. Only produce json as output. Use markdown code block to wrap the json output.

> Example:
    User: Generate 4 different objects around the origin.
    You:
    ```
    [
        {
            "name": "Box-1",
            "size": 1.0,
            "geometry": "box",
            "color": "rgb(255,11,10)",
            "location_x": 1.0,
            "location_y": 0.0,
            "location_z": 0.0
        },
        {
            "name": "Box-2",
            "size": 1.0,
            "geometry": "octahedron",
            "color": "rgb(255,11,10)",
            "location_x": -1.0,
            "location_y": 0.0,
            "location_z": 0.0
        },
        {
            "name": "Box-3",
            "size": 1.0,
            "geometry": "sphere",
            "color": "rgb(255,11,10)",
            "location_x": 0.0,
            "location_y": 1.0,
            "location_z": 0.0
        },
        {
            "name": "Box-4",
            "size": 1.0,
            "geometry": "cylinder",
            "color": "rgb(255,11,10)",
            "location_x": 0.0,
            "location_y": -1.0,
            "location_z": 0.0
        }
    ]
    ```

> User: """ + text

"""
Please construct a 3D environment where a girl is sitting under a tree in a garden.

Requirements:
1. List objects in this scene and make a markdown list.
2. The list must contain creative details, give at least 20 objects
"""


"""
Convert the result to json, 
Requirements:
1. Format: [
    {
        "name": "object-1",
        "location": [position_x, position_y, position_z]
    }
]
2. Generate relative position of objects
"""



"""
> Requirements:
    1. You can use box, octahedron, sphere, cylinder to build objects.
    2. The ground is z=0.
    3. You can only use 100 boxes.
    4. Format of each box is json, e.g.
    {
        "name": "Box-1",
        "geometry": "box", // choose from "box", "octahedron", "sphere", "cylinder"
        "size": 1.0,
        "color": "rgb(255,165,0)",
        "location_x": 1.0,
        "location_y": 0.0,
        "location_z": 0.0
    },
    5. Only produce json as output. Use markdown code block to wrap the json output.

> Example:
    ```
    [
        {
            "name": "Box-1",
            "size": 1.0,
            "geometry": "box",
            "color": "rgb(255,11,10)",
            "location_x": 1.0,
            "location_y": 0.0,
            "location_z": 0.0
        },
        {
            "name": "Box-2",
            "size": 1.0,
            "geometry": "octahedron",
            "color": "rgb(255,11,10)",
            "location_x": -1.0,
            "location_y": 0.0,
            "location_z": 0.0
        },
        {
            "name": "Box-3",
            "size": 1.0,
            "geometry": "sphere",
            "color": "rgb(255,11,10)",
            "location_x": 0.0,
            "location_y": 1.0,
            "location_z": 0.0
        },
        {
            "name": "Box-4",
            "size": 1.0,
            "geometry": "cylinder",
            "color": "rgb(255,11,10)",
            "location_x": 0.0,
            "location_y": -1.0,
            "location_z": 0.0
        }
    ]
    ```
"""
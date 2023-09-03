from toolbox import CatchException, update_ui, get_conf, select_api_key
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import datetime


def gen_image(llm_kwargs, prompt, resolution="256x256"):
    import requests, json, time, os
    from request_llm.bridge_all import model_info

    proxies, = get_conf('proxies')
    # Set up OpenAI API key and model 
    api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
    chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
    # 'https://api.openai.com/v1/chat/completions'
    img_endpoint = chat_endpoint.replace('chat/completions','images/generations')
    # # Generate the image
    url = img_endpoint
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        'n': 1,
        'size': resolution,
        'response_format': 'url'
    }
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    print(response.content)

    try:
        image_url = json.loads(response.content.decode('utf8'))['data'][0]['url']
    except:
        raise RuntimeError(response.content.decode())

    # 文件保存到本地
    r = requests.get(image_url, proxies=proxies)
    file_path = 'gpt_log/image_gen/'
    os.makedirs(file_path, exist_ok=True)
    file_name = 'Image' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.png'
    with open(file_path + file_name, 'wb+') as f:
        f.write(r.content)
    return image_url, file_path + file_name




@CatchException
def 图片生成(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 生成图像, 请先把模型切换至gpt-xxxx或者api2d-xxxx。如果中文效果不理想, 尝试Prompt。正在处理中 ....."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    resolution = plugin_kwargs.get("advanced_arg", '256x256')
    image_url, image_path = gen_image(llm_kwargs, prompt, resolution)
    chatbot.append([prompt,  
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

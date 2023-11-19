from toolbox import CatchException, update_ui, get_conf, select_api_key, get_log_folder
from crazy_functions.multi_stage.multi_stage_utils import GptAcademicState


def gen_image(llm_kwargs, prompt, resolution="1024x1024", model="dall-e-2", quality=None):
    import requests, json, time, os
    from request_llms.bridge_all import model_info

    proxies = get_conf('proxies')
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
        'model': model,
        'response_format': 'url'
    }
    if quality is not None: data.update({'quality': quality})
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    print(response.content)
    try:
        image_url = json.loads(response.content.decode('utf8'))['data'][0]['url']
    except:
        raise RuntimeError(response.content.decode())
    # 文件保存到本地
    r = requests.get(image_url, proxies=proxies)
    file_path = f'{get_log_folder()}/image_gen/'
    os.makedirs(file_path, exist_ok=True)
    file_name = 'Image' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.png'
    with open(file_path+file_name, 'wb+') as f: f.write(r.content)


    return image_url, file_path+file_name


def edit_image(llm_kwargs, prompt, image_path, resolution="1024x1024", model="dall-e-2"):
    import requests, json, time, os
    from request_llms.bridge_all import model_info

    proxies = get_conf('proxies')
    api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
    chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
    # 'https://api.openai.com/v1/chat/completions'
    img_endpoint = chat_endpoint.replace('chat/completions','images/edits')
    # # Generate the image
    url = img_endpoint
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    data = {
        'image': open(image_path, 'rb'),
        'prompt': prompt,
        'n': 1,
        'size': resolution,
        'model': model,
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
    file_path = f'{get_log_folder()}/image_gen/'
    os.makedirs(file_path, exist_ok=True)
    file_name = 'Image' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.png'
    with open(file_path+file_name, 'wb+') as f: f.write(r.content)


    return image_url, file_path+file_name


@CatchException
def 图片生成_DALLE2(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本,例如需要翻译的一段话,再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数,如温度和top_p等,一般原样传递下去就行
    plugin_kwargs   插件模型的参数,暂时没有用武之地
    chatbot         聊天显示框的句柄,用于显示给用户
    history         聊天历史,前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史,以免输入溢出
    chatbot.append(("您正在调用“图像生成”插件。", "[Local Message] 生成图像, 请先把模型切换至gpt-*或者api2d-*。如果中文Prompt效果不理想, 请尝试英文Prompt。正在处理中 ....."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 由于请求gpt需要一段时间,我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    resolution = plugin_kwargs.get("advanced_arg", '1024x1024')
    image_url, image_path = gen_image(llm_kwargs, prompt, resolution)
    chatbot.append([prompt,  
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 界面更新


@CatchException
def 图片生成_DALLE3(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    history = []    # 清空历史,以免输入溢出
    chatbot.append(("您正在调用“图像生成”插件。", "[Local Message] 生成图像, 请先把模型切换至gpt-*或者api2d-*。如果中文Prompt效果不理想, 请尝试英文Prompt。正在处理中 ....."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 由于请求gpt需要一段时间,我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    resolution = plugin_kwargs.get("advanced_arg", '1024x1024').lower()
    if resolution.endswith('-hd'):
        resolution = resolution.replace('-hd', '')
        quality = 'hd'
    else:
        quality = 'standard'
    image_url, image_path = gen_image(llm_kwargs, prompt, resolution, model="dall-e-3", quality=quality)
    chatbot.append([prompt,  
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 界面更新

class ImageEditState(GptAcademicState):
    # 尚未完成
    def get_image_file(self, x):
        import os, glob
        if len(x) == 0:             return False, None
        if not os.path.exists(x):   return False, None
        if x.endswith('.png'):      return True, x
        file_manifest = [f for f in glob.glob(f'{x}/**/*.png', recursive=True)]
        confirm = (len(file_manifest) >= 1 and file_manifest[0].endswith('.png') and os.path.exists(file_manifest[0]))
        file = None if not confirm else file_manifest[0]
        return confirm, file
    
    def get_resolution(self, x):
        return (x in ['256x256', '512x512', '1024x1024']), x
    
    def get_prompt(self, x):
        confirm = (len(x)>=5) and (not self.get_resolution(x)[0]) and (not self.get_image_file(x)[0])
        return confirm, x
    
    def reset(self):
        self.req = [
            {'value':None, 'description': '请先上传图像（必须是.png格式）, 然后再次点击本插件',    'verify_fn': self.get_image_file},
            {'value':None, 'description': '请输入分辨率,可选：256x256, 512x512 或 1024x1024',   'verify_fn': self.get_resolution},
            {'value':None, 'description': '请输入修改需求,建议您使用英文提示词',                 'verify_fn': self.get_prompt},
        ]
        self.info = ""

    def feed(self, prompt, chatbot):
        for r in self.req:
            if r['value'] is None:
                confirm, res = r['verify_fn'](prompt)
                if confirm:
                    r['value'] = res
                    self.set_state(chatbot, 'dummy_key', 'dummy_value')
                    break
        return self

    def next_req(self):
        for r in self.req:
            if r['value'] is None:
                return r['description']
        return "已经收集到所有信息"

    def already_obtained_all_materials(self):
        return all([x['value'] is not None for x in self.req])

@CatchException
def 图片修改_DALLE2(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # 尚未完成
    history = []    # 清空历史
    state = ImageEditState.get_state(chatbot, ImageEditState)
    state = state.feed(prompt, chatbot)
    if not state.already_obtained_all_materials():
        chatbot.append(["图片修改（先上传图片,再输入修改需求,最后输入分辨率）", state.next_req()])
        yield from update_ui(chatbot=chatbot, history=history)
        return

    image_path = state.req[0]
    resolution = state.req[1]
    prompt = state.req[2]
    chatbot.append(["图片修改, 执行中", f"图片:`{image_path}`<br/>分辨率:`{resolution}`<br/>修改需求:`{prompt}`"])
    yield from update_ui(chatbot=chatbot, history=history)

    image_url, image_path = edit_image(llm_kwargs, prompt, image_path, resolution)
    chatbot.append([state.prompt,  
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 界面更新


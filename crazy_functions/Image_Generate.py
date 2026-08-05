import requests
import base64
import json
import time
import os
from request_llms.bridge_chatgpt import make_multimodal_input
from toolbox import CatchException, have_any_recent_upload_image_files, update_ui, get_conf, select_api_key, get_log_folder, update_ui_latest_msg
from crazy_functions.multi_stage.multi_stage_utils import GptAcademicState
from loguru import logger

def gen_image(llm_kwargs, prompt, resolution="1024x1024", model="dall-e-2", quality=None, style=None):
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
    if quality is not None:
        data['quality'] = quality
    if style is not None:
        data['style'] = style
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    # logger.info(response.content)
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
    from request_llms.bridge_all import model_info

    proxies = get_conf('proxies')
    api_key = select_api_key(llm_kwargs['api_key'], llm_kwargs['llm_model'])
    chat_endpoint = model_info[llm_kwargs['llm_model']]['endpoint']
    # 'https://api.openai.com/v1/chat/completions'
    img_endpoint = chat_endpoint.replace('chat/completions','images/edits')
    # # Generate the image
    url = img_endpoint
    n = 1
    headers = {
        'Authorization': f"Bearer {api_key}",
    }
    make_transparent(image_path, image_path+'.tsp.png')
    make_square_image(image_path+'.tsp.png', image_path+'.tspsq.png')
    resize_image(image_path+'.tspsq.png', image_path+'.ready.png', max_size=1024)
    image_path = image_path+'.ready.png'
    with open(image_path, 'rb') as f:
        file_content = f.read()
        files = {
            'image': (os.path.basename(image_path), file_content),
            # 'mask': ('mask.png', open('mask.png', 'rb'))
            'prompt':   (None, prompt),
            "n":        (None, str(n)),
            'size':     (None, resolution),
        }

    response = requests.post(url, headers=headers, files=files, proxies=proxies)
    # logger.info(response.content)
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
def 图片生成_DALLE2(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    """
    txt             输入栏用户输入的文本,例如需要翻译的一段话,再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数,如温度和top_p等,一般原样传递下去就行
    plugin_kwargs   插件模型的参数,暂时没有用武之地
    chatbot         聊天显示框的句柄,用于显示给用户
    history         聊天历史,前情提要
    system_prompt   给gpt的静默提醒
    user_request    当前用户的请求信息（IP地址等）
    """
    history = []    # 清空历史,以免输入溢出
    if prompt.strip() == "":
        chatbot.append((prompt, "[Local Message] 图像生成提示为空白，请在“输入区”输入图像生成提示。"))
        yield from update_ui(chatbot=chatbot, history=history)
        return
    chatbot.append(("您正在调用“图像生成”插件。", "[Local Message] 生成图像, 使用前请切换模型到GPT系列。如果中文Prompt效果不理想, 请尝试英文Prompt。正在处理中 ....."))
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
    yield from update_ui(chatbot=chatbot, history=history)


@CatchException
def 图片生成_DALLE3(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    history = []    # 清空历史,以免输入溢出
    if prompt.strip() == "":
        chatbot.append((prompt, "[Local Message] 图像生成提示为空白，请在“输入区”输入图像生成提示。"))
        yield from update_ui(chatbot=chatbot, history=history)
        return
    chatbot.append(("您正在调用“图像生成”插件。", "[Local Message] 生成图像, 使用前请切换模型到GPT系列。如果中文Prompt效果不理想, 请尝试英文Prompt。正在处理中 ....."))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 由于请求gpt需要一段时间,我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    resolution_arg = plugin_kwargs.get("advanced_arg", '1024x1024-standard-vivid').lower()
    parts = resolution_arg.split('-')
    resolution = parts[0] # 解析分辨率
    quality = 'standard' # 质量与风格默认值
    style = 'vivid'
    # 遍历检查是否有额外参数
    for part in parts[1:]:
        if part in ['hd', 'standard']:
            quality = part
        elif part in ['vivid', 'natural']:
            style = part
    image_url, image_path = gen_image(llm_kwargs, prompt, resolution, model="dall-e-3", quality=quality, style=style)
    chatbot.append([prompt,
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history)



def gen_image_banana(chatbot, history, text_prompt, image_base64_list=None, resolution="1K", aspectRatio="1:1", model="nano-banana"):
    """
    Generate image using Nano-banana API (optimized DALL-E format API)

    Args:
        text_prompt: Text description for image generation
        image_base64_list: List of base64 encoded images or URLs (optional, for image-to-image)
        resolution: Image size, one of: "1K", "2K", "4K" (default: "1K")
        aspectRatio: Aspect ratio like "1:1", "16:9", "3:4", "4:3", "9:16", "2:3", "3:2", "4:5", "5:4", "21:9" (default: "1:1")
        model: Model name, "nano-banana" or "nano-banana-hd" for 4K quality (default: "nano-banana")

    Returns:
        tuple: (image_url, local_file_path)
    """


    proxies = get_conf('proxies')

    # Get API configuration
    if not get_conf('REROUTE_ALL_TO_ONE_API'):
        api_key = get_conf('GEMINI_API_KEY')
        # Default to a generic endpoint if not using ONE_API
        base_url = get_conf('GEMINI_BASE_URL') if get_conf('GEMINI_BASE_URL') else "https://api.example.com"
        if base_url.endswith('/v1'):
            base_url = base_url[:-3]
        url = base_url + "/v1/images/generations"
        download_image_proxies = proxies
    else:
        url = get_conf('ONE_API_URL')
        api_key = get_conf('ONE_API_KEY')
        if api_key == '$API_KEY':
            api_key = get_conf('API_KEY')
        download_image_proxies = proxies
        proxies = None

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Make API request

    try:
        payload = {
            "model": "google/gemini-3-pro-image-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text_prompt
                        },
                    ]
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {
                "aspect_ratio": aspectRatio,
                "image_size": resolution
            }
        }

        for image_base64 in image_base64_list:
            # {
            #     "type": "image_url",
            #     "image_url": {
            #         "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            #     }
            # }
            # img = f"data:image/jpeg;base64,{base64_image}"

            payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })


        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        image_url = None
        generated_content = ""
        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images"):
                generated_content = message.get('reasoning', "") + message.get('content', "")
                for image in message["images"]:
                    image_url = image["image_url"]["url"]
                    print(f"Generated image: {image_url[:50]}...")


        if response.status_code != 200:
            yield from update_ui_latest_msg(lastmsg=f"Generate Failed\n\n{generated_content}\n\nStatus Code: {response.status_code}", chatbot=chatbot, history=history, delay=0)
            return

        if image_url is None:
            raise RuntimeError("No image URL found in the response.")

        logger.info(f'Generated image.')
        yield from update_ui_latest_msg(lastmsg=f"Downloading image", chatbot=chatbot, history=history, delay=0)

        if ';base64,' in image_url:
            base64_string = image_url.split('base64,')[-1]
            image_data = base64.b64decode(base64_string)
            file_path = f'{get_log_folder()}/image_gen/'
            os.makedirs(file_path, exist_ok=True)
            file_name = 'Image' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.png'
            fp = file_path+file_name
            with open(fp, 'wb+') as f: f.write(image_data)
        else:
            raise ValueError("Invalid image URL format.")

        return image_url, fp

    except Exception as e:
        yield from update_ui_latest_msg(lastmsg=f"Generate failed, please try again later.", chatbot=chatbot, history=history, delay=0)
        raise RuntimeError(f"Failed to generate image, please try again later: {str(e)}")









@CatchException
def 图片生成_NanoBanana(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    history = []    # 清空历史,以免输入溢出

    if prompt.strip() == "":
        chatbot.append((prompt, "[Local Message] 图像生成提示为空白"))
        yield from update_ui(chatbot=chatbot, history=history)
        return
    chatbot.append((
        prompt,
        "正在调用 NanoBanana 图像生成, 正在处理中 ....."
    ))

    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 由于请求gpt需要一段时间,我们先及时地做一次界面更新
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")

    model = "nano-banana"
    resolution = plugin_kwargs["resolution"]
    aspectRatio = plugin_kwargs["aspect ratio"]

    # Validate aspect ratio
    valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2", "4:5", "5:4", "21:9"]
    if aspectRatio not in valid_ratios:
        aspectRatio = "1:1"

    try:
        # get image from recent upload
        has_recent_image_upload, image_paths = have_any_recent_upload_image_files(chatbot, pop=True)
        if has_recent_image_upload:
            _, image_base64_array = make_multimodal_input(prompt, image_paths)
        else:
            _, image_base64_array = prompt, []

        # get image from session storage
        if 'session_file_storage' in chatbot._cookies:
            try:
                image_base64_array += [base64.b64encode(open(chatbot._cookies['session_file_storage'], 'rb').read()).decode('utf-8')]
            except:
                logger.exception("Failed to read session_file_storage and parse to image base64.")

        # only keep last image if any
        if len(image_base64_array) > 1:
            image_base64_array = [image_base64_array[-1]]

        # Generate image
        _, image_path = yield from gen_image_banana(chatbot, history, prompt, image_base64_list=image_base64_array, resolution=resolution, aspectRatio=aspectRatio, model=model)

        # Build response message
        response_msg = f'模型: {model}<br/>分辨率: {resolution}<br/>比例: {aspectRatio}<br/><br/>'
        response_msg += f'本地文件地址: <br/>`{image_path}`<br/>'
        response_msg += f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'

        # register image
        chatbot._cookies['session_file_storage'] = image_path

        yield from update_ui_latest_msg(lastmsg=response_msg, chatbot=chatbot, history=history, delay=0)

    except Exception as e:
        chatbot.append([prompt, f'生成图像失败: {str(e)}'])

    yield from update_ui(chatbot=chatbot, history=history)



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

    def lock_plugin(self, chatbot):
        chatbot._cookies['lock_plugin'] = 'crazy_functions.Image_Generate->图片修改_DALLE2'
        self.dump_state(chatbot)

    def unlock_plugin(self, chatbot):
        self.reset()
        chatbot._cookies['lock_plugin'] = None
        self.dump_state(chatbot)

    def get_resolution(self, x):
        return (x in ['256x256', '512x512', '1024x1024']), x

    def get_prompt(self, x):
        confirm = (len(x)>=5) and (not self.get_resolution(x)[0]) and (not self.get_image_file(x)[0])
        return confirm, x

    def reset(self):
        self.req = [
            {'value':None, 'description': '请先上传图像（必须是.png格式）, 然后再次点击本插件',                      'verify_fn': self.get_image_file},
            {'value':None, 'description': '请输入分辨率,可选：256x256, 512x512 或 1024x1024, 然后再次点击本插件',   'verify_fn': self.get_resolution},
            {'value':None, 'description': '请输入修改需求,建议您使用英文提示词, 然后再次点击本插件',                 'verify_fn': self.get_prompt},
        ]
        self.info = ""

    def feed(self, prompt, chatbot):
        for r in self.req:
            if r['value'] is None:
                confirm, res = r['verify_fn'](prompt)
                if confirm:
                    r['value'] = res
                    self.dump_state(chatbot)
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
def 图片修改_DALLE2(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    # 尚未完成
    history = []    # 清空历史
    state = ImageEditState.get_state(chatbot, ImageEditState)
    state = state.feed(prompt, chatbot)
    state.lock_plugin(chatbot)
    if not state.already_obtained_all_materials():
        chatbot.append(["图片修改\n\n1. 上传图片（图片中需要修改的位置用橡皮擦擦除为纯白色，即RGB=255,255,255）\n2. 输入分辨率 \n3. 输入修改需求", state.next_req()])
        yield from update_ui(chatbot=chatbot, history=history)
        return

    image_path = state.req[0]['value']
    resolution = state.req[1]['value']
    prompt = state.req[2]['value']
    chatbot.append(["图片修改, 执行中", f"图片:`{image_path}`<br/>分辨率:`{resolution}`<br/>修改需求:`{prompt}`"])
    yield from update_ui(chatbot=chatbot, history=history)
    image_url, image_path = edit_image(llm_kwargs, prompt, image_path, resolution)
    chatbot.append([prompt,
        f'图像中转网址: <br/>`{image_url}`<br/>'+
        f'中转网址预览: <br/><div align="center"><img src="{image_url}"></div>'
        f'本地文件地址: <br/>`{image_path}`<br/>'+
        f'本地文件预览: <br/><div align="center"><img src="file={image_path}"></div>'
    ])
    yield from update_ui(chatbot=chatbot, history=history)
    state.unlock_plugin(chatbot)

def make_transparent(input_image_path, output_image_path):
    from PIL import Image
    image = Image.open(input_image_path)
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    image.save(output_image_path, "PNG")

def resize_image(input_path, output_path, max_size=1024):
    from PIL import Image
    with Image.open(input_path) as img:
        width, height = img.size
        if width > max_size or height > max_size:
            if width >= height:
                new_width = max_size
                new_height = int((max_size / width) * height)
            else:
                new_height = max_size
                new_width = int((max_size / height) * width)

            resized_img = img.resize(size=(new_width, new_height))
            resized_img.save(output_path)
        else:
            img.save(output_path)

def make_square_image(input_path, output_path):
    from PIL import Image
    with Image.open(input_path) as img:
        width, height = img.size
        size = max(width, height)
        new_img = Image.new("RGBA", (size, size), color="black")
        new_img.paste(img, ((size - width) // 2, (size - height) // 2))
        new_img.save(output_path)

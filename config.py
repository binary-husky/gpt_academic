import os
from typing import List
from pydantic import BaseModel

"""
    以下所有配置也都支持利用环境变量覆写，环境变量配置格式见docker-compose.yml。
    读取优先级：环境变量 > config_private.py > config.py
    --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    All the following configurations also support using environment variables to override,
    and the environment variable configuration format can be seen in docker-compose.yml.
    Configuration reading priority: environment variable > config_private.py > config.py
"""

# [step 1]>> API_KEY = "sk-123456789xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx123456789"。极少数情况下，还需要填写组织（格式如org-123456789abcdefghijklmno的），请向下翻，找 API_ORG 设置项
API_KEY = "此处填API密钥"  # 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey3,azure-apikey4"

# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改；如果使用本地或无地域限制的大模型时，此处也不需要修改
USE_PROXY = False
if USE_PROXY:
    """
    代理网络的地址，打开你的代理软件查看代理协议(socks5h / http)、地址(localhost)和端口(11284)
    填写格式是 [协议]://  [地址] :[端口]，填写之前不要忘记把USE_PROXY改成True，如果直接在海外服务器部署，此处不修改
            <配置教程&视频教程> https://github.com/binary-husky/gpt_academic/issues/1>
    [协议] 常见协议无非socks5h/http; 例如 v2**y 和 ss* 的默认本地协议是socks5h; 而cl**h 的默认本地协议是http
    [地址] 填localhost或者127.0.0.1（localhost意思是代理软件安装在本机上）
    [端口] 在代理软件的设置里找。虽然不同的代理软件界面不一样，但端口号都应该在最显眼的位置上
    """
    proxies = {
        #          [协议]://  [地址]  :[端口]
        "http": "socks5h://localhost:11284",  # 再例如  "http":  "http://127.0.0.1:7890",
        "https": "socks5h://localhost:11284",  # 再例如  "https": "http://127.0.0.1:7890",
    }
else:
    proxies = None

# [step 3]>> 模型选择是 (注意: LLM_MODEL是默认选中的模型, 它*必须*被包含在AVAIL_LLM_MODELS列表中 )
LLM_MODEL = "gpt-3.5-turbo-16k" # 可选 ↓↓↓
AVAIL_LLM_MODELS = ["gpt-4-1106-preview", "gpt-4-turbo-preview", "gpt-4-vision-preview", "gpt-4-turbo", "gpt-4-turbo-2024-04-09",
                    "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo", "azure-gpt-3.5",
                    "gpt-4", "gpt-4-32k", "azure-gpt-4", "glm-4", "glm-3-turbo",
                    "gemini-pro", "chatglm3"
                    ]
# --- --- --- ---
# P.S. 其他可用的模型还包括
# AVAIL_LLM_MODELS = [
#   "qianfan", "deepseekcoder",
#   "spark", "sparkv2", "sparkv3", "sparkv3.5",
#   "qwen-turbo", "qwen-plus", "qwen-max", "qwen-local",
#   "moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k",
#   "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0125"
#   "claude-3-haiku-20240307","claude-3-sonnet-20240229","claude-3-opus-20240229", "claude-2.1", "claude-instant-1.2",
#   "moss", "llama2", "chatglm_onnx", "internlm", "jittorllms_pangualpha", "jittorllms_llama",
#   "yi-34b-chat-0205", "yi-34b-chat-200k"
# ]
# --- --- --- ---
# 此外，为了更灵活地接入one-api多模型管理界面，您还可以在接入one-api时，
# 使用"one-api-*"前缀直接使用非标准方式接入的模型，例如
# AVAIL_LLM_MODELS = ["one-api-claude-3-sonnet-20240229(max_token=100000)"]
# --- --- --- ---
# GPTS默认分类，为空则默认使用系统推荐
GPTS_DEFAULT_CLASSIFICATION = []

# --------------- 以下配置可以优化体验 ---------------

# 重新URL重新定向，实现更换API_URL的作用（高危设置! 常规情况下不要修改! 通过修改此设置，您将把您的API-KEY和对话隐私完全暴露给您设定的中间人！）
# 格式: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "在这里填写重定向的api.openai.com的URL"}
# 举例: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "https://reverse-proxy-url/v1/chat/completions"}
API_URL_REDIRECT = {}

# 多线程函数插件中，默认允许多少路线程同时访问OpenAI。Free trial users的限制是每分钟3次，Pay-as-you-go users的限制是每分钟3500次
# 一言以蔽之：免费（5刀）用户填3，OpenAI绑了信用卡的用户可以填 16 或者更高。提高限制请查询：https://platform.openai.com/docs/guides/rate-limits/overview
DEFAULT_WORKER_NUM = 3

# prompt 的开放选项,
preset_prompt = {'key': ['所有', '个人'], 'value': '所有'}
# 默认llms调优参数，尽量不要改变顺序, 顺序要和llms_cookies_combo一致
LLM_DEFAULT_PARAMETER = {
    'top_p': 1.0, 'temperature': 1.0, 'n_choices': 1, 'stop': '',
    'presence_penalty': 2.0, 'frequency_penalty': 0, 'user_identifier': "",
    "response_format": 'text',
    'max_context': 2000, 'max_generation': 4096, 'logit_bias': "",
    'system_prompt': '',
}
# 支持的response_format类型
# https://platform.openai.com/docs/api-reference/audio/createTranscription#audio-createtranscription-response_format
RESPONSE_FORMAT = ['text', 'json_object']

# LaTeX 公式渲染策略，可选"default", "strict", "all"或者"disabled"
latex_option = ['all', 'strict', 'default', 'disabled']
# 色彩主题, 可选 ["Default", "Chuanhu-Small-and-Beautiful", "High-Contrast"]
# 更多主题, 请查阅Gradio主题商店: https://huggingface.co/spaces/gradio/theme-gallery 可选 ["Gstaff/Xkcd", "NoCrypt/Miku", ...]
THEME = "Default"
AVAIL_THEMES = ["Chuanhu-Plus", "High-Contrast", "Gstaff/Xkcd", "NoCrypt/Miku"]

# 默认的系统提示词（system prompt）
INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."

# 对话窗的高度 （仅在LAYOUT="TOP-DOWN"时生效）
CHATBOT_HEIGHT = 1115

# 代码高亮
CODE_HIGHLIGHT = True

# 窗口布局
LAYOUT = "LEFT-RIGHT"  # "LEFT-RIGHT"（左右布局） # "TOP-DOWN"（上下布局）

# 暗色模式 / 亮色模式
DARK_MODE = True

# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 30

# 网页的端口, -1代表随机端口
WEB_PORT = -1

# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2

# 插件分类默认选项
DEFAULT_FN_GROUPS = ['云文档', '飞书项目']

# 写入Excel文件是否合并单元格
merge_cell = False

# 定义界面上“询问多个GPT模型”插件应该使用哪些模型，请从AVAIL_LLM_MODELS中选择，并在不同模型之间用`&`间隔，例如"gpt-3.5-turbo&chatglm3&azure-gpt-4"
MULTI_QUERY_LLM_MODELS = "gpt-3.5-turbo&chatglm3"

# 选择本地模型变体（只有当AVAIL_LLM_MODELS包含了对应本地模型时，才会起作用）
# 如果你选择Qwen系列的模型，那么请在下面的QWEN_MODEL_SELECTION中指定具体的模型
# 也可以是具体的模型路径
QWEN_LOCAL_MODEL_SELECTION = "Qwen/Qwen-1_8B-Chat-Int8"

# 接入通义千问在线大模型 https://dashscope.console.aliyun.com/
DASHSCOPE_API_KEY = ""  # 阿里灵积云API_KEY

# 百度千帆（LLM_MODEL="qianfan"）
BAIDU_CLOUD_API_KEY = ''
BAIDU_CLOUD_SECRET_KEY = ''
BAIDU_CLOUD_QIANFAN_MODEL = 'ERNIE-Bot'  # 可选 "ERNIE-Bot-4"(文心大模型4.0), "ERNIE-Bot"(文心一言), "ERNIE-Bot-turbo", "BLOOMZ-7B", "Llama-2-70B-Chat", "Llama-2-13B-Chat", "Llama-2-7B-Chat"

# 如果使用ChatGLM2微调模型，请把 LLM_MODEL="chatglmft"，并在此处指定模型路径
CHATGLM_PTUNING_CHECKPOINT = ""  # 例如"/home/hmp/ChatGLM2-6B/ptuning/output/6b-pt-128-1e-2/checkpoint-100"

# 本地LLM模型如ChatGLM的执行方式 CPU/GPU
LOCAL_MODEL_DEVICE = "cpu"  # 可选 "cuda"
LOCAL_MODEL_QUANT = "FP16"  # 默认 "FP16" "INT4" 启用量化INT4版本 "INT8" 启用量化INT8版本

# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = 100

# 是否在提交时自动清空输入框
AUTO_CLEAR_TXT = False

# 加一个live2d装饰
ADD_WAIFU = False

# 设置用户名和密码（不需要修改）（相关功能不稳定，与gradio版本和网络都相关，如果本地使用不建议加这个）
# [("username", "password"), ("username2", "password2"), ...]
AUTHENTICATION = []


# 如果需要在二级路径下运行（常规情况下，不要修改!!）
# （举例 CUSTOM_PATH = "/gpt_academic/"，可以让软件运行在 http://ip:port/gpt_academic/ 下。）
CUSTOM_PATH = "/"

# HTTPS 秘钥和证书（不需要修改）
SSL_KEYFILE = ""
SSL_CERTFILE = ""

# 极少数情况下，openai的官方KEY需要伴随组织编码（格式如org-xxxxxxxxxxxxxxxxxxxxxxxx）使用
API_ORG = ""

# 如果需要使用Slack Claude，使用教程详情见 request_llms/README.md
SLACK_CLAUDE_BOT_ID = ''
SLACK_CLAUDE_USER_TOKEN = ''

# 如果需要使用AZURE（方法一：单个azure模型部署）详情请见额外文档 docs\use_azure.md
AZURE_ENDPOINT = "https://你亲手写的api名称.openai.azure.com/"
AZURE_URL_VERSION = 'openai/deployments/{v}/chat/completions?api-version=2023-05-15'  # {v}作为占位符
AZURE_ENGINE_DICT = {
    'gpt-35-16k': 1024 * 16,
    'gpt-4-32k': 1024 * 32,
    'gpt-4': 1024 * 8
}  # 读 docs\use_azure.md key是你的部署名，value请自行计算模型各自最大Token数，如3.5 = 4096 = 1024 * 4即可


# 如果需要使用AZURE（方法二：多个azure模型部署+动态切换）详情请见额外文档 docs\use_azure.md
AZURE_CFG_ARRAY = {}

# 阿里云实时语音识别 配置难度较高
# 参考 https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md
ENABLE_AUDIO = False
ALIYUN_TOKEN = ""  # 例如 f37f30e0f9934c34a992f6f64f7eba4f
ALIYUN_APPKEY = ""  # 例如 RoPlZrM88DnAFkZK
ALIYUN_ACCESSKEY = ""  # （无需填写）
ALIYUN_SECRET = ""  # （无需填写）

# 接入讯飞星火大模型 https://console.xfyun.cn/services/iat
XFYUN_APPID = "00000000"
XFYUN_API_SECRET = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
XFYUN_API_KEY = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# 接入智谱大模型
ZHIPUAI_API_KEY = ""
ZHIPUAI_MODEL = ""  # 此选项已废弃，不再需要填写

# Claude API 请求地址
ANTHROPIC_ENDPOINT_API = 'https://api.anthropic.com/v1/messages'
# Claude API KEY
ANTHROPIC_API_KEY = ""
# Claude API 重定向 OPENAI OR ONE API
ANTHROPIC_API_URL_REDIRECT = True

# 月之暗面 API KEY
MOONSHOT_API_KEY = ""

# 零一万物(Yi Model) API KEY
YIMODEL_API_KEY = ""

# Mathpix 拥有执行PDF的OCR功能，但是需要注册账号
MATHPIX_APPID = ""
MATHPIX_APPKEY = ""

# Mathpix 拥有执行PDF的OCR功能，但是需要注册账号
DOC2X_API_KEY = ""

# 自定义API KEY格式
CUSTOM_API_KEY_PATTERN = ""

# Google Gemini API-Key
GEMINI_API_KEY = ''

# HUGGINGFACE的TOKEN，下载LLAMA时起作用 https://huggingface.co/docs/hub/security-tokens
HUGGINGFACE_ACCESS_TOKEN = "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"

# GROBID服务器地址（填写多个可以均衡负载），用于高质量地读取PDF文档
# 获取方法：复制以下空间https://huggingface.co/spaces/qingxu98/grobid，设为public，然后GROBID_URL = "https://(你的hf用户名如qingxu98)-(你的填写的空间名如grobid).hf.space"
GROBID_URLS = [
    "https://qingxu98-grobid.hf.space", "https://qingxu98-grobid2.hf.space", "https://qingxu98-grobid3.hf.space",
    "https://qingxu98-grobid4.hf.space", "https://qingxu98-grobid5.hf.space", "https://qingxu98-grobid6.hf.space",
    "https://qingxu98-grobid7.hf.space", "https://qingxu98-grobid8.hf.space",
]

# 是否允许通过自然语言描述修改本页的配置，该功能具有一定的危险性，默认关闭
ALLOW_RESET_CONFIG = False

# 在使用AutoGen插件时，是否使用Docker容器运行代码
AUTOGEN_USE_DOCKER = False

# 临时的上传文件夹位置，请勿修改
PATH_PRIVATE_UPLOAD = "private_upload"

# 日志文件夹的位置，请勿修改
PATH_LOGGING = "gpt_log"

# 除了连接OpenAI之外，还有哪些场合允许使用代理，请勿修改
WHEN_TO_USE_PROXY = ["Download_LLM", "Download_Gradio_Theme", "Connect_Grobid",
                     "Warmup_Modules", "Nougat_Download", "AutoGen"]

# 金山云文档HOST
WPS_BASE_HOST = 'www.kdocs.cn'
# 用以支持金山云文档的cookies
WPS_COOKIES = {}

# qq云文档host
QQ_BASE_HOST = 'docs.qq.com'
# 用以支持QQ云文档的cookies
QQ_COOKIES = {}

# 飞书云文档host
FEISHU_BASE_HOST = 'xxx.feishu.cn'
# 用以支持飞书云文档的请求头+cookies，飞书需要保持cookies与请求头的CORS一致，所以请求头需要带上Cookie一起
FEISHU_HEADER_COOKIE = {}

# TODO 飞书项目的各种配置
# 飞书项目的请求头，带Cookie那种
PROJECT_FEISHU_HEADER = {}
# 飞书项目 host
PROJECT_BASE_HOST = 'project.feishu.cn'
# 飞书项目 user-key
PROJECT_USER_KEY = ''


class WorkItems(BaseModel):
    """
    目前飞书项目支持的工作项类型
    属性名称不能更改，属性value按照项目中的名称填写
    """
    # 工作项名称，不同项目可能存在不同的工作项名称，以下是枚举值，获取的到才会显示
    story_name: List = ['需求', 'APP研发需求']
    issue_name: List = ['缺陷BUG']
    case_name: List = ['测试用例']

    # 关联对象名称，用于查找需求相关的所有关联项
    issue_item_name: List = ['缺陷相关需求']
    case_item_name: List = ['归属需求']


# 飞书项目【需求】展示信息的反向映射列表，填入中文名称，自动查找对应的id
STORY_REVERSE_MAPPING = ['需求名称', '需求文档', '需求描述', '需求状态', '需求描述', '期望上线日期', '技术方案说明',
                         '冒烟次数', '测试计划', '测试报告']
# 飞书项目【获取首页/个人需求】展示信息的反向映射列表，填入中文名称，自动查找对应的id
STORY_LIST_REVERSE_MAPPING = ['需求名称', '需求文档', '需求描述', '需求状态', '期望上线日期', '技术方案说明']
# 飞书项目【获取首页/个人需求】除了开始时间与结束时间，增加时间筛选选项
STORY_LIST_FILTER_TIME = ['期望上线日期']
# 飞书项目【缺陷】展示信息的反向映射列表，填入中文名称，自动查找对应的id
ISSUE_REVERSE_MAPPING = ['缺陷名称', '缺陷描述', 'Bug类型', '严重程度', '发现阶段', '缺陷状态', '原因分析']
# 飞书项目【测试用例】展示信息的反向映射列表，填入中文名称，自动查找对应的id
CASE_REVERSE_MAPPING = ['测试点', '测试用例详情', '归属需求', '标签', '用例分级']

# *实验性功能*: 自动检测并屏蔽失效的KEY，请勿使用
BLOCK_INVALID_APIKEY = False

# 启用插件热加载
PLUGIN_HOT_RELOAD = False

# 自定义按钮的最大数量限制
NUM_CUSTOM_BASIC_BTN = 4


# TODO: App Setup
APPNAME = "Hello GPT"
avatar_images = (os.path.join('docs/assets/chatbot_avatar/logo.png'), os.path.join(
    'docs/assets/chatbot_avatar/user.png'))  # 对话头像
favicon_path = os.path.join('docs/assets/chatbot_avatar/favicon.png')  # 浏览器标签icon
qc_icon_path = os.path.join('docs/assets/chatbot_avatar/logo.png')  # 访问二维码
devs_document = 'https://github.com/Kilig947/Hello-GPT/blob/hello-gpt/README.md'  # 个人开发文档
robot_hook = ''  # 机器人报错通知地址

# TODO: FASTAPI配置
cancel_verification = True  # 是否接入单点登陆验证，True为不进行单点登陆
auth_url = ''  # 鉴权地址
auth_cookie_tag = ''  # cookies关键字
auth_func_based = lambda x: x.get('data').get('username')  # 登陆成功判断依据
routing_address = ''  # APP域名
app_reload = False  # 拉取代码后应用是否自动重启
redirect_address = 'https://xxxx/login'

"""
--------------- 配置关联关系说明 ---------------

在线大模型配置关联关系示意图
│
├── "gpt-3.5-turbo" 等openai模型
│   ├── API_KEY
│   ├── CUSTOM_API_KEY_PATTERN（不常用）
│   ├── API_ORG（不常用）
│   └── API_URL_REDIRECT（不常用）
│
├── "azure-gpt-3.5" 等azure模型（单个azure模型，不需要动态切换）
│   ├── API_KEY
│   ├── AZURE_ENDPOINT
│   ├── AZURE_API_KEY
│   ├── AZURE_ENGINE
│   └── API_URL_REDIRECT
│
├── "azure-gpt-3.5" 等azure模型（多个azure模型，需要动态切换，高优先级）
│   └── AZURE_CFG_ARRAY
│
├── "spark" 星火认知大模型 spark & sparkv2
│   ├── XFYUN_APPID
│   ├── XFYUN_API_SECRET
│   └── XFYUN_API_KEY
│
├── "claude-3-opus-20240229" 等claude模型
│   └── ANTHROPIC_API_KEY
│
├── "stack-claude"
│   ├── SLACK_CLAUDE_BOT_ID
│   └── SLACK_CLAUDE_USER_TOKEN
│
├── "qianfan" 百度千帆大模型库
│   ├── BAIDU_CLOUD_QIANFAN_MODEL
│   ├── BAIDU_CLOUD_API_KEY
│   └── BAIDU_CLOUD_SECRET_KEY
│
├── "glm-4", "glm-3-turbo", "zhipuai" 智谱AI大模型
│   └── ZHIPUAI_API_KEY
│
├── "yi-34b-chat-0205", "yi-34b-chat-200k" 等零一万物(Yi Model)大模型
│   └── YIMODEL_API_KEY
│
├── "qwen-turbo" 等通义千问大模型
│   └──  DASHSCOPE_API_KEY
│
├── "Gemini"
│   └──  GEMINI_API_KEY
│
└── "one-api-...(max_token=...)" 用一种更方便的方式接入one-api多模型管理界面
    ├── AVAIL_LLM_MODELS
    ├── API_KEY
    └── API_URL_REDIRECT


本地大模型示意图
│
├── "chatglm3"
├── "chatglm"
├── "chatglm_onnx"
├── "chatglmft"
├── "internlm"
├── "moss"
├── "jittorllms_pangualpha"
├── "jittorllms_llama"
├── "deepseekcoder"
├── "qwen-local"
├──  RWKV的支持见Wiki
└── "llama2"


用户图形界面布局依赖关系示意图
│
├── CHATBOT_HEIGHT 对话窗的高度
├── CODE_HIGHLIGHT 代码高亮
├── LAYOUT 窗口布局
├── DARK_MODE 暗色模式 / 亮色模式
├── DEFAULT_FN_GROUPS 插件分类默认选项
├── THEME 色彩主题
├── AUTO_CLEAR_TXT 是否在提交时自动清空输入框
├── ADD_WAIFU 加一个live2d装饰
└── ALLOW_RESET_CONFIG 是否允许通过自然语言描述修改本页的配置，该功能具有一定的危险性


插件在线服务配置依赖关系示意图
│
├── 语音功能
│   ├── ENABLE_AUDIO
│   ├── ALIYUN_TOKEN
│   ├── ALIYUN_APPKEY
│   ├── ALIYUN_ACCESSKEY
│   └── ALIYUN_SECRET
│
└── PDF文档精准解析
    ├── GROBID_URLS
    ├── MATHPIX_APPID
    └── MATHPIX_APPKEY


"""

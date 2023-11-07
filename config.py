"""
    以下所有配置也都支持利用环境变量覆写，环境变量配置格式见docker-compose.yml。
    读取优先级：环境变量 > config_private.py > config.py
    --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    All the following configurations also support using environment variables to override, 
    and the environment variable configuration format can be seen in docker-compose.yml. 
    Configuration reading priority: environment variable > config_private.py > config.py
"""

# [step 1]>> API_KEY = "sk-123456789xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx123456789"。极少数情况下，还需要填写组织（格式如org-123456789abcdefghijklmno的），请向下翻，找 API_ORG 设置项
API_KEY = "此处填API密钥"    # 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey3,azure-apikey4"


# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改；如果使用本地或无地域限制的大模型时，此处也不需要修改
USE_PROXY = False
if USE_PROXY:
    """
    填写格式是 [协议]://  [地址] :[端口]，填写之前不要忘记把USE_PROXY改成True，如果直接在海外服务器部署，此处不修改
            <配置教程&视频教程> https://github.com/binary-husky/gpt_academic/issues/1>
    [协议] 常见协议无非socks5h/http; 例如 v2**y 和 ss* 的默认本地协议是socks5h; 而cl**h 的默认本地协议是http
    [地址] 懂的都懂，不懂就填localhost或者127.0.0.1肯定错不了（localhost意思是代理软件安装在本机上）
    [端口] 在代理软件的设置里找。虽然不同的代理软件界面不一样，但端口号都应该在最显眼的位置上
    """
    # 代理网络的地址，打开你的*学*网软件查看代理的协议(socks5h / http)、地址(localhost)和端口(11284)
    proxies = {
        #          [协议]://  [地址]  :[端口]
        "http":  "socks5h://localhost:11284",  # 再例如  "http":  "http://127.0.0.1:7890",
        "https": "socks5h://localhost:11284",  # 再例如  "https": "http://127.0.0.1:7890",
    }
else:
    proxies = None

# ------------------------------------ 以下配置可以优化体验, 但大部分场合下并不需要修改 ------------------------------------

# 重新URL重新定向，实现更换API_URL的作用（高危设置! 常规情况下不要修改! 通过修改此设置，您将把您的API-KEY和对话隐私完全暴露给您设定的中间人！）
# 格式: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "在这里填写重定向的api.openai.com的URL"} 
# 举例: API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "https://reverse-proxy-url/v1/chat/completions"}
API_URL_REDIRECT = {}


# 多线程函数插件中，默认允许多少路线程同时访问OpenAI。Free trial users的限制是每分钟3次，Pay-as-you-go users的限制是每分钟3500次
# 一言以蔽之：免费（5刀）用户填3，OpenAI绑了信用卡的用户可以填 16 或者更高。提高限制请查询：https://platform.openai.com/docs/guides/rate-limits/overview
DEFAULT_WORKER_NUM = 3


# 色彩主题, 可选 ["Default", "Chuanhu-Small-and-Beautiful", "High-Contrast"]
# 更多主题, 请查阅Gradio主题商店: https://huggingface.co/spaces/gradio/theme-gallery 可选 ["Gstaff/Xkcd", "NoCrypt/Miku", ...]
THEME = "Default"
AVAIL_THEMES = ["Default", "Chuanhu-Small-and-Beautiful", "High-Contrast", "Gstaff/Xkcd", "NoCrypt/Miku"]


# 默认的系统提示词（system prompt）
INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."


# 对话窗的高度 （仅在LAYOUT="TOP-DOWN"时生效）
CHATBOT_HEIGHT = 1115


# 代码高亮
CODE_HIGHLIGHT = True


# 窗口布局
LAYOUT = "LEFT-RIGHT"   # "LEFT-RIGHT"（左右布局） # "TOP-DOWN"（上下布局）


# 暗色模式 / 亮色模式
DARK_MODE = True        


# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 30


# 网页的端口, -1代表随机端口
WEB_PORT = -1


# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2


# 插件分类默认选项
DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']


# 模型选择是 (注意: LLM_MODEL是默认选中的模型, 它*必须*被包含在AVAIL_LLM_MODELS列表中 )
LLM_MODEL = "gpt-3.5-turbo" # 可选 ↓↓↓
AVAIL_LLM_MODELS = ["gpt-3.5-turbo-16k", "gpt-3.5-turbo", "azure-gpt-3.5",
                    "api2d-gpt-3.5-turbo", 'api2d-gpt-3.5-turbo-16k', 
                    "gpt-4", "gpt-4-32k", "azure-gpt-4", "api2d-gpt-4", 
                    "chatglm3", "moss", "newbing", "claude-2"]
# P.S. 其他可用的模型还包括 ["zhipuai", "qianfan", "llama2", "qwen", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613",  "gpt-3.5-random"
# "spark", "sparkv2", "sparkv3", "chatglm_onnx", "claude-1-100k", "claude-2", "internlm", "jittorllms_pangualpha", "jittorllms_llama"]


# 定义界面上“询问多个GPT模型”插件应该使用哪些模型，请从AVAIL_LLM_MODELS中选择，并在不同模型之间用`&`间隔，例如"gpt-3.5-turbo&chatglm3&azure-gpt-4"
MULTI_QUERY_LLM_MODELS = "gpt-3.5-turbo&chatglm3"


# 百度千帆（LLM_MODEL="qianfan"）
BAIDU_CLOUD_API_KEY = ''
BAIDU_CLOUD_SECRET_KEY = ''
BAIDU_CLOUD_QIANFAN_MODEL = 'ERNIE-Bot'    # 可选 "ERNIE-Bot-4"(文心大模型4.0), "ERNIE-Bot"(文心一言), "ERNIE-Bot-turbo", "BLOOMZ-7B", "Llama-2-70B-Chat", "Llama-2-13B-Chat", "Llama-2-7B-Chat"


# 如果使用ChatGLM2微调模型，请把 LLM_MODEL="chatglmft"，并在此处指定模型路径
CHATGLM_PTUNING_CHECKPOINT = "" # 例如"/home/hmp/ChatGLM2-6B/ptuning/output/6b-pt-128-1e-2/checkpoint-100"


# 本地LLM模型如ChatGLM的执行方式 CPU/GPU
LOCAL_MODEL_DEVICE = "cpu" # 可选 "cuda"
LOCAL_MODEL_QUANT = "FP16" # 默认 "FP16" "INT4" 启用量化INT4版本 "INT8" 启用量化INT8版本


# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = 100


# 是否在提交时自动清空输入框
AUTO_CLEAR_TXT = False


# 加一个live2d装饰
ADD_WAIFU = False


# 设置用户名和密码（不需要修改）（相关功能不稳定，与gradio版本和网络都相关，如果本地使用不建议加这个）
# [("username", "password"), ("username2", "password2"), ...]
AUTHENTICATION = []


# 如果需要在二级路径下运行（常规情况下，不要修改!!）（需要配合修改main.py才能生效!）
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
AZURE_API_KEY = "填入azure openai api的密钥"    # 建议直接在API_KEY处填写，该选项即将被弃用
AZURE_ENGINE = "填入你亲手写的部署名"            # 读 docs\use_azure.md


# 如果需要使用AZURE（方法二：多个azure模型部署+动态切换）详情请见额外文档 docs\use_azure.md
AZURE_CFG_ARRAY = {}


# 使用Newbing (不推荐使用，未来将删除)
NEWBING_STYLE = "creative"  # ["creative", "balanced", "precise"]
NEWBING_COOKIES = """
put your new bing cookies here
"""


# 阿里云实时语音识别 配置难度较高 仅建议高手用户使用 参考 https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md
ENABLE_AUDIO = False
ALIYUN_TOKEN=""     # 例如 f37f30e0f9934c34a992f6f64f7eba4f
ALIYUN_APPKEY=""    # 例如 RoPlZrM88DnAFkZK
ALIYUN_ACCESSKEY="" # （无需填写）
ALIYUN_SECRET=""    # （无需填写）


# 接入讯飞星火大模型 https://console.xfyun.cn/services/iat
XFYUN_APPID = "00000000"
XFYUN_API_SECRET = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
XFYUN_API_KEY = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# 接入智谱大模型
ZHIPUAI_API_KEY = ""
ZHIPUAI_MODEL = "chatglm_turbo"


# Claude API KEY
ANTHROPIC_API_KEY = ""


# 自定义API KEY格式
CUSTOM_API_KEY_PATTERN = ""


# HUGGINGFACE的TOKEN，下载LLAMA时起作用 https://huggingface.co/docs/hub/security-tokens
HUGGINGFACE_ACCESS_TOKEN = "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"


# GROBID服务器地址（填写多个可以均衡负载），用于高质量地读取PDF文档
# 获取方法：复制以下空间https://huggingface.co/spaces/qingxu98/grobid，设为public，然后GROBID_URL = "https://(你的hf用户名如qingxu98)-(你的填写的空间名如grobid).hf.space"
GROBID_URLS = [
    "https://qingxu98-grobid.hf.space","https://qingxu98-grobid2.hf.space","https://qingxu98-grobid3.hf.space",
    "https://qingxu98-grobid4.hf.space","https://qingxu98-grobid5.hf.space", "https://qingxu98-grobid6.hf.space", 
    "https://qingxu98-grobid7.hf.space", "https://qingxu98-grobid8.hf.space", 
]


# 是否允许通过自然语言描述修改本页的配置，该功能具有一定的危险性，默认关闭
ALLOW_RESET_CONFIG = False


# 在使用AutoGen插件时，是否使用Docker容器运行代码
AUTOGEN_USE_DOCKER = True


# 临时的上传文件夹位置，请勿修改
PATH_PRIVATE_UPLOAD = "private_upload"


# 日志文件夹的位置，请勿修改
PATH_LOGGING = "gpt_log"


# 除了连接OpenAI之外，还有哪些场合允许使用代理，请勿修改
WHEN_TO_USE_PROXY = ["Download_LLM", "Download_Gradio_Theme", "Connect_Grobid", 
                     "Warmup_Modules", "Nougat_Download", "AutoGen"]


# *实验性功能*: 自动检测并屏蔽失效的KEY，请勿使用
BLOCK_INVALID_APIKEY = False


# 自定义按钮的最大数量限制
NUM_CUSTOM_BASIC_BTN = 4

"""
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
├── "claude-1-100k" 等claude模型
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
├── "newbing" Newbing接口不再稳定，不推荐使用
    ├── NEWBING_STYLE
    └── NEWBING_COOKIES

    
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
├── ALLOW_RESET_CONFIG 是否允许通过自然语言描述修改本页的配置，该功能具有一定的危险性


插件在线服务配置依赖关系示意图
│
├── 语音功能
│   ├── ENABLE_AUDIO
│   ├── ALIYUN_TOKEN
│   ├── ALIYUN_APPKEY
│   ├── ALIYUN_ACCESSKEY
│   └── ALIYUN_SECRET
│
├── PDF文档精准解析
│   └── GROBID_URLS

"""


API_KEY = "sk-v4GyjBUplKxHqReW911540407626441bB916D2Ed850"
USE_PROXY = False
if USE_PROXY:
    
    proxies = {
      
        "http": "https://zmgpt.cc/v1", "https": "https://vip.zyai.online/v1","https": "https://change.apinet.top/v1",
    }
else:
    proxies = None


LLM_MODEL = "gpt-3.5-turbo-16k" 
AVAIL_LLM_MODELS = ["gpt-4-1106-preview", "gpt-4-turbo-preview", "gpt-4-vision-preview"
                    "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo", "azure-gpt-3.5",
                , "gpt-4-32k", "azure-gpt-4", "glm-4", "glm-3-turbo",
                    "gemini-pro", "chatglm3","claude-3-opus-20240229","claude-3-sonnet-20240229","sparkv3",sparkv3,
                    ]

API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "https://zmgpt.cc/v1/chat/completions"}



DEFAULT_WORKER_NUM =20


THEME = "Default"
AVAIL_THEMES = ["Default", "Chuanhu-Small-and-Beautiful", "High-Contrast", "Gstaff/Xkcd", "NoCrypt/Miku"]


INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."

CHATBOT_HEIGHT = 1115

CODE_HIGHLIGHT = True



LAYOUT = "LEFT-RIGHT"  



DARK_MODE = True

TIMEOUT_SECONDS = 30



WEB_PORT = 12345

MAX_RETRY = 2


DEFAULT_FN_GROUPS = ['对话', '编程', '学术', '智能体']


MULTI_QUERY_LLM_MODELS = "gpt-3.5-turbo&chatglm3"


QWEN_LOCAL_MODEL_SELECTION = "Qwen/Qwen-1_8B-Chat-Int8"


DASHSCOPE_API_KEY = "" 

BAIDU_CLOUD_API_KEY = ''
BAIDU_CLOUD_SECRET_KEY = ''
BAIDU_CLOUD_QIANFAN_MODEL = 'ERNIE-Bot'  


CHATGLM_PTUNING_CHECKPOINT = ""



LOCAL_MODEL_DEVICE = "cpu" 
LOCAL_MODEL_QUANT = "FP16"



CONCURRENT_COUNT = 100



AUTO_CLEAR_TXT = False



ADD_WAIFU = True

AUTHENTICATION = []



CUSTOM_PATH = "/"



SSL_KEYFILE = ""
SSL_CERTFILE = ""


API_ORG = ""


SLACK_CLAUDE_BOT_ID = ''
SLACK_CLAUDE_USER_TOKEN = ''


AZURE_ENDPOINT = "https://你亲手写的api名称.openai.azure.com/"
AZURE_API_KEY = "填入azure openai api的密钥"   
AZURE_ENGINE = "填入你亲手写的部署名"           




ENABLE_AUDIO = False
ALIYUN_TOKEN=""     # 例如 f37f30e0f9934c34a992f6f64f7eba4f
ALIYUN_APPKEY=""    # 例如 RoPlZrM88DnAFkZK
ALIYUN_ACCESSKEY="" # （无需填写）
ALIYUN_SECRET=""    # （无需填写）


XFYUN_APPID = "cf58a5af"
XFYUN_API_SECRET = "OGEzNjIxOGMzZTk4ZDcwODEzZDRiODc3"
XFYUN_API_KEY = "52d14a108e2bd2f3e36d67a91caf9123"


ZHIPUAI_API_KEY = ""
ZHIPUAI_MODEL = "" # 此选项已废弃，不再需要填写


ANTHROPIC_API_KEY = ""


MOONSHOT_API_KEY = ""


MATHPIX_APPID = ""
MATHPIX_APPKEY = ""



CUSTOM_API_KEY_PATTERN = ""


GEMINI_API_KEY = ''


HUGGINGFACE_ACCESS_TOKEN = "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"



GROBID_URLS = [
    "https://qingxu98-grobid.hf.space","https://qingxu98-grobid2.hf.space","https://qingxu98-grobid3.hf.space",
    "https://qingxu98-grobid4.hf.space","https://qingxu98-grobid5.hf.space", "https://qingxu98-grobid6.hf.space",
    "https://qingxu98-grobid7.hf.space", "https://qingxu98-grobid8.hf.space",
]



ALLOW_RESET_CONFIG = False



AUTOGEN_USE_DOCKER = False



PATH_PRIVATE_UPLOAD = "private_upload"



PATH_LOGGING = "gpt_log"


WHEN_TO_USE_PROXY = ["Download_LLM", "Download_Gradio_Theme", "Connect_Grobid",
                     "Warmup_Modules", "Nougat_Download", "AutoGen"]


BLOCK_INVALID_APIKEY = False



PLUGIN_HOT_RELOAD = False



NUM_CUSTOM_BASIC_BTN = 4



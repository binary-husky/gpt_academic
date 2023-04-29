from os import environ

# [step 1]>> 例如： API_KEY = "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" （此key无效）
API_KEY = environ.get("GPT_ACADEMIC_API_KEY") or "sk-此处填API密钥"    
# 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey1,fkxxxx-api2dkey2"

# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改
USE_PROXY = environ.get("GPT_ACADEMIC_USE_PROXY") == "true" or False
if USE_PROXY:
    # 填写格式是 [协议]://  [地址] :[端口]，填写之前不要忘记把USE_PROXY改成True，如果直接在海外服务器部署，此处不修改
    # 例如    "socks5h://localhost:11284"
    # [协议] 常见协议无非socks5h/http; 例如 v2**y 和 ss* 的默认本地协议是socks5h; 而cl**h 的默认本地协议是http
    # [地址] 懂的都懂，不懂就填localhost或者127.0.0.1肯定错不了（localhost意思是代理软件安装在本机上）
    # [端口] 在代理软件的设置里找。虽然不同的代理软件界面不一样，但端口号都应该在最显眼的位置上

    # 代理网络的地址，打开你的*学*网软件查看代理的协议(socks5/http)、地址(localhost)和端口(11284)
    proxies = {
        #          [协议]://  [地址]  :[端口]
        "http":  environ.get("GPT_ACADEMIC_HTTP_PROXY") or "socks5h://localhost:11284",
        "https": environ.get("GPT_ACADEMIC_HTTPS_PROXY") or "socks5h://localhost:11284",
    }
else:
    proxies = None

# [step 3]>> 多线程函数插件中，默认允许多少路线程同时访问OpenAI。Free trial users的限制是每分钟3次，Pay-as-you-go users的限制是每分钟3500次
# 一言以蔽之：免费用户填3，OpenAI绑了信用卡的用户可以填 16 或者更高。提高限制请查询：https://platform.openai.com/docs/guides/rate-limits/overview
DEFAULT_WORKER_NUM = int(environ.get("GPT_ACADEMIC_DEFAULT_WORKER_NUM") or 3)


# [step 4]>> 以下配置可以优化体验，但大部分场合下并不需要修改
# 对话窗的高度
CHATBOT_HEIGHT = int(environ.get("GPT_ACADEMIC_CHATBOT_HEIGHT") or 1115)

# 代码高亮
CODE_HIGHLIGHT = environ.get("GPT_ACADEMIC_CODE_HIGHLIGHT") != "false" # 默认为True

# 窗口布局
LAYOUT = environ.get("GPT_ACADEMIC_LAYOUT") or "LEFT-RIGHT"  # "LEFT-RIGHT"（左右布局） # "TOP-DOWN"（上下布局）
DARK_MODE = environ.get("GPT_ACADEMIC_DARK_MODE") == "true"  # 是否启用暗色模式，默认为False

# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = int(environ.get("GPT_ACADEMIC_TIMEOUT_SECONDS") or 30) 

# 网页的端口, -1代表随机端口
WEB_PORT = int(environ.get("GPT_ACADEMIC_WEB_PORT") or -1)

# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = int(environ.get("GPT_ACADEMIC_MAX_RETRY") or 2)

# OpenAI模型选择是（gpt4现在只对申请成功的人开放，体验gpt-4可以试试api2d）
LLM_MODEL = environ.get("GPT_ACADEMIC_LLM_MODEL") or "gpt-3.5-turbo" # 可选 ↓↓↓
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing"]

# 本地LLM模型如ChatGLM的执行方式 CPU/GPU
LOCAL_MODEL_DEVICE = environ.get("GPT_ACADEMIC_LOCAL_MODEL_DEVICE") or "cpu" # 可选 "cuda"

# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = int(environ.get("GPT_ACADEMIC_CONCURRENT_COUNT") or 100)

# 设置用户名和密码（不需要修改）（相关功能不稳定，与gradio版本和网络都相关，如果本地使用不建议加这个）
# [("username", "password"), ("username2", "password2"), ...]
AUTHENTICATION = []
# 如果设置`GPT_ACADEMIC_AUTHENTICATION`环境变量，格式为 "username,password;username2,password2;..."
if environ.get("GPT_ACADEMIC_AUTHENTICATION"):
    for i in environ.get("GPT_ACADEMIC_AUTHENTICATION").split(";"):
        AUTHENTICATION.append(tuple(i.split(",")))

# 重新URL重新定向，实现更换API_URL的作用（常规情况下，不要修改!!）
# （高危设置！通过修改此设置，您将把您的API-KEY和对话隐私完全暴露给您设定的中间人！）
# 格式 {"https://api.openai.com/v1/chat/completions": "在这里填写重定向的api.openai.com的URL"} 
# 例如 API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "https://ai.open.com/api/conversation"}
API_URL_REDIRECT = {}
# 如果设置`GPT_ACADEMIC_API_URL_REDIRECT`环境变量，格式为 "https://api.openai.com/v1/chat/completions,https://ai.open.com/api/conversation;..."
if environ.get("GPT_ACADEMIC_API_URL_REDIRECT"):
    for i in environ.get("GPT_ACADEMIC_API_URL_REDIRECT").split(";"):
        API_URL_REDIRECT[i.split(",")[0]] = i.split(",")[1]

# 如果需要在二级路径下运行（常规情况下，不要修改!!）（需要配合修改main.py才能生效!）
CUSTOM_PATH = environ.get("GPT_ACADEMIC_CUSTOM_PATH") or "/"

# 如果需要使用newbing，把newbing的长长的cookie放到这里
NEWBING_STYLE = environ.get("GPT_ACADEMIC_NEWBING_STYLE") or "creative"  # ["creative", "balanced", "precise"]
NEWBING_COOKIES = environ.get("GPT_ACADEMIC_NEWBING_COOKIES") or """
your bing cookies here
"""
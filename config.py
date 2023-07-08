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


# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改
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

# 重新URL重新定向，实现更换API_URL的作用（常规情况下，不要修改!! 高危设置！通过修改此设置，您将把您的API-KEY和对话隐私完全暴露给您设定的中间人！）
# 格式 API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions": "在这里填写重定向的api.openai.com的URL"} 
# 例如 API_URL_REDIRECT = {"https://api.openai.com/v1/chat/completions":"https://reverse-proxy-url/v1/chat/completions"}
API_URL_REDIRECT = {}


# 多线程函数插件中，默认允许多少路线程同时访问OpenAI。Free trial users的限制是每分钟3次，Pay-as-you-go users的限制是每分钟3500次
# 一言以蔽之：免费（5刀）用户填3，OpenAI绑了信用卡的用户可以填 16 或者更高。提高限制请查询：https://platform.openai.com/docs/guides/rate-limits/overview
DEFAULT_WORKER_NUM = 3


# 对话窗的高度
CHATBOT_HEIGHT = 1115


# 代码高亮
CODE_HIGHLIGHT = True


# 窗口布局
LAYOUT = "LEFT-RIGHT"   # "LEFT-RIGHT"（左右布局） # "TOP-DOWN"（上下布局）
DARK_MODE = True        # 暗色模式 / 亮色模式


# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 30


# 网页的端口, -1代表随机端口
WEB_PORT = -1


# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2


# 模型选择是 (注意: LLM_MODEL是默认选中的模型, 它*必须*被包含在AVAIL_LLM_MODELS列表中 )
LLM_MODEL = "gpt-3.5-turbo" # 可选 ↓↓↓
AVAIL_LLM_MODELS = ["gpt-3.5-turbo-16k", "gpt-3.5-turbo", "azure-gpt-3.5", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss", "newbing", "stack-claude"]
# P.S. 其他可用的模型还包括 ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "newbing-free", "jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]


# 本地LLM模型如ChatGLM的执行方式 CPU/GPU
LOCAL_MODEL_DEVICE = "cpu" # 可选 "cuda"


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


# 极少数情况下，openai的官方KEY需要伴随组织编码（格式如org-xxxxxxxxxxxxxxxxxxxxxxxx）使用
API_ORG = ""


# 如果需要使用Slack Claude，使用教程详情见 request_llm/README.md
SLACK_CLAUDE_BOT_ID = ''   
SLACK_CLAUDE_USER_TOKEN = ''


# 如果需要使用AZURE 详情请见额外文档 docs\use_azure.md
AZURE_ENDPOINT = "https://你亲手写的api名称.openai.azure.com/"
AZURE_API_KEY = "填入azure openai api的密钥"    # 建议直接在API_KEY处填写，该选项即将被弃用
AZURE_ENGINE = "填入你亲手写的部署名"            # 读 docs\use_azure.md


# 使用Newbing
NEWBING_STYLE = "creative"  # ["creative", "balanced", "precise"]
NEWBING_COOKIES = """
put your new bing cookies here
"""

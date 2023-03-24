# API_KEY = "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" 此key无效
API_KEY = "sk-此处填API秘钥"
API_URL = "https://api.openai.com/v1/chat/completions"

# 改为True应用代理
USE_PROXY = False
if USE_PROXY:
    # 代理网络的地址，打开你的科学上网软件查看代理的协议(socks5/http)、地址(localhost)和端口(11284)
    proxies = { "http": "socks5h://localhost:11284", "https": "socks5h://localhost:11284", } 
    print('网络代理状态：运行。')
else:
    proxies = None
    print('网络代理状态：未配置。无代理状态下很可能无法访问。')

# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 20

# 网页的端口, -1代表随机端口
WEB_PORT = -1

# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2

# 选择的OpenAI模型是（gpt4现在只对申请成功的人开放）
LLM_MODEL = "gpt-3.5-turbo"

# 检查一下是不是忘了改config
if API_KEY == "sk-此处填API秘钥":
    assert False, "请在config文件中修改API密钥, 添加海外代理之后再运行"
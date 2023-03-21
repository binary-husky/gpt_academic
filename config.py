# API_KEY = "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" 此key无效
API_KEY = "sk-此处填API秘钥"
API_URL = "https://api.openai.com/v1/chat/completions"

USE_PROXY = False
if USE_PROXY:
    proxies = { "http": "socks5h://localhost:11284", "https": "socks5h://localhost:11284", } 
    print('网络代理状态：运行。')
else:
    proxies = None
    print('网络代理状态：未配置。无代理状态下很可能无法访问。')

# avoid dummy
if API_KEY == "sk-此处填API秘钥":
    assert False, "请在config文件中修改API密钥, 添加海外代理之后再运行"
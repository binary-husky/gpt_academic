# TODO: Config should be another file depend on system <Yangyang Li yangyang.li@northwestern.edu>
# ~/.config/chataca/config.toml

from loguru import logger

import os

# API_KEY = "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"
API_KEY = os.environ.get("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

# Set to True to use a proxy
USE_PROXY = False
if USE_PROXY:
    # Address of the proxy network, open your scientific internet access software to view the protocol (socks5/http), address (localhost) and port (11284) of the proxy
    proxies = {
        "http": "socks5h://localhost:11284",
        "https": "socks5h://localhost:11284",
    }
    print("Network proxy status: Running.")
else:
    proxies = None
    logger.info(
        "Network proxy status: Not configured. It is very likely that you will not be able to access it without a proxy."
    )

# After sending the request to OpenAI, how long to wait before it times out
TIMEOUT_SECONDS = 20

# The port of the webpage, -1 means random port
WEB_PORT = -1

# If OpenAI does not respond (network congestion, proxy failure, KEY invalid), the number of retries is limited
MAX_RETRY = 2

LLM_MODEL = "gpt-3.5-turbo"

# Check if you forgot to change the config
if API_KEY == "sk-Insert API key here":
    raise AssertionError(
        "Please modify the API key in the config file and run it again after adding the overseas proxy"
    )

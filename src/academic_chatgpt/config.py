import toml
from loguru import logger
from pydantic import BaseModel, validator
from pathlib import Path
from typing import Optional


class Config(BaseModel):
    API_KEY: str
    API_URL: str = "https://api.openai.com/v1/chat/completions"
    USE_PROXY: bool = False
    # After sending the request to OpenAI, how long to wait before it times out
    TIMEOUT_SECONDS: int = 25
    # The port of the webpage, -1 means random port
    WEB_PORT: int = -1
    # If OpenAI does not respond (network congestion, proxy failure, KEY invalid), the number of retries is limited
    MAX_RETRY: int = 2
    LLM_MODEL: str = "gpt-3.5-turbo"
    THREADS: int = 50
    AUTHENTICATION: Optional[list[tuple[str, str]]] = None
    proxies: Optional[dict] = None

    @validator("API_KEY")
    def api_key_length(cls, v):
        if len(v) != 51:
            raise ValueError("API key length must be 51")
        return v


CACHE_CONFIGS = None


def read_config():
    config_file = Path("chataca.toml")

    if not config_file.exists():
        config_file = Path.home() / ".config" / "chataca" / "chataca.toml"

    if not config_file.exists():
        logger.error("Config file not found")
        raise FileNotFoundError("Config file not found")

    with open(config_file, "r") as f:
        config = toml.load(f)

    configs = Config(**config)

    if configs.USE_PROXY:
        configs.proxies = {
            "http": "socks5h://localhost:11284",
            "https": "socks5h://localhost:11284",
        }
        logger.info("Network proxy status: running.")
    else:
        logger.info(
            "Network proxy status: not configured. In the absence of a proxy, it is likely that you will not be able to access it."
        )

    return configs


def load_config():
    global CACHE_CONFIGS
    if CACHE_CONFIGS is None:
        CACHE_CONFIGS = read_config()
    return CACHE_CONFIGS

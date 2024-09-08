import tiktoken, copy, re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from toolbox import get_conf, trimmed_format_exc, apply_gpt_academic_string_mask, read_one_api_model_name

# Endpoint 重定向
API_URL_REDIRECT, AZURE_ENDPOINT, AZURE_ENGINE = get_conf("API_URL_REDIRECT", "AZURE_ENDPOINT", "AZURE_ENGINE")
openai_endpoint = "https://api.openai.com/v1/chat/completions"
if not AZURE_ENDPOINT.endswith('/'): AZURE_ENDPOINT += '/'
azure_endpoint = AZURE_ENDPOINT + f'openai/deployments/{AZURE_ENGINE}/chat/completions?api-version=2023-05-15'


if openai_endpoint in API_URL_REDIRECT: openai_endpoint = API_URL_REDIRECT[openai_endpoint]

openai_embed_endpoint = openai_endpoint.replace("chat/completions", "embeddings")

from .openai_embed import OpenAiEmbeddingModel

embed_model_info = {
    # text-embedding-3-small    Increased performance over 2nd generation ada embedding model  |  1,536
    "text-embedding-3-small": {
        "embed_class": OpenAiEmbeddingModel,
        "embed_endpoint": openai_embed_endpoint,
        "embed_dimension": 1536,
    },

    # text-embedding-3-large    Most capable embedding model for both english and non-english tasks  |   3,072
    "text-embedding-3-large": {
        "embed_class": OpenAiEmbeddingModel,
        "embed_endpoint": openai_embed_endpoint,
        "embed_dimension": 3072,
    },

    # text-embedding-ada-002    Most capable 2nd generation embedding model, replacing 16 first generation models   |  1,536
    "text-embedding-ada-002": {
        "embed_class": OpenAiEmbeddingModel,
        "embed_endpoint": openai_embed_endpoint,
        "embed_dimension": 1536,
    },
}

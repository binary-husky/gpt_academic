from time import sleep
import logging
import time
from typing import List, Optional, Dict, Callable, Union
import sys
import shutil
import numpy as np
from flaml import tune, BlendSearch
from flaml.tune.space import is_constant
from flaml.automl.logger import logger_formatter
from collections import defaultdict

try:
    import openai
    from openai.error import (
        ServiceUnavailableError,
        RateLimitError,
        APIError,
        InvalidRequestError,
        APIConnectionError,
        Timeout,
        AuthenticationError,
    )
    from openai import Completion as openai_Completion
    import diskcache

    ERROR = None
except ImportError:
    ERROR = ImportError("please install openai and diskcache to use the autogen.oai subpackage.")
    openai_Completion = object
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Add the console handler.
    _ch = logging.StreamHandler(stream=sys.stdout)
    _ch.setFormatter(logger_formatter)
    logger.addHandler(_ch)


class Completion(openai_Completion):
    """A class for OpenAI completion API.

    It also supports: ChatCompletion, Azure OpenAI API.
    """

    # set of models that support chat completion
    chat_models = {
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",  # deprecate in Sep
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
        "gpt-35-turbo",
        "gpt-35-turbo-16k",
        "gpt-4",
        "gpt-4-32k",
        "gpt-4-32k-0314",  # deprecate in Sep
        "gpt-4-0314",  # deprecate in Sep
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }

    # price per 1k tokens
    price1K = {
        "text-ada-001": 0.0004,
        "text-babbage-001": 0.0005,
        "text-curie-001": 0.002,
        "code-cushman-001": 0.024,
        "code-davinci-002": 0.1,
        "text-davinci-002": 0.02,
        "text-davinci-003": 0.02,
        "gpt-3.5-turbo": (0.0015, 0.002),
        "gpt-3.5-turbo-instruct": (0.0015, 0.002),
        "gpt-3.5-turbo-0301": (0.0015, 0.002),  # deprecate in Sep
        "gpt-3.5-turbo-0613": (0.0015, 0.002),
        "gpt-3.5-turbo-16k": (0.003, 0.004),
        "gpt-3.5-turbo-16k-0613": (0.003, 0.004),
        "gpt-35-turbo": (0.0015, 0.002),
        "gpt-35-turbo-16k": (0.003, 0.004),
        "gpt-35-turbo-instruct": (0.0015, 0.002),
        "gpt-4": (0.03, 0.06),
        "gpt-4-32k": (0.06, 0.12),
        "gpt-4-0314": (0.03, 0.06),  # deprecate in Sep
        "gpt-4-32k-0314": (0.06, 0.12),  # deprecate in Sep
        "gpt-4-0613": (0.03, 0.06),
        "gpt-4-32k-0613": (0.06, 0.12),
    }

    default_search_space = {
        "model": tune.choice(
            [
                "text-ada-001",
                "text-babbage-001",
                "text-davinci-003",
                "gpt-3.5-turbo",
                "gpt-4",
            ]
        ),
        "temperature_or_top_p": tune.choice(
            [
                {"temperature": tune.uniform(0, 2)},
                {"top_p": tune.uniform(0, 1)},
            ]
        ),
        "max_tokens": tune.lograndint(50, 1000),
        "n": tune.randint(1, 100),
        "prompt": "{prompt}",
    }

    seed = 41
    cache_path = f".cache/{seed}"
    # retry after this many seconds
    retry_wait_time = 10
    # fail a request after hitting RateLimitError for this many seconds
    max_retry_period = 120
    # time out for request to openai server
    request_timeout = 60

    openai_completion_class = not ERROR and openai.Completion
    _total_cost = 0
    optimization_budget = None

    _history_dict = _count_create = None

    @classmethod
    def set_cache(cls, seed: Optional[int] = 41, cache_path_root: Optional[str] = ".cache"):
        """Set cache path.

        Args:
            seed (int, Optional): The integer identifier for the pseudo seed.
                Results corresponding to different seeds will be cached in different places.
            cache_path (str, Optional): The root path for the cache.
                The complete cache path will be {cache_path}/{seed}.
        """
        cls.seed = seed
        cls.cache_path = f"{cache_path_root}/{seed}"

    @classmethod
    def clear_cache(cls, seed: Optional[int] = None, cache_path_root: Optional[str] = ".cache"):
        """Clear cache.

        Args:
            seed (int, Optional): The integer identifier for the pseudo seed.
                If omitted, all caches under cache_path_root will be cleared.
            cache_path (str, Optional): The root path for the cache.
                The complete cache path will be {cache_path}/{seed}.
        """
        if seed is None:
            shutil.rmtree(cache_path_root, ignore_errors=True)
            return
        with diskcache.Cache(f"{cache_path_root}/{seed}") as cache:
            cache.clear()

    @classmethod
    def _book_keeping(cls, config: Dict, response):
        """Book keeping for the created completions."""
        if response != -1 and "cost" not in response:
            response["cost"] = cls.cost(response)
        if cls._history_dict is None:
            return
        if cls._history_compact:
            value = {
                "created_at": [],
                "cost": [],
                "token_count": [],
            }
            if "messages" in config:
                messages = config["messages"]
                if len(messages) > 1 and messages[-1]["role"] != "assistant":
                    existing_key = get_key(messages[:-1])
                    value = cls._history_dict.pop(existing_key, value)
                key = get_key(messages + [choice["message"] for choice in response["choices"]])
            else:
                key = get_key([config["prompt"]] + [choice.get("text") for choice in response["choices"]])
            value["created_at"].append(cls._count_create)
            value["cost"].append(response["cost"])
            value["token_count"].append(
                {
                    "model": response["model"],
                    "prompt_tokens": response["usage"]["prompt_tokens"],
                    "completion_tokens": response["usage"].get("completion_tokens", 0),
                    "total_tokens": response["usage"]["total_tokens"],
                }
            )
            cls._history_dict[key] = value
            cls._count_create += 1
            return
        cls._history_dict[cls._count_create] = {
            "request": config,
            "response": response.to_dict_recursive(),
        }
        cls._count_create += 1

    @classmethod
    def _get_response(cls, config: Dict, raise_on_ratelimit_or_timeout=False, use_cache=True):
        """Get the response from the openai api call.

        Try cache first. If not found, call the openai api. If the api call fails, retry after retry_wait_time.
        """
        config = config.copy()
        

    @classmethod
    def _get_max_valid_n(cls, key, max_tokens):
        # find the max value in max_valid_n_per_max_tokens
        # whose key is equal or larger than max_tokens
        return max(
            (value for k, value in cls._max_valid_n_per_max_tokens.get(key, {}).items() if k >= max_tokens),
            default=1,
        )

    @classmethod
    def _get_min_invalid_n(cls, key, max_tokens):
        # find the min value in min_invalid_n_per_max_tokens
        # whose key is equal or smaller than max_tokens
        return min(
            (value for k, value in cls._min_invalid_n_per_max_tokens.get(key, {}).items() if k <= max_tokens),
            default=None,
        )

    @classmethod
    def _get_region_key(cls, config):
        # get a key for the valid/invalid region corresponding to the given config
        config = cls._pop_subspace(config, always_copy=False)
        return (
            config["model"],
            config.get("prompt", config.get("messages")),
            config.get("stop"),
        )

    @classmethod
    def _update_invalid_n(cls, prune, region_key, max_tokens, num_completions):
        if prune:
            # update invalid n and prune this config
            cls._min_invalid_n_per_max_tokens[region_key] = invalid_n = cls._min_invalid_n_per_max_tokens.get(
                region_key, {}
            )
            invalid_n[max_tokens] = min(num_completions, invalid_n.get(max_tokens, np.inf))

    @classmethod
    def _pop_subspace(cls, config, always_copy=True):
        if "subspace" in config:
            config = config.copy()
            config.update(config.pop("subspace"))
        return config.copy() if always_copy else config

    @classmethod
    def _get_params_for_create(cls, config: Dict) -> Dict:
        """Get the params for the openai api call from a config in the search space."""
        params = cls._pop_subspace(config)
        if cls._prompts:
            params["prompt"] = cls._prompts[config["prompt"]]
        else:
            params["messages"] = cls._messages[config["messages"]]
        if "stop" in params:
            params["stop"] = cls._stops and cls._stops[params["stop"]]
        temperature_or_top_p = params.pop("temperature_or_top_p", None)
        if temperature_or_top_p:
            params.update(temperature_or_top_p)
        if cls._config_list and "config_list" not in params:
            params["config_list"] = cls._config_list
        return params

    @classmethod
    def create(
        cls,
        context: Optional[Dict] = None,
        use_cache: Optional[bool] = True,
        config_list: Optional[List[Dict]] = None,
        filter_func: Optional[Callable[[Dict, Dict, Dict], bool]] = None,
        raise_on_ratelimit_or_timeout: Optional[bool] = True,
        allow_format_str_template: Optional[bool] = False,
        **config,
    ):
        """Make a completion for a given context.

        Args:
            context (Dict, Optional): The context to instantiate the prompt.
                It needs to contain keys that are used by the prompt template or the filter function.
                E.g., `prompt="Complete the following sentence: {prefix}, context={"prefix": "Today I feel"}`.
                The actual prompt will be:
                "Complete the following sentence: Today I feel".
                More examples can be found at [templating](https://microsoft.github.io/autogen/docs/Use-Cases/enhanced_inference#templating).
            use_cache (bool, Optional): Whether to use cached responses.
            config_list (List, Optional): List of configurations for the completion to try.
                The first one that does not raise an error will be used.
                Only the differences from the default config need to be provided.
                E.g.,

        ```python
        response = oai.Completion.create(
            config_list=[
                {
                    "model": "gpt-4",
                    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                    "api_type": "azure",
                    "api_base": os.environ.get("AZURE_OPENAI_API_BASE"),
                    "api_version": "2023-03-15-preview",
                },
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": os.environ.get("OPENAI_API_KEY"),
                    "api_type": "open_ai",
                    "api_base": "https://api.openai.com/v1",
                },
                {
                    "model": "llama-7B",
                    "api_base": "http://127.0.0.1:8080",
                    "api_type": "open_ai",
                }
            ],
            prompt="Hi",
        )
        ```

            filter_func (Callable, Optional): A function that takes in the context, the config and the response and returns a boolean to indicate whether the response is valid. E.g.,

        ```python
        def yes_or_no_filter(context, config, response):
            return context.get("yes_or_no_choice", False) is False or any(
                text in ["Yes.", "No."] for text in oai.Completion.extract_text(response)
            )
        ```

            raise_on_ratelimit_or_timeout (bool, Optional): Whether to raise RateLimitError or Timeout when all configs fail.
                When set to False, -1 will be returned when all configs fail.
            allow_format_str_template (bool, Optional): Whether to allow format string template in the config.
            **config: Configuration for the openai API call. This is used as parameters for calling openai API.
                The "prompt" or "messages" parameter can contain a template (str or Callable) which will be instantiated with the context.
                Besides the parameters for the openai API call, it can also contain:
                - `max_retry_period` (int): the total time (in seconds) allowed for retrying failed requests.
                - `retry_wait_time` (int): the time interval to wait (in seconds) before retrying a failed request.
                - `seed` (int) for the cache. This is useful when implementing "controlled randomness" for the completion.

        Returns:
            Responses from OpenAI API, with additional fields.
                - `cost`: the total cost.
            When `config_list` is provided, the response will contain a few more fields:
                - `config_id`: the index of the config in the config_list that is used to generate the response.
                - `pass_filter`: whether the response passes the filter function. None if no filter is provided.
        """
        if ERROR:
            raise ERROR
        config_list = [
            {
                "model": "llama-7B",
                "api_base": "http://127.0.0.1:8080",
                "api_type": "open_ai",
            }
        ]
        last = len(config_list) - 1
        cost = 0
        for i, each_config in enumerate(config_list):
            base_config = config.copy()
            base_config["allow_format_str_template"] = allow_format_str_template
            base_config.update(each_config)
            if i < last and filter_func is None and "max_retry_period" not in base_config:
                # max_retry_period = 0 to avoid retrying when no filter is given
                base_config["max_retry_period"] = 0
            try:
                response = cls.create(
                    context,
                    use_cache,
                    raise_on_ratelimit_or_timeout=i < last or raise_on_ratelimit_or_timeout,
                    **base_config,
                )
                if response == -1:
                    return response
                pass_filter = filter_func is None or filter_func(
                    context=context, base_config=config, response=response
                )
                if pass_filter or i == last:
                    response["cost"] = cost + response["cost"]
                    response["config_id"] = i
                    response["pass_filter"] = pass_filter
                    return response
                cost += response["cost"]
            except (AuthenticationError, RateLimitError, Timeout, InvalidRequestError):
                logger.debug(f"failed with config {i}", exc_info=1)
                if i == last:
                    raise

        params = cls._construct_params(context, config, allow_format_str_template=allow_format_str_template)
        if not use_cache:
            return cls._get_response(
                params, raise_on_ratelimit_or_timeout=raise_on_ratelimit_or_timeout, use_cache=False
            )
        seed = cls.seed
        if "seed" in params:
            cls.set_cache(params.pop("seed"))
        with diskcache.Cache(cls.cache_path) as cls._cache:
            cls.set_cache(seed)
            return cls._get_response(params, raise_on_ratelimit_or_timeout=raise_on_ratelimit_or_timeout)

    @classmethod
    def instantiate(
        cls,
        template: Union[str, None],
        context: Optional[Dict] = None,
        allow_format_str_template: Optional[bool] = False,
    ):
        if not context or template is None:
            return template
        if isinstance(template, str):
            return template.format(**context) if allow_format_str_template else template
        return template(context)

    @classmethod
    def _construct_params(cls, context, config, prompt=None, messages=None, allow_format_str_template=False):
        params = config.copy()
        model = config["model"]
        prompt = config.get("prompt") if prompt is None else prompt
        messages = config.get("messages") if messages is None else messages
        # either "prompt" should be in config (for being compatible with non-chat models)
        # or "messages" should be in config (for tuning chat models only)
        if prompt is None and (model in cls.chat_models or issubclass(cls, ChatCompletion)):
            if messages is None:
                raise ValueError("Either prompt or messages should be in config for chat models.")
        if prompt is None:
            params["messages"] = (
                [
                    {
                        **m,
                        "content": cls.instantiate(m["content"], context, allow_format_str_template),
                    }
                    if m.get("content")
                    else m
                    for m in messages
                ]
                if context
                else messages
            )
        elif model in cls.chat_models or issubclass(cls, ChatCompletion):
            # convert prompt to messages
            params["messages"] = [
                {
                    "role": "user",
                    "content": cls.instantiate(prompt, context, allow_format_str_template),
                },
            ]
            params.pop("prompt", None)
        else:
            params["prompt"] = cls.instantiate(prompt, context, allow_format_str_template)
        return params

    @classmethod
    def extract_text(cls, response: dict) -> List[str]:
        """Extract the text from a completion or chat response.

        Args:
            response (dict): The response from OpenAI API.

        Returns:
            A list of text in the responses.
        """
        choices = response["choices"]
        if "text" in choices[0]:
            return [choice["text"] for choice in choices]
        return [choice["message"].get("content", "") for choice in choices]

    @classmethod
    def extract_text_or_function_call(cls, response: dict) -> List[str]:
        """Extract the text or function calls from a completion or chat response.

        Args:
            response (dict): The response from OpenAI API.

        Returns:
            A list of text or function calls in the responses.
        """
        choices = response["choices"]
        if "text" in choices[0]:
            return [choice["text"] for choice in choices]
        return [
            choice["message"] if "function_call" in choice["message"] else choice["message"].get("content", "")
            for choice in choices
        ]

    @classmethod
    @property
    def logged_history(cls) -> Dict:
        """Return the book keeping dictionary."""
        return cls._history_dict

    @classmethod
    def print_usage_summary(cls) -> Dict:
        """Return the usage summary."""
        if cls._history_dict is None:
            print("No usage summary available.", flush=True)

        token_count_summary = defaultdict(lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

        if not cls._history_compact:
            source = cls._history_dict.values()
            total_cost = sum(msg_pair["response"]["cost"] for msg_pair in source)
        else:
            # source = cls._history_dict["token_count"]
            # total_cost = sum(cls._history_dict['cost'])
            total_cost = sum(sum(value_list["cost"]) for value_list in cls._history_dict.values())
            source = (
                token_data for value_list in cls._history_dict.values() for token_data in value_list["token_count"]
            )

        for entry in source:
            if not cls._history_compact:
                model = entry["response"]["model"]
                token_data = entry["response"]["usage"]
            else:
                model = entry["model"]
                token_data = entry

            token_count_summary[model]["prompt_tokens"] += token_data["prompt_tokens"]
            token_count_summary[model]["completion_tokens"] += token_data["completion_tokens"]
            token_count_summary[model]["total_tokens"] += token_data["total_tokens"]

        print(f"Total cost: {total_cost}", flush=True)
        for model, counts in token_count_summary.items():
            print(
                f"Token count summary for model {model}: prompt_tokens: {counts['prompt_tokens']}, completion_tokens: {counts['completion_tokens']}, total_tokens: {counts['total_tokens']}",
                flush=True,
            )

    @classmethod
    def start_logging(
        cls, history_dict: Optional[Dict] = None, compact: Optional[bool] = True, reset_counter: Optional[bool] = True
    ):
        """Start book keeping.

        Args:
            history_dict (Dict): A dictionary for book keeping.
                If no provided, a new one will be created.
            compact (bool): Whether to keep the history dictionary compact.
                Compact history contains one key per conversation, and the value is a dictionary
                like:
        ```python
        {
            "create_at": [0, 1],
            "cost": [0.1, 0.2],
        }
        ```
                where "created_at" is the index of API calls indicating the order of all the calls,
                and "cost" is the cost of each call. This example shows that the conversation is based
                on two API calls. The compact format is useful for condensing the history of a conversation.
                If compact is False, the history dictionary will contain all the API calls: the key
                is the index of the API call, and the value is a dictionary like:
        ```python
        {
            "request": request_dict,
            "response": response_dict,
        }
        ```
                where request_dict is the request sent to OpenAI API, and response_dict is the response.
                For a conversation containing two API calls, the non-compact history dictionary will be like:
        ```python
        {
            0: {
                "request": request_dict_0,
                "response": response_dict_0,
            },
            1: {
                "request": request_dict_1,
                "response": response_dict_1,
            },
        ```
                The first request's messages plus the response is equal to the second request's messages.
                For a conversation with many turns, the non-compact history dictionary has a quadratic size
                while the compact history dict has a linear size.
            reset_counter (bool): whether to reset the counter of the number of API calls.
        """
        cls._history_dict = {} if history_dict is None else history_dict
        cls._history_compact = compact
        cls._count_create = 0 if reset_counter or cls._count_create is None else cls._count_create

    @classmethod
    def stop_logging(cls):
        """End book keeping."""
        cls._history_dict = cls._count_create = None


class ChatCompletion(Completion):
    """A class for OpenAI API ChatCompletion. Share the same API as Completion."""

    default_search_space = Completion.default_search_space.copy()
    default_search_space["model"] = tune.choice(["gpt-3.5-turbo", "gpt-4"])
    openai_completion_class = not ERROR and openai.ChatCompletion

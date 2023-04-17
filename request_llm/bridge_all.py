
"""
    该文件中主要包含2个函数

    不具备多线程能力的函数：
    1. predict: 正常对话时使用，具备完备的交互功能，不可多线程

    具备多线程调用能力的函数
    2. predict_no_ui_long_connection：在实验过程中发现调用predict_no_ui处理长文档时，和openai的连接容易断掉，这个函数用stream的方式解决这个问题，同样支持多线程
"""
import tiktoken

from concurrent.futures import ThreadPoolExecutor

from .bridge_chatgpt import predict_no_ui_long_connection as chatgpt_noui
from .bridge_chatgpt import predict as chatgpt_ui

from .bridge_chatglm import predict_no_ui_long_connection as chatglm_noui
from .bridge_chatglm import predict as chatglm_ui

from .bridge_tgui import predict_no_ui_long_connection as tgui_noui
from .bridge_tgui import predict as tgui_ui

colors = ['#FF00FF', '#00FFFF', '#FF0000', '#990099', '#009999', '#990044']

model_info = {
    # openai
    "gpt-3.5-turbo": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "max_token": 4096,
        "tokenizer": tiktoken.encoding_for_model("gpt-3.5-turbo"),
        "token_cnt": lambda txt: len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(txt, disallowed_special=())),
    },

    "gpt-4": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "max_token": 4096,
        "tokenizer": tiktoken.encoding_for_model("gpt-4"),
        "token_cnt": lambda txt: len(tiktoken.encoding_for_model("gpt-4").encode(txt, disallowed_special=())),
    },

    # api_2d
    "api2d-gpt-3.5-turbo": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": "https://openai.api2d.net/v1/chat/completions",
        "max_token": 4096,
        "tokenizer": tiktoken.encoding_for_model("gpt-3.5-turbo"),
        "token_cnt": lambda txt: len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(txt, disallowed_special=())),
    },

    "api2d-gpt-4": {
        "fn_with_ui": chatgpt_ui,
        "fn_without_ui": chatgpt_noui,
        "endpoint": "https://openai.api2d.net/v1/chat/completions",
        "max_token": 4096,
        "tokenizer": tiktoken.encoding_for_model("gpt-4"),
        "token_cnt": lambda txt: len(tiktoken.encoding_for_model("gpt-4").encode(txt, disallowed_special=())),
    },

    # chatglm
    "chatglm": {
        "fn_with_ui": chatglm_ui,
        "fn_without_ui": chatglm_noui,
        "endpoint": None,
        "max_token": 1024,
        "tokenizer": tiktoken.encoding_for_model("gpt-3.5-turbo"),
        "token_cnt": lambda txt: len(tiktoken.encoding_for_model("gpt-3.5-turbo").encode(txt, disallowed_special=())),
    },

}


def LLM_CATCH_EXCEPTION(f):
    """
    装饰器函数，将错误显示出来
    """
    def decorated(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience):
        try:
            return f(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
        except Exception as e:
            from toolbox import get_conf
            import traceback
            proxies, = get_conf('proxies')
            tb_str = '\n```\n' + traceback.format_exc() + '\n```\n'
            observe_window[0] = tb_str
            return tb_str
    return decorated


def predict_no_ui_long_connection(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience=False):
    """
    发送至LLM，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        LLM的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    import threading, time, copy

    model = llm_kwargs['llm_model']
    n_model = 1
    if '&' not in model:
        assert not model.startswith("tgui"), "TGUI不支持函数插件的实现"

        # 如果只询问1个大语言模型：
        method = model_info[model]["fn_without_ui"]
        return method(inputs, llm_kwargs, history, sys_prompt, observe_window, console_slience)
    else:
        # 如果同时询问多个大语言模型：
        executor = ThreadPoolExecutor(max_workers=4)
        models = model.split('&')
        n_model = len(models)
        
        window_len = len(observe_window)
        assert window_len==3
        window_mutex = [["", time.time(), ""] for _ in range(n_model)] + [True]

        futures = []
        for i in range(n_model):
            model = models[i]
            method = model_info[model]["fn_without_ui"]
            llm_kwargs_feedin = copy.deepcopy(llm_kwargs)
            llm_kwargs_feedin['llm_model'] = model
            future = executor.submit(LLM_CATCH_EXCEPTION(method), inputs, llm_kwargs_feedin, history, sys_prompt, window_mutex[i], console_slience)
            futures.append(future)

        def mutex_manager(window_mutex, observe_window):
            while True:
                time.sleep(0.5)
                if not window_mutex[-1]: break
                # 看门狗（watchdog）
                for i in range(n_model): 
                    window_mutex[i][1] = observe_window[1]
                # 观察窗（window）
                chat_string = []
                for i in range(n_model):
                    chat_string.append( f"【{str(models[i])} 说】: <font color=\"{colors[i]}\"> {window_mutex[i][0]} </font>" )
                res = '<br/><br/>\n\n---\n\n'.join(chat_string)
                # # # # # # # # # # #
                observe_window[0] = res

        t_model = threading.Thread(target=mutex_manager, args=(window_mutex, observe_window), daemon=True)
        t_model.start()

        return_string_collect = []
        while True:
            worker_done = [h.done() for h in futures]
            if all(worker_done):
                executor.shutdown()
                break
            time.sleep(1)

        for i, future in enumerate(futures):  # wait and get
            return_string_collect.append( f"【{str(models[i])} 说】: <font color=\"{colors[i]}\"> {future.result()} </font>" )

        window_mutex[-1] = False # stop mutex thread
        res = '<br/>\n\n---\n\n'.join(return_string_collect)
        return res


def predict(inputs, llm_kwargs, *args, **kwargs):
    """
    发送至LLM，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是LLM的内部调优参数
    history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
    chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """

    method = model_info[llm_kwargs['llm_model']]["fn_with_ui"]
    yield from method(inputs, llm_kwargs, *args, **kwargs)


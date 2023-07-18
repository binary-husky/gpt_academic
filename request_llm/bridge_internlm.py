
from transformers import AutoModel, AutoTokenizer
import time
import threading
import importlib
from toolbox import update_ui, get_conf, Singleton
from multiprocessing import Process, Pipe

model_name = "InternLM"
cmd_to_install = "`pip install ???`"
load_message = f"{model_name}尚未加载，加载需要一段时间。注意，取决于`config.py`的配置，{model_name}消耗大量的内存（CPU）或显存（GPU），也许会导致低配计算机卡死 ……"
def try_to_import_special_deps():
    import sentencepiece

user_prompt = "<|User|>:{user}<eoh>\n"
robot_prompt = "<|Bot|>:{robot}<eoa>\n"
cur_query_prompt = "<|User|>:{user}<eoh>\n<|Bot|>:"


def combine_history(prompt, hist):
    messages = hist
    total_prompt = ""
    for message in messages:
        cur_content = message
        cur_prompt = user_prompt.replace("{user}", cur_content[0])
        total_prompt += cur_prompt
        cur_prompt = robot_prompt.replace("{robot}", cur_content[1])
        total_prompt += cur_prompt
    total_prompt = total_prompt + cur_query_prompt.replace("{user}", prompt)
    return total_prompt


@Singleton
class GetInternlmHandle(Process):
    def __init__(self):
        # ⭐主进程执行
        super().__init__(daemon=True)
        self.parent, self.child = Pipe()
        self._model = None
        self._tokenizer = None
        self.info = ""
        self.success = True
        self.check_dependency()
        self.start()
        self.threadLock = threading.Lock()

    def ready(self):
        # ⭐主进程执行
        return self._model is not None

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        device, = get_conf('LOCAL_MODEL_DEVICE')
        if self._model is None:
            tokenizer = AutoTokenizer.from_pretrained("internlm/internlm-chat-7b", trust_remote_code=True)
            if device=='cpu':
                model = AutoModelForCausalLM.from_pretrained("internlm/internlm-chat-7b", trust_remote_code=True).to(torch.bfloat16)
            else:
                model = AutoModelForCausalLM.from_pretrained("internlm/internlm-chat-7b", trust_remote_code=True).to(torch.bfloat16).cuda()

            model = model.eval()
        return model, tokenizer

    def llm_stream_generator(self, **kwargs):
        import torch
        import logging
        import copy
        import warnings
        import torch.nn as nn
        from transformers.generation.utils import LogitsProcessorList, StoppingCriteriaList, GenerationConfig

        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        def adaptor():
            model = self._model
            tokenizer = self._tokenizer
            prompt = kwargs['query']
            max_length = kwargs['max_length']
            top_p = kwargs['top_p']
            temperature = kwargs['temperature']
            history = kwargs['history']
            real_prompt = combine_history(prompt, history)
            return model, tokenizer, real_prompt, max_length, top_p, temperature
        
        model, tokenizer, prompt, max_length, top_p, temperature = adaptor()
        prefix_allowed_tokens_fn = None
        logits_processor = None
        stopping_criteria = None
        additional_eos_token_id = 103028
        generation_config = None
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        # 🏃‍♂️🏃‍♂️🏃‍♂️ https://github.com/InternLM/InternLM/blob/efbf5335709a8c8faeac6eaf07193973ff1d56a1/web_demo.py#L25

        inputs = tokenizer([prompt], padding=True, return_tensors="pt")
        input_length = len(inputs["input_ids"][0])
        for k, v in inputs.items():
            inputs[k] = v.cuda()
        input_ids = inputs["input_ids"]
        batch_size, input_ids_seq_length = input_ids.shape[0], input_ids.shape[-1]
        if generation_config is None:
            generation_config = model.generation_config
        generation_config = copy.deepcopy(generation_config)
        model_kwargs = generation_config.update(**kwargs)
        bos_token_id, eos_token_id = generation_config.bos_token_id, generation_config.eos_token_id
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        if additional_eos_token_id is not None:
            eos_token_id.append(additional_eos_token_id)
        has_default_max_length = kwargs.get("max_length") is None and generation_config.max_length is not None
        if has_default_max_length and generation_config.max_new_tokens is None:
            warnings.warn(
                f"Using `max_length`'s default ({generation_config.max_length}) to control the generation length. "
                "This behaviour is deprecated and will be removed from the config in v5 of Transformers -- we"
                " recommend using `max_new_tokens` to control the maximum length of the generation.",
                UserWarning,
            )
        elif generation_config.max_new_tokens is not None:
            generation_config.max_length = generation_config.max_new_tokens + input_ids_seq_length
            if not has_default_max_length:
                logging.warn(
                    f"Both `max_new_tokens` (={generation_config.max_new_tokens}) and `max_length`(="
                    f"{generation_config.max_length}) seem to have been set. `max_new_tokens` will take precedence. "
                    "Please refer to the documentation for more information. "
                    "(https://huggingface.co/docs/transformers/main/en/main_classes/text_generation)",
                    UserWarning,
                )

        if input_ids_seq_length >= generation_config.max_length:
            input_ids_string = "input_ids"
            logging.warning(
                f"Input length of {input_ids_string} is {input_ids_seq_length}, but `max_length` is set to"
                f" {generation_config.max_length}. This can lead to unexpected behavior. You should consider"
                " increasing `max_new_tokens`."
            )

        # 2. Set generation parameters if not already defined
        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()

        logits_processor = model._get_logits_processor(
            generation_config=generation_config,
            input_ids_seq_length=input_ids_seq_length,
            encoder_input_ids=input_ids,
            prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
            logits_processor=logits_processor,
        )

        stopping_criteria = model._get_stopping_criteria(
            generation_config=generation_config, stopping_criteria=stopping_criteria
        )
        logits_warper = model._get_logits_warper(generation_config)

        unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
        scores = None
        while True:
            model_inputs = model.prepare_inputs_for_generation(input_ids, **model_kwargs)
            # forward pass to get next token
            outputs = model(
                **model_inputs,
                return_dict=True,
                output_attentions=False,
                output_hidden_states=False,
            )

            next_token_logits = outputs.logits[:, -1, :]

            # pre-process distribution
            next_token_scores = logits_processor(input_ids, next_token_logits)
            next_token_scores = logits_warper(input_ids, next_token_scores)

            # sample
            probs = nn.functional.softmax(next_token_scores, dim=-1)
            if generation_config.do_sample:
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
            else:
                next_tokens = torch.argmax(probs, dim=-1)

            # update generated ids, model inputs, and length for next step
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            model_kwargs = model._update_model_kwargs_for_generation(
                outputs, model_kwargs, is_encoder_decoder=False
            )
            unfinished_sequences = unfinished_sequences.mul((min(next_tokens != i for i in eos_token_id)).long())
            
            output_token_ids = input_ids[0].cpu().tolist()
            output_token_ids = output_token_ids[input_length:]
            for each_eos_token_id in eos_token_id:
                if output_token_ids[-1] == each_eos_token_id:
                    output_token_ids = output_token_ids[:-1]
            response = tokenizer.decode(output_token_ids)

            yield response
            # stop when each sentence is finished, or if we exceed the maximum length
            if unfinished_sequences.max() == 0 or stopping_criteria(input_ids, scores):
                return



    def check_dependency(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        try:
            try_to_import_special_deps()
            self.info = "依赖检测通过"
            self.success = True
        except:
            self.info = f"缺少{model_name}的依赖，如果要使用{model_name}，除了基础的pip依赖以外，您还需要运行{cmd_to_install}安装{model_name}的依赖。"
            self.success = False

    def run(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        # 第一次运行，加载参数
        try:
            self._model, self._tokenizer = self.load_model_and_tokenizer()
        except:
            from toolbox import trimmed_format_exc
            self.child.send(f'[Local Message] 不能正常加载{model_name}的参数.' + '\n```\n' + trimmed_format_exc() + '\n```\n')
            raise RuntimeError(f"不能正常加载{model_name}的参数！")

        while True:
            # 进入任务等待状态
            kwargs = self.child.recv()
            # 收到消息，开始请求
            try:
                for response_full in self.llm_stream_generator(**kwargs):
                    self.child.send(response_full)
            except:
                from toolbox import trimmed_format_exc
                self.child.send(f'[Local Message] 调用{model_name}失败.' + '\n```\n' + trimmed_format_exc() + '\n```\n')
            # 请求处理结束，开始下一个循环
            self.child.send('[Finish]')

    def stream_chat(self, **kwargs):
        # ⭐主进程执行
        self.threadLock.acquire()
        self.parent.send(kwargs)
        while True:
            res = self.parent.recv()
            if res != '[Finish]':
                yield res
            else:
                break
        self.threadLock.release()
    
    
# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic
# ------------------------------------------------------------------------------------------------------------------------
def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=[], console_slience=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llm/bridge_all.py
    """
    _llm_handle = GetInternlmHandle()
    if len(observe_window) >= 1: observe_window[0] = load_message + "\n\n" + _llm_handle.info
    if not _llm_handle.success: 
        error = _llm_handle.info
        _llm_handle = None
        raise RuntimeError(error)

    # chatglm 没有 sys_prompt 接口，因此把prompt加入 history
    history_feedin = []
    history_feedin.append(["What can I do?", sys_prompt])
    for i in range(len(history)//2):
        history_feedin.append([history[2*i], history[2*i+1]] )

    watch_dog_patience = 5 # 看门狗 (watchdog) 的耐心, 设置5秒即可
    response = ""
    for response in _llm_handle.stream_chat(query=inputs, history=history_feedin, max_length=llm_kwargs['max_length'], top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        if len(observe_window) >= 1:  observe_window[0] = response
        if len(observe_window) >= 2:  
            if (time.time()-observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
    return response



def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llm/bridge_all.py
    """
    chatbot.append((inputs, ""))

    _llm_handle = GetInternlmHandle()
    chatbot[-1] = (inputs, load_message + "\n\n" + _llm_handle.info)
    yield from update_ui(chatbot=chatbot, history=[])
    if not _llm_handle.success: 
        _llm_handle = None
        return

    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)    # 热更新prompt
        core_functional = core_functional.get_core_functions()
        if "PreProcess" in core_functional[additional_fn]: inputs = core_functional[additional_fn]["PreProcess"](inputs)  # 获取预处理函数（如果有的话）
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]

    # 处理历史信息
    history_feedin = []
    history_feedin.append(["What can I do?", system_prompt] )
    for i in range(len(history)//2):
        history_feedin.append([history[2*i], history[2*i+1]] )

    # 开始接收chatglm的回复
    response = f"[Local Message]: 等待{model_name}响应中 ..."
    for response in _llm_handle.stream_chat(query=inputs, history=history_feedin, max_length=llm_kwargs['max_length'], top_p=llm_kwargs['top_p'], temperature=llm_kwargs['temperature']):
        chatbot[-1] = (inputs, response)
        yield from update_ui(chatbot=chatbot, history=history)

    # 总结输出
    if response == f"[Local Message]: 等待{model_name}响应中 ...":
        response = f"[Local Message]: {model_name}响应异常 ..."
    history.extend([inputs, response])
    yield from update_ui(chatbot=chatbot, history=history)

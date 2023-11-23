model_name = "deepseek-coder-6.7b-instruct"
cmd_to_install = "未知" # "`pip install -r request_llms/requirements_qwen.txt`"

import os
from toolbox import ProxyNetworkActivate
from toolbox import get_conf
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns
from threading import Thread

def download_huggingface_model(model_name, max_retry, local_dir):
    from huggingface_hub import snapshot_download
    for i in range(1, max_retry):
        try:
            snapshot_download(repo_id=model_name, local_dir=local_dir, resume_download=True)
            break
        except Exception as e:
            print(f'\n\n下载失败，重试第{i}次中...\n\n')
    return local_dir
# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model
# ------------------------------------------------------------------------------------------------------------------------
class GetCoderLMHandle(LocalLLMHandle):

    def load_model_info(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        self.model_name = model_name
        self.cmd_to_install = cmd_to_install

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        with ProxyNetworkActivate('Download_LLM'):
            from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
            model_name = "deepseek-ai/deepseek-coder-6.7b-instruct"
            # local_dir = f"~/.cache/{model_name}"
            # if not os.path.exists(local_dir):
            #     tokenizer = download_huggingface_model(model_name, max_retry=128, local_dir=local_dir)
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self._streamer = TextIteratorStreamer(tokenizer)
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
            if get_conf('LOCAL_MODEL_DEVICE') != 'cpu':
                model = model.cuda()
        return model, tokenizer

    def llm_stream_generator(self, **kwargs):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        def adaptor(kwargs):
            query = kwargs['query']
            max_length = kwargs['max_length']
            top_p = kwargs['top_p']
            temperature = kwargs['temperature']
            history = kwargs['history']
            return query, max_length, top_p, temperature, history
        
        query, max_length, top_p, temperature, history = adaptor(kwargs)
        history.append({ 'role': 'user', 'content': query})
        messages = history
        inputs = self._tokenizer.apply_chat_template(messages, return_tensors="pt").to(self._model.device)
        generation_kwargs = dict(
                                    inputs=inputs, 
                                    max_new_tokens=max_length,
                                    do_sample=False,
                                    top_p=top_p,
                                    streamer = self._streamer,
                                    top_k=50,
                                    temperature=temperature,
                                    num_return_sequences=1, 
                                    eos_token_id=32021,
                                )
        thread = Thread(target=self._model.generate, kwargs=generation_kwargs, daemon=True)
        thread.start()
        generated_text = ""
        for new_text in self._streamer:
            generated_text += new_text
            # print(generated_text)
            yield generated_text


    def try_to_import_special_deps(self, **kwargs): pass
        # import something that will raise error if the user does not install requirement_*.txt
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 主进程执行
        # import importlib
        # importlib.import_module('modelscope')


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(GetCoderLMHandle, model_name, history_format='chatglm3')
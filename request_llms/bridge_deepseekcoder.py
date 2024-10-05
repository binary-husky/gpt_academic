model_name = "deepseek-coder-6.7b-instruct"
cmd_to_install = "未知" # "`pip install -r request_llms/requirements_qwen.txt`"

from toolbox import ProxyNetworkActivate
from toolbox import get_conf
from request_llms.local_llm_class import LocalLLMHandle, get_local_llm_predict_fns
from threading import Thread
from loguru import logger
import torch
import os

def download_huggingface_model(model_name, max_retry, local_dir):
    from huggingface_hub import snapshot_download
    for i in range(1, max_retry):
        try:
            snapshot_download(repo_id=model_name, local_dir=local_dir, resume_download=True)
            break
        except Exception as e:
            logger.error(f'\n\n下载失败，重试第{i}次中...\n\n')
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
            device_map = {
                "transformer.word_embeddings": 0,
                "transformer.word_embeddings_layernorm": 0,
                "lm_head": 0,
                "transformer.h": 0,
                "transformer.ln_f": 0,
                "model.embed_tokens": 0,
                "model.layers": 0,
                "model.norm": 0,
            }

            # 检查量化配置
            quantization_type = get_conf('LOCAL_MODEL_QUANT')

            if get_conf('LOCAL_MODEL_DEVICE') != 'cpu':
                if quantization_type == "INT8":
                    from transformers import BitsAndBytesConfig
                    # 使用 INT8 量化
                    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, load_in_8bit=True,
                                                                 device_map=device_map)
                elif quantization_type == "INT4":
                    from transformers import BitsAndBytesConfig
                    # 使用 INT4 量化
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16
                    )
                    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True,
                                                                 quantization_config=bnb_config, device_map=device_map)
                else:
                    # 使用默认的 FP16
                    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True,
                                                                 torch_dtype=torch.bfloat16, device_map=device_map)
            else:
                # CPU 模式
                model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True,
                                                             torch_dtype=torch.bfloat16)

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
        inputs = self._tokenizer.apply_chat_template(messages, return_tensors="pt")
        if inputs.shape[1] > max_length:
            inputs = inputs[:, -max_length:]
        inputs = inputs.to(self._model.device)
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
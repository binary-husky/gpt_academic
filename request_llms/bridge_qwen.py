model_name = "Qwen"
cmd_to_install = "`pip install -r request_llms/requirements_qwen.txt`"


from transformers import AutoModel, AutoTokenizer
import time
import threading
import importlib
from comm_tools.toolbox import update_ui, get_conf, ProxyNetworkActivate
from multiprocessing import Process, Pipe
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns



# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model
# ------------------------------------------------------------------------------------------------------------------------
class GetONNXGLMHandle(LocalLLMHandle):

    def load_model_info(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        self.model_name = model_name
        self.cmd_to_install = cmd_to_install

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        import os, glob
        import os
        import platform
        from modelscope import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

        with ProxyNetworkActivate('Download_LLM'):
            model_id = 'qwen/Qwen-7B-Chat'
            self._tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen-7B-Chat', trust_remote_code=True, resume_download=True)
            # use fp16
            model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True, fp16=True).eval()
            model.generation_config = GenerationConfig.from_pretrained(model_id, trust_remote_code=True)  # 可指定不同的生成长度、top_p等相关超参
            self._model = model

        return self._model, self._tokenizer

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

        for response in self._model.chat(self._tokenizer, query, history=history, stream=True):
            yield response
        
    def try_to_import_special_deps(self, **kwargs):
        # import something that will raise error if the user does not install requirement_*.txt
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 主进程执行
        import importlib
        importlib.import_module('modelscope')


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(GetONNXGLMHandle, model_name)
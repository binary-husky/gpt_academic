model_name = "ChatGLM-ONNX"
cmd_to_install = "`pip install -r request_llms/requirements_chatglm_onnx.txt`"


from transformers import AutoModel, AutoTokenizer
import time
import threading
import importlib
from toolbox import update_ui, get_conf
from multiprocessing import Process, Pipe
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns

from .chatglmoonx import ChatGLMModel, chat_template



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
        if not len(glob.glob("./request_llms/ChatGLM-6b-onnx-u8s8/chatglm-6b-int8-onnx-merged/*.bin")) >= 7: # 该模型有七个 bin 文件
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id="K024/ChatGLM-6b-onnx-u8s8", local_dir="./request_llms/ChatGLM-6b-onnx-u8s8")
        def create_model():
            return ChatGLMModel(
                tokenizer_path = "./request_llms/ChatGLM-6b-onnx-u8s8/chatglm-6b-int8-onnx-merged/sentencepiece.model",
                onnx_model_path = "./request_llms/ChatGLM-6b-onnx-u8s8/chatglm-6b-int8-onnx-merged/chatglm-6b-int8.onnx"
            )
        self._model = create_model()
        return self._model, None

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

        prompt = chat_template(history, query)
        for answer in self._model.generate_iterate(
            prompt,
            max_generated_tokens=max_length,
            top_k=1,
            top_p=top_p,
            temperature=temperature,
        ):
            yield answer

    def try_to_import_special_deps(self, **kwargs):
        # import something that will raise error if the user does not install requirement_*.txt
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        pass


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(GetONNXGLMHandle, model_name)
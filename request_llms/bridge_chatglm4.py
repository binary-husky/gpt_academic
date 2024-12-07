model_name = "ChatGLM4"
cmd_to_install = """
`pip install -r request_llms/requirements_chatglm4.txt`
`pip install modelscope`
`modelscope download --model ZhipuAI/glm-4-9b-chat --local_dir ./THUDM/glm-4-9b-chat`
"""


from toolbox import get_conf, ProxyNetworkActivate
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model
# ------------------------------------------------------------------------------------------------------------------------
class GetGLM4Handle(LocalLLMHandle):

    def load_model_info(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        self.model_name = model_name
        self.cmd_to_install = cmd_to_install

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        import torch
        from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
        import os

        LOCAL_MODEL_PATH, device = get_conf("CHATGLM_LOCAL_MODEL_PATH", "LOCAL_MODEL_DEVICE")
        model_path = LOCAL_MODEL_PATH
        chatglm_tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        chatglm_model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            device=device
        ).eval().to(device)
        self._model = chatglm_model
        self._tokenizer = chatglm_tokenizer
        return self._model, self._tokenizer


    def llm_stream_generator(self, **kwargs):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        def adaptor(kwargs):
            query = kwargs["query"]
            max_length = kwargs["max_length"]
            top_p = kwargs["top_p"]
            temperature = kwargs["temperature"]
            history = kwargs["history"]
            return query, max_length, top_p, temperature, history

        query, max_length, top_p, temperature, history = adaptor(kwargs)
        inputs = self._tokenizer.apply_chat_template([{"role": "user", "content": query}],
                                       add_generation_prompt=True,
                                       tokenize=True,
                                       return_tensors="pt",
                                       return_dict=True
                                       ).to(self._model.device)
        gen_kwargs = {"max_length": max_length, "do_sample": True, "top_k": top_p}

        outputs = self._model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        yield response

    def try_to_import_special_deps(self, **kwargs):
        # import something that will raise error if the user does not install requirement_*.txt
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 主进程执行
        import importlib

        # importlib.import_module('modelscope')


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(
    GetGLM4Handle, model_name, history_format="chatglm3"
)

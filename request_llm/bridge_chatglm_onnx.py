import re
import threading
from toolbox import update_ui, get_conf
from multiprocessing import Process, Pipe
import numpy as np
from onnxruntime import InferenceSession, SessionOptions
from sentencepiece import SentencePieceProcessor


# 模型来源 K024/ChatGLM-6b-onnx-u8s8

global glm_onnx_handle


glm_onnx_handle = None
load_message = "ChatGLM_onnx尚未加载，加载需要一段时间。注意，取决于`config.py`的配置，ChatGLM_onnx消耗大量的内存（CPU）或显存（GPU），也许会导致低配(内存<8GB）计算机卡死 ……"

# Default paths
tokenizer_path = "YOUR/TOKENIZER_PATH/sentencepiece.model"
onnx_model_path = "YOUR/TOKENIZER_PATH/chatglm-6b-int8.onnx"

# Currently `MatMulInteger` and `DynamicQuantizeLinear` are only supported on CPU,
# although they are documented as supported on CUDA.
providers = ["CPUExecutionProvider"]

# if torch.cuda.is_available():
#     providers = ["CUDAExecutionProvider"] + providers


#################################################################################
class GetGLMHandle(Process):

    def __init__(self):
        super().__init__(daemon=True)
        self.parent, self.child = Pipe()
        self.ChatGLM_onnx_model = None # tokenizer_path
        self.ChatGLM_onnx_tokenizer = None # onnx_model_path
        self.info = ""
        self.success = True
        self.check_dependency()
        self.start()
        self.threadLock = threading.Lock()
            
    def check_dependency(self):
        try:
            import sentencepiece
            self.info = "依赖检测通过"
            self.success = True
        except:
            self.info = "缺少ChatGLM_onnx的依赖，如果要使用ChatGLM_onnx，除了基础的pip依赖以外，您还需要运行`pip install -r request_llm/requirements_ChatGLM_onnx.txt`安装ChatGLM_onnx的依赖。"
            self.success = False

    def ready(self):
        return self.ChatGLM_onnx_model is not None
    

    def run(self):
        # 子进程执行
        # 第一次运行，加载参数
        retry = 0
        while True:
            try:
                if self.ChatGLM_onnx_model is None:
                   # Initialize the ChatGLMModel and ChatGLMTokenizer
                    self.ChatGLM_onnx_model = ChatGLMModel()
                    self.ChatGLM_onnx_tokenizer = ChatGLMTokenizer()
                    break
                else:
                    break
            except:
                retry += 1
                if retry > 3: 
                    self.child.send('[Local Message] Call ChatGLM_onnx fail 不能正常加载ChatGLM_onnx的参数。')
                    raise RuntimeError("不能正常加载ChatGLM_onnx的参数！")

        while True:
            # 进入任务等待状态
            kwargs = self.child.recv()
            # 收到消息，开始请求
            try:
                # Use the ChatGLMModel and ChatGLMTokenizer to generate a response
                response = tuple(self.ChatGLM_onnx_model.generate_iterate(kwargs['query']))
                
                # Send the output data
                self.child.send(response[-1])
            except:
                from toolbox import trimmed_format_exc
                self.child.send('[Local Message] Call ChatGLM_onnx fail.' + '\n```\n' + trimmed_format_exc() + '\n```\n')
            # 请求处理结束，开始下一个循环
            self.child.send('[Finish]')

        

    def stream_chat(self, **kwargs):
        # 主进程执行
        self.threadLock.acquire()
        self.parent.send(kwargs)
        while True:
            res = self.parent.recv()
            if res != '[Finish]':
                yield res
            else:
                break
        self.threadLock.release()
    

#################################################################################
class ChatGLMModel():

    def __init__(self, onnx_model_path=onnx_model_path, tokenizer_path=tokenizer_path, profile=False) -> None:
        self.tokenizer = ChatGLMTokenizer(tokenizer_path)
        options = SessionOptions()
        options.enable_profiling = profile
        self.session = InferenceSession(onnx_model_path, options, providers=providers)
        self.eop_token_id = self.tokenizer["<eop>"]
        # input & output names
        self.past_names = [f"past_{name}_{i}" for i in range(28) for name in ["key", "value"]]
        self.present_names = [f"present_{name}_{i}" for i in range(28) for name in ["key", "value"]]
        self.output_names = ["logits"] + self.present_names

        # default kv_cache for first inference
        self.default_past_key_values = {
            k: np.zeros((1, 0, 32, 128), dtype=np.float32) for k in self.past_names
        }

    def prepare_input(self, prompt: str):
        input_ids, prefix_mask = self.tokenizer.encode(prompt)

        input_ids = np.array([input_ids], dtype=np.longlong)
        prefix_mask = np.array([prefix_mask], dtype=np.longlong)

        return input_ids, prefix_mask, self.default_past_key_values


    def sample_next_token(self, logits: np.ndarray, top_k=50, top_p=0.7, temperature=1):
        # softmax with temperature
        exp_logits = np.exp(logits / temperature)
        probs = exp_logits / np.sum(exp_logits)

        # top k
        top_k_idx = np.argsort(-probs)[:top_k]
        top_k_probs = probs[top_k_idx]

        # top p
        cumsum_probs = np.cumsum(top_k_probs)
        top_k_probs[(cumsum_probs - top_k_probs) > top_p] = 0.0
        top_k_probs = top_k_probs / np.sum(top_k_probs)

        # sample
        next_token = np.random.choice(top_k_idx, size=1, p=top_k_probs)
        return next_token[0].item()


    def generate_iterate(self, prompt: str, max_generated_tokens=100, top_k=50, top_p=0.7, temperature=1):
        input_ids, prefix_mask, past_key_values = self.prepare_input(prompt)
        output_tokens = []

        while True:
            inputs = {
                "input_ids": input_ids,
                "prefix_mask": prefix_mask,
                "use_past": np.array(len(output_tokens) > 0),
            }
            inputs.update(past_key_values)

            logits, *past_key_values = self.session.run(self.output_names, inputs)
            past_key_values = { k: v for k, v in zip(self.past_names, past_key_values) }

            next_token = self.sample_next_token(logits[0, -1], top_k=top_k, top_p=top_p, temperature=temperature)
            
            output_tokens += [next_token]

            if next_token == self.eop_token_id or len(output_tokens) > max_generated_tokens:
                break

            input_ids = np.array([[next_token]], dtype=np.longlong)
            prefix_mask = np.concatenate([prefix_mask, np.array([[0]], dtype=np.longlong)], axis=1)

            yield process_response(self.tokenizer.decode(output_tokens))

        return process_response(self.tokenizer.decode(output_tokens))

class ChatGLMTokenizer:
    def __init__(self, vocab_file):
        assert vocab_file is not None
        self.vocab_file = vocab_file
        self.special_tokens = ["[MASK]", "[gMASK]", "[sMASK]", "<unused_0>", "<sop>", "<eop>", "<ENC>", "<dBLOCK>"]
        self.text_tokenizer = SentencePieceProcessor(str(vocab_file))

    def __len__(self):
        return len(self.text_tokenizer)

    def __getitem__(self, key: str):
        return self.text_tokenizer[key]


    def preprocess(self, text: str, linebreak=True, whitespaces=True):
        if linebreak:
            text = text.replace("\\n", "<n>")
        if whitespaces:
            text = text.replace("\\t", "<|tab|>")
            text = re.sub(r" {2,80}", self.replace_spaces_with_blank, text)
        return text


    def encode(
        self, text: str, text_pair: str = None,
        linebreak=True, whitespaces=True,
        add_dummy_prefix=True, special_tokens=True,
    ) -> tuple[list[int], list[int]]:
        """
        text: Text to encode. Bidirectional part with a [gMASK] and an <sop> for causal LM.
        text_pair: causal LM part.
        linebreak: Whether to encode newline (\n) in text.
        whitespaces: Whether to encode multiple whitespaces or tab in text, useful for source code encoding.
        special_tokens: Whether to encode special token ([MASK], [gMASK], etc.) in text.
        add_dummy_prefix: Whether to add dummy blank space in the beginning.
        """
        text = self.preprocess(text, linebreak, whitespaces)
        if not add_dummy_prefix:
            text = "<n>" + text

        tokens = self.text_tokenizer.encode(text)
        prefix_mask = [1] * len(tokens)
        if special_tokens:
            tokens += [self.text_tokenizer["[gMASK]"], self.text_tokenizer["<sop>"]]
            prefix_mask += [1, 0]

        if text_pair is not None:
            text_pair = self.preprocess(text_pair, linebreak, whitespaces)
            pair_tokens = self.text_tokenizer.encode(text_pair)
            tokens += pair_tokens
            prefix_mask += [0] * len(pair_tokens)
            if special_tokens:
                tokens += [self.text_tokenizer["<eop>"]]
                prefix_mask += [0]

        return (tokens if add_dummy_prefix else tokens[2:]), prefix_mask


    def decode(self, text_ids: list[int]) -> str:
        text = self.text_tokenizer.decode(text_ids)
        text = text.replace("<n>", "\n")
        text = text.replace("<|tab|>", "\t")
        text = re.sub(r"<\|blank_(\d\d?)\|>", self.replace_blank_with_spaces, text)
        return text
    def replace_spaces_with_blank(match: re.Match[str]):
        return f"<|blank_{len(match.group())}|>"
    
    def replace_blank_with_spaces(match: re.Match[str]):
        return " " * int(match.group(1))

#################################################################################


def chat_template(history: list[tuple[str, str]], current: str):
    prompt = ""
    chat_round = 0
    for question, answer in history:
        prompt += f"[Round {chat_round}]\n问：{question}\n答：{answer}\n"
        chat_round += 1
    prompt += f"[Round {chat_round}]\n问：{current}\n答："
    return prompt

def process_response(response: str):
    response = response.strip()
    response = response.replace("[[训练时间]]", "2023年")
    punkts = [
        [",", "，"],
        ["!", "！"],
        [":", "："],
        [";", "；"],
        ["\?", "？"],
    ]
    for item in punkts:
        response = re.sub(r"([\u4e00-\u9fff])%s" % item[0], r"\1%s" % item[1], response)
        response = re.sub(r"%s([\u4e00-\u9fff])" % item[0], r"%s\1" % item[1], response)
    return response

#################################################################################


def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=[], console_slience=False):
    """
    多线程方法
    函数的说明请见 request_llm/bridge_all.py
    """
    if glm_onnx_handle is None:
        glm_onnx_handle = GetGLMHandle()
        if len(observe_window) >= 1: observe_window[0] = load_message + "\n\n" + glm_onnx_handle.info
        if not glm_onnx_handle.success:
            error = glm_onnx_handle.info
            glm_onnx_handle = None
            raise RuntimeError(error)

    # ChatGLM_onnx doesn't have a sys_prompt interface, so add the prompt to history
    history_feedin = []
    history_feedin.append(["What can I do?", sys_prompt])
    for i in range(len(history) // 2):
        history_feedin.append([history[2 * i], history[2 * i + 1]])

    watch_dog_patience = 5  # Watchdog patience, set to 5 seconds
    response = ""
    for response in glm_onnx_handle.stream_chat(query=inputs, history=history_feedin):
        print(response)
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
    return response

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    """
    单线程方法
    函数的说明请见 request_llm/bridge_all.py
    """
    chatbot.append((inputs, ""))

    global glm_onnx_handle
    if glm_onnx_handle is None:
        glm_onnx_handle = GetGLMHandle()
        chatbot[-1] = (inputs, load_message + "\n\n" + glm_onnx_handle.info)
        yield from update_ui(chatbot=chatbot, history=[])
        if not glm_onnx_handle.success:
            glm_onnx_handle = None
            return

    if additional_fn is not None:
        import core_functional
        importlib.reload(core_functional)  # Hot-reload prompt
        core_functional = core_functional.get_core_functions()
        if "PreProcess" in core_functional[additional_fn]:
            inputs = core_functional[additional_fn]["PreProcess"](inputs)
        inputs = core_functional[additional_fn]["Prefix"] + inputs + core_functional[additional_fn]["Suffix"]

    history_feedin = []
    history_feedin.append(["What can I do?", system_prompt])
    for i in range(len(history) // 2):
        history_feedin.append([history[2 * i], history[2 * i + 1]])

    response = "[Local Message]: 等待ChatGLM_onnx响应中 ..."
    for response in glm_onnx_handle.stream_chat(query=inputs, history=history_feedin):
        chatbot[-1] = (inputs, response)
        yield from update_ui(chatbot=chatbot, history=history)

    if response == "[Local Message]: 等待ChatGLM_onnx响应中 ...":
        response = "[Local Message]: ChatGLM_onnx响应异常 ..."
    history.extend([inputs, response])
    yield from update_ui(chatbot=chatbot, history=history)





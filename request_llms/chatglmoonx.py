






# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Source Code From https://huggingface.co/K024/ChatGLM-6b-onnx-u8s8/blob/main/model.py
# ------------------------------------------------------------------------------------------------------------------------
import re
import numpy as np
# import torch
from onnxruntime import InferenceSession, SessionOptions


# Currently `MatMulInteger` and `DynamicQuantizeLinear` are only supported on CPU,
# although they are documented as supported on CUDA.
providers = ["CPUExecutionProvider"]

# if torch.cuda.is_available():
#     providers = ["CUDAExecutionProvider"] + providers


# Default paths
tokenizer_path = "chatglm-6b-int8-onnx-merged/sentencepiece.model"
onnx_model_path = "chatglm-6b-int8-onnx-merged/chatglm-6b-int8.onnx"


# input & output names
past_names = [f"past_{name}_{i}" for i in range(28) for name in ["key", "value"]]
present_names = [f"present_{name}_{i}" for i in range(28) for name in ["key", "value"]]
output_names = ["logits"] + present_names


# default kv_cache for first inference
default_past_key_values = {
    k: np.zeros((1, 0, 32, 128), dtype=np.float32) for k in past_names
}


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


class ChatGLMModel():

    def __init__(self, onnx_model_path=onnx_model_path, tokenizer_path=tokenizer_path, profile=False) -> None:
        self.tokenizer = ChatGLMTokenizer(tokenizer_path)
        options = SessionOptions()
        options.enable_profiling = profile
        self.session = InferenceSession(onnx_model_path, options, providers=providers)
        self.eop_token_id = self.tokenizer["<eop>"]


    def prepare_input(self, prompt: str):
        input_ids, prefix_mask = self.tokenizer.encode(prompt)

        input_ids = np.array([input_ids], dtype=np.longlong)
        prefix_mask = np.array([prefix_mask], dtype=np.longlong)

        return input_ids, prefix_mask, default_past_key_values


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

            logits, *past_key_values = self.session.run(output_names, inputs)
            past_key_values = { k: v for k, v in zip(past_names, past_key_values) }

            next_token = self.sample_next_token(logits[0, -1], top_k=top_k, top_p=top_p, temperature=temperature)

            output_tokens += [next_token]

            if next_token == self.eop_token_id or len(output_tokens) > max_generated_tokens:
                break

            input_ids = np.array([[next_token]], dtype=np.longlong)
            prefix_mask = np.concatenate([prefix_mask, np.array([[0]], dtype=np.longlong)], axis=1)

            yield process_response(self.tokenizer.decode(output_tokens))

        return process_response(self.tokenizer.decode(output_tokens))














# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Source Code From https://huggingface.co/K024/ChatGLM-6b-onnx-u8s8/blob/main/tokenizer.py
# ------------------------------------------------------------------------------------------------------------------------

import re
from sentencepiece import SentencePieceProcessor


def replace_spaces_with_blank(match: re.Match[str]):
    return f"<|blank_{len(match.group())}|>"


def replace_blank_with_spaces(match: re.Match[str]):
    return " " * int(match.group(1))


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
            text = text.replace("\n", "<n>")
        if whitespaces:
            text = text.replace("\t", "<|tab|>")
            text = re.sub(r" {2,80}", replace_spaces_with_blank, text)
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
        text = re.sub(r"<\|blank_(\d\d?)\|>", replace_blank_with_spaces, text)
        return text



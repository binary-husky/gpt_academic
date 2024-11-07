model_name = "InternLM"
cmd_to_install = "`pip install -r request_llms/requirements_chatglm.txt`"

from transformers import AutoModel, AutoTokenizer
import time
import threading
import importlib
from toolbox import update_ui, get_conf, ProxyNetworkActivate
from multiprocessing import Process, Pipe
from .local_llm_class import LocalLLMHandle, get_local_llm_predict_fns


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model Utils
# ------------------------------------------------------------------------------------------------------------------------
def try_to_import_special_deps():
    import sentencepiece

def combine_history(prompt, hist):
    user_prompt = "<|User|>:{user}<eoh>\n"
    robot_prompt = "<|Bot|>:{robot}<eoa>\n"
    cur_query_prompt = "<|User|>:{user}<eoh>\n<|Bot|>:"
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

# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 Local Model
# ------------------------------------------------------------------------------------------------------------------------
class GetInternlmHandle(LocalLLMHandle):

    def load_model_info(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        self.model_name = model_name
        self.cmd_to_install = cmd_to_install

    def try_to_import_special_deps(self, **kwargs):
        """
        import something that will raise error if the user does not install requirement_*.txt
        """
        import sentencepiece

    def load_model_and_tokenizer(self):
        # 🏃‍♂️🏃‍♂️🏃‍♂️ 子进程执行
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        device = get_conf('LOCAL_MODEL_DEVICE')
        with ProxyNetworkActivate('Download_LLM'):
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
        import copy
        import warnings
        import torch.nn as nn
        from loguru import logger as logging 
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
        device = get_conf('LOCAL_MODEL_DEVICE')
        for k, v in inputs.items():
            inputs[k] = v.to(device)
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
                logging.warning(
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


# ------------------------------------------------------------------------------------------------------------------------
# 🔌💻 GPT-Academic Interface
# ------------------------------------------------------------------------------------------------------------------------
predict_no_ui_long_connection, predict = get_local_llm_predict_fns(GetInternlmHandle, model_name)
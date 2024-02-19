
from crazy_functions.json_fns.pydantic_io import GptJsonIO, JsonStringError
from request_llms.bridge_all import predict_no_ui_long_connection
def get_code_block(reply):
    import re
    pattern = r"```([\s\S]*?)```" # regex pattern to match code blocks
    matches = re.findall(pattern, reply) # find all code blocks in text
    if len(matches) == 1:
        return "```" + matches[0] + "```" #  code block
    raise RuntimeError("GPT is not generating proper code.")

def is_same_thing(a, b, llm_kwargs):
    from pydantic import BaseModel, Field
    class IsSameThing(BaseModel):
        is_same_thing: bool = Field(description="determine whether two objects are same thing.", default=False)

    def run_gpt_fn(inputs, sys_prompt, history=[]):
        return predict_no_ui_long_connection(
            inputs=inputs, llm_kwargs=llm_kwargs,
            history=history, sys_prompt=sys_prompt, observe_window=[]
        )

    gpt_json_io = GptJsonIO(IsSameThing)
    inputs_01 = "Identity whether the user input and the target is the same thing: \n target object: {a} \n user input object: {b} \n\n\n".format(a=a, b=b)
    inputs_01 += "\n\n\n Note that the user may describe the target object with a different language, e.g. cat and 猫 are the same thing."
    analyze_res_cot_01 = run_gpt_fn(inputs_01, "", [])

    inputs_02 = inputs_01 + gpt_json_io.format_instructions
    analyze_res = run_gpt_fn(inputs_02, "", [inputs_01, analyze_res_cot_01])

    try:
        res = gpt_json_io.generate_output_auto_repair(analyze_res, run_gpt_fn)
        return res.is_same_thing
    except JsonStringError as e:
        return False
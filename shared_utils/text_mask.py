import re
from functools import lru_cache

# 这段代码是使用Python编程语言中的re模块，即正则表达式库，来定义了一个正则表达式模式。
# 这个模式被编译成一个正则表达式对象，存储在名为const_extract_exp的变量中，以便于后续快速的匹配和查找操作。
# 这里解释一下正则表达式中的几个特殊字符：
# - . 表示任意单一字符。
# - * 表示前一个字符可以出现0次或多次。
# - ? 在这里用作非贪婪匹配，也就是说它会匹配尽可能少的字符。在(.*?)中，它确保我们匹配的任意文本是尽可能短的，也就是说，它会在</show_llm>和</show_render>标签之前停止匹配。
# - () 括号在正则表达式中表示捕获组。
# - 在这个例子中，(.*?)表示捕获任意长度的文本，直到遇到括号外部最近的限定符，即</show_llm>和</show_render>。

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=/1=-=-=-=-=-=-=-=-=-=-=-=-=-=/2-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
const_extract_re = re.compile(
    r"<gpt_academic_string_mask><show_llm>(.*?)</show_llm><show_render>(.*?)</show_render></gpt_academic_string_mask>"
)


@lru_cache(maxsize=128)
def apply_gpt_academic_string_mask(string, mode="show_all"):
    """
    根据字符串要给谁看（大模型，还是web渲染），对字符串进行处理，返回处理后的字符串
    示意图：https://mermaid.live/edit#pako:eNqlkUtLw0AUhf9KuOta0iaTplkIPlpduFJwoZEwJGNbzItpita2O6tF8QGKogXFtwu7cSHiq3-mk_oznFR8IYLgrGbuOd9hDrcCpmcR0GDW9ubNPKaBMDauuwI_A9M6YN-3y0bODwxsYos4BdMoBrTg5gwHF-d0mBH6-vqFQe58ed5m9XPW2uteX3Tubrj0ljLYcwxxR3h1zB43WeMs3G19yEM9uapDMe_NG9i2dagKw1Fee4c1D9nGEbtc-5n6HbNtJ8IyHOs8tbs7V2HrlDX2w2Y7XD_5haHEtQiNsOwfMVa_7TzsvrWIuJGo02qTrdwLk9gukQylHv3Afv1ML270s-HZUndrmW1tdA-WfvbM_jMFYuAQ6uCCxVdciTJ1CPLEITpo_GphypeouzXuw6XAmyi7JmgBLZEYlHwLB2S4gHMUO-9DH7tTnvf1CVoFFkBLSOk4QmlRTqpIlaWUHINyNFXjaQWpCYRURUKiWovBYo8X4ymEJFlECQUpqaQkJmuvWygPpg
    """
    if mode == "show_all":
        return string
    if mode == "show_llm":
        string = const_extract_re.sub(r"\1", string)
    elif mode == "show_render":
        string = const_extract_re.sub(r"\2", string)
    else:
        raise ValueError("Invalid mode")
    return string


@lru_cache(maxsize=128)
def build_gpt_academic_masked_string(text_show_llm="", text_show_render=""):
    """
    根据字符串要给谁看（大模型，还是web渲染），生成带掩码tag的字符串
    """
    return f"<gpt_academic_string_mask><show_llm>{text_show_llm}</show_llm><show_render>{text_show_render}</show_render></gpt_academic_string_mask>"


if __name__ == "__main__":
    # Test
    input_string = (
        "你好\n"
        + build_gpt_academic_masked_string(text_show_llm="mermaid", text_show_render="")
        + "你好\n"
    )
    print(
        apply_gpt_academic_string_mask(input_string, "show_llm")
    )  # Should print the strings with 'abc' in place of the academic mask tags
    print(
        apply_gpt_academic_string_mask(input_string, "show_render")
    )  # Should print the strings with 'xyz' in place of the academic mask tags

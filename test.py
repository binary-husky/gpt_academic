#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import gradio as gr

import func_box


class my_class():

    def __init__(self):
        self.numb = 0

    def coun_up(self):
        self.numb += 1


def set_obj(sts):
    btn = sts['btn'].update(visible=False)
    btn2 = sts['btn2'].update(visible=True)
    sts['obj'] = my_class()
    return sts, btn, btn2


def print_obj(sts):
    print(sts)
    print(sts['btn'], type(sts['btn']))
    sts['obj'].coun_up()
    print(sts['obj'].numb)

class ChatBotFrame:

    def __init__(self):
        self.cancel_handles = []
        self.initial_prompt = "Serve me as a writing and programming assistant."
        self.title_html = f"<h1 align=\"center\">ChatGPT For Tester"
        self.description = """代码开源和更新[地址🚀](https://github.com/binary-husky/chatgpt_academic)，感谢热情的[开发者们❤️](https://github.com/binary-husky/chatgpt_academic/graphs/contributors)"""


class ChatBot():
    def __init__(self):
        self.demo = gr.Blocks()

    def draw_test(self):
        with self.demo:
            # self.temp = gr.Markdown('')
            self.txt = gr.Textbox(label="Input", lines=2)
            self.btn = gr.Button(value="Submit1")
            self.btn2 = gr.Button(value="Submit2", visible=False)
            self.obj = gr.State({'obj': None, 'btn': self.btn, 'btn2': self.btn2})
            dic = func_box.YamlHandle().load()
            gr.EventData

            self.btn.click(set_obj, inputs=[self.obj], outputs=[self.obj, self.btn, self.btn2])
            self.btn2.click(print_obj, inputs=[self.obj], outputs=[self.txt])
        self.demo.launch()

if __name__ == '__main__':
    import gradio as gr


    def highlight_text(text, highlights):
        for h in highlights:
            text = text.replace(h, f"<span class='highlight' onclick='alert(\"{h}\")'>{h}</span>")
        return text


    app = gr.Interface(
        fn=highlight_text,
        inputs=["text", "highlighted_text"],
        outputs="html",
        interpretation="default",
        examples=[["The quick brown fox jumps over the lazy dog.", ["quick", "brown", "fox", "lazy"]]],
        layout="unaligned",
        capture_session=True
    )

    app.launch()











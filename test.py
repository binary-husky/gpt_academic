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


class ChatBot:
    def __init__(self):
        self.demo = gr.Blocks()

    def draw_test(self):
        with self.demo:
            with gr.Tab('122121', id='add_') as self.tab1:
                self.txt = gr.Textbox(label="Input", lines=2)
                self.btn = gr.Button(value="Submit1")
                self.pro_prompt_list = gr.Dataset(components=[gr.HTML(visible=False)], samples_per_page=10,label="Prompt usage frequency",
                                                  samples=[['None'],['None'],['None'],['None'],['None'],['None'],['None'],['None'],['None'],['None'],['None'],], type='index')
                self.list_staus = gr.State(self.pro_prompt_list)
                self.tab_state = gr.State(self.tab1)
            self.btn.click(fn=self.on_button_click, inputs=[self.tab_state], outputs=[self.tab1])
            self.demo.launch()

    # Add a new input textbox when self.btn is clicked
    def on_button_click(self, tab):
        tab.children.append(gr.Button(value="Submit2"))
        return tab


if __name__ == '__main__':
    ChatBot().draw_test()












#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :


import gradio as gr


def sentence_builder(quantity, xixi):
    return f"{quantity}_{xixi}"


with gr.Blocks() as demo:

    txt = gr.Textbox(label="Input", lines=2)
    txt_2 = gr.CheckboxGroup(['USA', "Japan"], value=['USA'], label='你好呀')
    txt_3 = gr.Textbox(value="", label="Output")
    btn = gr.Button(value="Submit")
    btn.click(sentence_builder, inputs=[txt, txt_2], outputs=[txt_3])

class ChatGPTForTester:

    def __init__(self):
        self.demo = gr.Blocks()

    def book(self):
        with self.demo:
            txt = gr.Textbox(label="Input", lines=2)
            txt_2 = gr.CheckboxGroup(['USA', "Japan"], value=['USA'], label='你好呀')
            txt_3 = gr.Textbox(value="", label="Output")
            btn = gr.Button(value="Submit")
            btn.click(sentence_builder, inputs=[txt, txt_2], outputs=[txt_3])

    def book2(self):
        with self.demo:
            txt = gr.Textbox(label="Input", lines=2)
            txt_2 = gr.CheckboxGroup(['USA', "Japan"], value=['USA'], label='我好呀')
            txt_3 = gr.Textbox(value="", label="Output")
            btn = gr.Button(value="Submit")
            btn.click(sentence_builder, inputs=[txt, txt_2], outputs=[txt_3])

    def main(self):
        self.book2()
        self.book()
        self.demo.launch()



class MyClass:

    def __init__(self):
        self.my_attribute1 = ''

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return []

    def my_method(self):
        self.test = '12312312312'
        print("This is my method.")

if __name__ == "__main__":
    __url = gr.State(f'https://')
    print(__url)




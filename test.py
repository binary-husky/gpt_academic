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

if __name__ == "__main__":
    demo.launch()


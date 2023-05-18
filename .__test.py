#! .\venv\
# encoding: utf-8
# @Time   : 2023/4/19
# @Author : Spike
# @Descr   :
import gradio as gr

with gr.Blocks() as demo:   # 绘制一个块对象，在此基础上可以使用Row、Column、Tab、Box等等布局元素
    gr.Markdown(f"<h1 align=\"center\">我是Bolcks</h1>")
    with gr.Row():
        with gr.Column(scale=100):    # 组件绘制在布局元素下，则会根据布局元素的规定展示
            gr.Markdown('# 这里是列1')
            chatbot = gr.Chatbot().style(height=400)
            status = gr.Markdown()

        with gr.Column(scale=50):
            gr.Markdown('# 这里是列2')
            i_say = gr.Textbox()
            submit = gr.Button(value='submit', variant='primary')
            with gr.Row():
                you_say = gr.Textbox(show_label=False, placeholder='没有任何用的输出框')
                Noo = gr.Button(value='没有任何用的按钮')


    def respond(say, chat_history):
        import random
        bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        chat_history.append((say, bot_message))
        return "我要开始胡说了", chat_history

    # 注册函数 fn=要注册的函数， input=函数接收的参数， outputs=函数处理后返回接收的组件
    submit.click(fn=respond, inputs=[i_say, chatbot], outputs=[status, chatbot])

demo.launch()
























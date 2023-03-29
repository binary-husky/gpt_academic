from pathlib import Path

import gradio as gr
from .check_proxy import check_proxy
from .functional import get_functionals
from .functional_crazy import get_crazy_functionals
from loguru import logger

from .predict import predict
from .utils import find_free_port, format_io
from .config import load_config
from .theme import adjust_theme

import threading
import webbrowser
import time


def auto_opentab_delay(port):
    def open():
        time.sleep(2)
        webbrowser.open_new_tab(f"http://localhost:{port}")

    t = threading.Thread(target=open)
    t.daemon = True
    t.start()


def main():
    # It is recommended that you copy a config_private.py to your own secrets, such as API and proxy URLs, to avoid accidentally uploading to GitHub and being seen by others
    configs = load_config()
    cancel_events = []
    # If WEB_PORT is -1, select the WEB port randomly
    PORT = find_free_port() if configs.WEB_PORT <= 0 else configs.WEB_PORT

    initial_prompt = "Serve me as a writing and programming assistant."
    title_html = """<h1 align="center">ChatGPT Academic Optimization</h1>"""
    # Inquiry record, python version is recommended to be 3.9+ (the newer the better)
    log_path = Path("gpt_log")
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / "chat_secrets.log"

    try:
        logger.add(log_file, level="INFO", encoding="utf-8")
    except Exception:
        logger.add(log_file, level="INFO")

    logger.info(
        f"All inquiry records will be automatically saved in the local directory {log_file.absolute()}, please pay attention to self-privacy protection!"
    )

    # Some common functional modules
    functional = get_functionals()

    # Test some crazy experimental functional modules
    crazy_functional = get_crazy_functionals()

    # Process the transformation of markdown text format
    gr.Chatbot.postprocess = format_io

    set_theme = adjust_theme()

    with gr.Blocks(theme=set_theme, analytics_enabled=False) as demo:
        gr.HTML(title_html)

        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot()
                chatbot.style(height=1200)
                chatbot.style()
                history = gr.State([])
                TRUE = gr.State(True)
                gr.State(False)
            with gr.Column(scale=1):
                with gr.Row():
                    txt = gr.Textbox(
                        show_label=False, placeholder="Input question here."
                    ).style(container=False)
                with gr.Row():
                    submitBtn = gr.Button("Submmit", variant="primary")
                with gr.Row():
                    resetBtn = gr.Button("Reset", variant="secondary")
                    resetBtn.style(size="sm")
                    stopBtn = gr.Button("Stop", variant="secondary")
                    stopBtn.style(size="sm")

                with gr.Row():
                    for k in functional:
                        variant = (
                            functional[k]["Color"]
                            if "Color" in functional[k]
                            else "secondary"
                        )

                        functional[k]["Button"] = gr.Button(k, variant=variant)

                    with gr.Column(scale=12):
                        project_path = gr.Textbox(
                            show_label=False, placeholder="project path."
                        ).style(container=False)

                    for k in crazy_functional:
                        with gr.Column(scale=1):
                            variant = (
                                crazy_functional[k]["Color"]
                                if "Color" in crazy_functional[k]
                                else "secondary"
                            )
                            crazy_functional[k]["Button"] = gr.Button(
                                k, variant=variant
                            )

                statusDisplay = gr.Markdown(f"{check_proxy(configs.proxies)}")
                systemPromptTxt = gr.Textbox(
                    show_label=True,
                    placeholder="System Prompt",
                    label="System prompt",
                    value=initial_prompt,
                ).style(container=True)

                # inputs, top_p, temperature, top_k, repetition_penalty
                with gr.Accordion("arguments", open=False):
                    top_p = gr.Slider(
                        minimum=0,
                        maximum=2.0,
                        value=1.0,
                        step=0.01,
                        interactive=True,
                        label="Top-p (nucleus sampling)",
                    )
                    temperature = gr.Slider(
                        minimum=-0,
                        maximum=5.0,
                        value=1.0,
                        step=0.01,
                        interactive=True,
                        label="Temperature",
                    )

        predict_args = dict(
            fn=predict,
            inputs=[txt, top_p, temperature, chatbot, history, systemPromptTxt],
            outputs=[chatbot, history, statusDisplay],
            show_progress=True,
        )
        dict(fn=lambda: "", inputs=[], outputs=[txt])

        cancel_events.append(txt.submit(**predict_args))
        cancel_events.append(submitBtn.click(**predict_args))
        resetBtn.click(
            lambda: ([], [], "Reset"), None, [chatbot, history, statusDisplay]
        )

        for k in functional:
            click_handle = functional[k]["Button"].click(
                predict,
                [
                    txt,
                    top_p,
                    temperature,
                    chatbot,
                    history,
                    systemPromptTxt,
                    TRUE,
                    gr.State(k),
                ],
                [chatbot, history, statusDisplay],
                show_progress=True,
            )
            cancel_events.append(click_handle)
        for k in crazy_functional:
            click_handle = crazy_functional[k]["Button"].click(
                crazy_functional[k]["Function"],
                [
                    # txt,
                    # crazy_functional[k]["Path"],
                    project_path,
                    top_p,
                    temperature,
                    chatbot,
                    history,
                    systemPromptTxt,
                    gr.State(PORT),
                ],
                [chatbot, history, statusDisplay],
            )
            cancel_events.append(click_handle)
        stopBtn.click(fn=None, inputs=None, outputs=None, cancels=cancel_events)

    auto_opentab_delay(PORT)
    demo.title = "ChatGPT Academic Optimization"
    demo.queue(concurrency_count=configs.THREADS).launch(
        server_name="0.0.0.0",
        share=True,
        server_port=PORT,
        auth=configs.AUTHENTICATION,
    )


def cli():
    try:
        main()
    except KeyboardInterrupt:
        gr.close_all()


if __name__ == "__main__":
    cli()

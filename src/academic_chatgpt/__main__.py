import threading
import time
import webbrowser
from pathlib import Path

import gradio as gr
from .check_proxy import check_proxy
from .functional import get_functionals
from .functional_crazy import get_crazy_functionals
from loguru import logger

from .predict import predict
from .utils import find_free_port, format_io
from .config import load_config


def main():
    # It is recommended that you copy a config_private.py to your own secrets, such as API and proxy URLs, to avoid accidentally uploading to GitHub and being seen by others
    configs = load_config()

    # If WEB_PORT is -1, select the WEB port randomly
    PORT = find_free_port() if configs.WEB_PORT <= 0 else configs.WEB_PORT

    initial_prompt = "Serve me as a writing and programming assistant."
    title_html = """<h1 align="center">ChatGPT Academic Optimization</h1>"""
    # Inquiry record, python version is recommended to be 3.9+ (the newer the better)

    Path("gpt_log").mkdir(parents=True, exist_ok=True)

    try:
        logger.add("gpt_log/chat_secrets.log", level="INFO", encoding="utf-8")
    except Exception:
        logger.add("gpt_log/chat_secrets.log", level="INFO")

    logger.info(
        "All inquiry records will be automatically saved in the local directory ./gpt_log/chat_secrets.log, please pay attention to self-privacy protection!"
    )

    # Some common functional modules
    functional = get_functionals()

    # Test some crazy experimental functional modules
    crazy_functional = get_crazy_functionals()

    # Process the transformation of markdown text format
    gr.Chatbot.postprocess = format_io

    # Make some style adjustments
    try:
        set_theme = gr.themes.Default(
            primary_hue=gr.themes.utils.colors.orange,
            font=[
                "ui-sans-serif",
                "system-ui",
                "sans-serif",
                gr.themes.utils.fonts.GoogleFont("Source Sans Pro"),
            ],
            font_mono=[
                "ui-monospace",
                "Consolas",
                "monospace",
                gr.themes.utils.fonts.GoogleFont("IBM Plex Mono"),
            ],
        )
    except Exception:
        set_theme = None
        logger.warning(
            "The gradio version is older and cannot customize fonts and colors"
        )

    with gr.Blocks(theme=set_theme, analytics_enabled=False) as demo:
        gr.HTML(title_html)
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot()
                chatbot.style(height=1000)
                chatbot.style()
                history = gr.State([])
                TRUE = gr.State(True)
                gr.State(False)
            with gr.Column(scale=1):
                with gr.Row():
                    with gr.Column(scale=12):
                        txt = gr.Textbox(
                            show_label=False, placeholder="Input question here."
                        ).style(container=False)
                    with gr.Column(scale=1):
                        submitBtn = gr.Button("Ask", variant="primary")
                with gr.Row():
                    for k in functional:
                        variant = (
                            functional[k]["Color"]
                            if "Color" in functional[k]
                            else "secondary"
                        )
                        functional[k]["Button"] = gr.Button(k, variant=variant)
                    for k in crazy_functional:
                        variant = (
                            crazy_functional[k]["Color"]
                            if "Color" in crazy_functional[k]
                            else "secondary"
                        )
                        crazy_functional[k]["Button"] = gr.Button(k, variant=variant)

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
                        minimum=-0,
                        maximum=1.0,
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

        txt.submit(
            predict,
            [txt, top_p, temperature, chatbot, history, systemPromptTxt],
            [chatbot, history, statusDisplay],
        )
        submitBtn.click(
            predict,
            [txt, top_p, temperature, chatbot, history, systemPromptTxt],
            [chatbot, history, statusDisplay],
            show_progress=True,
        )
        for k in functional:
            functional[k]["Button"].click(
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
        for k in crazy_functional:
            crazy_functional[k]["Button"].click(
                crazy_functional[k]["Function"],
                [
                    txt,
                    top_p,
                    temperature,
                    chatbot,
                    history,
                    systemPromptTxt,
                    gr.State(PORT),
                ],
                [chatbot, history, statusDisplay],
            )

    # Delay function, do some preparation work, and finally try to open the browser
    def auto_opentab_delay():
        logger.info(f"URL http://localhost:{PORT}")

        def open():
            time.sleep(2)

        webbrowser.open_new_tab(f"http://localhost:{PORT}")
        t = threading.Thread(target=open)
        t.daemon = True
        t.start()

    auto_opentab_delay()
    demo.title = "ChatGPT Academic Optimization"
    demo.queue().launch(server_name="0.0.0.0", share=True, server_port=PORT)


if __name__ == "__main__":
    main()

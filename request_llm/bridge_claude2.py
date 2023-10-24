import os
import json
import time
import gradio as gr
import logging
import traceback
import requests
import importlib
from pathlib import Path

# Additional imports
from dotenv import load_dotenv
from gradio.mix import NonBlockingMix
from threading import Thread
from typing import List

# Load environment variables from a .env file
load_dotenv()

# Constants
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TIMEOUT_SECONDS = 30
MAX_RETRY = 3

# Helper function to get the full error message
def get_full_error(chunk, stream_response):
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk

# Helper function to handle user input and interaction
def chatbot_conversation(inputs: str, history: List[str], system_prompt: str):
    # Initialize the chatbot response
    chatbot_response = ""

    try:
        # Prepare the chatbot prompt
        conversation = []
        for i in range(0, len(history), 2):
            user_message = history[i]
            bot_message = history[i + 1]
            if user_message:
                conversation.append({"role": "user", "content": user_message})
            if bot_message:
                conversation.append({"role": "assistant", "content": bot_message})

        # Add the user's new message to the conversation
        conversation.append({"role": "user", "content": inputs})

        # Generate the prompt
        prompt = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in conversation])

        # Send the request to the chatbot API
        chatbot_response = predict_chatbot(prompt, system_prompt)

    except Exception as e:
        traceback.print_exc()
        chatbot_response = "An error occurred. Please try again."

    return chatbot_response

# Function to predict chatbot response
def predict_chatbot(prompt: str, system_prompt: str):
    from anthropic import Anthropic

    # Retry in case of network issues
    for _ in range(MAX_RETRY):
        try:
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            stream = anthropic.completions.create(
                prompt=prompt,
                max_tokens_to_sample=4096,
                model="your_model_name_here",  # Replace with your GPT model name
                stream=True,
                temperature=0.7
            )
            response = ""
            for completion in stream:
                response += completion.completion

            return response

        except Exception as e:
            traceback.print_exc()
            time.sleep(2)

    return "Failed to get a response. Please try again later."

# Define the chatbot interface using Gradio
def chatbot_ui(inputs: str, history: List[str], system_prompt: str):
    chatbot_response = chatbot_conversation(inputs, history, system_prompt)
    return chatbot_response

# Run the chatbot interface
if __name__ == "__main__":
    gr.Interface(
        fn=chatbot_ui,
        inputs=["text", "text", "text"],
        outputs="text",
        layout="vertical",
        live=True,
        enable_queue=True
    ).launch()

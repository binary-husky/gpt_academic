import requests
import pickle
import io
import os
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from loguru import logger

class DockerServiceApiComModel(BaseModel):
    client_command: Optional[str] = Field(default=None, title="Client command", description="The command to be executed on the client side")
    client_file_attach: Optional[dict] = Field(default=None, title="Client file attach", description="The file to be attached to the client side")
    server_message: Optional[Any] = Field(default=None, title="Server standard error", description="The standard error from the server side")
    server_std_err: Optional[str] = Field(default=None, title="Server standard error", description="The standard error from the server side")
    server_std_out: Optional[str] = Field(default=None, title="Server standard output", description="The standard output from the server side")
    server_file_attach: Optional[dict] = Field(default=None, title="Server file attach", description="The file to be attached to the server side")

def process_received(received: DockerServiceApiComModel, save_file_dir="./daas_output", output_manifest=None):
    # Process the received data
    if received.server_message:
        try:
            output_manifest['server_message'] += received.server_message
        except:
            output_manifest['server_message'] = received.server_message
    if received.server_std_err:
        output_manifest['server_std_err'] += received.server_std_err
    if received.server_std_out:
        output_manifest['server_std_out'] += received.server_std_out
    if received.server_file_attach:
        # print(f"Recv file attach: {received.server_file_attach}")
        for file_name, file_content in received.server_file_attach.items():
            new_fp = os.path.join(save_file_dir, file_name)
            new_fp_dir = os.path.dirname(new_fp)
            if not os.path.exists(new_fp_dir):
                os.makedirs(new_fp_dir, exist_ok=True)
            with open(new_fp, 'wb') as f:
                f.write(file_content)
            output_manifest['server_file_attach'].append(new_fp)
    return output_manifest

def stream_daas(docker_service_api_com_model, server_url, save_file_dir):
    # Prepare the file
    # Pickle the object
    pickled_data = pickle.dumps(docker_service_api_com_model)

    # Create a file-like object from the pickled data
    file_obj = io.BytesIO(pickled_data)

    # Prepare the file for sending
    files = {'file': ('docker_service_api_com_model.pkl', file_obj, 'application/octet-stream')}

    # Send the POST request
    response = requests.post(server_url, files=files, stream=True)

    max_full_package_size = 1024 * 1024 * 1024 * 1  # 1 GB

    received_output_manifest = {}
    received_output_manifest['server_message'] = ""
    received_output_manifest['server_std_err'] = ""
    received_output_manifest['server_std_out'] = ""
    received_output_manifest['server_file_attach'] = []

    # Check if the request was successful
    if response.status_code == 200:
        # Process the streaming response
        chunk_buf = None
        for chunk in response.iter_content(max_full_package_size):
            if chunk:
                if chunk_buf is None: chunk_buf = chunk
                else: chunk_buf += chunk

                try:
                    received = pickle.loads(chunk_buf)
                    chunk_buf = None
                    received_output_manifest = process_received(received, save_file_dir, output_manifest = received_output_manifest)
                    yield received_output_manifest
                except Exception as e:
                    # logger.error(f"pickle data was truncated, but don't worry, we will continue to receive the rest of the data.")
                    continue

    else:
        logger.error(f"Error: Received status code {response.status_code}, response.text: {response.text}")

    return received_output_manifest
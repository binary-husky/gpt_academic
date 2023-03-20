FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN echo '[global]' > /etc/pip.conf && \
    echo 'index-url = https://mirrors.aliyun.com/pypi/simple/' >> /etc/pip.conf && \
    echo 'trusted-host = mirrors.aliyun.com' >> /etc/pip.conf

RUN pip3 install gradio requests[socks] mdtex2html

COPY . /gpt
WORKDIR /gpt


CMD ["python3", "main.py"]
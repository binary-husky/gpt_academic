# 此Dockerfile适用于“无本地模型”的迷你运行环境构建
# 如果需要使用chatglm等本地模型或者latex运行依赖，请参考 docker-compose.yml
# - 如何构建: 先修改 `config.py`， 然后 `docker build -t gpt-academic . `
# - 如何运行(Linux下): `docker run --rm -it --net=host gpt-academic `
# - 如何运行(其他操作系统，选择任意一个固定端口50923): `docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic `

FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 非必要步骤，更换pip源 （以下三行，可以删除）
RUN echo '[global]' > /etc/pip.conf && \
    echo 'index-url = https://mirrors.aliyun.com/pypi/simple/' >> /etc/pip.conf && \
    echo 'trusted-host = mirrors.aliyun.com' >> /etc/pip.conf

# 语音输出功能（以下1,2行更换阿里源，第3,4行安装ffmpeg，都可以删除） 
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update
RUN apt-get install ffmpeg -y
RUN apt-get clean

# 进入工作路径（必要）
WORKDIR /gpt

# 安装大部分依赖，利用Docker缓存加速以后的构建 （以下两行，可以删除）
COPY requirements.txt ./
RUN uv venv --python=3.12 && uv pip install --verbose -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
ENV PATH="/gpt/.venv/bin:$PATH"
RUN python -c 'import loguru'

# 装载项目文件，安装剩余依赖（必要）
COPY . .
RUN uv venv --python=3.12 && uv pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# # 非必要步骤，用于预热模块（可以删除）
RUN python -c 'from check_proxy import warm_up_modules; warm_up_modules()'

# 启动（必要）
CMD ["bash", "-c", "python main.py"]

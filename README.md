# ChatGPT 学术优化

**如果喜欢这个项目，请给它一个Star**
<div align="center">
<img src="公式.gif" width="700" >
</div>

<div align="center">
<img src="润色.gif" width="700" >
</div>



## 使用docker

``` sh
# 下载项目
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# 配置 海外Proxy 和 OpenAI API KEY
config.py
# 安装
docker build -t gpt-academic .
# 运行
docker run --rm -it --net=host gpt-academic

```

## 参考项目
```
https://github.com/Python-Markdown/markdown
https://github.com/gradio-app/gradio
https://github.com/polarwinkel/mdtex2html
https://github.com/GaiZhenbiao/ChuanhuChatGPT
```

# ChatGPT 学术优化

**如果喜欢这个项目，请给它一个Star；如果你发明了更好用的学术快捷键，欢迎发issue或者pull requests**

- 支持GPT输出的markdown表格
<div align="center">
<img src="demo2.jpg" width="500" >
</div>

- 如果输出包含公式，会同时以tex形式和渲染形式显示，方便复制和阅读
<div align="center">
<img src="demo.jpg" width="500" >
</div>

- 所有按钮都通过读取functional.py动态生成，可随意加自定义功能，解放粘贴板
<div align="center">
<img src="公式.gif" width="700" >
</div>

- 代码的显示自然也不在话下 https://www.bilibili.com/video/BV1F24y147PD/
<div align="center">
<img src="润色.gif" width="700" >
</div>

## 直接运行 (Windows or Linux)

```
# 下载项目
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# 在config.py中，配置 海外Proxy 和 OpenAI API KEY
- 1.如果你在国内，需要设置海外代理才能够使用 OpenAI API，你可以通过 config.py 文件来进行设置。
- 2.配置 OpenAI API KEY。你需要在 OpenAI 官网上注册并获取 API KEY。一旦你拿到了 API KEY，在 config.py 文件里配置好即可。
# 安装依赖
python -m pip install -r requirements.txt
# 运行
python main.py
```


## 使用docker (Linux)

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


## 自定义新的便捷按钮（学术快捷键自定义）
打开functional.py，只需看一眼就知道怎么弄了
例如
```
"英译中": {

    # 前缀，会被加在你的输入之前。例如，用来描述你的要求，例如翻译、解释代码、润色等等
    "Prefix": "请翻译把下面一段内容成中文，然后用一个markdown表格逐一解释文中出现的专有名词：\n\n", 
    
    # 后缀，会被加在你的输入之后。例如，配合前缀可以把你的输入内容用引号圈起来。
    "Suffix": "",
    
},
```
如果你发明了更好用的学术快捷键，欢迎发issue或者pull requests！

## 配置代理

在```config.py```中修改端口与代理软件对应
![image](https://user-images.githubusercontent.com/96192199/226571294-37a47cd9-4d40-4c16-97a2-d360845406f7.png)
![image](https://user-images.githubusercontent.com/96192199/226838985-e5c95956-69c2-4c23-a4dd-cd7944eeb451.png)
配置完成后，你可以用以下命令测试代理是否工作，如果一切正常，下面的代码将输出你的代理服务器所在地：
```
python check_proxy.py
```


## 参考项目
```
https://github.com/Python-Markdown/markdown
https://github.com/gradio-app/gradio
https://github.com/polarwinkel/mdtex2html
https://github.com/GaiZhenbiao/ChuanhuChatGPT
```

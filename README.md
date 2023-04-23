

# <img src="docs/logo.png" width="40" > ChatGPT 学术优化

**如果喜欢这个项目，请给它一个Star；如果你发明了更好用的快捷键或函数插件，欢迎发issue或者pull requests**

If you like this project, please give it a Star. If you've come up with more useful academic shortcuts or functional plugins, feel free to open an issue or pull request. We also have a README in [English|](docs/README_EN.md)[日本語|](docs/README_JP.md)[Русский|](docs/README_RS.md)[Français](docs/README_FR.md) translated by this project itself.

> **Note**
>
> 1.请注意只有**红颜色**标识的函数插件（按钮）才支持读取文件，部分插件位于插件区的**下拉菜单**中。另外我们以**最高优先级**欢迎和处理任何新插件的PR！
>
> 2.本项目中每个文件的功能都在自译解[`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)详细说明。随着版本的迭代，您也可以随时自行点击相关函数插件，调用GPT重新生成项目的自我解析报告。常见问题汇总在[`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)当中。
> 
> 3.已支持OpenAI和API2D的api-key共存，可在配置文件中填写如`API_KEY="openai-key1,openai-key2,api2d-key3"`。需要临时更换`API_KEY`时，在输入区输入临时的`API_KEY`然后回车键提交后即可生效。

<div align="center">
    
功能 | 描述
--- | ---
一键润色 | 支持一键润色、一键查找论文语法错误
一键中英互译 | 一键中英互译
一键代码解释 | 可以正确显示代码、解释代码
[自定义快捷键](https://www.bilibili.com/video/BV14s4y1E7jN) | 支持自定义快捷键
[配置代理服务器](https://www.bilibili.com/video/BV1rc411W7Dr) | 支持配置代理服务器
模块化设计 | 支持自定义高阶的函数插件与[函数插件]，插件支持[热更新](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[自我程序剖析](https://www.bilibili.com/video/BV1cj411A7VW) | [函数插件] [一键读懂](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)本项目的源代码
[程序剖析](https://www.bilibili.com/video/BV1cj411A7VW) | [函数插件] 一键可以剖析其他Python/C/C++/Java/Lua/...项目树
读论文 | [函数插件] 一键解读latex论文全文并生成摘要
Latex全文[翻译](https://www.bilibili.com/video/BV1nk4y1Y7Js/)、[润色](https://www.bilibili.com/video/BV1FT411H7c5/) | [函数插件] 一键翻译或润色latex论文
批量注释生成 | [函数插件] 一键批量生成函数注释
chat分析报告生成 | [函数插件] 运行后自动生成总结汇报
Markdown[中英互译](https://www.bilibili.com/video/BV1yo4y157jV/) | [函数插件] 看到上面5种语言的[README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md)了吗？
[arxiv小助手](https://www.bilibili.com/video/BV1LM4y1279X) | [函数插件] 输入arxiv文章url即可一键翻译摘要+下载PDF
[PDF论文全文翻译功能](https://www.bilibili.com/video/BV1KT411x7Wn) | [函数插件] PDF论文提取题目&摘要+翻译全文（多线程）
[谷歌学术统合小助手](https://www.bilibili.com/video/BV19L411U7ia) | [函数插件] 给定任意谷歌学术搜索页面URL，让gpt帮你[写relatedworks](https://www.bilibili.com/video/BV1GP411U7Az/)
公式/图片/表格显示 | 可以同时显示公式的tex形式和渲染形式，支持公式、代码高亮
多线程函数插件支持 | 支持多线调用chatgpt，一键处理海量文本或程序
启动暗色gradio[主题](https://github.com/binary-husky/chatgpt_academic/issues/173) | 在浏览器url后面添加```/?__dark-theme=true```可以切换dark主题
[多LLM模型](https://www.bilibili.com/video/BV1wT411p7yf)支持，[API2D](https://api2d.com/)接口支持 | 同时被GPT3.5、GPT4和[清华ChatGLM](https://github.com/THUDM/ChatGLM-6B)伺候的感觉一定会很不错吧？
huggingface免科学上网[在线体验](https://huggingface.co/spaces/qingxu98/gpt-academic) | 登陆huggingface后复制[此空间](https://huggingface.co/spaces/qingxu98/gpt-academic)
…… | ……

</div>


- 新界面（修改`config.py`中的LAYOUT选项即可实现“左右布局”和“上下布局”的切换）
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>


- 所有按钮都通过读取functional.py动态生成，可随意加自定义功能，解放粘贴板
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- 润色/纠错
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- 如果输出包含公式，会同时以tex形式和渲染形式显示，方便复制和阅读
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- 懒得看项目代码？整个工程直接给chatgpt炫嘴里
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- 多种大语言模型混合调用（ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4）
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

多种大语言模型混合调用[huggingface测试版](https://huggingface.co/spaces/qingxu98/academic-chatgpt-beta)（huggingface版不支持chatglm）


---

## 安装-方法1：直接运行 (Windows, Linux or MacOS)

1. 下载项目
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. 配置API_KEY和代理设置

在`config.py`中，配置 海外Proxy 和 OpenAI API KEY，说明如下
```
1. 如果你在国内，需要设置海外代理才能够顺利使用OpenAI API，设置方法请仔细阅读config.py（1.修改其中的USE_PROXY为True; 2.按照说明修改其中的proxies）。
2. 配置 OpenAI API KEY。支持任意数量的OpenAI的密钥和API2D的密钥共存/负载均衡，多个KEY用英文逗号分隔即可，例如输入 API_KEY="OpenAI密钥1,API2D密钥2,OpenAI密钥3,OpenAI密钥4"
3. 与代理网络有关的issue（网络超时、代理不起作用）汇总到 https://github.com/binary-husky/chatgpt_academic/issues/1
```
（P.S. 程序运行时会优先检查是否存在名为`config_private.py`的私密配置文件，并用其中的配置覆盖`config.py`的同名配置。因此，如果您能理解我们的配置读取逻辑，我们强烈建议您在`config.py`旁边创建一个名为`config_private.py`的新配置文件，并把`config.py`中的配置转移（复制）到`config_private.py`中。`config_private.py`不受git管控，可以让您的隐私信息更加安全。）


3. 安装依赖
```sh
# （选择I: 如熟悉python）推荐
python -m pip install -r requirements.txt
# 备注：使用官方pip源或者阿里pip源，其他pip源（如一些大学的pip）有可能出问题，临时换源方法：python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# （选择II: 如不熟悉python）使用anaconda，步骤也是类似的：
# （II-1）conda create -n gptac_venv python=3.11
# （II-2）conda activate gptac_venv
# （II-3）python -m pip install -r requirements.txt
```

如果需要支持清华ChatGLM后端，需要额外安装更多依赖（前提条件：熟悉python + 电脑配置够强）：
```sh
python -m pip install -r request_llm/requirements_chatglm.txt
```

4. 运行
```sh
python main.py
```

5. 测试函数插件
```
- 测试Python项目分析
    （选择1）input区域 输入 `./crazy_functions/test_project/python/dqn` ， 然后点击 "解析整个Python项目"
    （选择2）展开文件上传区，将python文件/包含python文件的压缩包拖拽进去，在出现反馈提示后， 然后点击 "解析整个Python项目"
- 测试自我代码解读（本项目自译解）
    点击 "[多线程Demo] 解析此项目本身（源码自译解）"
- 测试函数插件模板函数（要求gpt回答历史上的今天发生了什么），您可以根据此函数为模板，实现更复杂的功能
    点击 "[函数插件模板Demo] 历史上的今天"
- 函数插件区下拉菜单中有更多功能可供选择
```

## 安装-方法2：使用Docker

1. 仅ChatGPT（推荐大多数人选择）

``` sh
# 下载项目
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# 配置 “海外Proxy”， “API_KEY” 以及 “WEB_PORT” (例如50923) 等
用任意文本编辑器编辑 config.py
# 安装
docker build -t gpt-academic .
#（最后一步-选择1）在Linux环境下，用`--net=host`更方便快捷
docker run --rm -it --net=host gpt-academic
#（最后一步-选择2）在macOS/windows环境下，只能用-p选项将容器上的端口(例如50923)暴露给主机上的端口
docker run --rm -it -p 50923:50923 gpt-academic
```

2. ChatGPT+ChatGLM（需要对Docker熟悉 + 读懂Dockerfile + 电脑配置够强）

``` sh
# 修改Dockerfile
cd docs && nano Dockerfile+ChatGLM
# 构建 （Dockerfile+ChatGLM在docs路径下，请先cd docs）
docker build -t gpt-academic --network=host -f Dockerfile+ChatGLM .
# 运行 (1) 直接运行: 
docker run --rm -it --net=host --gpus=all gpt-academic
# 运行 (2) 我想运行之前进容器做一些调整: 
docker run --rm -it --net=host --gpus=all gpt-academic bash
```


## 安装-方法3：其他部署方式（需要云服务器知识与经验）

1. 远程云服务器部署
请访问[部署wiki-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

2. 使用WSL2（Windows Subsystem for Linux 子系统）
请访问[部署wiki-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

3. 如何在二级网址（如`http://localhost/subpath`）下运行
请访问[FastAPI运行说明](docs/WithFastapi.md)

## 安装-代理配置
1. 常规方法
[配置代理](https://github.com/binary-husky/chatgpt_academic/issues/1)

2. 纯新手教程
[纯新手教程](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E9%97%AE%E9%A2%98%E7%9A%84%E6%96%B0%E6%89%8B%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95%EF%BC%88%E6%96%B9%E6%B3%95%E5%8F%AA%E9%80%82%E7%94%A8%E4%BA%8E%E6%96%B0%E6%89%8B%EF%BC%89)


---

## 自定义新的便捷按钮 / 自定义函数插件

1. 自定义新的便捷按钮（学术快捷键）
任意文本编辑器打开`core_functional.py`，添加条目如下，然后重启程序即可。（如果按钮已经添加成功并可见，那么前缀、后缀都支持热修改，无需重启程序即可生效。）
例如
```
"超级英译中": {
    # 前缀，会被加在你的输入之前。例如，用来描述你的要求，例如翻译、解释代码、润色等等
    "Prefix": "请翻译把下面一段内容成中文，然后用一个markdown表格逐一解释文中出现的专有名词：\n\n", 
    
    # 后缀，会被加在你的输入之后。例如，配合前缀可以把你的输入内容用引号圈起来。
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. 自定义函数插件

编写强大的函数插件来执行任何你想得到的和想不到的任务。
本项目的插件编写、调试难度很低，只要您具备一定的python基础知识，就可以仿照我们提供的模板实现自己的插件功能。
详情请参考[函数插件指南](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)。


---


## 部分功能展示

1. 图片显示：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/228737599-bf0a9d9c-1808-4f43-ae15-dfcc7af0f295.png" width="800" >
</div>

2. 本项目的代码自译解（如果一个程序能够读懂并剖析自己）：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936618-9b487e4b-ab5b-4b6e-84c6-16942102e917.png" width="800" >
</div>

3. 其他任意Python/Cpp/Java/Go/Rect/...项目剖析：
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="800" >
</div>

4. Latex论文一键阅读理解与摘要生成
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227504406-86ab97cd-f208-41c3-8e4a-7000e51cf980.png" width="800" >
</div>

5. 自动报告生成
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

6. 模块化功能设计
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>


7. 源代码转译英文

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229720562-fe6c3508-6142-4635-a83d-21eb3669baee.png" height="400" >
</div>

8. 互联网在线信息综合

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/233575247-fb00819e-6d1b-4bb7-bd54-1d7528f03dd9.png" width="800" >
<img src="https://user-images.githubusercontent.com/96192199/233779501-5ce826f0-6cca-4d59-9e5f-b4eacb8cc15f.png" width="800" >

</div>



## Todo 与 版本规划:
- version 3.3+ (todo): NewBing支持
- version 3.2: 函数插件支持更多参数接口 (保存对话功能, 解读任意语言代码+同时询问任意的LLM组合)
- version 3.1: 支持同时问询多个gpt模型！支持api2d，支持多个apikey负载均衡
- version 3.0: 对chatglm和其他小型llm的支持
- version 2.6: 重构了插件结构，提高了交互性，加入更多插件
- version 2.5: 自更新，解决总结大工程源代码时文本过长、token溢出的问题
- version 2.4: (1)新增PDF全文翻译功能; (2)新增输入区切换位置的功能; (3)新增垂直布局选项; (4)多线程函数插件优化。
- version 2.3: 增强多线程交互性
- version 2.2: 函数插件支持热重载
- version 2.1: 可折叠式布局
- version 2.0: 引入模块化函数插件
- version 1.0: 基础功能

chatgpt_academic开发者QQ群：734063350

## 参考与学习

```
代码中参考了很多其他优秀项目中的设计，主要包括：

# 借鉴项目1：借鉴了ChuanhuChatGPT中诸多技巧
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# 借鉴项目2：清华ChatGLM-6B：
https://github.com/THUDM/ChatGLM-6B
```

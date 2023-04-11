
> **Note**
>
> 紧急：很抱歉2.60版本的一部分代码重构出错，目前2.67及以上版本已经解决，请您及时更新。
>

# ChatGPT 学术优化

**如果喜欢这个项目，请给它一个Star；如果你发明了更好用的快捷键或函数插件，欢迎发issue或者pull requests（dev分支）**

If you like this project, please give it a Star. If you've come up with more useful academic shortcuts or functional plugins, feel free to open an issue or pull request （to `dev` branch）.

> **Note**
>
> 1.请注意只有“红颜色”标识的函数插件（按钮）才支持读取文件。目前对pdf/word格式文件的支持插件正在逐步完善中，需要更多developer的帮助。
>
> 2.本项目中每个文件的功能都在自译解[`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)详细说明。随着版本的迭代，您也可以随时自行点击相关函数插件，调用GPT重新生成项目的自我解析报告。常见问题汇总在[`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)当中。
> 
> 3.如果您不太习惯部分中文命名的函数、注释或者界面，您可以随时点击相关函数插件，调用ChatGPT一键生成纯英文的项目源代码。
>


<div align="center">
    
功能 | 描述
--- | ---
一键润色 | 支持一键润色、一键查找论文语法错误
一键中英互译 | 一键中英互译
一键代码解释 | 可以正确显示代码、解释代码
[自定义快捷键](https://www.bilibili.com/video/BV14s4y1E7jN) | 支持自定义快捷键
[配置代理服务器](https://www.bilibili.com/video/BV1rc411W7Dr) | 支持配置代理服务器
模块化设计 | 支持自定义高阶的实验性功能与[函数插件]，插件支持[热更新](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[自我程序剖析](https://www.bilibili.com/video/BV1cj411A7VW) | [函数插件] [一键读懂](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)本项目的源代码
[程序剖析](https://www.bilibili.com/video/BV1cj411A7VW) | [函数插件] 一键可以剖析其他Python/C/C++/Java项目树
读论文 | [函数插件] 一键解读latex论文全文并生成摘要
Latex全文翻译、润色 | [函数插件] 一键翻译或润色latex论文
批量注释生成 | [函数插件] 一键批量生成函数注释
chat分析报告生成 | [函数插件] 运行后自动生成总结汇报
[arxiv小助手](https://www.bilibili.com/video/BV1LM4y1279X) | [函数插件] 输入arxiv文章url即可一键翻译摘要+下载PDF
[PDF论文全文翻译功能](https://www.bilibili.com/video/BV1KT411x7Wn) | [函数插件] PDF论文提取题目&摘要+翻译全文（多线程）
[谷歌学术统合小助手](https://www.bilibili.com/video/BV19L411U7ia) (Version>=2.45) | [函数插件] 给定任意谷歌学术搜索页面URL，让gpt帮你选择有趣的文章
公式显示 | 可以同时显示公式的tex形式和渲染形式
图片显示 | 可以在markdown中显示图片
多线程函数插件支持 | 支持多线调用chatgpt，一键处理海量文本或程序
支持GPT输出的markdown表格 | 可以输出支持GPT的markdown表格
启动暗色gradio[主题](https://github.com/binary-husky/chatgpt_academic/issues/173) | 在浏览器url后面添加```/?__dark-theme=true```可以切换dark主题
huggingface免科学上网[在线体验](https://huggingface.co/spaces/qingxu98/gpt-academic) | 登陆huggingface后复制[此空间](https://huggingface.co/spaces/qingxu98/gpt-academic)
[多LLM模型](https://www.bilibili.com/video/BV1EM411K7VH/)混合支持（[v3.0分支](https://github.com/binary-husky/chatgpt_academic/tree/v3.0)测试中） | 同时被ChatGPT和[清华ChatGLM](https://github.com/THUDM/ChatGLM-6B)伺候的感觉一定会很不错吧？
兼容[TGUI](https://github.com/oobabooga/text-generation-webui)接入更多样的语言模型 | 接入opt-1.3b, galactica-1.3b等模型（[v3.0分支](https://github.com/binary-husky/chatgpt_academic/tree/v3.0)测试中）
…… | ……

</div>

<!-- - 新界面（左：master主分支, 右：dev开发前沿） -->
- 新界面
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>



- 所有按钮都通过读取functional.py动态生成，可随意加自定义功能，解放粘贴板
<div align="center">
<img src="img/公式.gif" width="700" >
</div>

- 润色/纠错
<div align="center">
<img src="img/润色.gif" width="700" >
</div>


- 支持GPT输出的markdown表格
<div align="center">
<img src="img/demo2.jpg" width="500" >
</div>

- 如果输出包含公式，会同时以tex形式和渲染形式显示，方便复制和阅读
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>



- 懒得看项目代码？整个工程直接给chatgpt炫嘴里
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- 多种大语言模型混合调用（[v3.0分支](https://github.com/binary-husky/chatgpt_academic/tree/v3.0)测试中）

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231222778-34776885-a7f0-4f2c-b5f4-7cc2ef3ecb58.png" width="700" >
</div>



## 直接运行 (Windows, Linux or MacOS)

### 1. 下载项目
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

### 2. 配置API_KEY和代理设置

在`config.py`中，配置 海外Proxy 和 OpenAI API KEY，说明如下
```
1. 如果你在国内，需要设置海外代理才能够顺利使用 OpenAI API，设置方法请仔细阅读config.py（1.修改其中的USE_PROXY为True; 2.按照说明修改其中的proxies）。
2. 配置 OpenAI API KEY。你需要在 OpenAI 官网上注册并获取 API KEY。一旦你拿到了 API KEY，在 config.py 文件里配置好即可。
3. 与代理网络有关的issue（网络超时、代理不起作用）汇总到 https://github.com/binary-husky/chatgpt_academic/issues/1
```
（P.S. 程序运行时会优先检查是否存在名为`config_private.py`的私密配置文件，并用其中的配置覆盖`config.py`的同名配置。因此，如果您能理解我们的配置读取逻辑，我们强烈建议您在`config.py`旁边创建一个名为`config_private.py`的新配置文件，并把`config.py`中的配置转移（复制）到`config_private.py`中。`config_private.py`不受git管控，可以让您的隐私信息更加安全。）


### 3. 安装依赖
```sh
# （选择一）推荐
python -m pip install -r requirements.txt   

# （选择二）如果您使用anaconda，步骤也是类似的：
# （选择二.1）conda create -n gptac_venv python=3.11
# （选择二.2）conda activate gptac_venv
# （选择二.3）python -m pip install -r requirements.txt

# 备注：使用官方pip源或者阿里pip源，其他pip源（如一些大学的pip）有可能出问题，临时换源方法： 
# python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 4. 运行
```sh
python main.py
```

### 5. 测试实验性功能
```
- 测试C++项目头文件分析
    input区域 输入 `./crazy_functions/test_project/cpp/libJPG` ， 然后点击 "[实验] 解析整个C++项目（input输入项目根路径）"
- 测试给Latex项目写摘要
    input区域 输入 `./crazy_functions/test_project/latex/attention` ， 然后点击 "[实验] 读tex论文写摘要（input输入项目根路径）"
- 测试Python项目分析
    input区域 输入 `./crazy_functions/test_project/python/dqn` ， 然后点击 "[实验] 解析整个py项目（input输入项目根路径）"
- 测试自我代码解读
    点击 "[实验] 请解析并解构此项目本身"
- 测试实验功能模板函数（要求gpt回答历史上的今天发生了什么），您可以根据此函数为模板，实现更复杂的功能
    点击 "[实验] 实验功能函数模板"
```

## 使用docker (Linux)

``` sh
# 下载项目
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# 配置 海外Proxy 和 OpenAI API KEY
用任意文本编辑器编辑 config.py
# 安装
docker build -t gpt-academic .
# 运行
docker run --rm -it --net=host gpt-academic

# 测试实验性功能
## 测试自我代码解读
点击 "[实验] 请解析并解构此项目本身"
## 测试实验功能模板函数（要求gpt回答历史上的今天发生了什么），您可以根据此函数为模板，实现更复杂的功能
点击 "[实验] 实验功能函数模板"
##（请注意在docker中运行时，需要额外注意程序的文件访问权限问题）
## 测试C++项目头文件分析
input区域 输入 ./crazy_functions/test_project/cpp/libJPG ， 然后点击 "[实验] 解析整个C++项目（input输入项目根路径）"
## 测试给Latex项目写摘要
input区域 输入 ./crazy_functions/test_project/latex/attention ， 然后点击 "[实验] 读tex论文写摘要（input输入项目根路径）"
## 测试Python项目分析
input区域 输入 ./crazy_functions/test_project/python/dqn ， 然后点击 "[实验] 解析整个py项目（input输入项目根路径）"

```

## 其他部署方式
- 使用WSL2（Windows Subsystem for Linux 子系统）
请访问[部署wiki-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

- nginx远程部署
请访问[部署wiki-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E7%9A%84%E6%8C%87%E5%AF%BC)


## 自定义新的便捷按钮（学术快捷键自定义）
打开functional.py，添加条目如下，然后重启程序即可。（如果按钮已经添加成功并可见，那么前缀、后缀都支持热修改，无需重启程序即可生效。）
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


如果你发明了更好用的学术快捷键，欢迎发issue或者pull requests！

## 配置代理
### 方法一：常规方法
在```config.py```中修改端口与代理软件对应

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226571294-37a47cd9-4d40-4c16-97a2-d360845406f7.png" width="500" >
<img src="https://user-images.githubusercontent.com/96192199/226838985-e5c95956-69c2-4c23-a4dd-cd7944eeb451.png" width="500" >
</div>

配置完成后，你可以用以下命令测试代理是否工作，如果一切正常，下面的代码将输出你的代理服务器所在地：
```
python check_proxy.py
```
### 方法二：纯新手教程
[纯新手教程](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E9%97%AE%E9%A2%98%E7%9A%84%E6%96%B0%E6%89%8B%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95%EF%BC%88%E6%96%B9%E6%B3%95%E5%8F%AA%E9%80%82%E7%94%A8%E4%BA%8E%E6%96%B0%E6%89%8B%EF%BC%89)

## 兼容性测试

### 图片显示：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/228737599-bf0a9d9c-1808-4f43-ae15-dfcc7af0f295.png" width="800" >
</div>


### 如果一个程序能够读懂并剖析自己：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936618-9b487e4b-ab5b-4b6e-84c6-16942102e917.png" width="800" >
</div>

### 其他任意Python/Cpp项目剖析：
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="800" >
</div>

### Latex论文一键阅读理解与摘要生成
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227504406-86ab97cd-f208-41c3-8e4a-7000e51cf980.png" width="800" >
</div>

### 自动报告生成
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

### 模块化功能设计
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>


### 源代码转译英文

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229720562-fe6c3508-6142-4635-a83d-21eb3669baee.png" height="400" >
</div>

## Todo 与 版本规划:

- version 3 (Todo): 
- - 支持gpt4和其他更多llm
- version 2.4+ (Todo): 
- - 总结大工程源代码时文本过长、token溢出的问题
- - 实现项目打包部署
- - 函数插件参数接口优化
- - 自更新
- version 2.4: (1)新增PDF全文翻译功能; (2)新增输入区切换位置的功能; (3)新增垂直布局选项; (4)多线程函数插件优化。
- version 2.3: 增强多线程交互性
- version 2.2: 函数插件支持热重载
- version 2.1: 可折叠式布局
- version 2.0: 引入模块化函数插件
- version 1.0: 基础功能

## 参考与学习


```
代码中参考了很多其他优秀项目中的设计，主要包括：

# 借鉴项目1：借鉴了ChuanhuChatGPT中读取OpenAI json的方法、记录历史问询记录的方法以及gradio queue的使用技巧
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# 借鉴项目2：
https://github.com/THUDM/ChatGLM-6B

```

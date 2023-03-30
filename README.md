

# ChatGPT 学术优化

**如果喜欢这个项目，请给它一个Star；如果你发明了更好用的学术快捷键，欢迎发issue或者pull requests**

If you like this project, please give it a Star. If you've come up with more useful academic shortcuts, feel free to open an issue or pull request.

```
代码中参考了很多其他优秀项目中的设计，主要包括：

# 借鉴项目1：借鉴了ChuanhuChatGPT中读取OpenAI json的方法、记录历史问询记录的方法以及gradio queue的使用技巧
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# 借鉴项目2：借鉴了mdtex2html中公式处理的方法
https://github.com/polarwinkel/mdtex2html

项目使用OpenAI的gpt-3.5-turbo模型，期待gpt-4早点放宽门槛😂
```

> **Note**
>
> 1.请注意只有“红颜色”标识的函数插件（按钮）才支持读取文件。目前暂不能完善地支持pdf格式文献的翻译解读，尚不支持word格式文件的读取。
>
> 2.本项目中每个文件的功能都在自译解[`project_self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)详细说明。随着版本的迭代，您也可以随时自行点击相关函数插件，调用GPT重新生成项目的自我解析报告。常见问题汇总在[`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)当中。
> 
> 3.如果您不太习惯部分中文命名的函数，您可以随时点击相关函数插件，调用GPT一键生成纯英文的项目源代码。

<div align="center">
    
功能 | 描述
--- | ---
一键润色 | 支持一键润色、一键查找论文语法错误
一键中英互译 | 一键中英互译
一键代码解释 | 可以正确显示代码、解释代码
自定义快捷键 | 支持自定义快捷键
配置代理服务器 | 支持配置代理服务器
模块化设计 | 支持自定义高阶的实验性功能
自我程序剖析 | [实验性功能] 一键读懂本项目的源代码
程序剖析 | [实验性功能] 一键可以剖析其他Python/C++项目
读论文 | [实验性功能] 一键解读latex论文全文并生成摘要
批量注释生成 | [实验性功能] 一键批量生成函数注释
chat分析报告生成 | [实验性功能] 运行后自动生成总结汇报
公式显示 | 可以同时显示公式的tex形式和渲染形式
图片显示 | 可以在markdown中显示图片
支持GPT输出的markdown表格 | 可以输出支持GPT的markdown表格
…… | ……

</div>

- 新界面
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/228600410-7d44e34f-63f1-4046-acb8-045cb05da8bb.png" width="700" >
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
<img src="img/demo.jpg" width="500" >
</div>


- 懒得看项目代码？整个工程直接给chatgpt炫嘴里
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

## 直接运行 (Windows, Linux or MacOS)

下载项目

```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

我们建议将`config.py`复制为`config_private.py`并将后者用作个性化配置文件以避免`config.py`中的变更影响你的使用或不小心将包含你的OpenAI API KEY的`config.py`提交至本项目。

```sh
cp config.py config_private.py
```

在`config_private.py`中，配置 海外Proxy 和 OpenAI API KEY
```
1. 如果你在国内，需要设置海外代理才能够使用 OpenAI API，你可以通过 config.py 文件来进行设置。
2. 配置 OpenAI API KEY。你需要在 OpenAI 官网上注册并获取 API KEY。一旦你拿到了 API KEY，在 config.py 文件里配置好即可。
```
安装依赖

```sh
python -m pip install -r requirements.txt
```

或者，如果你希望使用`conda`

```sh
conda create -n gptac 'gradio>=3.23' requests
conda activate gptac
python3 -m pip install mdtex2html
```

运行

```sh
python main.py
```

测试实验性功能
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

与代理网络有关的issue（网络超时、代理不起作用）汇总到 https://github.com/binary-husky/chatgpt_academic/issues/1

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

## 使用WSL2（Windows Subsystem for Linux 子系统）
选择这种方式默认您已经具备一定基本知识，因此不再赘述多余步骤。如果不是这样，您可以从[这里](https://learn.microsoft.com/zh-cn/windows/wsl/about)或GPT处获取更多关于子系统的信息。

WSL2可以配置使用Windows侧的代理上网，前置步骤可以参考[这里](https://www.cnblogs.com/tuilk/p/16287472.html)
由于Windows相对WSL2的IP会发生变化，我们需要每次启动前先获取这个IP来保证顺利访问，将config.py中设置proxies的部分更改为如下代码：
```python
import subprocess
cmd_get_ip = 'grep -oP  "(\d+\.)+(\d+)" /etc/resolv.conf'
ip_proxy = subprocess.run(
        cmd_get_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
        ).stdout.strip() # 获取windows的IP
proxies = { "http": ip_proxy + ":51837", "https": ip_proxy + ":51837", } # 请自行修改
```
在启动main.py后，可以在windows浏览器中访问服务。至此测试、使用与上面其他方法无异。 

## 远程部署
如果您需要将本项目部署到公网服务器，请设置好`PORT`（固定端口）和`AUTHENTICATION`（避免您的`APIKEY`被滥用），并将`main.py`的最后一句话修改为：
```python
demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", share=False, server_port=PORT, auth=AUTHENTICATION) # 取消share
```

如果您打算使用域名，强烈建议用`nginx`配置反向代理。需要往配置文件增加的内容如下：
```nginx
http {
    # 其他配置
    #......
    # 配置websocket
    map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
    }
upstream my_chataca {
	# 这里配置负载均衡策略
    ip_hash; # 如果使用负载均衡，建议使用ip_hash
    # 假设本项目运行的端口为8080
	server 127.0.0.1:8080 max_fails=3 fail_timeout=10;
}

server {
	listen 80;
	listen [::]:80;
	server_name yourdomain.com;
	return 301 https://yourdomain.com$request_uri;# 强制使用https
}

server {
	listen 443 ssl http2;
	listen [::]:443 ssl http2;
	server_name yourdomain.com;
	ssl_protocols TLSv1.2 TLSv1.3;
	ssl_prefer_server_ciphers on;
	ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
	ssl_session_tickets off;
	ssl_session_timeout 1d;
	ssl_session_cache shared:SSL:10m;
	add_header Strict-Transport-Security
		"max-age=31536000; includeSubDomains"
		always;
	ssl_certificate xxxxxx.pem; # 证书文件
	ssl_certificate_key xxxxxx.key; # 证书文件

	location / {
		proxy_pass http://my_chataca;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto https;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection $connection_upgrade;
	}
}

}
```


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

在```config.py```中修改端口与代理软件对应

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226571294-37a47cd9-4d40-4c16-97a2-d360845406f7.png" width="500" >
<img src="https://user-images.githubusercontent.com/96192199/226838985-e5c95956-69c2-4c23-a4dd-cd7944eeb451.png" width="500" >
</div>

配置完成后，你可以用以下命令测试代理是否工作，如果一切正常，下面的代码将输出你的代理服务器所在地：
```
python check_proxy.py
```

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
<img src="https://user-images.githubusercontent.com/96192199/227504981-4c6c39c0-ae79-47e6-bffe-0e6442d9da65.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

## Todo:

- (Top Priority) 调用另一个开源项目text-generation-webui的web接口，使用其他llm模型
- 总结大工程源代码时，文本过长、token溢出的问题（目前的方法是直接二分丢弃处理溢出，过于粗暴，有效信息大量丢失）
- UI不够美观


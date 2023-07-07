# 通过微软Azure云服务申请 Openai API

由于Openai和微软的关系，现在是可以通过微软的Azure云计算服务直接访问openai的api，免去了注册和网络的问题。

快速入门的官方文档的链接是：[快速入门 - 开始通过 Azure OpenAI 服务使用 ChatGPT 和 GPT-4 - Azure OpenAI Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/chatgpt-quickstart?pivots=programming-language-python)

# 申请API

按文档中的“先决条件”的介绍，出了编程的环境以外，还需要以下三个条件：

1.  Azure账号并创建订阅

2.  为订阅添加Azure OpenAI 服务

3.  部署模型

## Azure账号并创建订阅

### Azure账号

创建Azure的账号时最好是有微软的账号，这样似乎更容易获得免费额度（第一个月的200美元，实测了一下，如果用一个刚注册的微软账号登录Azure的话，并没有这一个月的免费额度）。

创建Azure账号的网址是：[立即创建 Azure 免费帐户 | Microsoft Azure](https://azure.microsoft.com/zh-cn/free/)

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_944786_iH6AECuZ_tY0EaBd_1685327219?w=1327\&h=695\&type=image/png)

打开网页后，点击 “免费开始使用” 会跳转到登录或注册页面，如果有微软的账户，直接登录即可，如果没有微软账户，那就需要到微软的网页再另行注册一个。

注意，Azure的页面和政策时不时会变化，已实际最新显示的为准就好。

### 创建订阅

注册好Azure后便可进入主页：

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_444847_tk-9S-pxOYuaLs_K_1685327675?w=1865\&h=969\&type=image/png)

首先需要在订阅里进行添加操作，点开后即可进入订阅的页面：

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_612820_z_1AlaEgnJR-rUl0_1685327892?w=1865\&h=969\&type=image/png)

第一次进来应该是空的，点添加即可创建新的订阅（可以是“免费”或者“即付即用”的订阅），其中订阅ID是后面申请Azure OpenAI需要使用的。

## 为订阅添加Azure OpenAI服务

之后回到首页，点Azure OpenAI即可进入OpenAI服务的页面（如果不显示的话，则在首页上方的搜索栏里搜索“openai”即可）。

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_269759_nExkGcPC0EuAR5cp_1685328130?w=1865\&h=969\&type=image/png)

不过现在这个服务还不能用。在使用前，还需要在这个网址申请一下：

[Request Access to Azure OpenAI Service (microsoft.com)](https://customervoice.microsoft.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR7en2Ais5pxKtso_Pz4b1_xUOFA5Qk1UWDRBMjg0WFhPMkIzTzhKQ1dWNyQlQCN0PWcu)

这里有二十来个问题，按照要求和自己的实际情况填写即可。

其中需要注意的是

1.  千万记得填对"订阅ID"

2.  需要填一个公司邮箱（可以不是注册用的邮箱）和公司网址

之后，在回到上面那个页面，点创建，就会进入创建页面了：

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_72708_9d9JYhylPVz3dFWL_1685328372?w=824\&h=590\&type=image/png)

需要填入“资源组”和“名称”，按照自己的需要填入即可。

完成后，在主页的“资源”里就可以看到刚才创建的“资源”了，点击进入后，就可以进行最后的部署了。

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_871541_CGCnbgtV9Uk1Jccy_1685329861?w=1217\&h=628\&type=image/png)

## 部署模型

进入资源页面后，在部署模型前，可以先点击“开发”，把密钥和终结点记下来。

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_852567_dxCZOrkMlWDSLH0d_1685330736?w=856\&h=568\&type=image/png)

之后，就可以去部署模型了，点击“部署”即可，会跳转到 Azure OpenAI Stuido 进行下面的操作：

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_169225_uWs1gMhpNbnwW4h2_1685329901?w=1865\&h=969\&type=image/png)

进入 Azure OpenAi Studio 后，点击新建部署，会弹出如下对话框：

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_391255_iXUSZAzoud5qlxjJ_1685330224?w=656\&h=641\&type=image/png)

在这里选 gpt-35-turbo 或需要的模型并按需要填入“部署名”即可完成模型的部署。

![](https://wdcdn.qpic.cn/MTY4ODg1Mjk4NzI5NTU1NQ_724099_vBaHcUilsm1EtPgK_1685330396?w=1869\&h=482\&type=image/png)

这个部署名需要记下来。

到现在为止，申请操作就完成了，需要记下来的有下面几个东西：

● 密钥（对应AZURE_API_KEY，1或2都可以）

● 终结点 （对应AZURE_ENDPOINT）

● 部署名（对应AZURE_ENGINE，不是模型名）


# 修改 config.py

```
LLM_MODEL = "azure-gpt-3.5"  # 指定启动时的默认模型，当然事后从下拉菜单选也ok

AZURE_ENDPOINT = "填入终结点"
AZURE_API_KEY = "填入azure openai api的密钥"
AZURE_API_VERSION = "2023-05-15"  # 默认使用 2023-05-15 版本，无需修改
AZURE_ENGINE = "填入部署名" # 见上图

```


# 关于费用

Azure OpenAI API 还是需要一些费用的（免费订阅只有1个月有效期）

具体可以可以看这个网址 ：[Azure OpenAI 服务 - 定价| Microsoft Azure](https://azure.microsoft.com/zh-cn/pricing/details/cognitive-services/openai-service/?cdn=disable)

并非网上说的什么“一年白嫖”，但注册方法以及网络问题都比直接使用openai的api要简单一些。

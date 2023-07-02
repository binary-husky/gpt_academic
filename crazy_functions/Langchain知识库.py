from comm_tools.toolbox import CatchException, update_ui, ProxyNetworkActivate
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive, get_files_from_everything



@CatchException
def 知识库问答(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数, 如温度和top_p等, 一般原样传递下去就行
    plugin_kwargs   插件模型的参数，暂时没有用武之地
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    history = []    # 清空历史，以免输入溢出
    chatbot.append(("这是什么功能？", "[Local Message] 从一批文件(txt, md, tex)中读取数据构建知识库, 然后进行问答。"))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # resolve deps
    try:
        from zh_langchain import construct_vector_store
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        from .crazy_utils import knowledge_archive_interface
    except Exception as e:
        chatbot.append(
            ["依赖不足", 
             "导入依赖失败。正在尝试自动安装，请查看终端的输出或耐心等待..."]
        )
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        from .crazy_utils import try_install_deps
        try_install_deps(['zh_langchain==0.2.1'])
    
    # < --------------------读取参数--------------- >
    if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
    kai_id = plugin_kwargs.get("advanced_arg", 'default')

    # < --------------------读取文件--------------- >
    file_manifest = []
    spl = ["txt", "doc", "docx", "email", "epub", "html", "json", "md", "msg", "pdf", "ppt", "pptx", "rtf"]
    for sp in spl:
        _, file_manifest_tmp, _ = get_files_from_everything(txt, type=f'.{sp}')
        file_manifest += file_manifest_tmp
    
    if len(file_manifest) == 0:
        chatbot.append(["没有找到任何可读取文件", "当前支持的格式包括: txt, md, docx, pptx, pdf, json等"])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return
    
    # < -------------------预热文本向量化模组--------------- >
    chatbot.append(['<br/>'.join(file_manifest), "正在预热文本向量化模组, 如果是第一次运行, 将消耗较长时间下载中文向量化模型..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    print('Checking Text2vec ...')
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    with ProxyNetworkActivate():    # 临时地激活代理网络
        HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")

    # < -------------------构建知识库--------------- >
    chatbot.append(['<br/>'.join(file_manifest), "正在构建知识库..."])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    print('Establishing knowledge archive ...')
    with ProxyNetworkActivate():    # 临时地激活代理网络
        kai = knowledge_archive_interface()
        kai.feed_archive(file_manifest=file_manifest, id=kai_id)
    kai_files = kai.get_loaded_file()
    kai_files = '<br/>'.join(kai_files)
    # chatbot.append(['知识库构建成功', "正在将知识库存储至cookie中"])
    # yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
    # chatbot._cookies['langchain_plugin_embedding'] = kai.get_current_archive_id()
    # chatbot._cookies['lock_plugin'] = 'crazy_functions.Langchain知识库->读取知识库作答'
    # chatbot.append(['完成', "“根据知识库作答”函数插件已经接管问答系统, 提问吧! 但注意, 您接下来不能再使用其他插件了，刷新页面即可以退出知识库问答模式。"])
    chatbot.append(['构建完成', f"当前知识库内的有效文件：\n\n---\n\n{kai_files}\n\n---\n\n请切换至“知识库问答”插件进行知识库访问, 或者使用此插件继续上传更多文件。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

@CatchException
def 读取知识库作答(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port=-1):
    # resolve deps
    try:
        from zh_langchain import construct_vector_store
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        from .crazy_utils import knowledge_archive_interface
    except Exception as e:
        chatbot.append(["依赖不足", "导入依赖失败。正在尝试自动安装，请查看终端的输出或耐心等待..."])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        from .crazy_utils import try_install_deps
        try_install_deps(['zh_langchain==0.2.1'])

    # < -------------------  --------------- >
    kai = knowledge_archive_interface()

    if 'langchain_plugin_embedding' in chatbot._cookies:
        resp, prompt = kai.answer_with_archive_by_id(txt, chatbot._cookies['langchain_plugin_embedding'])
    else:
        if ("advanced_arg" in plugin_kwargs) and (plugin_kwargs["advanced_arg"] == ""): plugin_kwargs.pop("advanced_arg")
        kai_id = plugin_kwargs.get("advanced_arg", 'default')
        resp, prompt = kai.answer_with_archive_by_id(txt, kai_id)

    chatbot.append((txt, '[Local Message] ' + prompt))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=prompt, inputs_show_user=txt, 
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=[], 
        sys_prompt=system_prompt
    )
    history.extend((prompt, gpt_say))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 由于请求gpt需要一段时间，我们先及时地做一次界面更新

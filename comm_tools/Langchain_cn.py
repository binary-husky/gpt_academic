import os.path
from comm_tools import toolbox
from crazy_functions import crazy_utils
import gradio as gr
from comm_tools import func_box
import time

def knowledge_base_writing(files, links: str, select, name, ipaddr: gr.Request):
    try:
        from zh_langchain import construct_vector_store
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        from crazy_functions.crazy_utils import knowledge_archive_interface
    except Exception as e:
        yield '导入依赖失败。正在尝试自动安装', gr.Dropdown.update(), '' # 刷新界面
        from crazy_functions.crazy_utils import try_install_deps
        try_install_deps(['zh_langchain==0.2.1'])
    # < --------------------读取参数--------------- >
    vector_path = os.path.join(func_box.knowledge_path, ipaddr.client.host)
    if name and select != '新建知识库':
        os.rename(os.path.join(vector_path, select), os.path.join(vector_path, name))
        kai_id = name
    elif name and select == '新建知识库': kai_id = name
    elif select and select != '新建知识库': kai_id = select
    else: kai_id = func_box.created_atime()
    yield '开始咯开始咯～', gr.Dropdown.update(), ''
    # < --------------------读取文件--------------- >
    file_manifest = []
    network_files = links.splitlines()
    spl,  = toolbox.get_conf('spl')
    # 本地文件
    for sp in spl:
        _, file_manifest_tmp, _ = crazy_utils.get_files_from_everything(files, type=f'.{sp}')
        file_manifest += file_manifest_tmp
    for net_file in network_files:
        _, file_manifest_tmp, _ = crazy_utils.get_files_from_everything(net_file, type=f'.md')
        file_manifest += file_manifest_tmp
    if len(file_manifest) == 0:
        types = "\t".join(f"`{s}`" for s in spl)
        yield (toolbox.markdown_convertion(f'没有找到任何可读取文件， 当前支持解析的文件格式包括: \n\n{types}'),
               gr.Dropdown.update(), '')
        return
    # < -------------------预热文本向量化模组--------------- >
    yield ('正在加载向量化模型...', gr.Dropdown.update(), '')
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    with toolbox.ProxyNetworkActivate():    # 临时地激活代理网络
        HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")
    # < -------------------构建知识库--------------- >
    preprocessing_files = func_box.to_markdown_tabs(head=['文件'], tabs=[file_manifest])
    yield (toolbox.markdown_convertion(f'正在准备将以下文件向量化，生成知识库文件：\n\n{preprocessing_files}'),
           gr.Dropdown.update(), '')
    with toolbox.ProxyNetworkActivate():    # 临时地激活代理网络
        kai = knowledge_archive_interface(vs_path=vector_path)
        kai.feed_archive(file_manifest=file_manifest, id=kai_id)
    kai_files = kai.get_loaded_file()
    kai_files = func_box.to_markdown_tabs(head=['文件'], tabs=[kai_files])
    yield (toolbox.markdown_convertion(f'构建完成, 当前知识库内有效的文件如下, 已自动帮您选中知识库，现在你可以畅快的开始提问啦～\n\n{kai_files}'),
           gr.Dropdown.update(value='新建知识库', choices=obtain_a_list_of_knowledge_bases(ipaddr)), kai_id)


def knowledge_base_query(txt, kai_id, chatbot, history, llm_kwargs, ipaddr: gr.Request):
    # resolve deps
    try:
        from zh_langchain import construct_vector_store
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        from crazy_functions.crazy_utils import knowledge_archive_interface
    except Exception as e:
        chatbot.append(["依赖不足", "导入依赖失败。正在尝试自动安装，请查看终端的输出或耐心等待..."])
        yield from toolbox.update_ui(chatbot=chatbot, history=history) # 刷新界面
        from crazy_functions.crazy_utils import try_install_deps
        try_install_deps(['zh_langchain==0.2.1'])

    # < -------------------为空时，不去查询向量数据库--------------- >
    if not txt: return txt
    # < -------------------检索Prompt--------------- >
    kai = knowledge_archive_interface(vs_path=os.path.join(func_box.knowledge_path, ipaddr.client.host))
    new_txt = f'{txt}'
    for id in kai_id:
        # < -------------------查询向量数据库--------------- >
        chatbot.append([txt, f'正在将问题向量化，然后对{func_box.html_tag_color(id)}知识库进行匹配'])
        yield from toolbox.update_ui(chatbot=chatbot, history=history)  # 刷新界面
        resp, prompt, _ok = kai.answer_with_archive_by_id(txt, id)
        if resp:
            referenced_documents = "\n".join([f"{k}: " + doc.page_content for k, doc in enumerate(resp['source_documents'])])
            new_txt += f'\n以下三个引号内的是知识库提供的参考文档：\n"""\n{referenced_documents}\n"""'
    return new_txt


def obtain_a_list_of_knowledge_bases(ipaddr):
    def get_directory_list(folder_path):
        directory_list = []
        for root, dirs, files in os.walk(folder_path):
            for dir_name in dirs:
                directory_list.append(dir_name)
        return directory_list
    know_path = os.path.join(func_box.knowledge_path, ipaddr.client.host)
    sys_path = os.path.join(func_box.knowledge_path, 'system')
    return get_directory_list(know_path)+get_directory_list(sys_path)


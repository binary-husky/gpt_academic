import os.path
from comm_tools import toolbox
from crazy_functions import crazy_utils
import gradio as gr
from comm_tools import func_box
from crazy_functions import crazy_box


def classification_filtering_tag(cls_select, cls_name, ipaddr):
    if cls_select == '新建分类':
        cls_select = cls_name
    elif cls_select == '个人知识库':
        cls_select = os.path.join(cls_select, ipaddr)
    return cls_select


def knowledge_base_writing(cls_select, cls_name, links: str, select, name, kai_handle, ipaddr: gr.Request):
    # < --------------------读取参数--------------- >
    cls_select = classification_filtering_tag(cls_select, cls_name, ipaddr.client.host)
    if not cls_select:
        yield '新建分类名称请不要为空', '', gr.Dropdown.update(), gr.Dropdown.update(), kai_handle
        return
    vector_path = os.path.join(func_box.knowledge_path, cls_select)
    if name and select != '新建知识库':
        kai_id = name
        os.rename(os.path.join(vector_path, select), os.path.join(vector_path, name))
        _, load_file = func_box.get_directory_list(vector_path, ipaddr.client.host)
        yield '更名成功～', '', gr.Dropdown.update(), gr.Dropdown.update(choices=load_file, value=kai_id), kai_handle
    elif name and select == '新建知识库': kai_id = name
    elif select and select != '新建知识库': kai_id = select
    else: kai_id = func_box.created_atime()
    # < --------------------限制上班时间段构建知识库--------------- >
    reject_build_switch, = toolbox.get_conf('reject_build_switch')
    if reject_build_switch:
        if not func_box.check_expected_time():
            yield '上班时间段不允许启动构建知识库任务，若有紧急任务请联系管理员', '', gr.Dropdown.update(), gr.Dropdown.update(), kai_handle
            return
    # < --------------------读取文件正式开始--------------- >
    yield '开始咯开始咯～', '', gr.Dropdown.update(), gr.Dropdown.update(), kai_handle
    files = kai_handle['file_path']
    file_manifest = []
    spl,  = toolbox.get_conf('spl')
    # 本地文件
    error = ''
    for sp in spl:
        _, file_manifest_tmp, _ = crazy_utils.get_files_from_everything(files, type=f'.{sp}')
        file_manifest += file_manifest_tmp
    # 网络文件
    try:
        task_info, kdocs_manifest_tmp, _ = crazy_box.get_kdocs_from_everything(links, type='', ipaddr=ipaddr.client.host)
        if kdocs_manifest_tmp:
            error += task_info
            yield (f"", error, gr.Dropdown.update(), gr.Dropdown.update(), kai_handle)
    except:
        import traceback
        error_str = traceback.format_exc()
        error += f'提取出错文件错误啦\n\n```\n{error_str}\n```'
        yield (f"", error, gr.Dropdown.update(), gr.Dropdown.update(), kai_handle)
        kdocs_manifest_tmp = []
    file_manifest += kdocs_manifest_tmp
    # < --------------------缺陷文件拆分--------------- >
    file_manifest = func_box.handling_defect_files(file_manifest)
    # < --------------------正式准备启动！--------------- >
    if len(file_manifest) == 0:
        types = "\t".join(f"`{s}`" for s in spl)
        link_type = f'\n\n目录: https://www.kdocs.cn/{func_box.html_tag_color("ent")}/41000207/{func_box.html_tag_color("130730080903")}\n\n' \
                    f'分享文件: https://www.kdocs.cn/l/{func_box.html_tag_color("cpfcxiGjEvqK")}'
        yield (f'没有找到任何可读取文件， 当前支持解析的本地文件格式如下: \n\n{types}\n\n在线文档链接支持如下: {link_type}',
               error, gr.Dropdown.update(),
               gr.Dropdown.update(),  kai_handle)
        return
    # < -------------------预热文本向量化模组--------------- >
    yield ('正在加载向量化模型...', '', gr.Dropdown.update(), gr.Dropdown.update(), kai_handle)
    from langchain.embeddings.huggingface import HuggingFaceEmbeddings
    with toolbox.ProxyNetworkActivate():    # 临时地激活代理网络
        HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")
    # < -------------------构建知识库--------------- >
    tab_show = [os.path.basename(i) for i in file_manifest]
    preprocessing_files = func_box.to_markdown_tabs(head=['文件'], tabs=[tab_show])
    yield (f'正在准备将以下文件向量化，生成知识库文件，若文件数据较多，可能需要等待几小时：\n\n{preprocessing_files}',
           error, gr.Dropdown.update(),
           gr.Dropdown.update(), kai_handle)
    with toolbox.ProxyNetworkActivate():    # 临时地激活代理网络
        kai = crazy_utils.knowledge_archive_interface(vs_path=vector_path)
        qa_handle, vs_path = kai.construct_vector_store(vs_id=kai_id, files=file_manifest)
    with open(os.path.join(vector_path, kai_id, ipaddr.client.host), mode='w') as f: pass
    _, kai_files = kai.get_init_file(kai_id)
    kai_handle['file_list'] = [os.path.basename(file) for file in kai_files if os.path.exists(file)]
    kai_files = func_box.to_markdown_tabs(head=['文件'], tabs=[tab_show])
    kai_handle['know_obj'].update({kai_id: qa_handle})
    kai_handle['know_name'] = kai_id
    load_list, user_list = func_box.get_directory_list(vector_path, ipaddr.client.host)
    yield (f'构建完成, 当前知识库内有效的文件如下, 已自动帮您选中知识库，现在你可以畅快的开始提问啦～\n\n{kai_files}',
           error, gr.Dropdown.update(value=cls_select),
           gr.Dropdown.update(value='新建知识库', choices=load_list),  kai_handle)


def knowledge_base_query(txt, kai_id, chatbot, history, llm_kwargs):
    # < -------------------为空时，不去查询向量数据库--------------- >
    if not txt: return txt
    # < -------------------检索Prompt--------------- >
    new_txt = f'{txt}'
    if kai_id:
        chatbot.append([txt, f'正在将问题向量化，然后对{func_box.html_tag_color(str(kai_id))}知识库进行匹配'])
    for id in kai_id:   #
        if llm_kwargs['know_dict']['know_obj'].get(id, False):
            kai = llm_kwargs['know_dict']['know_obj'][id]
        else:
            know_cls = llm_kwargs['know_cls']
            know_cls = classification_filtering_tag(know_cls, know_cls, llm_kwargs['ipaddr'])
            vs_path = os.path.join(func_box.knowledge_path, know_cls)
            kai = crazy_utils.knowledge_archive_interface(vs_path=vs_path)
            llm_kwargs['know_dict']['know_obj'][id] = kai
        # < -------------------查询向量数据库--------------- >
        yield from toolbox.update_ui(chatbot=chatbot, history=history)  # 刷新界面
        vector_config = llm_kwargs['vector']
        resp, prompt, _ok = kai.answer_with_archive_by_id(txt, id,
                                                          VECTOR_SEARCH_SCORE_THRESHOLD=vector_config['score'],
                                                          VECTOR_SEARCH_TOP_K=vector_config['top-k'],
                                                          CHUNK_SIZE=vector_config['size'])
        if resp:
            referenced_documents = "\n".join(
                [f"{k}: " + doc.page_content for k, doc in enumerate(resp['source_documents'])])
            new_txt += f'\n以下三个引号内的是{id}提供的参考文档：\n"""\n{referenced_documents}\n"""'
    return new_txt

def obtain_classification_knowledge_base(cls_name, ipaddr: gr.Request):
    if cls_name == '个人知识库':
        load_path = os.path.join(func_box.knowledge_path, '个人知识库', ipaddr.client.host)
    else:
        load_path = os.path.join(func_box.knowledge_path, cls_name)
    load_list, user_list = func_box.get_directory_list(load_path, ipaddr.client.host)
    status = f"你只能重构自己上传的知识库哦 😎" \
             f"\n\n{func_box.to_markdown_tabs(head=['可编辑知识库', '可用知识库'], tabs=[user_list, load_list], column=False)}\n\n"
    return gr.Dropdown.update(choices=user_list), gr.Dropdown.update(choices=load_list, label=f'{cls_name}'), status


def obtaining_knowledge_base_files(cls_select, cls_name, vs_id, chatbot, kai_handle, ipaddr: gr.Request):
    if vs_id:
        cls_select = classification_filtering_tag(cls_select, cls_name, ipaddr.client.host)
        vs_path = os.path.join(func_box.knowledge_path, cls_select)
        if isinstance(chatbot, toolbox.ChatBotWithCookies):
            pass
        else:
            chatbot = toolbox.ChatBotWithCookies(chatbot)
            chatbot.write_list(chatbot)
        chatbot.append([None, f'正在检查知识库内文件{"  ".join([func_box.html_tag_color(i)for i in vs_id])}'])
        yield chatbot, gr.Column.update(visible=False), '🏃🏻‍ 正在努力轮询中....请稍等， tips：知识库可以多选，但只会预加载第一个选中的知识库～️', kai_handle
        kai_files = {}
        for id in vs_id:
            if kai_handle['know_obj'].get(id, None):
                kai = kai_handle['know_obj'][id]
            else:
                kai = crazy_utils.knowledge_archive_interface(vs_path=vs_path)
            qa_handle, _dict = kai.get_init_file(vs_id=id)
            kai_files.update(_dict)
            kai_handle['know_obj'].update({id: qa_handle})
        tabs = [[_id, func_box.html_view_blank(file), kai_files[file][_id]] for file in kai_files for _id in kai_files[file]]
        kai_handle['file_list'] = [os.path.basename(file) for file in kai_files if os.path.exists(file)]
        chatbot.append([None, f'检查完成，当前选择的知识库内可用文件如下：'
                              f'\n\n {func_box.to_markdown_tabs(head=["所属知识库", "文件", "文件类型"], tabs=tabs, column=True)}\n\n'
                              f'🤩 快来向我提问吧～'])
        yield chatbot, gr.Column.update(visible=False), '✅ 检查完成', kai_handle
    else:
        yield chatbot, gr.update(), 'Done', kai_handle



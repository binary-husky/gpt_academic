import os.path
import threading

from common import toolbox
from crazy_functions import crazy_utils
import gradio as gr
from common import func_box, database_processor
from crazy_functions.kingsoft_fns import crazy_box, docs_kingsoft, docs_qqdocs

from crazy_functions.vector_fns.vector_database import LocalDocQA
from crazy_functions.vector_fns import vector_database


class knowledge_archive_interface():
    def __init__(self, vs_path) -> None:
        self.current_id = ""
        self.kai_path = None
        import nltk
        if vector_database.NLTK_DATA_PATH not in nltk.data.path:
            nltk.data.path = [vector_database.NLTK_DATA_PATH] + nltk.data.path
        self.qa_handle = LocalDocQA()
        self.qa_handle.init_cfg()
        self.text2vec_large_chinese = None
        self.vs_root_path = vs_path
        self.ds_docstore = ''

    def get_chinese_text2vec(self):
        if self.text2vec_large_chinese is None:
            # < -------------------预热文本向量化模组--------------- >
            from common.toolbox import ProxyNetworkActivate
            print('Checking Text2vec ...')
            from langchain.embeddings import HuggingFaceEmbeddings
            with ProxyNetworkActivate('Download_LLM'):  # 临时地激活代理网络
                self.text2vec_large_chinese = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")
        return self.text2vec_large_chinese

    def filter_quarterly_files(self, files):
        database_files = list(self.get_loaded_file(files))

    def construct_vector_store(self, vs_id, files):
        for file in files:
            assert os.path.exists(file), "输入文件不存在"
        vs_path = os.path.join(self.vs_root_path, vs_id)
        vs_path, loaded_files = self.qa_handle.init_knowledge_vector_store(filepath=files, vs_path=vs_path,
                                                                           sentence_size=100,
                                                                           text2vec=self.get_chinese_text2vec())
        return self, vs_path

    def get_current_archive_id(self):
        return self.current_id

    def get_loaded_file(self, files):
        return self.qa_handle.get_loaded_file(files)

    def get_init_file(self, vs_id):
        from langchain.vectorstores import FAISS
        vs_path = os.path.join(self.vs_root_path, vs_id)
        self.qa_handle.vector_store = FAISS.load_local(vs_path, self.get_chinese_text2vec())
        ds = self.qa_handle.vector_store.docstore
        self.ds_docstore = ds
        file_dict = {ds._dict[k].metadata['source']: {vs_id: ds._dict[k].metadata['filetype']} for k in ds._dict}
        return self, file_dict

    def answer_with_archive_by_id(self, txt, vs_id, llm_kwargs=None, VECTOR_SEARCH_SCORE_THRESHOLD=0,
                                  VECTOR_SEARCH_TOP_K=4, CHUNK_SIZE=521):
        if llm_kwargs:
            vector_config = llm_kwargs.get('vector')
            VECTOR_SEARCH_SCORE_THRESHOLD = vector_config['score']
            VECTOR_SEARCH_TOP_K = vector_config['top-k']
            CHUNK_SIZE = vector_config['size']
        self.kai_path = os.path.join(self.vs_root_path, vs_id)
        if not os.path.exists(self.kai_path):
            return '', '', False
        resp, prompt = self.qa_handle.get_knowledge_based_conent_test(
            query=txt,
            vs_path=self.kai_path,
            score_threshold=VECTOR_SEARCH_SCORE_THRESHOLD,
            vector_search_top_k=VECTOR_SEARCH_TOP_K,
            chunk_conent=True,
            chunk_size=CHUNK_SIZE,
            text2vec=self.get_chinese_text2vec(),
        )
        return resp, prompt, True


def classification_filtering_tag(cls_select, ipaddr):
    if cls_select == '个人知识库':
        cls_select = os.path.join(cls_select, ipaddr)
    return cls_select


def knowledge_base_writing(cls_select, links: str, select, name, kai_handle, ipaddr: gr.Request):
    # < --------------------读取参数--------------- >
    user_addr = func_box.user_client_mark(ipaddr)
    cls_select = classification_filtering_tag(cls_select, user_addr)
    if not cls_select:
        raise gr.Error('新建分类名称请不要为空')
    vector_path = os.path.join(func_box.knowledge_path, cls_select)
    if name and select:
        kai_id = name
        os.rename(os.path.join(vector_path, select), os.path.join(vector_path, name))
        _, load_file = func_box.get_directory_list(vector_path, user_addr)
        yield ('', f'更名成功～ `{select}` -> `{name}`',
               gr.update(), gr.update(choices=load_file,
                                      value=kai_id), gr.update(), kai_handle)
        if not links and not kai_handle.get('file_list'): return  # 如果文件和链接都为空，那么就有必要往下执行了
    elif select:
        kai_id = select
    else:
        kai_id = func_box.created_atime()
        waring = '新建知识库时，知识库名称建议不要为空，本次知识库名称取用服务器时间`kai_id`为知识库名称！！！'
        yield '', waring, gr.Dropdown.update(), gr.update(), gr.Dropdown.update(), kai_handle
    # < --------------------限制上班时间段构建知识库--------------- >
    reject_build_switch = toolbox.get_conf('reject_build_switch')
    if reject_build_switch:
        if not func_box.check_expected_time():
            raise gr.Error('上班时间段不允许启动构建知识库任务，若有紧急任务请联系管理员')
    # < --------------------读取文件正式开始--------------- >
    yield '开始咯开始咯～', '', gr.update(), gr.update(), gr.update(), kai_handle
    files = kai_handle['file_path']
    file_manifest = []
    spl = toolbox.get_conf('spl')
    # 本地文件
    error = ''
    for sp in spl:
        _, file_manifest_tmp, _ = crazy_utils.get_files_from_everything(files, type=f'.{sp}')
        file_manifest += file_manifest_tmp
    # 网络文件
    try:
        task_info, kdocs_manifest_tmp, _ = docs_kingsoft.get_kdocs_from_everything(links, type='', ipaddr=user_addr)
        # task_info, kdocs_manifest_tmp, _ = crzay_kingsoft.get(links, type='', ipaddr=user_addr)
        if kdocs_manifest_tmp:
            error += task_info
            yield (f"", error, gr.update(), gr.update(), gr.update(), kai_handle)
    except:
        import traceback
        error_str = traceback.format_exc()
        error += f'提取出错文件错误啦\n\n```\n{error_str}\n```'
        yield (f"", error, gr.update(), gr.update(), gr.update(), kai_handle)
        kdocs_manifest_tmp = []
    file_manifest += kdocs_manifest_tmp
    # < --------------------缺陷文件拆分--------------- >
    file_manifest = func_box.handling_defect_files(file_manifest)
    # < --------------------正式准备启动！--------------- >
    if len(file_manifest) == 0:
        types = "\t".join(f"`{s}`" for s in spl)
        link_type = f'\n\n目录: https://www.kdocs.cn/{func_box.html_tag_color("ent")}/41000207/{func_box.html_tag_color("130730080903")}\n\n' \
                    f'分享文件: https://www.kdocs.cn/l/{func_box.html_tag_color("cpfcxiGjEvqK")}'
        yield (
        f'没有找到任何可读取文件， 当前支持解析的本地文件格式如下: \n\n{types}\n\n在线文档链接支持如下: {link_type}',
        error, gr.Dropdown.update(), gr.Dropdown.update(),
        gr.Dropdown.update(), kai_handle)
        return
    # # < -------------------预热文本向量化模组--------------- >
    # yield ('正在加载向量化模型...', '', gr.Dropdown.update(), gr.Dropdown.update(), gr.Dropdown.update(), kai_handle)
    # with toolbox.ProxyNetworkActivate():    # 临时地激活代理网络
    #     HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")
    # < -------------------构建知识库--------------- >
    tab_show = [os.path.basename(i) for i in file_manifest]
    preprocessing_files = func_box.to_markdown_tabs(head=['文件'], tabs=[tab_show])
    yield (f'正在准备将以下文件向量化，生成知识库文件，若文件数据较多，可能需要等待几小时：\n\n{preprocessing_files}',
           error, gr.Dropdown.update(), gr.Dropdown.update(),
           gr.update(), kai_handle)
    with toolbox.ProxyNetworkActivate():  # 临时地激活代理网络
        kai = knowledge_archive_interface(vs_path=vector_path)
        qa_handle, vs_path = kai.construct_vector_store(vs_id=kai_id, files=file_manifest)
    with open(os.path.join(vector_path, kai_id, user_addr), mode='w') as f:
        pass
    _, kai_files = kai.get_init_file(kai_id)
    kai_handle['file_list'] = [os.path.basename(file) for file in kai_files if os.path.exists(file)]
    kai_files = func_box.to_markdown_tabs(head=['文件'], tabs=[tab_show])
    kai_handle['know_obj'].update({kai_id: qa_handle})
    kai_handle['know_name'] = kai_id
    load_list, user_list = func_box.get_directory_list(vector_path, user_addr)
    yield (f'构建完成, 当前知识库内有效的文件如下, 已自动帮您选中知识库，现在你可以畅快的开始提问啦～\n\n{kai_files}',
           error, gr.Dropdown.update(value=cls_select, choices=load_list),
           gr.Dropdown.update(value='新建知识库', choices=load_list),
           gr.Dropdown.update(value=kai_id, choices=load_list), kai_handle)


def knowledge_base_query(txt, chatbot, history, llm_kwargs, plugin_kwargs):
    # < -------------------为空时，不去查询向量数据库--------------- >
    if not txt: return txt
    know_cls_kw = {llm_kwargs['know_cls']: llm_kwargs['know_id']}
    new_txt = f'{txt}'
    # < -------------------检查应该走哪套流程-------------- >
    associated_knowledge_base, = crazy_box.json_args_return(plugin_kwargs, ['关联知识库'])
    if associated_knowledge_base:
        know_cls_kw = {}
        for _kw in associated_knowledge_base:
            know_cls_kw[_kw] = associated_knowledge_base[_kw]['查询列表']
        txt = None
    gpt_say = f'正在将问题向量化，然后对`{str(know_cls_kw)}`知识库进行匹配.\n\n'
    if list(know_cls_kw.values())[-1]:
        if gpt_say not in str(chatbot):
            chatbot.append([txt, gpt_say])
            yield from toolbox.update_ui(chatbot=chatbot, history=history)  # 刷新界面
    for know_cls in know_cls_kw:
        for id in know_cls_kw[know_cls]:
            if llm_kwargs['know_dict']['know_obj'].get(id, False):
                kai = llm_kwargs['know_dict']['know_obj'][id]
            else:
                know_cls = classification_filtering_tag(know_cls, llm_kwargs['ipaddr'])
                vs_path = os.path.join(func_box.knowledge_path, know_cls)
                kai = knowledge_archive_interface(vs_path=vs_path)
                llm_kwargs['know_dict']['know_obj'][id] = kai
            # < -------------------查询向量数据库--------------- >
            prompt_cls = '知识库提示词'
            resp, prompt, _ok = kai.answer_with_archive_by_id(new_txt, id, llm_kwargs)
            referenced_documents = "\n".join(
                [f"{k}: " + doc.page_content for k, doc in enumerate(resp['source_documents'])])
            source_documents = "\n".join({func_box.html_view_blank(doc.metadata.get('source', '')): '' for k, doc in
                                          enumerate(resp['source_documents'])})
            if not referenced_documents:
                gpt_say += f"`{id}`知识库中没有与问题匹配的文本，所以不会提供任何参考文本，你可以在Settings-更改`知识库检索相关度`中进行调优。\n"
                chatbot[-1] = [txt, gpt_say]
            else:
                if associated_knowledge_base:
                    prompt_name = associated_knowledge_base[know_cls].get(prompt_cls)
                    tips = f'匹配中了`{id}`知识库，使用的Prompt是`{prompt_cls}`分类下的`{prompt_name}`, 插件自定义参数允许指定其他Prompt哦～'
                    if tips not in str(chatbot):
                        gpt_say += tips
                    prompt_con = database_processor.SqliteHandle(table=f'prompt_{prompt_cls}_sys').find_prompt_result(
                        prompt_name)
                else:
                    prompt_name = '引用知识库回答'
                    tips = f'`{id}`知识库问答使用的Prompt是`{prompt_cls}`分类下的' \
                           f'`{prompt_name}`, 你可以保存一个同名的Prompt到个人分类下，知识库问答会优先使用个人分类下的提示词。'
                    if tips not in str(chatbot):
                        gpt_say += tips
                    prompt_con = database_processor.SqliteHandle(table=f'prompt_{prompt_cls}_sys').find_prompt_result(
                        prompt_name, individual_priority=llm_kwargs['ipaddr'])
                gpt_say += f"\n\n引用文档:\n\n> {source_documents}"
                chatbot[-1] = [txt, gpt_say]
                prompt_content = func_box.replace_expected_text(prompt=prompt_con, content=referenced_documents,
                                                                expect='{{{v}}}')
                new_txt = func_box.replace_expected_text(prompt=prompt_content, content=new_txt, expect='{{{q}}}')
            yield from toolbox.update_ui(chatbot=chatbot, history=history)  # 刷新界面
    return new_txt


def obtain_classification_knowledge_base(cls_name, ipaddr: gr.Request):
    user = func_box.user_client_mark(ipaddr)
    if cls_name == '个人知识库':
        load_path = os.path.join(func_box.knowledge_path, '个人知识库', user)
    else:
        load_path = os.path.join(func_box.knowledge_path, cls_name)
    load_list, user_list = func_box.get_directory_list(load_path, user)
    know_user_build = toolbox.get_conf('know_user_build')
    if know_user_build:
        mesg = '构建重构没有任何限制，你可以更改config中的`know_user_build`，限制只能重构构建个人的知识库'
    else:
        mesg = '你只能重构自己上传的知识库哦😎'
    status = f"{mesg}" \
             f"\n\n{func_box.to_markdown_tabs(head=['可编辑知识库', '可用知识库'], tabs=[user_list, load_list], column=False)}\n\n"
    return gr.Dropdown.update(choices=user_list), gr.Dropdown.update(choices=load_list, label=f'{cls_name}'), status


def want_to_rename_it(cls_name, select, ipaddr: gr.Request):
    user = func_box.user_client_mark(ipaddr)
    if cls_name == '个人知识库':
        load_path = os.path.join(func_box.knowledge_path, '个人知识库', user)
    else:
        load_path = os.path.join(func_box.knowledge_path, cls_name)
    load_list, user_list = func_box.get_directory_list(load_path, user)
    if select in load_list:
        return gr.Button.update(visible=True)
    else:
        return gr.update(visible=False)


def obtaining_knowledge_base_files(cls_select, vs_id, chatbot, kai_handle, model, ipaddr: gr.Request):
    if vs_id and '预加载知识库' in model:
        cls_select = classification_filtering_tag(cls_select, func_box.user_client_mark(ipaddr))
        vs_path = os.path.join(func_box.knowledge_path, cls_select)
        you_say = f'请检查知识库内文件{"  ".join([func_box.html_tag_color(i) for i in vs_id])}'
        chatbot.append([you_say, None])
        yield chatbot, '🏃🏻‍ 正在努力轮询中....请稍等， tips：知识库可以多选，但不要贪杯哦～️', kai_handle
        kai_files = {}
        for id in vs_id:
            if kai_handle['know_obj'].get(id, None):
                kai = kai_handle['know_obj'][id]
            else:
                kai = knowledge_archive_interface(vs_path=vs_path)
            qa_handle, _dict = kai.get_init_file(vs_id=id)
            kai_files.update(_dict)
            kai_handle['know_obj'].update({id: qa_handle})
        tabs = [[_id, func_box.html_view_blank(file), kai_files[file][_id]] for file in kai_files for _id in
                kai_files[file]]
        kai_handle['file_list'] = [os.path.basename(file) for file in kai_files if os.path.exists(file)]
        chatbot[-1] = [you_say, f'检查完成，当前选择的知识库内可用文件如下：'
                                f'\n\n {func_box.to_markdown_tabs(head=["所属知识库", "文件", "文件类型"], tabs=tabs, column=True)}\n\n'
                                f'🤩 快来向我提问吧～']
        yield chatbot, '✅ 检查完成', kai_handle
    else:
        yield chatbot, 'Done', kai_handle


def single_step_thread_building_knowledge(cls_name, know_id, file_manifest, llm_kwargs):
    cls_select = classification_filtering_tag(cls_name, llm_kwargs['ipaddr'])
    vector_path = os.path.join(func_box.knowledge_path, cls_select)
    os.makedirs(vector_path, exist_ok=True)

    def thread_task():
        kai = knowledge_archive_interface(vs_path=vector_path)
        qa_handle, vs_path = kai.construct_vector_store(vs_id=know_id, files=file_manifest)
        llm_kwargs['know_dict']['know_obj'][know_id] = qa_handle

    threading.Thread(target=thread_task, ).start()

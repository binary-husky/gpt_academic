# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
from webui_elem.func_signals.__import__ import *


# TODO < -------------------------------- 知识库函数注册区 -------------------------------------->
def kb_select_show(select: gr.Dropdown):
    if select == '新建知识库':
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)


def kb_name_select_then(kb_name):
    kb_dict = base.kb_list_to_dict([kb_name])
    kb_name = list(kb_dict.keys())[0]
    file_details = pd.DataFrame(base.get_kb_file_details(kb_name))
    if 'file_name' in file_details:
        db_file_list = file_details['file_name'].to_list()
        file_name = db_file_list[0]
        last_details = __get_kb_details_df(file_details, file_details["No"] == 1)
        last_fragment = __get_kb_fragment_df(kb_name, file_name)
        kb_file_list = gr.update(choices=db_file_list, value=file_name)
        kb_file_details = gr.DataFrame.update(value=last_details, label=f'{file_name}-文件详情')
        kb_file_fragment = gr.DataFrame.update(value=last_fragment, label=f'{file_name}-文件片段编辑')
    else:
        kb_file_list = gr.update(choices=[], value='')
        kb_file_details = gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_details_template)))
        kb_file_fragment = gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_fragment_template)))

    kb_name_tm = base.kb_details_to_dict()
    kb_info = base.get_kb_details_by_name(kb_name).get('kb_info', '')
    update_output = {
        'kb_name_list': gr.update(choices=base.kb_dict_to_list(kb_name_tm) + ['新建知识库']),
        'kb_info_txt': kb_info,
        'kb_file_list': kb_file_list,
        'kb_file_details': kb_file_details,
        'kb_file_fragment': kb_file_fragment
    }
    return list(update_output.values())


def kb_name_change_btn(name):
    if name:
        return gr.Button.update(variant='primary')
    else:
        return gr.Button.update(variant='secondary')


def kb_upload_btn(upload: gr.Files, cloud: str):
    if upload or URL(cloud).host:
        return gr.Button.update(variant='primary')
    else:
        return gr.Button.update(variant='secondary')


def kb_introduce_change_btn(kb_name, kb_info):
    kb_dict = base.kb_list_to_dict([kb_name])
    kb_name = list(kb_dict.keys())[0]
    resp = kb_doc_api.update_info(kb_name, kb_info)

    if not resp.data != 200:
        raise gr.Error(json.dumps(resp.__dict__, indent=4, ensure_ascii=False))
    else:
        return gr.update()
        # yield gr.update(value=spike_toast('更新知识库简介成功'), visible=True)
        # time.sleep(1)
        # yield gr.update(visible=False)


def kb_date_add_row(source_data: pd.DataFrame):
    # 添加一行数据
    last_index = source_data.iloc[-1].iloc[1]
    # 检查最后一行的第一个元素是否为整数类型
    if last_index.dtype == 'int64':
        new_index = last_index + 1
    else:
        new_index = 'ErrorType'
    new_row_data = [uuid.uuid4(), new_index, '', '']
    source_data.loc[len(source_data)] = new_row_data

    return gr.update(value=source_data)


def kb_new_confirm(kb_name, kb_type, kb_model, kb_info):
    kb_name_tm = base.kb_details_to_dict()

    if not kb_name or not kb_type or not kb_model:
        keywords = {"知识库名称": kb_name, "向量类型": kb_type, "Embedding 模型": kb_model}
        error_keyword = " - ".join([f"【{i}】" for i in keywords if not keywords[i]])
        raise gr.Error(f'缺失 {error_keyword} 字段,无法创建, ')

    kb_server_list = base.KBServiceFactory.get_service_by_name(kb_name)
    if kb_name in kb_name_tm or kb_server_list is not None:
        if kb_name_tm.get(kb_name, {}).get('model') == kb_model:
            raise gr.Error(f'{kb_name} @ {kb_model} 已存在同名知识库，请重新命名')

    kb = base.KBServiceFactory.get_service(kb_name, kb_type, kb_model)
    kb.kb_info = kb_info
    try:
        kb.create_kb()
    except Exception as e:
        msg = f"创建知识库出错： {e}"
        logger.error(f'{e.__class__.__name__}: {msg}')
        if not utils.validate_kb_name(kb_name):
            raise gr.Error("Don't attack me")
        shutil.rmtree(os.path.join(init_path.private_knowledge_path, kb_name))
        raise gr.Error(msg)
    select_name = base.kb_name_tm_merge(kb_name, kb_type, kb_model)
    new_output = {
        'new_clo': gr.update(visible=False),
        'edit_clo': gr.update(visible=True),
    }

    edit_output = {
        'kb_name_list': gr.update(choices=[select_name] + base.kb_dict_to_list(kb_name_tm) + ['新建知识库'],
                                  value=select_name),
        'kb_info_txt': kb_info,
        'kb_file_list': gr.update(choices=[], value=''),
        'kb_file_details': gr.DataFrame.update(value=pd.DataFrame(data=copy.deepcopy(kb_config.file_details_template))),
        'kb_file_fragment': gr.DataFrame.update(
            value=pd.DataFrame(data=copy.deepcopy(kb_config.file_fragment_template)))
    }

    return list(new_output.values()) + list(edit_output.values()) + [
        gr.update(choices=list(kb_name_tm.keys()) + [kb_name])]


def kb_download_embedding_model(model_name):
    if not model_name:
        raise gr.Error('必须要选一个')
    from common.embeddings_api import embed_download
    obj, stream = embed_download(model_name)
    download_result = "```\n"
    for tag, chuck in stream:
        download_result += chuck
        yield gr.update(value=download_result)
    yield gr.update(value=download_result + '\n```\n`Done`')


def __get_kb_details_df(file_details: pd.DataFrame, condition: pd.Series):
    select_document = file_details[condition]

    select_kb_details = copy.deepcopy(kb_config.file_details_template)

    select_kb_details.update({
        '文档加载器': select_document['document_loader'].to_list(),
        '分词器': select_document['text_splitter'].to_list(),
        '文档片段数量': select_document['docs_count'].to_list(),
        '向量库': select_document['in_db'].to_list(),
        '源文件': select_document['in_folder'].to_list()
    })
    return pd.DataFrame(data=select_kb_details)


def __get_kb_fragment_df(kb_name, file_name):
    kb_fragment = copy.deepcopy(kb_config.file_fragment_template)

    info_fragment = kb_doc_api.search_docs(query='', knowledge_base_name=kb_name,
                                           top_k=1, score_threshold=1,
                                           file_name=file_name, metadata={})

    for i, v in enumerate(info_fragment):
        kb_fragment['id'].append(info_fragment[i].id)
        kb_fragment['N'].append(i + 1)
        kb_fragment['内容'].append(info_fragment[i].page_content)
        kb_fragment['删除'].append('')
    return pd.DataFrame(data=kb_fragment)


def kb_file_update_confirm(upload_files: List, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader,
                           cloud_link, ipaddr: gr.Request):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    user = user_client_mark(ipaddr)
    cloud_map, status = detach_cloud_links(cloud_link, {'ipaddr': user}, ['*'])
    if status:
        raise gr.Error(f'文件下载失败，{cloud_map}')
    files = []
    if upload_files:
        files.extend([f.name for f in upload_files])
    files += list(cloud_map.keys())
    response = kb_doc_api.upload_docs(files=files, knowledge_base_name=kb_name, override=True,
                                      to_vector_store=True, chunk_size=kb_max, chunk_overlap=kb_similarity,
                                      loader_enhance=kb_loader, docs={}, not_refresh_vs_cache=False,
                                      text_splitter_name=kb_tokenizer)
    if response.code != 200:
        raise gr.Error(json.dumps(response.__dict__, indent=4, ensure_ascii=False))
    if response.data.get('failed_files'):
        raise gr.Error(json.dumps(response.data, indent=4, ensure_ascii=False))
    return kb_name_select_then(kb_name)


def kb_select_file(kb_name, kb_file: str):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    file_details = pd.DataFrame(base.get_kb_file_details(kb_name))

    last_details = __get_kb_details_df(file_details, file_details["file_name"] == kb_file)
    last_fragment = __get_kb_fragment_df(kb_name, kb_file)

    return gr.update(value=last_details, label=f'{kb_file}-文件详情'), gr.update(value=last_fragment,
                                                                                 label=f'{kb_file}-文档片段编辑')


def kb_base_del(kb_name, del_confirm, _):
    if del_confirm == 'CANCELED':
        return gr.update(visible=False), gr.update(visible=True), gr.update()
    else:
        kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
        response = kb_api.delete_kb(kb_name)
        if response.code != 200:
            raise gr.Error(json.dumps(response.__dict__, indent=4, ensure_ascii=False))
        kb_name_list = base.kb_dict_to_list(base.kb_details_to_dict()) + ['新建知识库']
        kb_name_tm = base.kb_details_to_dict()
        return (gr.update(visible=True), gr.update(visible=False), gr.update(choices=kb_name_list, value='新建知识库'),
                list(kb_name_tm.keys()))


def kb_docs_file_source_del(kb_name, kb_file, _):
    if kb_file == 'CANCELED':
        return gr.update(), gr.update(), gr.update(), gr.update()
    kb_name_d = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.delete_docs(knowledge_base_name=kb_name_d, file_names=[kb_file],
                                  delete_content=True, not_refresh_vs_cache=False)
    if resp.code == 200 and not resp.data.get('failed_files'):
        toast = gr.update(
            value=spike_toast('彻底删除成功 🏴‍☠️'),
            visible=True)
        _, _, file_list, details, fragment = kb_name_select_then(kb_name)
        yield toast, file_list, details, fragment
        time.sleep(1)
        yield gr.update(visible=False), file_list, details, fragment
    else:
        yield gr.Error(f'删除失败, {resp.__dict__}')


def kb_vector_del(kb_name, kb_file):
    kb_name_d = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.delete_docs(knowledge_base_name=kb_name_d, file_names=[kb_file],
                                  delete_content=False, not_refresh_vs_cache=False)
    if resp.code == 200 and not resp.data.get('failed_files'):
        toast = gr.update(
            value=spike_toast('仅从向量库中删除，后续该文档不会被向量召回，如需重新引用，重载向量数据即可'),
            visible=True)
        yield toast, *kb_select_file(kb_name, kb_file)
        time.sleep(1)
        yield gr.update(visible=False), gr.update(), gr.update()
    else:
        yield gr.Error(f'删除失败, {resp.__dict__}')


def kb_vector_reload(_, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader, kb_file):
    kb_name_k = list(base.kb_list_to_dict([kb_name]).keys())[0]
    resp = kb_doc_api.update_docs(
        knowledge_base_name=kb_name_k, file_names=[kb_file], docs={},
        chunk_size=kb_max, chunk_overlap=kb_similarity, override_custom_docs=True,
        loader_enhance=kb_loader, not_refresh_vs_cache=False,
        text_splitter_name=kb_tokenizer
    )
    if resp.code == 200 and not resp.data.get('failed_files'):
        yield gr.update(value=spike_toast('重载向量数据成功'), visible=True), *kb_select_file(kb_name, kb_file)
        time.sleep(1)
        yield gr.update(visible=False), gr.update(), gr.update()
    else:
        yield gr.Error(f'重载向量数据失败, {resp.__dict__}'), gr.update(), gr.update()


def kb_base_changed_save(_, kb_name, kb_info, kb_max, kb_similarity, kb_tokenizer, kb_loader,
                         kb_file, kb_dataFrame: pd.DataFrame):
    kb_name = list(base.kb_list_to_dict([kb_name]).keys())[0]
    info_fragment = kb_doc_api.search_docs(query='', knowledge_base_name=kb_name,
                                           top_k=1, score_threshold=1,
                                           file_name=kb_file, metadata={})

    origin_docs = {}
    for x in info_fragment:
        origin_docs[x.id] = {"page_content": x.page_content,
                             "type": x.type,
                             "metadata": x.metadata}
    changed_docs = []
    for index, row in kb_dataFrame.iterrows():
        origin_doc = origin_docs.get(row['id'])
        if origin_doc:
            if row["删除"] not in ["Y", "y", 1, '1']:
                changed_docs.append({
                    "page_content": row["内容"],
                    "type": origin_doc['type'],
                    "metadata": origin_doc["metadata"],
                })
            else:
                logger.warning(f'删除{row.get("id")}片段：{origin_doc.get("page_content")}')
        else:
            changed_docs.append({
                "page_content": row["内容"],
                "type": 'Document',
                "metadata": {"metadata": kb_file},
            })
    if changed_docs:
        resp = kb_doc_api.update_docs(
            knowledge_base_name=kb_name, file_names=[kb_file], docs={kb_file: changed_docs},
            chunk_size=kb_max, chunk_overlap=kb_similarity, override_custom_docs=False,
            loader_enhance=kb_loader, not_refresh_vs_cache=False,
            text_splitter_name=kb_tokenizer
        )
        if resp.code == 200 and not resp.data.get('failed_files'):
            last_fragment = __get_kb_fragment_df(kb_name, kb_file)
            yield gr.update(value=spike_toast('更新成功'), visible=True), gr.update(value=last_fragment)
            time.sleep(1)
            yield gr.update(value=spike_toast('更新成功'), visible=False), gr.update(value=last_fragment)
        else:
            yield gr.Error(f'更新失败, {resp.__dict__}')

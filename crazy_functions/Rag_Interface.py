from toolbox import CatchException, update_ui, get_conf, get_log_folder, update_ui_lastest_msg
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive

RAG_WORKER_REGISTER = {}
MAX_HISTORY_ROUND = 5
MAX_CONTEXT_TOKEN_LIMIT = 4096
REMEMBER_PREVIEW = 1000

@CatchException
def Rag问答(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    # import vector store lib
    VECTOR_STORE_TYPE = "Milvus"
    if VECTOR_STORE_TYPE == "Milvus":
        try:
            from crazy_functions.rag_fns.milvus_worker import MilvusRagWorker as LlamaIndexRagWorker
        except:
            VECTOR_STORE_TYPE = "Simple"
    if VECTOR_STORE_TYPE == "Simple":
        from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker

    # 1. we retrieve rag worker from global context
    user_name = chatbot.get_user()
    checkpoint_dir = get_log_folder(user_name, plugin_name='experimental_rag')
    if user_name in RAG_WORKER_REGISTER:
        rag_worker = RAG_WORKER_REGISTER[user_name]
    else:
        rag_worker = RAG_WORKER_REGISTER[user_name] = LlamaIndexRagWorker(
            user_name, 
            llm_kwargs, 
            checkpoint_dir=checkpoint_dir, 
            auto_load_checkpoint=True)
    current_context = f"{VECTOR_STORE_TYPE} @ {checkpoint_dir}"
    tip = "提示：输入“清空向量数据库”可以清空RAG向量数据库"
    if txt == "清空向量数据库":
        chatbot.append([txt, f'正在清空 ({current_context}) ...'])
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        rag_worker.purge()
        yield from update_ui_lastest_msg('已清空', chatbot, history, delay=0) # 刷新界面
        return

    chatbot.append([txt, f'正在召回知识 ({current_context}) ...'])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 2. clip history to reduce token consumption
    #   2-1. reduce chat round
    txt_origin = txt

    if len(history) > MAX_HISTORY_ROUND * 2:
        history = history[-(MAX_HISTORY_ROUND * 2):]
    txt_clip, history, flags = input_clipping(txt, history, max_token_limit=MAX_CONTEXT_TOKEN_LIMIT, return_clip_flags=True)
    input_is_clipped_flag = (flags["original_input_len"] != flags["clipped_input_len"])

    #   2-2. if input is clipped, add input to vector store before retrieve
    if input_is_clipped_flag:
        yield from update_ui_lastest_msg('检测到长输入, 正在向量化 ...', chatbot, history, delay=0) # 刷新界面
        # save input to vector store
        rag_worker.add_text_to_vector_store(txt_origin)
        yield from update_ui_lastest_msg('向量化完成 ...', chatbot, history, delay=0) # 刷新界面
        if len(txt_origin) > REMEMBER_PREVIEW:
            HALF = REMEMBER_PREVIEW//2
            i_say_to_remember = txt[:HALF] + f" ...\n...(省略{len(txt_origin)-REMEMBER_PREVIEW}字)...\n... " + txt[-HALF:]
            if (flags["original_input_len"] - flags["clipped_input_len"]) > HALF:
                txt_clip = txt_clip  + f" ...\n...(省略{len(txt_origin)-len(txt_clip)-HALF}字)...\n... " + txt[-HALF:]
            else:
                pass
            i_say = txt_clip
        else:
            i_say_to_remember = i_say = txt_clip
    else:
        i_say_to_remember = i_say = txt_clip

    # 3. we search vector store and build prompts
    nodes = rag_worker.retrieve_from_store_with_query(i_say)
    prompt = rag_worker.build_prompt(query=i_say, nodes=nodes)

    # 4. it is time to query llms
    if len(chatbot) != 0: chatbot.pop(-1) # pop temp chat, because we are going to add them again inside `request_gpt_model_in_new_thread_with_ui_alive`
    model_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=prompt, inputs_show_user=i_say,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
        sys_prompt=system_prompt,
        retry_times_at_unknown_error=0
    )

    # 5. remember what has been asked / answered
    yield from update_ui_lastest_msg(model_say + '</br></br>' + f'对话记忆中, 请稍等 ({current_context}) ...', chatbot, history, delay=0.5) # 刷新界面
    rag_worker.remember_qa(i_say_to_remember, model_say)
    history.extend([i_say, model_say])

    yield from update_ui_lastest_msg(model_say, chatbot, history, delay=0, msg=tip) # 刷新界面

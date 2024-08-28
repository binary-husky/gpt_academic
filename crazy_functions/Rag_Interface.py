from toolbox import CatchException, update_ui, get_conf, get_log_folder
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.rag_fns.llama_index_worker import LlamaIndexRagWorker

RAG_WORKER_REGISTER = {}

@CatchException
def Rag问答(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    # first, we retrieve rag worker from global context
    user_name = chatbot.get_user()
    if user_name in RAG_WORKER_REGISTER:
        rag_worker = RAG_WORKER_REGISTER[user_name]
    else:
        rag_worker = RAG_WORKER_REGISTER[user_name] = LlamaIndexRagWorker(
            user_name, 
            llm_kwargs, 
            checkpoint_dir=get_log_folder(user_name, plugin_name='experimental_rag'), 
            auto_load_checkpoint=True)

    # second, we search vector store and build prompts
    i_say = txt
    nodes = rag_worker.retrieve_from_store_with_query(i_say)
    prompt = rag_worker.build_prompt(query=i_say, nodes=nodes)

    # third, it is time to query llms
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=prompt, inputs_show_user=i_say,
        llm_kwargs=llm_kwargs, chatbot=chatbot, history=history,
        sys_prompt=system_prompt,
        retry_times_at_unknown_error=0
    )

    # finally, remember what has been asked / answered
    rag_worker.remember_qa(i_say, gpt_say)
    history.extend([i_say, gpt_say])

    # yield, see you next time
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面 # 界面更新

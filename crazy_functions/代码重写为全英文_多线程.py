import threading
from request_llm.bridge_chatgpt import predict_no_ui_long_connection
from toolbox import update_ui
from toolbox import CatchException, write_results_to_file, report_execption
from .crazy_utils import breakdown_txt_to_satisfy_token_limit

def extract_code_block_carefully(txt):
    splitted = txt.split('```')
    n_code_block_seg = len(splitted) - 1
    if n_code_block_seg <= 1: return txt
    # 剩下的情况都开头除去 ``` 结尾除去一次 ```
    txt_out = '```'.join(splitted[1:-1])
    return txt_out



def break_txt_into_half_at_some_linebreak(txt):
    lines = txt.split('\n')
    n_lines = len(lines)
    pre = lines[:(n_lines//2)]
    post = lines[(n_lines//2):]
    return "\n".join(pre), "\n".join(post)


@CatchException
def 全项目切换英文(txt, llm_kwargs, plugin_kwargs, chatbot, history, sys_prompt, web_port):
    # 第1步：清空历史，以免输入溢出
    history = []

    # 第2步：尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        import tiktoken
    except:
        report_execption(chatbot, history, 
            a = f"解析项目: {txt}", 
            b = f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade tiktoken```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 第3步：集合文件
    import time, glob, os, shutil, re
    os.makedirs('gpt_log/generated_english_version', exist_ok=True)
    os.makedirs('gpt_log/generated_english_version/crazy_functions', exist_ok=True)
    file_manifest = [f for f in glob.glob('./*.py') if ('test_project' not in f) and ('gpt_log' not in f)] + \
                    [f for f in glob.glob('./crazy_functions/*.py') if ('test_project' not in f) and ('gpt_log' not in f)]
    # file_manifest = ['./toolbox.py']
    i_say_show_user_buffer = []

    # 第4步：随便显示点什么防止卡顿的感觉
    for index, fp in enumerate(file_manifest):
        # if 'test_project' in fp: continue
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        i_say_show_user =f'[{index}/{len(file_manifest)}] 接下来请将以下代码中包含的所有中文转化为英文，只输出转化后的英文代码，请用代码块输出代码: {os.path.abspath(fp)}'
        i_say_show_user_buffer.append(i_say_show_user)
        chatbot.append((i_say_show_user, "[Local Message] 等待多线程操作，中间过程不予显示."))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


    # 第5步：Token限制下的截断与处理
    MAX_TOKEN = 3000
    import tiktoken
    from toolbox import get_conf
    enc = tiktoken.encoding_for_model(*get_conf('LLM_MODEL'))
    def get_token_fn(txt): return len(enc.encode(txt))


    # 第6步：任务函数
    mutable_return = [None for _ in file_manifest]
    observe_window = [[""] for _ in file_manifest]
    def thread_worker(fp,index):
        if index > 10: 
            time.sleep(60)
            print('Openai 限制免费用户每分钟20次请求，降低请求频率中。')
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            file_content = f.read()
        i_say_template = lambda fp, file_content: f'接下来请将以下代码中包含的所有中文转化为英文，只输出代码，文件名是{fp}，文件代码是 ```{file_content}```'
        try:
            gpt_say = ""
            # 分解代码文件
            file_content_breakdown = breakdown_txt_to_satisfy_token_limit(file_content, get_token_fn, MAX_TOKEN)
            for file_content_partial in file_content_breakdown:
                i_say = i_say_template(fp, file_content_partial)
                # # ** gpt request **
                gpt_say_partial = predict_no_ui_long_connection(inputs=i_say, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=observe_window[index])
                gpt_say_partial = extract_code_block_carefully(gpt_say_partial)
                gpt_say += gpt_say_partial
            mutable_return[index] = gpt_say
        except ConnectionAbortedError as token_exceed_err:
            print('至少一个线程任务Token溢出而失败', e)
        except Exception as e:
            print('至少一个线程任务意外失败', e)

    # 第7步：所有线程同时开始执行任务函数
    handles = [threading.Thread(target=thread_worker, args=(fp,index)) for index, fp in enumerate(file_manifest)]
    for h in handles:
        h.daemon = True
        h.start()
    chatbot.append(('开始了吗？', f'多线程操作已经开始'))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 第8步：循环轮询各个线程是否执行完毕
    cnt = 0
    while True:
        cnt += 1
        time.sleep(0.2)
        th_alive = [h.is_alive() for h in handles]
        if not any(th_alive): break
        # 更好的UI视觉效果
        observe_win = []
        for thread_index, alive in enumerate(th_alive): 
            observe_win.append("[ ..."+observe_window[thread_index][0][-60:].replace('\n','').replace('```','...').replace(' ','.').replace('<br/>','.....').replace('$','.')+"... ]")
        stat = [f'执行中: {obs}\n\n' if alive else '已完成\n\n' for alive, obs in zip(th_alive, observe_win)]
        stat_str = ''.join(stat)
        chatbot[-1] = (chatbot[-1][0], f'多线程操作已经开始，完成情况: \n\n{stat_str}' + ''.join(['.']*(cnt%10+1)))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 第9步：把结果写入文件
    for index, h in enumerate(handles):
        h.join() # 这里其实不需要join了，肯定已经都结束了
        fp = file_manifest[index]
        gpt_say = mutable_return[index]
        i_say_show_user = i_say_show_user_buffer[index]

        where_to_relocate = f'gpt_log/generated_english_version/{fp}'
        if gpt_say is not None:
            with open(where_to_relocate, 'w+', encoding='utf-8') as f:  
                f.write(gpt_say)
        else:  # 失败
            shutil.copyfile(file_manifest[index], where_to_relocate)
        chatbot.append((i_say_show_user, f'[Local Message] 已完成{os.path.abspath(fp)}的转化，\n\n存入{os.path.abspath(where_to_relocate)}'))
        history.append(i_say_show_user); history.append(gpt_say)
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        time.sleep(1)

    # 第10步：备份一个文件
    res = write_results_to_file(history)
    chatbot.append(("生成一份任务执行报告", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

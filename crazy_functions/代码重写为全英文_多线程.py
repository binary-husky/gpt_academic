import threading
from predict import predict_no_ui_long_connection
from toolbox import CatchException, write_results_to_file



@CatchException
def 全项目切换英文(txt, top_p, temperature, chatbot, history, sys_prompt, WEB_PORT):
    history = []    # 清空历史，以免输入溢出
    # 集合文件
    import time, glob, os
    os.makedirs('gpt_log/generated_english_version', exist_ok=True)
    os.makedirs('gpt_log/generated_english_version/crazy_functions', exist_ok=True)
    file_manifest = [f for f in glob.glob('./*.py') if ('test_project' not in f) and ('gpt_log' not in f)] + \
                    [f for f in glob.glob('./crazy_functions/*.py') if ('test_project' not in f) and ('gpt_log' not in f)]
    i_say_show_user_buffer = []

    # 随便显示点什么防止卡顿的感觉
    for index, fp in enumerate(file_manifest):
        # if 'test_project' in fp: continue
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()
        i_say_show_user =f'[{index}/{len(file_manifest)}] 接下来请将以下代码中包含的所有中文转化为英文，只输出代码: {os.path.abspath(fp)}'
        i_say_show_user_buffer.append(i_say_show_user)
        chatbot.append((i_say_show_user, "[Local Message] 等待多线程操作，中间过程不予显示."))
        yield chatbot, history, '正常'

    # 任务函数
    mutable_return = [None for _ in file_manifest]
    def thread_worker(fp,index):
        with open(fp, 'r', encoding='utf-8') as f:
            file_content = f.read()
        i_say = f'接下来请将以下代码中包含的所有中文转化为英文，只输出代码，文件名是{fp}，文件代码是 ```{file_content}```'
        # ** gpt request **
        gpt_say = predict_no_ui_long_connection(inputs=i_say, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt)
        mutable_return[index] = gpt_say

    # 所有线程同时开始执行任务函数
    handles = [threading.Thread(target=thread_worker, args=(fp,index)) for index, fp in enumerate(file_manifest)]
    for h in handles:
        h.daemon = True
        h.start()
    chatbot.append(('开始了吗？', f'多线程操作已经开始'))
    yield chatbot, history, '正常'

    # 循环轮询各个线程是否执行完毕
    cnt = 0
    while True:
        time.sleep(1)
        th_alive = [h.is_alive() for h in handles]
        if not any(th_alive): break
        stat = ['执行中' if alive else '已完成' for alive in th_alive]
        stat_str = '|'.join(stat)
        cnt += 1
        chatbot[-1] = (chatbot[-1][0], f'多线程操作已经开始，完成情况: {stat_str}' + ''.join(['.']*(cnt%4)))
        yield chatbot, history, '正常'

    # 把结果写入文件
    for index, h in enumerate(handles):
        h.join() # 这里其实不需要join了，肯定已经都结束了
        fp = file_manifest[index]
        gpt_say = mutable_return[index]
        i_say_show_user = i_say_show_user_buffer[index]

        where_to_relocate = f'gpt_log/generated_english_version/{fp}'
        with open(where_to_relocate, 'w+', encoding='utf-8') as f: f.write(gpt_say.lstrip('```').rstrip('```'))
        chatbot.append((i_say_show_user, f'[Local Message] 已完成{os.path.abspath(fp)}的转化，\n\n存入{os.path.abspath(where_to_relocate)}'))
        history.append(i_say_show_user); history.append(gpt_say)
        yield chatbot, history, '正常'
        time.sleep(1)

    # 备份一个文件
    res = write_results_to_file(history)
    chatbot.append(("生成一份任务执行报告", res))
    yield chatbot, history, '正常'

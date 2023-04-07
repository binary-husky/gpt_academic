import traceback

def request_gpt_model_in_new_thread_with_ui_alive(inputs, inputs_show_user, top_p, temperature, chatbot, history, sys_prompt, refresh_interval=0.2):
    import time
    from concurrent.futures import ThreadPoolExecutor
    from request_llm.bridge_chatgpt import predict_no_ui_long_connection
    # 用户反馈
    chatbot.append([inputs_show_user, ""])
    msg = '正常'
    yield chatbot, [], msg
    executor = ThreadPoolExecutor(max_workers=16)
    mutable = ["", time.time()]
    future = executor.submit(lambda:
                             predict_no_ui_long_connection(
                                 inputs=inputs, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt, observe_window=mutable)
                             )
    while True:
        # yield一次以刷新前端页面
        time.sleep(refresh_interval)
        # “喂狗”（看门狗）
        mutable[1] = time.time()
        if future.done():
            break
        chatbot[-1] = [chatbot[-1][0], mutable[0]]
        msg = "正常"
        yield chatbot, [], msg
    return future.result()


def request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(inputs_array, inputs_show_user_array, top_p, temperature, chatbot, history_array, sys_prompt_array, refresh_interval=0.2, max_workers=10, scroller_max_len=30):
    import time
    from concurrent.futures import ThreadPoolExecutor
    from request_llm.bridge_chatgpt import predict_no_ui_long_connection
    assert len(inputs_array) == len(history_array)
    assert len(inputs_array) == len(sys_prompt_array)
    executor = ThreadPoolExecutor(max_workers=max_workers)
    n_frag = len(inputs_array)
    # 用户反馈
    chatbot.append(["请开始多线程操作。", ""])
    msg = '正常'
    yield chatbot, [], msg
    # 异步原子
    mutable = [["", time.time()] for _ in range(n_frag)]

    def _req_gpt(index, inputs, history, sys_prompt):
        try:
            gpt_say = predict_no_ui_long_connection(
                inputs=inputs, top_p=top_p, temperature=temperature, history=history, sys_prompt=sys_prompt, observe_window=mutable[index]
            )
        except:
            # 收拾残局
            tb_str = '```\n' + traceback.format_exc() + '```'
            gpt_say = f"[Local Message] 线程{index}在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
            if len(mutable[index][0]) > 0:
                gpt_say += "此线程失败前收到的回答：" + mutable[index][0]
        return gpt_say
    # 异步任务开始
    futures = [executor.submit(_req_gpt, index, inputs, history, sys_prompt) for index, inputs, history, sys_prompt in zip(
        range(len(inputs_array)), inputs_array, history_array, sys_prompt_array)]
    cnt = 0
    while True:
        # yield一次以刷新前端页面
        time.sleep(refresh_interval)
        cnt += 1
        worker_done = [h.done() for h in futures]
        if all(worker_done):
            executor.shutdown()
            break
        # 更好的UI视觉效果
        observe_win = []
        # 每个线程都要“喂狗”（看门狗）
        for thread_index, _ in enumerate(worker_done):
            mutable[thread_index][1] = time.time()
        # 在前端打印些好玩的东西
        for thread_index, _ in enumerate(worker_done):
            print_something_really_funny = "[ ...`"+mutable[thread_index][0][-scroller_max_len:].\
                replace('\n', '').replace('```', '...').replace(
                    ' ', '.').replace('<br/>', '.....').replace('$', '.')+"`... ]"
            observe_win.append(print_something_really_funny)
        stat_str = ''.join([f'执行中: {obs}\n\n' if not done else '已完成\n\n' for done, obs in zip(
            worker_done, observe_win)])
        chatbot[-1] = [chatbot[-1][0],
                       f'多线程操作已经开始，完成情况: \n\n{stat_str}' + ''.join(['.']*(cnt % 10+1))]
        msg = "正常"
        yield chatbot, [], msg
    # 异步任务结束
    gpt_response_collection = []
    for inputs_show_user, f in zip(inputs_show_user_array, futures):
        gpt_res = f.result()
        gpt_response_collection.extend([inputs_show_user, gpt_res])
    return gpt_response_collection


def breakdown_txt_to_satisfy_token_limit(txt, get_token_fn, limit):
    def cut(txt_tocut, must_break_at_empty_line):  # 递归
        if get_token_fn(txt_tocut) <= limit:
            return [txt_tocut]
        else:
            lines = txt_tocut.split('\n')
            estimated_line_cut = limit / get_token_fn(txt_tocut) * len(lines)
            estimated_line_cut = int(estimated_line_cut)
            for cnt in reversed(range(estimated_line_cut)):
                if must_break_at_empty_line:
                    if lines[cnt] != "":
                        continue
                print(cnt)
                prev = "\n".join(lines[:cnt])
                post = "\n".join(lines[cnt:])
                if get_token_fn(prev) < limit:
                    break
            if cnt == 0:
                print('what the fuck ?')
                raise RuntimeError("存在一行极长的文本！")
            # print(len(post))
            # 列表递归接龙
            result = [prev]
            result.extend(cut(post, must_break_at_empty_line))
            return result
    try:
        return cut(txt, must_break_at_empty_line=True)
    except RuntimeError:
        return cut(txt, must_break_at_empty_line=False)


def breakdown_txt_to_satisfy_token_limit_for_pdf(txt, get_token_fn, limit):
    def cut(txt_tocut, must_break_at_empty_line):  # 递归
        if get_token_fn(txt_tocut) <= limit:
            return [txt_tocut]
        else:
            lines = txt_tocut.split('\n')
            estimated_line_cut = limit / get_token_fn(txt_tocut) * len(lines)
            estimated_line_cut = int(estimated_line_cut)
            cnt = 0
            for cnt in reversed(range(estimated_line_cut)):
                if must_break_at_empty_line:
                    if lines[cnt] != "":
                        continue
                print(cnt)
                prev = "\n".join(lines[:cnt])
                post = "\n".join(lines[cnt:])
                if get_token_fn(prev) < limit:
                    break
            if cnt == 0:
                # print('what the fuck ? 存在一行极长的文本！')
                raise RuntimeError("存在一行极长的文本！")
            # print(len(post))
            # 列表递归接龙
            result = [prev]
            result.extend(cut(post, must_break_at_empty_line))
            return result
    try:
        return cut(txt, must_break_at_empty_line=True)
    except RuntimeError:
        try:
            return cut(txt, must_break_at_empty_line=False)
        except RuntimeError:
            # 这个中文的句号是故意的，作为一个标识而存在
            res = cut(txt.replace('.', '。\n'), must_break_at_empty_line=False)
            return [r.replace('。\n', '.') for r in res]

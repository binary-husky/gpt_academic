from toolbox import update_ui, get_conf, trimmed_format_exc

def input_clipping(inputs, history, max_token_limit):
    import numpy as np
    from request_llm.bridge_all import model_info
    enc = model_info["gpt-3.5-turbo"]['tokenizer']
    def get_token_num(txt): return len(enc.encode(txt, disallowed_special=()))

    mode = 'input-and-history'
    # 当 输入部分的token占比 小于 全文的一半时，只裁剪历史
    input_token_num = get_token_num(inputs)
    if input_token_num < max_token_limit//2: 
        mode = 'only-history'
        max_token_limit = max_token_limit - input_token_num

    everything = [inputs] if mode == 'input-and-history' else ['']
    everything.extend(history)
    n_token = get_token_num('\n'.join(everything))
    everything_token = [get_token_num(e) for e in everything]
    delta = max(everything_token) // 16 # 截断时的颗粒度
        
    while n_token > max_token_limit:
        where = np.argmax(everything_token)
        encoded = enc.encode(everything[where], disallowed_special=())
        clipped_encoded = encoded[:len(encoded)-delta]
        everything[where] = enc.decode(clipped_encoded)[:-1]    # -1 to remove the may-be illegal char
        everything_token[where] = get_token_num(everything[where])
        n_token = get_token_num('\n'.join(everything))

    if mode == 'input-and-history':
        inputs = everything[0]
    else:
        pass
    history = everything[1:]
    return inputs, history

def request_gpt_model_in_new_thread_with_ui_alive(
        inputs, inputs_show_user, llm_kwargs, 
        chatbot, history, sys_prompt, refresh_interval=0.2,
        handle_token_exceed=True, 
        retry_times_at_unknown_error=2,
        ):
    """
    Request GPT model，请求GPT模型同时维持用户界面活跃。

    输入参数 Args （以_array结尾的输入变量都是列表，列表长度为子任务的数量，执行时，会把列表拆解，放到每个子线程中分别执行）:
        inputs (string): List of inputs （输入）
        inputs_show_user (string): List of inputs to show user（展现在报告中的输入，借助此参数，在汇总报告中隐藏啰嗦的真实输入，增强报告的可读性）
        top_p (float): Top p value for sampling from model distribution （GPT参数，浮点数）
        temperature (float): Temperature value for sampling from model distribution（GPT参数，浮点数）
        chatbot: chatbot inputs and outputs （用户界面对话窗口句柄，用于数据流可视化）
        history (list): List of chat history （历史，对话历史列表）
        sys_prompt (string): List of system prompts （系统输入，列表，用于输入给GPT的前提提示，比如你是翻译官怎样怎样）
        refresh_interval (float, optional): Refresh interval for UI (default: 0.2) （刷新时间间隔频率，建议低于1，不可高于3，仅仅服务于视觉效果）
        handle_token_exceed：是否自动处理token溢出的情况，如果选择自动处理，则会在溢出时暴力截断，默认开启
        retry_times_at_unknown_error：失败时的重试次数

    输出 Returns:
        future: 输出，GPT返回的结果
    """
    import time
    from concurrent.futures import ThreadPoolExecutor
    from request_llm.bridge_all import predict_no_ui_long_connection
    # 用户反馈
    chatbot.append([inputs_show_user, ""])
    yield from update_ui(chatbot=chatbot, history=[]) # 刷新界面
    executor = ThreadPoolExecutor(max_workers=16)
    mutable = ["", time.time(), ""]
    def _req_gpt(inputs, history, sys_prompt):
        retry_op = retry_times_at_unknown_error
        exceeded_cnt = 0
        while True:
            # watchdog error
            if len(mutable) >= 2 and (time.time()-mutable[1]) > 5: 
                raise RuntimeError("检测到程序终止。")
            try:
                # 【第一种情况】：顺利完成
                result = predict_no_ui_long_connection(
                    inputs=inputs, llm_kwargs=llm_kwargs,
                    history=history, sys_prompt=sys_prompt, observe_window=mutable)
                return result
            except ConnectionAbortedError as token_exceeded_error:
                # 【第二种情况】：Token溢出
                if handle_token_exceed:
                    exceeded_cnt += 1
                    # 【选择处理】 尝试计算比例，尽可能多地保留文本
                    from toolbox import get_reduce_token_percent
                    p_ratio, n_exceed = get_reduce_token_percent(str(token_exceeded_error))
                    MAX_TOKEN = 4096
                    EXCEED_ALLO = 512 + 512 * exceeded_cnt
                    inputs, history = input_clipping(inputs, history, max_token_limit=MAX_TOKEN-EXCEED_ALLO)
                    mutable[0] += f'[Local Message] 警告，文本过长将进行截断，Token溢出数：{n_exceed}。\n\n'
                    continue # 返回重试
                else:
                    # 【选择放弃】
                    tb_str = '```\n' + trimmed_format_exc() + '```'
                    mutable[0] += f"[Local Message] 警告，在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                    return mutable[0] # 放弃
            except:
                # 【第三种情况】：其他错误：重试几次
                tb_str = '```\n' + trimmed_format_exc() + '```'
                print(tb_str)
                mutable[0] += f"[Local Message] 警告，在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                if retry_op > 0:
                    retry_op -= 1
                    mutable[0] += f"[Local Message] 重试中，请稍等 {retry_times_at_unknown_error-retry_op}/{retry_times_at_unknown_error}：\n\n"
                    if ("Rate limit reached" in tb_str) or ("Too Many Requests" in tb_str):
                        time.sleep(30)
                    time.sleep(5)
                    continue # 返回重试
                else:
                    time.sleep(5)
                    return mutable[0] # 放弃

    # 提交任务
    future = executor.submit(_req_gpt, inputs, history, sys_prompt)
    while True:
        # yield一次以刷新前端页面
        time.sleep(refresh_interval)
        # “喂狗”（看门狗）
        mutable[1] = time.time()
        if future.done():
            break
        chatbot[-1] = [chatbot[-1][0], mutable[0]]
        yield from update_ui(chatbot=chatbot, history=[]) # 刷新界面

    final_result = future.result()
    chatbot[-1] = [chatbot[-1][0], final_result]
    yield from update_ui(chatbot=chatbot, history=[]) # 如果最后成功了，则删除报错信息
    return final_result


def request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency(
        inputs_array, inputs_show_user_array, llm_kwargs, 
        chatbot, history_array, sys_prompt_array, 
        refresh_interval=0.2, max_workers=-1, scroller_max_len=30,
        handle_token_exceed=True, show_user_at_complete=False,
        retry_times_at_unknown_error=2,
        ):
    """
    Request GPT model using multiple threads with UI and high efficiency
    请求GPT模型的[多线程]版。
    具备以下功能：
        实时在UI上反馈远程数据流
        使用线程池，可调节线程池的大小避免openai的流量限制错误
        处理中途中止的情况
        网络等出问题时，会把traceback和已经接收的数据转入输出

    输入参数 Args （以_array结尾的输入变量都是列表，列表长度为子任务的数量，执行时，会把列表拆解，放到每个子线程中分别执行）:
        inputs_array (list): List of inputs （每个子任务的输入）
        inputs_show_user_array (list): List of inputs to show user（每个子任务展现在报告中的输入，借助此参数，在汇总报告中隐藏啰嗦的真实输入，增强报告的可读性）
        llm_kwargs: llm_kwargs参数
        chatbot: chatbot （用户界面对话窗口句柄，用于数据流可视化）
        history_array (list): List of chat history （历史对话输入，双层列表，第一层列表是子任务分解，第二层列表是对话历史）
        sys_prompt_array (list): List of system prompts （系统输入，列表，用于输入给GPT的前提提示，比如你是翻译官怎样怎样）
        refresh_interval (float, optional): Refresh interval for UI (default: 0.2) （刷新时间间隔频率，建议低于1，不可高于3，仅仅服务于视觉效果）
        max_workers (int, optional): Maximum number of threads (default: see config.py) （最大线程数，如果子任务非常多，需要用此选项防止高频地请求openai导致错误）
        scroller_max_len (int, optional): Maximum length for scroller (default: 30)（数据流的显示最后收到的多少个字符，仅仅服务于视觉效果）
        handle_token_exceed (bool, optional): （是否在输入过长时，自动缩减文本）
        handle_token_exceed：是否自动处理token溢出的情况，如果选择自动处理，则会在溢出时暴力截断，默认开启
        show_user_at_complete (bool, optional): (在结束时，把完整输入-输出结果显示在聊天框)
        retry_times_at_unknown_error：子任务失败时的重试次数

    输出 Returns:
        list: List of GPT model responses （每个子任务的输出汇总，如果某个子任务出错，response中会携带traceback报错信息，方便调试和定位问题。）
    """
    import time, random
    from concurrent.futures import ThreadPoolExecutor
    from request_llm.bridge_all import predict_no_ui_long_connection
    assert len(inputs_array) == len(history_array)
    assert len(inputs_array) == len(sys_prompt_array)
    if max_workers == -1: # 读取配置文件
        try: max_workers, = get_conf('DEFAULT_WORKER_NUM')
        except: max_workers = 8
        if max_workers <= 0: max_workers = 3
    # 屏蔽掉 chatglm的多线程，可能会导致严重卡顿
    if not (llm_kwargs['llm_model'].startswith('gpt-') or llm_kwargs['llm_model'].startswith('api2d-')):
        max_workers = 1
        
    executor = ThreadPoolExecutor(max_workers=max_workers)
    n_frag = len(inputs_array)
    # 用户反馈
    chatbot.append(["请开始多线程操作。", ""])
    yield from update_ui(chatbot=chatbot, history=[]) # 刷新界面
    # 跨线程传递
    mutable = [["", time.time(), "等待中"] for _ in range(n_frag)]

    # 子线程任务
    def _req_gpt(index, inputs, history, sys_prompt):
        gpt_say = ""
        retry_op = retry_times_at_unknown_error
        exceeded_cnt = 0
        mutable[index][2] = "执行中"
        while True:
            # watchdog error
            if len(mutable[index]) >= 2 and (time.time()-mutable[index][1]) > 5: 
                raise RuntimeError("检测到程序终止。")
            try:
                # 【第一种情况】：顺利完成
                # time.sleep(10); raise RuntimeError("测试")
                gpt_say = predict_no_ui_long_connection(
                    inputs=inputs, llm_kwargs=llm_kwargs, history=history, 
                    sys_prompt=sys_prompt, observe_window=mutable[index], console_slience=True
                )
                mutable[index][2] = "已成功"
                return gpt_say
            except ConnectionAbortedError as token_exceeded_error:
                # 【第二种情况】：Token溢出，
                if handle_token_exceed:
                    exceeded_cnt += 1
                    # 【选择处理】 尝试计算比例，尽可能多地保留文本
                    from toolbox import get_reduce_token_percent
                    p_ratio, n_exceed = get_reduce_token_percent(str(token_exceeded_error))
                    MAX_TOKEN = 4096
                    EXCEED_ALLO = 512 + 512 * exceeded_cnt
                    inputs, history = input_clipping(inputs, history, max_token_limit=MAX_TOKEN-EXCEED_ALLO)
                    gpt_say += f'[Local Message] 警告，文本过长将进行截断，Token溢出数：{n_exceed}。\n\n'
                    mutable[index][2] = f"截断重试"
                    continue # 返回重试
                else:
                    # 【选择放弃】
                    tb_str = '```\n' + trimmed_format_exc() + '```'
                    gpt_say += f"[Local Message] 警告，线程{index}在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                    if len(mutable[index][0]) > 0: gpt_say += "此线程失败前收到的回答：\n\n" + mutable[index][0]
                    mutable[index][2] = "输入过长已放弃"
                    return gpt_say # 放弃
            except:
                # 【第三种情况】：其他错误
                tb_str = '```\n' + trimmed_format_exc() + '```'
                print(tb_str)
                gpt_say += f"[Local Message] 警告，线程{index}在执行过程中遭遇问题, Traceback：\n\n{tb_str}\n\n"
                if len(mutable[index][0]) > 0: gpt_say += "此线程失败前收到的回答：\n\n" + mutable[index][0]
                if retry_op > 0: 
                    retry_op -= 1
                    wait = random.randint(5, 20)
                    if ("Rate limit reached" in tb_str) or ("Too Many Requests" in tb_str):
                        wait = wait * 3
                        fail_info = "OpenAI绑定信用卡可解除频率限制 "
                    else:
                        fail_info = ""
                    # 也许等待十几秒后，情况会好转
                    for i in range(wait):
                        mutable[index][2] = f"{fail_info}等待重试 {wait-i}"; time.sleep(1)
                    # 开始重试
                    mutable[index][2] = f"重试中 {retry_times_at_unknown_error-retry_op}/{retry_times_at_unknown_error}"
                    continue # 返回重试
                else:
                    mutable[index][2] = "已失败"
                    wait = 5
                    time.sleep(5)
                    return gpt_say # 放弃

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
        # 在前端打印些好玩的东西
        stat_str = ''.join([f'`{mutable[thread_index][2]}`: {obs}\n\n' 
                            if not done else f'`{mutable[thread_index][2]}`\n\n' 
                            for thread_index, done, obs in zip(range(len(worker_done)), worker_done, observe_win)])
        # 在前端打印些好玩的东西
        chatbot[-1] = [chatbot[-1][0], f'多线程操作已经开始，完成情况: \n\n{stat_str}' + ''.join(['.']*(cnt % 10+1))]
        yield from update_ui(chatbot=chatbot, history=[]) # 刷新界面
    
    # 异步任务结束
    gpt_response_collection = []
    for inputs_show_user, f in zip(inputs_show_user_array, futures):
        gpt_res = f.result()
        gpt_response_collection.extend([inputs_show_user, gpt_res])
    
    # 是否在结束时，在界面上显示结果
    if show_user_at_complete:
        for inputs_show_user, f in zip(inputs_show_user_array, futures):
            gpt_res = f.result()
            chatbot.append([inputs_show_user, gpt_res])
            yield from update_ui(chatbot=chatbot, history=[]) # 刷新界面
            time.sleep(0.3)
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


def force_breakdown(txt, limit, get_token_fn):
    """
    当无法用标点、空行分割时，我们用最暴力的方法切割
    """
    for i in reversed(range(len(txt))):
        if get_token_fn(txt[:i]) < limit:
            return txt[:i], txt[i:]
    return "Tiktoken未知错误", "Tiktoken未知错误"

def breakdown_txt_to_satisfy_token_limit_for_pdf(txt, get_token_fn, limit):
    # 递归
    def cut(txt_tocut, must_break_at_empty_line, break_anyway=False):  
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
                prev = "\n".join(lines[:cnt])
                post = "\n".join(lines[cnt:])
                if get_token_fn(prev) < limit:
                    break
            if cnt == 0:
                if break_anyway:
                    prev, post = force_breakdown(txt_tocut, limit, get_token_fn)
                else:
                    raise RuntimeError(f"存在一行极长的文本！{txt_tocut}")
            # print(len(post))
            # 列表递归接龙
            result = [prev]
            result.extend(cut(post, must_break_at_empty_line, break_anyway=break_anyway))
            return result
    try:
        # 第1次尝试，将双空行（\n\n）作为切分点
        return cut(txt, must_break_at_empty_line=True)
    except RuntimeError:
        try:
            # 第2次尝试，将单空行（\n）作为切分点
            return cut(txt, must_break_at_empty_line=False)
        except RuntimeError:
            try:
                # 第3次尝试，将英文句号（.）作为切分点
                res = cut(txt.replace('.', '。\n'), must_break_at_empty_line=False) # 这个中文的句号是故意的，作为一个标识而存在
                return [r.replace('。\n', '.') for r in res]
            except RuntimeError as e:
                try:
                    # 第4次尝试，将中文句号（。）作为切分点
                    res = cut(txt.replace('。', '。。\n'), must_break_at_empty_line=False)
                    return [r.replace('。。\n', '。') for r in res]
                except RuntimeError as e:
                    # 第5次尝试，没办法了，随便切一下敷衍吧
                    return cut(txt, must_break_at_empty_line=False, break_anyway=True)



def read_and_clean_pdf_text(fp):
    """
    这个函数用于分割pdf，用了很多trick，逻辑较乱，效果奇好

    **输入参数说明**
    - `fp`：需要读取和清理文本的pdf文件路径

    **输出参数说明**
    - `meta_txt`：清理后的文本内容字符串
    - `page_one_meta`：第一页清理后的文本内容列表

    **函数功能**
    读取pdf文件并清理其中的文本内容，清理规则包括：
    - 提取所有块元的文本信息，并合并为一个字符串
    - 去除短块（字符数小于100）并替换为回车符
    - 清理多余的空行
    - 合并小写字母开头的段落块并替换为空格
    - 清除重复的换行
    - 将每个换行符替换为两个换行符，使每个段落之间有两个换行符分隔
    """
    import fitz, copy
    import re
    import numpy as np
    from colorful import print亮黄, print亮绿
    fc = 0  # Index 0 文本
    fs = 1  # Index 1 字体
    fb = 2  # Index 2 框框
    REMOVE_FOOT_NOTE = True # 是否丢弃掉 不是正文的内容 （比正文字体小，如参考文献、脚注、图注等）
    REMOVE_FOOT_FFSIZE_PERCENT = 0.95 # 小于正文的？时，判定为不是正文（有些文章的正文部分字体大小不是100%统一的，有肉眼不可见的小变化）
    def primary_ffsize(l):
        """
        提取文本块主字体
        """
        fsize_statiscs = {}
        for wtf in l['spans']:
            if wtf['size'] not in fsize_statiscs: fsize_statiscs[wtf['size']] = 0
            fsize_statiscs[wtf['size']] += len(wtf['text'])
        return max(fsize_statiscs, key=fsize_statiscs.get)
        
    def ffsize_same(a,b):
        """
        提取字体大小是否近似相等
        """
        return abs((a-b)/max(a,b)) < 0.02

    with fitz.open(fp) as doc:
        meta_txt = []
        meta_font = []

        meta_line = []
        meta_span = []
        ############################## <第 1 步，搜集初始信息> ##################################
        for index, page in enumerate(doc):
            # file_content += page.get_text()
            text_areas = page.get_text("dict")  # 获取页面上的文本信息
            for t in text_areas['blocks']:
                if 'lines' in t:
                    pf = 998
                    for l in t['lines']:
                        txt_line = "".join([wtf['text'] for wtf in l['spans']])
                        if len(txt_line) == 0: continue
                        pf = primary_ffsize(l)
                        meta_line.append([txt_line, pf, l['bbox'], l])
                        for wtf in l['spans']: # for l in t['lines']:
                            meta_span.append([wtf['text'], wtf['size'], len(wtf['text'])])
                    # meta_line.append(["NEW_BLOCK", pf])
            # 块元提取                           for each word segment with in line                       for each line         cross-line words                          for each block
            meta_txt.extend([" ".join(["".join([wtf['text'] for wtf in l['spans']]) for l in t['lines']]).replace(
                '- ', '') for t in text_areas['blocks'] if 'lines' in t])
            meta_font.extend([np.mean([np.mean([wtf['size'] for wtf in l['spans']])
                             for l in t['lines']]) for t in text_areas['blocks'] if 'lines' in t])
            if index == 0:
                page_one_meta = [" ".join(["".join([wtf['text'] for wtf in l['spans']]) for l in t['lines']]).replace(
                    '- ', '') for t in text_areas['blocks'] if 'lines' in t]
                
        ############################## <第 2 步，获取正文主字体> ##################################
        fsize_statiscs = {}
        for span in meta_span:
            if span[1] not in fsize_statiscs: fsize_statiscs[span[1]] = 0
            fsize_statiscs[span[1]] += span[2]
        main_fsize = max(fsize_statiscs, key=fsize_statiscs.get)
        if REMOVE_FOOT_NOTE:
            give_up_fize_threshold = main_fsize * REMOVE_FOOT_FFSIZE_PERCENT

        ############################## <第 3 步，切分和重新整合> ##################################
        mega_sec = []
        sec = []
        for index, line in enumerate(meta_line):
            if index == 0: 
                sec.append(line[fc])
                continue
            if REMOVE_FOOT_NOTE:
                if meta_line[index][fs] <= give_up_fize_threshold:
                    continue
            if ffsize_same(meta_line[index][fs], meta_line[index-1][fs]):
                # 尝试识别段落
                if meta_line[index][fc].endswith('.') and\
                    (meta_line[index-1][fc] != 'NEW_BLOCK') and \
                    (meta_line[index][fb][2] - meta_line[index][fb][0]) < (meta_line[index-1][fb][2] - meta_line[index-1][fb][0]) * 0.7:
                    sec[-1] += line[fc]
                    sec[-1] += "\n\n"
                else:
                    sec[-1] += " "
                    sec[-1] += line[fc]
            else:
                if (index+1 < len(meta_line)) and \
                    meta_line[index][fs] > main_fsize:
                    # 单行 + 字体大
                    mega_sec.append(copy.deepcopy(sec))
                    sec = []
                    sec.append("# " + line[fc])
                else:
                    # 尝试识别section
                    if meta_line[index-1][fs] > meta_line[index][fs]:
                        sec.append("\n" + line[fc])
                    else:
                        sec.append(line[fc])
        mega_sec.append(copy.deepcopy(sec))

        finals = []
        for ms in mega_sec:
            final = " ".join(ms)
            final = final.replace('- ', ' ')
            finals.append(final)
        meta_txt = finals

        ############################## <第 4 步，乱七八糟的后处理> ##################################
        def 把字符太少的块清除为回车(meta_txt):
            for index, block_txt in enumerate(meta_txt):
                if len(block_txt) < 100:
                    meta_txt[index] = '\n'
            return meta_txt
        meta_txt = 把字符太少的块清除为回车(meta_txt)

        def 清理多余的空行(meta_txt):
            for index in reversed(range(1, len(meta_txt))):
                if meta_txt[index] == '\n' and meta_txt[index-1] == '\n':
                    meta_txt.pop(index)
            return meta_txt
        meta_txt = 清理多余的空行(meta_txt)

        def 合并小写开头的段落块(meta_txt):
            def starts_with_lowercase_word(s):
                pattern = r"^[a-z]+"
                match = re.match(pattern, s)
                if match:
                    return True
                else:
                    return False
            for _ in range(100):
                for index, block_txt in enumerate(meta_txt):
                    if starts_with_lowercase_word(block_txt):
                        if meta_txt[index-1] != '\n':
                            meta_txt[index-1] += ' '
                        else:
                            meta_txt[index-1] = ''
                        meta_txt[index-1] += meta_txt[index]
                        meta_txt[index] = '\n'
            return meta_txt
        meta_txt = 合并小写开头的段落块(meta_txt)
        meta_txt = 清理多余的空行(meta_txt)

        meta_txt = '\n'.join(meta_txt)
        # 清除重复的换行
        for _ in range(5):
            meta_txt = meta_txt.replace('\n\n', '\n')

        # 换行 -> 双换行
        meta_txt = meta_txt.replace('\n', '\n\n')

        ############################## <第 5 步，展示分割效果> ##################################
        # for f in finals:
        #    print亮黄(f)
        #    print亮绿('***************************')

    return meta_txt, page_one_meta

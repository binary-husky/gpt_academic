import copy
from shared_utils.config_loader import get_conf

def get_token_num(txt, tokenizer):
    return len(tokenizer.encode(txt, disallowed_special=()))

def get_model_info():
    from request_llms.bridge_all import model_info
    return model_info

def clip_history(inputs, history, tokenizer, max_token_limit):
    """
    reduce the length of history by clipping.
    this function search for the longest entries to clip, little by little,
    until the number of token of history is reduced under threshold.

    通过裁剪来缩短历史记录的长度。
    此函数逐渐地搜索最长的条目进行剪辑，
    直到历史记录的标记数量降低到阈值以下。

    被动触发裁剪
    """
    import numpy as np

    input_token_num = get_token_num(inputs)

    if max_token_limit < 5000:
        output_token_expect = 256  # 4k & 2k models
    elif max_token_limit < 9000:
        output_token_expect = 512  # 8k models
    else:
        output_token_expect = 1024  # 16k & 32k models

    if input_token_num < max_token_limit * 3 / 4:
        # 当输入部分的token占比小于限制的3/4时，裁剪时
        # 1. 把input的余量留出来
        max_token_limit = max_token_limit - input_token_num
        # 2. 把输出用的余量留出来
        max_token_limit = max_token_limit - output_token_expect
        # 3. 如果余量太小了，直接清除历史
        if max_token_limit < output_token_expect:
            history = []
            return history
    else:
        # 当输入部分的token占比 > 限制的3/4时，直接清除历史
        history = []
        return history

    everything = [""]
    everything.extend(history)
    n_token = get_token_num("\n".join(everything))
    everything_token = [get_token_num(e) for e in everything]

    # 截断时的颗粒度
    delta = max(everything_token) // 16

    while n_token > max_token_limit:
        where = np.argmax(everything_token)
        encoded = tokenizer.encode(everything[where], disallowed_special=())
        clipped_encoded = encoded[: len(encoded) - delta]
        everything[where] = tokenizer.decode(clipped_encoded)[
            :-1
        ]  # -1 to remove the may-be illegal char
        everything_token[where] = get_token_num(everything[where])
        n_token = get_token_num("\n".join(everything))

    history = everything[1:]
    return history



def auto_context_clip_each_message(current, history):
    """
    clip_history 是被动触发的

    主动触发裁剪
    """
    context = history + [current]
    trigger_clip_token_len = get_conf('AUTO_CONTEXT_CLIP_TRIGGER_TOKEN_LEN')
    model_info = get_model_info()
    tokenizer = model_info['gpt-4']['tokenizer']
    # 只保留最近的128条记录，无论token长度，防止计算token时计算过长的时间
    max_round = get_conf('AUTO_CONTEXT_MAX_ROUND')
    char_len = sum([len(h) for h in context])
    if char_len < trigger_clip_token_len*2:
        # 不需要裁剪
        history = context[:-1]
        current = context[-1]
        return current, history
    if len(context) > max_round:
        context = context[-max_round:]
    # 计算各个历史记录的token长度
    context_token_num = [get_token_num(h, tokenizer) for h in context]
    context_token_num_old = copy.copy(context_token_num)
    total_token_num = total_token_num_old = sum(context_token_num)
    if total_token_num < trigger_clip_token_len:
        # 不需要裁剪
        history = context[:-1]
        current = context[-1]
        return current, history
    clip_token_len = trigger_clip_token_len * 0.85
    # 越长越先被裁，越靠后越先被裁
    max_clip_ratio: list[float] = get_conf('AUTO_CONTEXT_MAX_CLIP_RATIO')
    max_clip_ratio = list(reversed(max_clip_ratio))
    if len(context) > len(max_clip_ratio):
        # give up the oldest context
        context = context[-len(max_clip_ratio):]
        context_token_num = context_token_num[-len(max_clip_ratio):]
    if len(context) < len(max_clip_ratio):
        # match the length of two array
        max_clip_ratio = max_clip_ratio[-len(context):]

    # compute rank
    clip_prior_weight = [(token_num/clip_token_len + (len(context) - index)*0.1) for index, token_num in enumerate(context_token_num)]
    # print('clip_prior_weight', clip_prior_weight)
    # get sorted index of context_token_num, from largest to smallest
    sorted_index = sorted(range(len(context_token_num)), key=lambda k: clip_prior_weight[k], reverse=True)

    # pre compute space yield
    for index in sorted_index:
        print('index', index, f'current total {total_token_num}, target {clip_token_len}')
        if total_token_num < clip_token_len:
            # no need to clip
            break
        # clip room left
        clip_room_left = total_token_num - clip_token_len
        # get the clip ratio
        allowed_token_num_this_entry = max_clip_ratio[index] * clip_token_len
        if context_token_num[index] < allowed_token_num_this_entry:
            print('index', index, '[allowed] before', context_token_num[index], 'allowed', allowed_token_num_this_entry)
            continue

        token_to_clip = context_token_num[index] - allowed_token_num_this_entry
        if token_to_clip*0.85 > clip_room_left:
            print('index', index, '[careful clip] token_to_clip', token_to_clip, 'clip_room_left', clip_room_left)
            token_to_clip = clip_room_left

        token_percent_to_clip = token_to_clip / context_token_num[index]
        char_percent_to_clip = token_percent_to_clip
        text_this_entry = context[index]
        char_num_to_clip = int(len(text_this_entry) * char_percent_to_clip)
        if char_num_to_clip < 500:
            # 如果裁剪的字符数小于500，则不裁剪
            print('index', index, 'before', context_token_num[index], 'allowed', allowed_token_num_this_entry)
            continue
        char_num_to_clip += 200 # 稍微多加一点
        char_to_preseve = len(text_this_entry) - char_num_to_clip
        _half = int(char_to_preseve / 2)
        # 前半 + ... (content clipped because token overflows) ... + 后半
        text_this_entry_clip = text_this_entry[:_half] + \
                             " ... (content clipped because token overflows) ... " \
                             + text_this_entry[-_half:]
        context[index] = text_this_entry_clip
        post_clip_token_cnt = get_token_num(text_this_entry_clip, tokenizer)
        print('index', index, 'before', context_token_num[index], 'allowed', allowed_token_num_this_entry, 'after', post_clip_token_cnt)
        context_token_num[index] = post_clip_token_cnt
        total_token_num = sum(context_token_num)
    context_token_num_final = [get_token_num(h, tokenizer) for h in context]
    print('context_token_num_old', context_token_num_old)
    print('context_token_num_final', context_token_num_final)
    print('token change from', total_token_num_old, 'to', sum(context_token_num_final), 'target', clip_token_len)
    history = context[:-1]
    current = context[-1]
    return current, history



def auto_context_clip_search_optimal(current, history, promote_latest_long_message=False):
    """
    current: 当前消息
    history: 历史消息列表
    promote_latest_long_message: 是否特别提高最后一条长message的权重，避免过度裁剪

    主动触发裁剪
    """
    context = history + [current]
    trigger_clip_token_len = get_conf('AUTO_CONTEXT_CLIP_TRIGGER_TOKEN_LEN')
    model_info = get_model_info()
    tokenizer = model_info['gpt-4']['tokenizer']
    # 只保留最近的128条记录，无论token长度，防止计算token时计算过长的时间
    max_round = get_conf('AUTO_CONTEXT_MAX_ROUND')
    char_len = sum([len(h) for h in context])
    if char_len < trigger_clip_token_len:
        # 不需要裁剪
        history = context[:-1]
        current = context[-1]
        return current, history
    if len(context) > max_round:
        context = context[-max_round:]
    # 计算各个历史记录的token长度
    context_token_num = [get_token_num(h, tokenizer) for h in context]
    context_token_num_old = copy.copy(context_token_num)
    total_token_num = total_token_num_old = sum(context_token_num)
    if total_token_num < trigger_clip_token_len:
        # 不需要裁剪
        history = context[:-1]
        current = context[-1]
        return current, history
    clip_token_len = trigger_clip_token_len * 0.90
    max_clip_ratio: list[float] = get_conf('AUTO_CONTEXT_MAX_CLIP_RATIO')
    max_clip_ratio = list(reversed(max_clip_ratio))
    if len(context) > len(max_clip_ratio):
        # give up the oldest context
        context = context[-len(max_clip_ratio):]
        context_token_num = context_token_num[-len(max_clip_ratio):]
    if len(context) < len(max_clip_ratio):
        # match the length of two array
        max_clip_ratio = max_clip_ratio[-len(context):]

    _scale = _scale_init = 1.25
    token_percent_arr = [(token_num/clip_token_len) for index, token_num in enumerate(context_token_num)]

    # promote last long message, avoid clipping it too much
    if promote_latest_long_message:
        promote_weight_constant = 1.6
        promote_index = -1
        threshold = 0.50
        for index, token_percent in enumerate(token_percent_arr):
            if token_percent > threshold:
                promote_index = index
        if promote_index >= 0:
            max_clip_ratio[promote_index] = promote_weight_constant

    max_clip_ratio_arr = max_clip_ratio
    step = 0.05
    for i in range(int(_scale_init / step) - 1):
        _take = 0
        for max_clip, token_r in zip(max_clip_ratio_arr, token_percent_arr):
            _take += min(max_clip * _scale, token_r)
        if _take < 1.0:
            break
        _scale -= 0.05

    # print('optimal scale', _scale)
    # print([_scale * max_clip for max_clip in max_clip_ratio_arr])
    # print([token_r for token_r in token_percent_arr])
    # print([min(token_r, _scale * max_clip) for token_r, max_clip in zip(token_percent_arr, max_clip_ratio_arr)])
    eps = 0.05
    max_clip_ratio = [_scale * max_clip + eps for max_clip in max_clip_ratio_arr]

    # compute rank
    # clip_prior_weight_old = [(token_num/clip_token_len + (len(context) - index)*0.1) for index, token_num in enumerate(context_token_num)]
    clip_prior_weight = [ token_r / max_clip  for max_clip, token_r in zip(max_clip_ratio_arr, token_percent_arr)]

    # sorted_index_old = sorted(range(len(context_token_num)), key=lambda k: clip_prior_weight_old[k], reverse=True)
    # print('sorted_index_old', sorted_index_old)
    sorted_index = sorted(range(len(context_token_num)), key=lambda k: clip_prior_weight[k], reverse=True)
    # print('sorted_index', sorted_index)

    # pre compute space yield
    for index in sorted_index:
        # print('index', index, f'current total {total_token_num}, target {clip_token_len}')
        if total_token_num < clip_token_len:
            # no need to clip
            break
        # clip room left
        clip_room_left = total_token_num - clip_token_len
        # get the clip ratio
        allowed_token_num_this_entry = max_clip_ratio[index] * clip_token_len
        if context_token_num[index] < allowed_token_num_this_entry:
            # print('index', index, '[allowed] before', context_token_num[index], 'allowed', allowed_token_num_this_entry)
            continue

        token_to_clip = context_token_num[index] - allowed_token_num_this_entry
        if token_to_clip*0.85 > clip_room_left:
            # print('index', index, '[careful clip] token_to_clip', token_to_clip, 'clip_room_left', clip_room_left)
            token_to_clip = clip_room_left

        token_percent_to_clip = token_to_clip / context_token_num[index]
        char_percent_to_clip = token_percent_to_clip
        text_this_entry = context[index]
        char_num_to_clip = int(len(text_this_entry) * char_percent_to_clip)
        if char_num_to_clip < 500:
            # 如果裁剪的字符数小于500，则不裁剪
            # print('index', index, 'before', context_token_num[index], 'allowed', allowed_token_num_this_entry)
            continue
        eps = 200
        char_num_to_clip = char_num_to_clip + eps # 稍微多加一点
        char_to_preseve = len(text_this_entry) - char_num_to_clip
        _half = int(char_to_preseve / 2)
        # 前半 + ... (content clipped because token overflows) ... + 后半
        text_this_entry_clip = text_this_entry[:_half] + \
                             " ... (content clipped because token overflows) ... " \
                             + text_this_entry[-_half:]
        context[index] = text_this_entry_clip
        post_clip_token_cnt = get_token_num(text_this_entry_clip, tokenizer)
        # print('index', index, 'before', context_token_num[index], 'allowed', allowed_token_num_this_entry, 'after', post_clip_token_cnt)
        context_token_num[index] = post_clip_token_cnt
        total_token_num = sum(context_token_num)
    context_token_num_final = [get_token_num(h, tokenizer) for h in context]
    # print('context_token_num_old', context_token_num_old)
    # print('context_token_num_final', context_token_num_final)
    # print('token change from', total_token_num_old, 'to', sum(context_token_num_final), 'target', clip_token_len)
    history = context[:-1]
    current = context[-1]
    return current, history

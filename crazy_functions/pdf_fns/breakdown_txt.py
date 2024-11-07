from crazy_functions.ipc_fns.mp import run_in_subprocess_with_timeout
from loguru import logger

def force_breakdown(txt, limit, get_token_fn):
    """ 当无法用标点、空行分割时，我们用最暴力的方法切割
    """
    for i in reversed(range(len(txt))):
        if get_token_fn(txt[:i]) < limit:
            return txt[:i], txt[i:]
    return "Tiktoken未知错误", "Tiktoken未知错误"


def maintain_storage(remain_txt_to_cut, remain_txt_to_cut_storage):
    """ 为了加速计算，我们采样一个特殊的手段。当 remain_txt_to_cut > `_max` 时， 我们把 _max 后的文字转存至 remain_txt_to_cut_storage
    当 remain_txt_to_cut < `_min` 时，我们再把 remain_txt_to_cut_storage 中的部分文字取出
    """
    _min = int(5e4)
    _max = int(1e5)
    # print(len(remain_txt_to_cut), len(remain_txt_to_cut_storage))
    if len(remain_txt_to_cut) < _min and len(remain_txt_to_cut_storage) > 0:
        remain_txt_to_cut = remain_txt_to_cut + remain_txt_to_cut_storage
        remain_txt_to_cut_storage = ""
    if len(remain_txt_to_cut) > _max:
        remain_txt_to_cut_storage = remain_txt_to_cut[_max:] + remain_txt_to_cut_storage
        remain_txt_to_cut = remain_txt_to_cut[:_max]
    return remain_txt_to_cut, remain_txt_to_cut_storage


def cut(limit, get_token_fn, txt_tocut, must_break_at_empty_line, break_anyway=False):
    """ 文本切分
    """
    res = []
    total_len = len(txt_tocut)
    fin_len = 0
    remain_txt_to_cut = txt_tocut
    remain_txt_to_cut_storage = ""
    # 为了加速计算，我们采样一个特殊的手段。当 remain_txt_to_cut > `_max` 时， 我们把 _max 后的文字转存至 remain_txt_to_cut_storage
    remain_txt_to_cut, remain_txt_to_cut_storage = maintain_storage(remain_txt_to_cut, remain_txt_to_cut_storage)

    while True:
        if get_token_fn(remain_txt_to_cut) <= limit:
            # 如果剩余文本的token数小于限制，那么就不用切了
            res.append(remain_txt_to_cut); fin_len+=len(remain_txt_to_cut)
            break
        else:
            # 如果剩余文本的token数大于限制，那么就切
            lines = remain_txt_to_cut.split('\n')

            # 估计一个切分点
            estimated_line_cut = limit / get_token_fn(remain_txt_to_cut) * len(lines)
            estimated_line_cut = int(estimated_line_cut)

            # 开始查找合适切分点的偏移（cnt）
            cnt = 0
            for cnt in reversed(range(estimated_line_cut)):
                if must_break_at_empty_line:
                    # 首先尝试用双空行（\n\n）作为切分点
                    if lines[cnt] != "":
                        continue
                prev = "\n".join(lines[:cnt])
                post = "\n".join(lines[cnt:])
                if get_token_fn(prev) < limit:
                    break

            if cnt == 0:
                # 如果没有找到合适的切分点
                if break_anyway:
                    # 是否允许暴力切分
                    prev, post = force_breakdown(remain_txt_to_cut, limit, get_token_fn)
                else:
                    # 不允许直接报错
                    raise RuntimeError(f"存在一行极长的文本！{remain_txt_to_cut}")

            # 追加列表
            res.append(prev); fin_len+=len(prev)
            # 准备下一次迭代
            remain_txt_to_cut = post
            remain_txt_to_cut, remain_txt_to_cut_storage = maintain_storage(remain_txt_to_cut, remain_txt_to_cut_storage)
            process = fin_len/total_len
            logger.info(f'正在文本切分 {int(process*100)}%')
            if len(remain_txt_to_cut.strip()) == 0:
                break
    return res


def breakdown_text_to_satisfy_token_limit_(txt, limit, llm_model="gpt-3.5-turbo"):
    """ 使用多种方式尝试切分文本，以满足 token 限制
    """
    from request_llms.bridge_all import model_info
    enc = model_info[llm_model]['tokenizer']
    def get_token_fn(txt): return len(enc.encode(txt, disallowed_special=()))
    try:
        # 第1次尝试，将双空行（\n\n）作为切分点
        return cut(limit, get_token_fn, txt, must_break_at_empty_line=True)
    except RuntimeError:
        try:
            # 第2次尝试，将单空行（\n）作为切分点
            return cut(limit, get_token_fn, txt, must_break_at_empty_line=False)
        except RuntimeError:
            try:
                # 第3次尝试，将英文句号（.）作为切分点
                res = cut(limit, get_token_fn, txt.replace('.', '。\n'), must_break_at_empty_line=False) # 这个中文的句号是故意的，作为一个标识而存在
                return [r.replace('。\n', '.') for r in res]
            except RuntimeError as e:
                try:
                    # 第4次尝试，将中文句号（。）作为切分点
                    res = cut(limit, get_token_fn, txt.replace('。', '。。\n'), must_break_at_empty_line=False)
                    return [r.replace('。。\n', '。') for r in res]
                except RuntimeError as e:
                    # 第5次尝试，没办法了，随便切一下吧
                    return cut(limit, get_token_fn, txt, must_break_at_empty_line=False, break_anyway=True)

breakdown_text_to_satisfy_token_limit = run_in_subprocess_with_timeout(breakdown_text_to_satisfy_token_limit_, timeout=60)

if __name__ == '__main__':
    from crazy_functions.crazy_utils import read_and_clean_pdf_text
    file_content, page_one = read_and_clean_pdf_text("build/assets/at.pdf")

    from request_llms.bridge_all import model_info
    for i in range(5):
        file_content += file_content

    logger.info(len(file_content))
    TOKEN_LIMIT_PER_FRAGMENT = 2500
    res = breakdown_text_to_satisfy_token_limit(file_content, TOKEN_LIMIT_PER_FRAGMENT)


from crazy_functions.ipc_fns.mp import run_in_subprocess_with_timeout
from loguru import logger
import time
import re

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

def cut_new(limit, get_token_fn, txt_tocut, must_break_at_empty_line, must_break_at_one_empty_line=False, break_anyway=False):
    """ 文本切分
    """
    res = []
    res_empty_line = []
    total_len = len(txt_tocut)
    fin_len = 0
    remain_txt_to_cut = txt_tocut
    remain_txt_to_cut_storage = ""
    # 为了加速计算，我们采样一个特殊的手段。当 remain_txt_to_cut > `_max` 时， 我们把 _max 后的文字转存至 remain_txt_to_cut_storage
    remain_txt_to_cut, remain_txt_to_cut_storage = maintain_storage(remain_txt_to_cut, remain_txt_to_cut_storage)
    empty=0

    while True:
        if get_token_fn(remain_txt_to_cut) <= limit:
            # 如果剩余文本的token数小于限制，那么就不用切了
            res.append(remain_txt_to_cut); fin_len+=len(remain_txt_to_cut)
            res_empty_line.append(empty)
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
                if must_break_at_empty_line or must_break_at_one_empty_line:
                    empty=1
                prev = "\n".join(lines[:cnt])
                post = "\n".join(lines[cnt:])
                if get_token_fn(prev) < limit :
                    break
                    # empty=0
                if get_token_fn(prev)>limit:
                    if '.' not in prev or '。' not in prev:
                        # empty = 0
                        break

            # if cnt
            if cnt == 0:
                # 如果没有找到合适的切分点
                if break_anyway:
                    # 是否允许暴力切分
                    prev, post = force_breakdown(remain_txt_to_cut, limit, get_token_fn)
                    empty =0
                else:
                    # 不允许直接报错
                    raise RuntimeError(f"存在一行极长的文本！{remain_txt_to_cut}")

            # 追加列表
            res.append(prev); fin_len+=len(prev)
            res_empty_line.append(empty)
            # 准备下一次迭代
            remain_txt_to_cut = post
            remain_txt_to_cut, remain_txt_to_cut_storage = maintain_storage(remain_txt_to_cut, remain_txt_to_cut_storage)
            process = fin_len/total_len
            logger.info(f'正在文本切分 {int(process*100)}%')
            if len(remain_txt_to_cut.strip()) == 0:
                break
    return res,res_empty_line


def breakdown_text_to_satisfy_token_limit_new_(txt, limit, llm_model="gpt-3.5-turbo"):
    """ 使用多种方式尝试切分文本，以满足 token 限制
    """
    from request_llms.bridge_all import model_info
    enc = model_info[llm_model]['tokenizer']
    def get_token_fn(txt): return len(enc.encode(txt, disallowed_special=()))
    try:
        # 第1次尝试，将双空行（\n\n）作为切分点
        res, empty_line =cut_new(limit, get_token_fn, txt, must_break_at_empty_line=True)
        return res,empty_line
    except RuntimeError:
        try:
            # 第2次尝试，将单空行（\n）作为切分点
            res, _ = cut_new(limit, get_token_fn, txt, must_break_at_empty_line=False,must_break_at_one_empty_line=True)
            return res, _
        except RuntimeError:
            try:
                # 第3次尝试，将英文句号（.）作为切分点
                res, _ = cut_new(limit, get_token_fn, txt.replace('.', '。\n'), must_break_at_empty_line=False) # 这个中文的句号是故意的，作为一个标识而存在
                return [r.replace('。\n', '.') for r in res],_

            except RuntimeError as e:
                try:
                    # 第4次尝试，将中文句号（。）作为切分点
                    res,_ = cut_new(limit, get_token_fn, txt.replace('。', '。。\n'), must_break_at_empty_line=False)
                    return [r.replace('。。\n', '。') for r in res], _
                except RuntimeError as e:
                    # 第5次尝试，没办法了，随便切一下吧
                    res, _ = cut_new(limit, get_token_fn, txt, must_break_at_empty_line=False, break_anyway=True)
                    return res,_
breakdown_text_to_satisfy_token_limit_new = run_in_subprocess_with_timeout(breakdown_text_to_satisfy_token_limit_new_, timeout=60)

def cut_from_end_to_satisfy_token_limit_(txt, limit, reserve_token=500, llm_model="gpt-3.5-turbo"):
    """从后往前裁剪文本，以论文为单位进行裁剪

    参数：
        txt: 要处理的文本（格式化后的论文列表字符串）
        limit: token数量上限
        reserve_token: 需要预留的token数量，默认500
        llm_model: 使用的模型名称
    返回：
        裁剪后的文本
    """
    from request_llms.bridge_all import model_info
    enc = model_info[llm_model]['tokenizer']
    def get_token_fn(txt): return len(enc.encode(txt, disallowed_special=()))

    # 计算当前文本的token数
    current_tokens = get_token_fn(txt)
    target_limit = limit - reserve_token

    # 如果当前token数已经在限制范围内，直接返回
    if current_tokens <= target_limit:
        return txt

    # 按论文编号分割文本
    papers = re.split(r'\n(?=\d+\. \*\*)', txt)
    if not papers:
        return txt

    # 从前往后累加论文，直到达到token限制
    result = papers[0]  # 保留第一篇
    current_tokens = get_token_fn(result)

    for paper in papers[1:]:
        paper_tokens = get_token_fn(paper)
        if current_tokens + paper_tokens <= target_limit:
            result += "\n" + paper
            current_tokens += paper_tokens
        else:
            break

    return result

# 添加超时保护
cut_from_end_to_satisfy_token_limit = run_in_subprocess_with_timeout(cut_from_end_to_satisfy_token_limit_, timeout=20)

if __name__ == '__main__':
    from crazy_functions.crazy_utils import read_and_clean_pdf_text
    file_content, page_one = read_and_clean_pdf_text("build/assets/at.pdf")

    from request_llms.bridge_all import model_info
    for i in range(5):
        file_content += file_content

    logger.info(len(file_content))
    TOKEN_LIMIT_PER_FRAGMENT = 2500
    res = breakdown_text_to_satisfy_token_limit(file_content, TOKEN_LIMIT_PER_FRAGMENT)

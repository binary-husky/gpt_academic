import requests
import random
from functools import lru_cache
class GROBID_OFFLINE_EXCEPTION(Exception): pass

def get_avail_grobid_url():
    from toolbox import get_conf
    GROBID_URLS, = get_conf('GROBID_URLS')
    if len(GROBID_URLS) == 0: return None
    try:
        _grobid_url = random.choice(GROBID_URLS) # 随机负载均衡
        if _grobid_url.endswith('/'): _grobid_url = _grobid_url.rstrip('/')
        res = requests.get(_grobid_url+'/api/isalive')
        if res.text=='true': return _grobid_url
        else: return None
    except:
        return None

@lru_cache(maxsize=32)
def parse_pdf(pdf_path, grobid_url):
    import scipdf   # pip install scipdf_parser
    if grobid_url.endswith('/'): grobid_url = grobid_url.rstrip('/')
    article_dict = scipdf.parse_pdf_to_dict(pdf_path, grobid_url=grobid_url)
    return article_dict


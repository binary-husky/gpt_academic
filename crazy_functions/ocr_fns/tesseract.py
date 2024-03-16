import subprocess, os, urllib.request
from toolbox import get_conf

TESSERACT_PATH = get_conf("TESSERACT_PATH")

lang_list = ["afr","amh","ara","asm","aze","aze_cyrl","bel","ben","bod","bos","bre","bul","cat","ceb","ces","chi_sim","chi_sim_vert","chi_tra","chi_tra_vert","chr","cos","cym","dan",
             "deu","div","dzo","ell","eng","enm","epo","equ","est","eus","fao","fas","fil","fin","fra","frk","frm","fry","gla","gle","glg","grc","guj","hat","heb","hin","hrv","hun",
             "hye","iku","ind","isl","ita","ita_old","jav","jpn","jpn_vert","kan","kat","kat_old","kaz","khm","kir","kmr","kor","kor_vert","lao","lat","lav","lit","ltz","mal","mar",
             "mkd","mlt","mon","mri","msa","mya","nep","nld","nor","oci","ori","pan","pol","por","pus","que","ron","rus","san","sin","slk","slv","snd","spa","spa_old","sqi","srp",
             "srp_latn","sun","swa","swe","syr","tam","tat","tel","tgk","tha","tir","ton","tur","uig","ukr","urd","uzb","uzb_cyrl","vie","yid","yor"]
             
def download_lang(lang):
    #从码云的某个仓库下载，github太慢。要是哪天链接挂了就换一个
    url = f"https://gitee.com/dalaomai/tessdata_fast/raw/main/{lang}.traineddata"
    
    path = os.path.dirname(TESSERACT_PATH)
    path = os.path.join(path, "tessdata")
    path = os.path.join(path, f"{lang}.traineddata")
    
    response = urllib.request.urlopen(url)
    if response.status == 200:
        with open(path, 'wb') as file:
            file.write(response.read())
            print(f'已将{lang}语言包下载至{path}')
    else:
        print('未能成功从{url}下载语言包')
             
def lang_exists(lang):
    path = os.path.dirname(TESSERACT_PATH)
    path = os.path.join(path, "tessdata")
    path = os.path.join(path, f"{lang}.traineddata")
    return os.path.isfile(path)
    
def normalize_lang(text):
    langs = []
    for l in lang_list:
        if l in text:
            langs.append(l)
    if langs.__len__() == 0:
        langs = ["chi_sim", "eng"]
    
    invalid_langs = []
    for lang in langs:
        if lang_exists(lang):
            ...
        else:
            try:
                download_lang(lang)
            except Exception as e:
                print(f"下载语言包失败: {e}")
                invalid_langs.append(lang)
    for lang in invalid_langs:
        langs.remove(lang)
        
    if langs.__len__() == 0:
        langs = ["osd"]
        
    return "+".join(langs)
    
def tesseract_ocr(img_path, output_path, lang):
    subprocess.run(f"\"{TESSERACT_PATH}\" \"{img_path}\" \"{output_path}\" -l {lang}")
    if os.path.isfile(output_path):
        os.remove(output_path)
    os.rename(output_path+".txt", output_path)
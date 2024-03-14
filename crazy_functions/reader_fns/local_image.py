# encoding: utf-8
# @Time   : 2023/7/3
# @Author : Spike
# @Descr   :
import time
import os.path
import requests
import concurrent.futures
from common import db_handler
from common.path_handler import init_path


# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`


class ImgHandler:
    def __init__(self, img_path, output_dir=None, trust_value=0.9):
        self.font_path = os.path.join(init_path.base_path, 'docs/OCR/fonts/simfang.ttf')
        self.trust_value = trust_value
        if output_dir:
            self.output_dir = os.path.join(output_dir, 'img_vision')
            os.makedirs(self.output_dir, exist_ok=True)
        self.img_path = img_path
        if self.img_path.startswith('http'):
            response = requests.get(url=self.img_path, verify=False)
            file_name = self.img_path.split('/')[-1]
            self.img_path = os.path.join(self.output_dir, f'download_{file_name}.jpeg')
            with open(self.img_path, mode='wb') as f:
                f.write(response.content)

    def _content_draw_result(self, result):
        # 显示结果
        from PIL import Image
        from paddleocr import draw_ocr
        boxes = [line[0] for line in result if line[1][1] > self.trust_value]
        txts = [line[1][0] for line in result]
        txts_select = [line[1][0] for line in result if line[1][1] > self.trust_value]
        scores = [line[1][1] for line in result]
        draw_error = False
        try:
            image = Image.open(self.img_path).convert('RGB')
            im_show = draw_ocr(image, boxes, txts, scores, font_path=self.font_path)
            im_show = Image.fromarray(im_show)
            save_file = f'draw-{os.path.basename(self.img_path)}'
            im_show.save(os.path.join(self.output_dir, save_file))
        except Exception:
            print('绘制选择文字出错')
            save_file = self.img_path
            draw_error = '右侧无文案说明仅代表绘制选择文字, 不影响实际OCR成果'
        return txts_select, save_file, draw_error

    def get_paddle_ocr(self, show_result: bool = True):
        from paddleocr import PaddleOCR
        model_dir = os.path.join(init_path.base_path, 'docs', 'OCR', 'ch_PP-OCRv3_rec_infer')
        det_dir = os.path.join(init_path.base_path, 'docs', 'OCR', 'ch_PP-OCRv3_det_infer')
        cls_dir = os.path.join(init_path.base_path, 'docs', 'OCR', 'ch_ppocr_mobile_v2.0_cls_infer')
        ocr = PaddleOCR(use_angle_cls=True, cls_model_dir=cls_dir,
                        rec_model_dir=model_dir, det_model_dir=det_dir)
        result = ocr.ocr(self.img_path, cls=True)
        result = result[0]
        if show_result:
            txt_select, self.img_path, draw_error = self._content_draw_result(result)
        else:
            draw_error = ''
            txt_select = result
        return '\n'.join(txt_select), self.img_path, draw_error

    def get_llm_vision(self, llm_kwargs):
        from request_llms.bridge_all import predict_no_ui_long_connection
        from common import func_box
        sql_handler = db_handler.PromptDb('图片理解_sys')
        prompt = sql_handler.find_prompt_result('llm-vision')
        input_ = func_box.replace_expected_text(prompt, content=func_box.html_local_img(self.img_path),
                                                expect='{{{v}}}')
        watchdog = ["", time.time(), ""]
        vision_result = predict_no_ui_long_connection(input_, llm_kwargs, [],
                                                      '', observe_window=watchdog)
        return vision_result, self.img_path, watchdog[2]

    def identify_cache(self, cache_tag, cor_switch, kwargs):
        cache_sql = db_handler.OcrCacheDb()
        if isinstance(kwargs, bool):
            ocr_func = self.get_paddle_ocr
        else:
            ocr_func = self.get_llm_vision
        if cor_switch:
            cache_cont = cache_sql.get_cashed(tag=cache_tag)
            if cache_cont:
                content = cache_cont
                file_path = cache_tag
                status = '本次识别结果读取数据库缓存'
            else:
                return self.identify_cache(cache_tag, False, kwargs)
        else:
            content, file_path, status = ocr_func(kwargs)
            if not status and content:  # 没有错误才落库
                cache_sql.update_cashed(cache_tag, content)
        return content, file_path, status


def submit_threads_img_handle(ocr_mapping, output_dir, cor_cache: bool = False, model_kwargs=True, max_threads=10):
    threads = {}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
    # 提交任务，并将线程对象作为键，字典的键作为值存储
    for key in ocr_mapping:
        obj = ImgHandler(img_path=key, output_dir=output_dir).identify_cache
        threads[key] = executor.submit(obj, key, cor_cache, model_kwargs)
    # 返回线程字典
    return threads


if __name__ == '__main__':
    sql_handler = db_handler.PromptDb('图片理解_sys')
    prompt = sql_handler.find_prompt_result('llm-vision')
    print(prompt)

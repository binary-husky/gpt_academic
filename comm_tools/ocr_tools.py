#! .\venv\
# encoding: utf-8
# @Time   : 2023/7/3
# @Author : Spike
# @Descr   :
import os.path
import requests
from comm_tools import func_box
from paddleocr import PaddleOCR, draw_ocr, PPStructure, save_structure_res
from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx

# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`


class Paddle_ocr_select():

    def __init__(self, ipaddr='', trust_value=0.9):
        self.font_path = os.path.join(func_box.base_path, 'docs/fonts/simfang.ttf')
        self.ipaddr = ipaddr
        self.trust_value = trust_value

    def img_def_content(self, img_path, show_result: bool=True):
        ocr = PaddleOCR(use_angle_cls=True)  # need to run only once to download and load model into memory
        result = ocr.ocr(img_path, cls=True)
        save_path = os.path.join(func_box.users_path, self.ipaddr, 'ocr_temp')
        save_file = os.path.join(save_path, f'{func_box.created_at()}.jpeg')
        os.makedirs(save_path, exist_ok=True)
        if show_result:
            # 显示结果
            from PIL import Image
            result = result[0]
            if img_path.startswith('http'):
                response = requests.get(img_path)
                with open(save_file, 'wb') as f:
                    f.write(response.content)
                image = Image.open(save_file).convert('RGB')
            else:
                image = Image.open(img_path).convert('RGB')
            boxes = [line[0] for line in result if line[1][1] > self.trust_value]
            txts = [line[1][0] for line in result]
            txts_select = [line[1][0] for line in result if line[1][1] > self.trust_value]
            scores = [line[1][1] for line in result]
            im_show = draw_ocr(image, boxes, txts, scores, font_path=self.font_path)
            im_show = Image.fromarray(im_show)
            im_show.save(save_file)
        else:
            save_file=''
            txts_select = []
        return '\n'.join(txts_select), save_file

    def img_tabs_content(self):
        import os
        import cv2
        from paddleocr import PPStructure, draw_structure_result, save_structure_res
        table_engine = PPStructure(show_log=True, image_orientation=True)
        save_folder = './private_upload'
        img_path = './gpt_log/img.png'
        img = cv2.imread(img_path)
        result = table_engine(img)
        save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])
        for line in result:
            line.pop('img')
            print(line)
        from PIL import Image # PaddleOCR下提供字体包
        image = Image.open(img_path).convert('RGB')
        im_show = draw_structure_result(image, result, font_path=self.font_path)
        im_show = Image.fromarray(im_show)
        im_show.save('result.jpg')


if __name__ == '__main__':
    file = '../gpt_log/img.png'
    Paddle_ocr_select().img_tabs_content()
# encoding: utf-8
# @Time   : 2024/3/3
# @Author : Spike
# @Descr   :
import os
import fitz


class PDFHandler:
    def __init__(self, pdf_path, output_dir=None):
        """
        Args:
            pdf_path: 读取文件路径
            output_dir: 保存路径，如果没有另存为操作，可以为空
        """
        self.output_dir = None
        if output_dir:
            self.output_dir = os.path.join(output_dir, '.pdf')
            os.makedirs(self.output_dir, exist_ok=True)
        self.markdown_content = ''
        self.pdf_path = pdf_path
        self.file_name = os.path.basename(pdf_path).split('.')[0]

    def __get_markdown_heading_level(self, para_size):
        """根据字体大小确定Markdown标题的级别"""
        para_size = int(para_size)
        heading_level = 0
        if para_size > 40:
            heading_level = 1
        elif para_size > 20:
            heading_level = 2
        elif para_size > 10:
            heading_level = 3
        heading_level = '#' * heading_level + ' ' if heading_level > 0 else ""
        return heading_level

    def __extract_images(self, block):
        """提取PDF中的图片"""
        if block['width'] < 200 or block['height'] < 200 or block['size'] < 10*1024:
            return ""
        bbox_tag = "-".join([str(int(i)) for i in block["bbox"]])
        if not self.output_dir:
            self.output_dir = os.path.join(os.path.dirname(self.pdf_path), self.file_name)
            os.makedirs(self.output_dir, exist_ok=True)
        save_file_name = os.path.join(self.output_dir, f'{block["number"]}-{block["size"]}_{bbox_tag}.{block["ext"]}')
        open(save_file_name, 'wb').write(block['image'])
        return f"![{self.file_name}]({save_file_name})\n"

    def __extract_text(self, block):
        """提取PDF文本"""
        md_text = ""
        lines = block['lines']
        for i in lines:
            meta_text = ""
            per_fix = ""
            for span in i['spans']:
                per_fix = self.__get_markdown_heading_level(span['size'])
                # 定义结束符号集合
                end_symbols = ['。', ';', '；', '.', ')', '!', '！']
                # 检测 meta_text 是否以指定的结束符号之一结尾
                if span['text'][-1] in end_symbols:
                    # 如果是，执行换行操作（这里以添加换行符为例）
                    span['text'] += '\n'
                meta_text += span['text']
            md_text += per_fix + meta_text
            if per_fix: md_text += '\n'

        return md_text + '\n'

    def get_markdown(self):
        text = ''
        with fitz.open(self.pdf_path) as doc:
            for index, page in enumerate(doc):
                block_areas = page.get_text("dict")['blocks']
                for block in block_areas:
                    if 'image' in block:
                        text += self.__extract_images(block)
                    else:
                        text += self.__extract_text(block)
        return text


if __name__ == '__main__':
    PDFHandler('/Documents/PDFbatch/罗宾斯第13版重点.pdf', '').get_markdown()

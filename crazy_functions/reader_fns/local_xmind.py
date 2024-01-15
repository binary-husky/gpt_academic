# encoding: utf-8
# @Time   : 2024/1/15
# @Author : Spike
# @Descr   : Word 文件处理工具
import os
import xmindparser
from os import PathLike
from typing import Dict
import typing as typing
import xmind
import openpyxl


class XmindHandle:

    def __init__(self, xmind_path, output_dir):
        self.output_dir = os.path.join(output_dir, 'xmind')
        os.makedirs(self.output_dir, exist_ok=True)
        self.xmind_path = xmind_path
        try:  # xmindparser
            self.dictSheet = xmindparser.xmind_to_dict(xmind_path)
        except Exception as e:  # 读取失败换 xmind
            workbook = xmind.load(xmind_path)
            sheet = workbook.getPrimarySheet()
            self.dictSheet = [sheet.getData()]
        self.excel_result = {}
        self.markdown_result = {}

    def _WalkTopic(self, dictXmind: Dict, resultDict: Dict):
        strTitle: typing.AnyStr = dictXmind['title']
        if 'topics' in dictXmind:
            pass
            # print(dictXmind['topics'])
            listTopics: typing.List = dictXmind['topics']

            if (listTopics.__len__() > 0):
                resultDict[strTitle] = {}
                for topic in listTopics:
                    self._WalkTopic(topic, resultDict[strTitle])
        else:
            resultDict[strTitle] = strTitle

    def _WalkTopicForList(self, dictOri: typing.Dict) -> typing.AnyStr:
        levelOri = 0
        listStr = []

        def Print2MDListInternal(dictContent: typing.Dict, level):
            if type(dictContent).__name__ != 'dict':
                return
            level = level + 1
            for topic, topicDict in dictContent.items():
                listStr.append('  ' * (level - 1))
                listStr.append('- ')
                listStr.append(topic)
                listStr.append('\n')
                Print2MDListInternal(topicDict, level)

        Print2MDListInternal(dictOri, levelOri)
        return ''.join(listStr)

    def _WalkTopicForExcel(self, dictXmind, row=[], depth=0, result_list=[]):
        title = dictXmind['title']
        if depth >= len(row):
            row.append(title)  # Add new title at the current depth
        else:
            row[depth] = title  # Replace title at current depth
            row = row[:depth + 1]  # Truncate row to current depth + 1

        if 'topics' in dictXmind:
            for topic in dictXmind['topics']:
                self._WalkTopicForExcel(topic, list(row), depth + 1, result_list)
        else:
            result_list.append(list(row))  # Append a copy of the current row

    def get_excel(self):
        for canvas in self.dictSheet:
            result_list = []
            self._WalkTopicForExcel(canvas['topic'], result_list=result_list)
            # Determine the maximum length of rows for consistent column size
            max_length = max(len(row) for row in result_list)
            for row in result_list:
                row.extend([''] * (max_length - len(row)))  # Fill shorter rows with empty strings

            self.excel_result[canvas['title']] = result_list
        return self.excel_result

    def get_markdown(self) -> Dict:
        for canvas in self.dictSheet:
            dict_results: Dict = {}
            self._WalkTopic(canvas['topic'], dict_results)
            strResult = self._WalkTopicForList(dict_results)
            self.markdown_result[canvas['title']] = strResult
        return self.markdown_result

    def save_excel(self) -> str:
        workbook = openpyxl.Workbook()
        first_sheet = True
        if not self.excel_result:
            self.excel_result = self.get_excel()
        for topic in self.excel_result:
            # Create a new sheet for each canvas
            if first_sheet:
                sheet = workbook.active
                sheet.title = topic
                first_sheet = False
            else:
                sheet = workbook.create_sheet(title=topic)
            # Write the data to the Excel sheet
            for row in self.excel_result[topic]:
                sheet.append(row)
        # Save the workbook
        file_name = os.path.splitext(os.path.basename(self.xmind_path))[0]
        excel_path = os.path.join(self.output_dir, f'{os.path.basename(file_name)}.xlsx')
        workbook.save(filename=excel_path)
        return excel_path

    def save_markdown(self) -> list[str]:
        if not self.markdown_result:
            self.markdown_result = self.get_markdown()
        md_path = []
        for topic in self.markdown_result:
            file_name = os.path.splitext(os.path.basename(self.xmind_path))[0]
            path_output = os.path.join(self.output_dir, f'{file_name}_{topic}.md')
            with open(path_output, 'w', encoding='utf-8') as f:
                f.write(self.markdown_result[topic])
                md_path.append(path_output)
        return md_path


if __name__ == '__main__':
    XmindHandle('/Users/kilig/Desktop/整体系统.xmind', './test').get_markdown()

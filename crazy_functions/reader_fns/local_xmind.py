# encoding: utf-8
# @Time   : 2024/1/15
# @Author : Spike
# @Descr   : Word 文件处理工具
import os
import xmindparser
from typing import Dict
import typing as typing
import xmind


class XmindHandle:

    def __int__(self, xmind_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        try:  # xmindparser
            self.dictSheet = xmindparser.xmind_to_dict(xmind_path)
        except Exception as e:  # 读取失败换 xmind
            workbook = xmind.load(xmind_path)
            sheet = workbook.getPrimarySheet()
            self.dictSheet = [sheet.getData()]

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

    def _Print2MDList(self, dictOri: typing.Dict) -> typing.AnyStr:
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

    def xmind_2_md(self, pathSource):
        dictResult: Dict = {}
        xm_content = ''
        md_path = []
        for canvas in self.dictSheet:
            self._WalkTopic(canvas['topic'], dictResult)
            strResult = self._Print2MDList(dictResult)
            xm_content += strResult
            temp_path = os.path.join(os.path.dirname(os.path.dirname(pathSource)), 'markdown')
            os.makedirs(temp_path, exist_ok=True)
            pathOutput = os.path.join(temp_path, f'{os.path.basename(pathSource)}_{canvas["title"]}.md')
            with open(pathOutput, 'w', encoding='utf-8') as f:
                f.write(strResult)
                md_path.append(pathOutput)
        return xm_content, md_path

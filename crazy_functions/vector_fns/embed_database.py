#! .\venv\
# encoding: utf-8
# @Time   : 2023/12/29
# @Author : Spike
# @Descr   :


import os
from embedchain import Pipeline

from embedchain.vectordb.zilliz import ZillizVectorDB

app = Pipeline(db=ZillizVectorDB())

app.add("https://www.youtube.com/watch?v=ZnEgvGPMRXA")

elon_bot = Pipeline()

elon_bot.from_config()
# elon_bot.add()

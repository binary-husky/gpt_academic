# encoding: utf-8
# @Time   : 2024/3/24
# @Author : Spike
# @Descr   :
import os
import shutil
import time
import uuid
import gradio as gr
import pandas as pd
import copy
import json
import yaml
import random
from typing import List
from yarl import URL
from common.toolbox import get_conf, ChatBotWithCookies
from common.func_box import (user_client_mark, spike_toast, get_files_list, prompt_personal_tag, html_view_blank,
                             to_markdown_tabs, num_tokens_from_string, html_tag_color, check_json_format,
                             pattern_html, check_list_format, match_chat_information, link_mtime_to_md, html_local_file,
                             get_avatar_img, replace_special_chars, favicon_ascii)
from common.knowledge_base.kb_service import base
from common.knowledge_base import kb_doc_api, kb_api, utils
from common.configs import kb_config
from common.path_handler import init_path
from crazy_functions.reader_fns.crazy_box import detach_cloud_links
from common.logger_handler import logger
from common.db_handler import UserDb, PromptDb
from common.history_handler import HistoryJsonHandle, thread_write_chat_json


def get_database_cls(t):
    return "_".join(str(t).split('_')[0:-1])

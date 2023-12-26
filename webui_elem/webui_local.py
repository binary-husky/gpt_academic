#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/15
# @Author : Spike
# @Descr   :

import os
import locale
import logging
import commentjson as json
from comm_tools.path_handle import init_path


class I18nAuto:
    def __init__(self):
        language = os.environ.get("LANGUAGE", 'auto')
        language = language.replace("-", "_")
        if language == "auto":
            language = locale.getdefaultlocale()[0] # get the language code of the system (ex. zh_CN)
        self.language_map = {}
        self.language_file = os.path.join(init_path.base_path, 'docs', 'locale')
        self.file_is_exists = f"{self.language_file}/{language}.json"
        if os.path.isfile(self.file_is_exists):
            with open(self.file_is_exists, "r", encoding="utf-8") as f:
                self.language_map.update(json.load(f))
        else:
            logging.warning(f"Language file for {language} does not exist. Using English instead.")
            logging.warning(f"Available languages: {', '.join([x[:-5] for x in os.listdir('.docs/locale')])}")
            with open(f"{self.language_file}/en_US.json", "r", encoding="utf-8") as f:
                self.language_map.update(json.load(f))

    def __call__(self, key):
        if self.file_is_exists and key in self.language_map:
            return self.language_map[key]
        else:
            self.language_map.update({key: key})
            with open(self.file_is_exists, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.language_map,  indent=4, ensure_ascii=False))
            return key

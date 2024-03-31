# encoding: utf-8
# @Time   : 2024/3/25
# @Author : Spike
# @Descr   :
from request_llms.bridge_all import predict_no_ui_long_connection as no_ui_long_connection, model_info


class SummaryMetadata:

    def __init__(self, llm_kwargs: dict, max_token: int = None):
        self.bridge_chain = no_ui_long_connection



if __name__ == '__main__':
    print(model_info['claude-3-haiku-20240307'])
# """
# 对各个llm模型进行单元测试
# """
def validate_path():
    import os, sys
    dir_name = os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) +  '/..')
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)
    
validate_path() # validate path so you can run from base directory
if __name__ == "__main__":
    # from request_llms.bridge_newbingfree import predict_no_ui_long_connection
    # from request_llms.bridge_moss import predict_no_ui_long_connection
    # from request_llms.bridge_jittorllms_pangualpha import predict_no_ui_long_connection
    # from request_llms.bridge_jittorllms_llama import predict_no_ui_long_connection
    # from request_llms.bridge_claude import predict_no_ui_long_connection
    # from request_llms.bridge_internlm import predict_no_ui_long_connection
    # from request_llms.bridge_qwen import predict_no_ui_long_connection
    # from request_llms.bridge_spark import predict_no_ui_long_connection
    from request_llms.bridge_zhipu import predict_no_ui_long_connection

    llm_kwargs = {
        'max_length': 4096,
        'top_p': 1,
        'temperature': 1,
    }

    result = predict_no_ui_long_connection( inputs="请问什么是质子？", 
                                            llm_kwargs=llm_kwargs,
                                            history=["你好", "我好！"],
                                            sys_prompt="")
    print('final result:', result)

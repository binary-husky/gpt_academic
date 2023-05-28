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
    from request_llm.bridge_newbingfree import predict_no_ui_long_connection
    # from request_llm.bridge_moss import predict_no_ui_long_connection
    # from request_llm.bridge_jittorllms_pangualpha import predict_no_ui_long_connection
    # from request_llm.bridge_jittorllms_llama import predict_no_ui_long_connection

    llm_kwargs = {
        'max_length': 512,
        'top_p': 1,
        'temperature': 1,
    }

    result = predict_no_ui_long_connection(inputs="你好", 
                                        llm_kwargs=llm_kwargs,
                                        history=[],
                                        sys_prompt="")
    print('final result:', result)


    result = predict_no_ui_long_connection(inputs="what is a hero?", 
                                        llm_kwargs=llm_kwargs,
                                        history=["hello world"],
                                        sys_prompt="")
    print('final result:', result)

    result = predict_no_ui_long_connection(inputs="如何理解传奇?", 
                                        llm_kwargs=llm_kwargs,
                                        history=[],
                                        sys_prompt="")
    print('final result:', result)

    # # print(result)
    # from multiprocessing import Process, Pipe
    # class GetGLMHandle(Process):
    #     def __init__(self):
    #         super().__init__(daemon=True)
    #         pass
    #     def run(self):
    #         # 子进程执行
    #         # 第一次运行，加载参数
    #         def validate_path():
    #             import os, sys
    #             dir_name = os.path.dirname(__file__)
    #             root_dir_assume = os.path.abspath(os.path.dirname(__file__) +  '/..')
    #             os.chdir(root_dir_assume + '/request_llm/jittorllms')
    #             sys.path.append(root_dir_assume + '/request_llm/jittorllms')
    #         validate_path() # validate path so you can run from base directory

    #         jittorllms_model = None
    #         import types
    #         try:
    #             if jittorllms_model is None:
    #                 from models import get_model
    #                 # availabel_models = ["chatglm", "pangualpha", "llama", "chatrwkv"]
    #                 args_dict = {'model': 'chatrwkv'}
    #                 print('self.jittorllms_model = get_model(types.SimpleNamespace(**args_dict))')
    #                 jittorllms_model = get_model(types.SimpleNamespace(**args_dict))
    #                 print('done get model')
    #         except:
    #             # self.child.send('[Local Message] Call jittorllms fail 不能正常加载jittorllms的参数。')
    #             raise RuntimeError("不能正常加载jittorllms的参数！")
            
    # x = GetGLMHandle()
    # x.start()


    # input()
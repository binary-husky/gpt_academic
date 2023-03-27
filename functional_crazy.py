
def get_crazy_functionals():
    from crazy_functions.读文章写摘要 import 读文章写摘要
    from crazy_functions.生成函数注释 import 批量生成函数注释
    from crazy_functions.解析项目源代码 import 解析项目本身
    from crazy_functions.解析项目源代码 import 解析一个Python项目
    from crazy_functions.解析项目源代码 import 解析一个C项目的头文件
    from crazy_functions.解析项目源代码 import 解析一个C项目
    from crazy_functions.高级功能函数模板 import 高阶功能模板函数

    return {
        "[实验] 请解析并解构此项目本身": {
            "Function": 解析项目本身
        },
        "[实验] 解析整个py项目（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个Python项目
        },
        "[实验] 解析整个C++项目头文件（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个C项目的头文件
        },
        "[实验] 解析整个C++项目（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 解析一个C项目
        },
        "[实验] 读tex论文写摘要（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 读文章写摘要
        },
        "[实验] 批量生成函数注释（配合input输入框）": {
            "Color": "stop",    # 按钮颜色
            "Function": 批量生成函数注释
        },
        "[实验] 实验功能函数模板": {
            "Color": "stop",    # 按钮颜色
            "Function": 高阶功能模板函数
        },
    }

def on_file_uploaded(files, chatbot, txt):
    if len(files) == 0: return chatbot, txt
    import shutil, os, time, glob
    from toolbox import extract_archive
    try: shutil.rmtree('./private_upload/')
    except: pass
    time_tag = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    os.makedirs(f'private_upload/{time_tag}', exist_ok=True)
    for file in files:
        file_origin_name = os.path.basename(file.orig_name)
        shutil.copy(file.name, f'private_upload/{time_tag}/{file_origin_name}')
        extract_archive(f'private_upload/{time_tag}/{file_origin_name}', 
                        dest_dir=f'private_upload/{time_tag}/{file_origin_name}.extract')
    moved_files = [fp for fp in glob.glob('private_upload/**/*', recursive=True)]
    txt = f'private_upload/{time_tag}'
    moved_files_str = '\t\n\n'.join(moved_files)
    chatbot.append(['我上传了文件，请查收', 
                    f'[Local Message] 收到以下文件: \n\n{moved_files_str}\n\n调用路径参数已自动修正到: \n\n{txt}\n\n现在您可以直接选择任意实现性功能'])
    return chatbot, txt

def on_report_generated(files, chatbot):
    from toolbox import find_recent_files
    report_files = find_recent_files('gpt_log')
    if len(report_files) == 0: return report_files, chatbot
    # files.extend(report_files)
    chatbot.append(['汇总报告如何远程获取？', '汇总报告已经添加到右侧文件上传区，请查收。'])
    return report_files, chatbot


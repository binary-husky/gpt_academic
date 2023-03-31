import json
import ctypes
import sys
import os
import time
if  not ctypes.windll.shell32.IsUserAnAdmin():
    # 获取管理员权限
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1) 
else:
    #设置配置文件
    # 获取当前Python文件所在的目录
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # 打开JSON文件，使用相对路径
    with open(os.path.join(dir_path, 'cfg.json'),'r') as f:
        config=json.load(f)
    config['key']= input('your api-key:')#输入api-key
    agt=input('代理端口:')  #输入端口号
    config['agent']= { "http": "socks5h://localhost:"+agt, "https": "socks5h://localhost:"+agt}
    print('\n***请仔细检查是否填写正确，有误误可以选择重新运行此脚本再次配置***')
    print('\n***3秒后自动安装依赖***')
    time.sleep(3)#暂停以显示提示
    # 保存修改后的JSON文件
    with open(os.path.join(dir_path, 'cfg.json'), 'w') as f:
        json.dump(config, f)


    # 安装依赖
    # 获取当前脚本所在的目录路径
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # 更改运行路径到脚本所在目录
    os.chdir(script_dir)
    # 使用相对路径安装软件包
    os.system("python -m pip install -r requirements.txt")

    import winshell
    from win32com.client import Dispatch
    
    shell = Dispatch('WScript.Shell')
    #创建GPT快捷方式
    # 获取桌面路径
    desktop_path = winshell.desktop()
    # 要创建快捷方式的文件路径
    target_file_path = os.path.abspath('main.py')
    # 自定义图标路径
    custom_icon_path = os.path.abspath('ico\\favicon256.ico')
    # 自定义图标在图标文件中的位置（从0开始）
    custom_icon_index = '0'
    # 快捷方式文件名
    shortcut_name = 'Hi_GPT.lnk'
    # 创建快捷方式
    shortcut = shell.CreateShortCut(os.path.join(desktop_path, shortcut_name))
    shortcut.Targetpath = target_file_path    
    shortcut.IconLocation = custom_icon_path +','+custom_icon_index
    shortcut.save() 
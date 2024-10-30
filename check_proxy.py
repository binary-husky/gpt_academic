from loguru import logger

def check_proxy(proxies, return_ip=False):
    """
    检查代理配置并返回结果。

    Args:
        proxies (dict): 包含http和https代理配置的字典。
        return_ip (bool, optional): 是否返回代理的IP地址。默认为False。

    Returns:
        str or None: 检查的结果信息或代理的IP地址（如果`return_ip`为True）。
    """
    import requests
    proxies_https = proxies['https'] if proxies is not None else '无'
    ip = None
    try:
        response = requests.get("https://ipapi.co/json/", proxies=proxies, timeout=4)  # ⭐ 执行GET请求以获取代理信息
        data = response.json()
        if 'country_name' in data:
            country = data['country_name']
            result = f"代理配置 {proxies_https}, 代理所在地：{country}"
            if 'ip' in data:
                ip = data['ip']
        elif 'error' in data:
            alternative, ip = _check_with_backup_source(proxies)  # ⭐ 调用备用方法检查代理配置
            if alternative is None:
                result = f"代理配置 {proxies_https}, 代理所在地：未知，IP查询频率受限"
            else:
                result = f"代理配置 {proxies_https}, 代理所在地：{alternative}"
        else:
            result = f"代理配置 {proxies_https}, 代理数据解析失败：{data}"

        if not return_ip:
            logger.warning(result)
            return result
        else:
            return ip
    except:
        result = f"代理配置 {proxies_https}, 代理所在地查询超时，代理可能无效"
        if not return_ip:
            logger.warning(result)
            return result
        else:
            return ip

def _check_with_backup_source(proxies):
    """
    通过备份源检查代理，并获取相应信息。

    Args:
        proxies (dict): 包含代理信息的字典。

    Returns:
        tuple: 代理信息(geo)和IP地址(ip)的元组。
    """
    import random, string, requests
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    try:
        res_json = requests.get(f"http://{random_string}.edns.ip-api.com/json", proxies=proxies, timeout=4).json()  # ⭐ 执行代理检查和备份源请求
        return res_json['dns']['geo'], res_json['dns']['ip']
    except:
        return None, None

def backup_and_download(current_version, remote_version):
    """
    一键更新协议：备份当前版本，下载远程版本并解压缩。

    Args:
        current_version (str): 当前版本号。
        remote_version (str): 远程版本号。

    Returns:
        str: 新版本目录的路径。
    """
    from toolbox import get_conf
    import shutil
    import os
    import requests
    import zipfile
    os.makedirs(f'./history', exist_ok=True)
    backup_dir = f'./history/backup-{current_version}/'
    new_version_dir = f'./history/new-version-{remote_version}/'
    if os.path.exists(new_version_dir):
        return new_version_dir
    os.makedirs(new_version_dir)
    shutil.copytree('./', backup_dir, ignore=lambda x, y: ['history'])
    proxies = get_conf('proxies')
    try:    r = requests.get('https://github.com/binary-husky/chatgpt_academic/archive/refs/heads/master.zip', proxies=proxies, stream=True)
    except: r = requests.get('https://public.agent-matrix.com/publish/master.zip', proxies=proxies, stream=True)
    zip_file_path = backup_dir+'/master.zip'  # ⭐ 保存备份文件的路径
    with open(zip_file_path, 'wb+') as f:
        f.write(r.content)
    dst_path = new_version_dir
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        for zip_info in zip_ref.infolist():
            dst_file_path = os.path.join(dst_path, zip_info.filename)
            if os.path.exists(dst_file_path):
                os.remove(dst_file_path)
            zip_ref.extract(zip_info, dst_path)
    return new_version_dir


def patch_and_restart(path):
    """
    一键更新协议：覆盖和重启

    Args:
        path (str): 新版本代码所在的路径

    注意事项:
        如果您的程序没有使用config_private.py私密配置文件，则会将config.py重命名为config_private.py以避免配置丢失。

    更新流程:
        - 复制最新版本代码到当前目录
        - 更新pip包依赖
        - 如果更新失败，则提示手动安装依赖库并重启
    """
    from distutils import dir_util
    import shutil
    import os
    import sys
    import time
    import glob
    from shared_utils.colorful import log亮黄, log亮绿, log亮红

    if not os.path.exists('config_private.py'):
        log亮黄('由于您没有设置config_private.py私密配置，现将您的现有配置移动至config_private.py以防止配置丢失，',
              '另外您可以随时在history子文件夹下找回旧版的程序。')
        shutil.copyfile('config.py', 'config_private.py')

    path_new_version = glob.glob(path + '/*-master')[0]
    dir_util.copy_tree(path_new_version, './')  # ⭐ 将最新版本代码复制到当前目录

    log亮绿('代码已经更新，即将更新pip包依赖……')
    for i in reversed(range(5)): time.sleep(1); log亮绿(i)

    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    except:
        log亮红('pip包依赖安装出现问题，需要手动安装新增的依赖库 `python -m pip install -r requirements.txt`，然后在用常规的`python main.py`的方式启动。')

    log亮绿('更新完成，您可以随时在history子文件夹下找回旧版的程序，5s之后重启')
    log亮红('假如重启失败，您可能需要手动安装新增的依赖库 `python -m pip install -r requirements.txt`，然后在用常规的`python main.py`的方式启动。')
    log亮绿(' ------------------------------ -----------------------------------')

    for i in reversed(range(8)): time.sleep(1); log亮绿(i)
    os.execl(sys.executable, sys.executable, *sys.argv)  # 重启程序


def get_current_version():
    """
    获取当前的版本号。

    Returns:
        str: 当前的版本号。如果无法获取版本号，则返回空字符串。
    """
    import json
    try:
        with open('./version', 'r', encoding='utf8') as f:
            current_version = json.loads(f.read())['version']  # ⭐ 从读取的json数据中提取版本号
    except:
        current_version = ""
    return current_version


def auto_update(raise_error=False):
    """
    一键更新协议：查询版本和用户意见

    Args:
        raise_error (bool, optional): 是否在出错时抛出错误。默认为 False。

    Returns:
        None
    """
    try:
        from toolbox import get_conf
        import requests
        import json
        proxies = get_conf('proxies')
        try:    response = requests.get("https://raw.githubusercontent.com/binary-husky/chatgpt_academic/master/version", proxies=proxies, timeout=5)
        except: response = requests.get("https://public.agent-matrix.com/publish/version", proxies=proxies, timeout=5)
        remote_json_data = json.loads(response.text)
        remote_version = remote_json_data['version']
        if remote_json_data["show_feature"]:
            new_feature = "新功能：" + remote_json_data["new_feature"]
        else:
            new_feature = ""
        with open('./version', 'r', encoding='utf8') as f:
            current_version = f.read()
            current_version = json.loads(current_version)['version']
        if (remote_version - current_version) >= 0.01-1e-5:
            from shared_utils.colorful import log亮黄
            log亮黄(f'\n新版本可用。新版本:{remote_version}，当前版本:{current_version}。{new_feature}')  # ⭐ 在控制台打印新版本信息
            logger.info('（1）Github更新地址:\nhttps://github.com/binary-husky/chatgpt_academic\n')
            user_instruction = input('（2）是否一键更新代码（Y+回车=确认，输入其他/无输入+回车=不更新）？')
            if user_instruction in ['Y', 'y']:
                path = backup_and_download(current_version, remote_version)  # ⭐ 备份并下载文件
                try:
                    patch_and_restart(path)  # ⭐ 执行覆盖并重启操作
                except:
                    msg = '更新失败。'
                    if raise_error:
                        from toolbox import trimmed_format_exc
                        msg += trimmed_format_exc()
                    logger.warning(msg)
            else:
                logger.info('自动更新程序：已禁用')
                return
        else:
            return
    except:
        msg = '自动更新程序：已禁用。建议排查：代理网络配置。'
        if raise_error:
            from toolbox import trimmed_format_exc
            msg += trimmed_format_exc()
        logger.info(msg)

def warm_up_modules():
    """
    预热模块，加载特定模块并执行预热操作。
    """
    logger.info('正在执行一些模块的预热 ...')
    from toolbox import ProxyNetworkActivate
    from request_llms.bridge_all import model_info
    with ProxyNetworkActivate("Warmup_Modules"):
        enc = model_info["gpt-3.5-turbo"]['tokenizer']
        enc.encode("模块预热", disallowed_special=())
        enc = model_info["gpt-4"]['tokenizer']
        enc.encode("模块预热", disallowed_special=())

def warm_up_vectordb():
    """
    执行一些模块的预热操作。

    本函数主要用于执行一些模块的预热操作，确保在后续的流程中能够顺利运行。

    ⭐ 关键作用：预热模块

    Returns:
        None
    """
    logger.info('正在执行一些模块的预热 ...')
    from toolbox import ProxyNetworkActivate
    with ProxyNetworkActivate("Warmup_Modules"):
        import nltk
        with ProxyNetworkActivate("Warmup_Modules"): nltk.download("punkt")


if __name__ == '__main__':
    import os
    os.environ['no_proxy'] = '*'  # 避免代理网络产生意外污染
    from toolbox import get_conf
    proxies = get_conf('proxies')
    check_proxy(proxies)
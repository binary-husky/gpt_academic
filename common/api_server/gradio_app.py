# encoding: utf-8
# @Time   : 2024/2/17
# @Author : Spike
# @Descr   :
import requests
import os
import httpx
import re
from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from common.path_handler import init_path
from common.toolbox import get_conf, default_user_name

cancel_verification, auth_url, auth_cookie_tag, auth_func_based, routing_address, favicon_path, redirect_address = (
    get_conf('cancel_verification', 'auth_url', 'auth_cookie_tag',
             'auth_func_based', 'routing_address', 'favicon_path', 'redirect_address'))


def check_cookie(cookie):
    header = {
        'Cookie': f"{auth_cookie_tag}={cookie}",
        "Origin": ''
    }
    try:
        resp = requests.get(url=auth_url, headers=header, verify=False).json()
        user = auth_func_based(resp)
    except:
        user = cancel_verification
    if not user:
        return user
    else:
        return user


async def get_favicon():
    return RedirectResponse(url=f'/spike/file={favicon_path}')


async def check_authentication(request: Request, call_next):
    cookie = request.cookies.get(f'{auth_cookie_tag}', '')
    user = check_cookie(cookie)
    if not user:
        new_website_url = redirect_address  # 重定向到鉴权网站
        return RedirectResponse(new_website_url)
    return await call_next(request)


async def homepage(request: Request):
    cookie = request.cookies.get(f'{auth_cookie_tag}', '')
    user = check_cookie(cookie)
    if user:
        return RedirectResponse(url='/spike/')
    else:
        new_website_url = redirect_address  # 新网站的URL
        return RedirectResponse(new_website_url)


async def logout():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie('access-token')
    response.delete_cookie('access-token-unsecure')
    return response


def file_authorize_user(path_or_url, request, gradio_app):
    PATH_PRIVATE_UPLOAD, PATH_LOGGING = get_conf('PATH_PRIVATE_UPLOAD', 'PATH_LOGGING')
    sensitive_path = None
    path_or_url = os.path.relpath(path_or_url)
    if path_or_url.startswith(PATH_LOGGING):
        sensitive_path = os.path.relpath(init_path.logs_path)
    if path_or_url.startswith(PATH_PRIVATE_UPLOAD):
        sensitive_path = os.path.relpath(init_path.users_private_path)
    if sensitive_path:
        token = request.cookies.get("access-token") or request.cookies.get("access-token-unsecure")
        user = gradio_app.tokens.get(token)  # get user
        user_name = user if user else request.client.host
        allowed_users = [user_name, 'autogen', default_user_name]  # three user path that can be accessed
        for user_allowed in allowed_users:
            # exact match
            spilt_path = path_or_url.split(os.sep)
            # 用户标志在第二层
            access_2_path = f"{os.sep}".join(spilt_path[:2])
            user_1_allowed_path = f"{os.sep}".join(spilt_path[:1] + [user_allowed])
            # 用户标志在第三层
            access_3_path = f"{os.sep}".join(spilt_path[:3])
            user_2_allowed_path = f"{os.sep}".join(spilt_path[:2] + [user_allowed])
            if access_2_path == user_1_allowed_path or access_3_path == user_2_allowed_path:
                return True
        return False  # "越权访问!"
    return True

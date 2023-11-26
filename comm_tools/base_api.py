#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :
import json, re
import requests
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from comm_tools import toolbox, func_box

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")
cancel_verification, auth_url, auth_cookie_tag, auth_func_based, routing_address = (
    toolbox.get_conf('cancel_verification', 'auth_url', 'auth_cookie_tag', 'auth_func_based', 'routing_address'))

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


favicon_path = toolbox.get_conf('favicon_path')
@app.get("/favicon.ico")  # 设置icon
async def get_favicon():
   return RedirectResponse(url=f'/gradio/file={favicon_path}')


@app.middleware("https")
async def check_authentication(request: Request, call_next):
    if request.url.path == '/gradio/api/predict' or request.url.path == '/gradio/reset':
        return await call_next(request)
    pattern = re.compile(r".*\/private_upload\/.*")
    if pattern.match(request.url.path):
        if not toolbox.get_conf('AUTHENTICATION'):    # 暂时没办法拿到用户信息
            if request.client.host not in request.url.path:
                return JSONResponse(content={'detail': "You're bad. You can't download other people's files."})
    cookie = request.cookies.get(f'{auth_cookie_tag}', '')
    user = check_cookie(cookie)
    if not user:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)
    return await call_next(request)


@app.get('/')
async def homepage(request: Request):
    cookie = request.cookies.get(f'{auth_cookie_tag}', '')
    user = check_cookie(cookie)
    if user:
        return RedirectResponse(url='/gradio/')
    else:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)


if __name__ == '__main__':
    print(auth_func_based({'data': {'username': '123213'}}))

# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :
import json, re
import requests
import httpx
from pydantic import BaseModel
from fastapi import FastAPI, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from common import toolbox, func_box

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
    return RedirectResponse(url=f'/spike/file={favicon_path}')


@app.middleware("https")
async def check_authentication(request: Request, call_next):
    if request.url.path == '/spike/api/predict' or request.url.path == '/spike/reset':
        return await call_next(request)
    pattern = re.compile(r".*\/private_upload\/.*")
    if pattern.match(request.url.path):
        if toolbox.get_conf('AUTHENTICATION') != 'SQL':  # 暂时没办法拿到用户信息，所以不禁止用户访问
            if request.client.host not in request.url.path:
                return JSONResponse(content={'Error': "You can't download other people's files."})
        else:
            async with httpx.AsyncClient() as client:
                res = await client.get(str(request.base_url)+'spike/user', cookies=request.cookies)
                res_user = res.text[1:-1]
            if res_user not in request.url.path:
                return JSONResponse(content={'Error': "You can't download other people's files."})
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
        return RedirectResponse(url='/spike/')
    else:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)


@app.get("/logout")
async def logout():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie('access-token')
    response.delete_cookie('access-token-unsecure')
    return response


if __name__ == '__main__':
    print(auth_func_based({'data': {'username': '123213'}}))

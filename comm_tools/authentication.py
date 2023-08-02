#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :
import json
import requests

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from comm_tools import func_box

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")


def check_cookie(cookie):
    header = {
        'Cookie': f"ovsmgr_sid={cookie}",
        "Origin": 'https://kso-chatbot-cc.4wps.net/'
    }
    resp = requests.get(url='https://ovsmgr-api.4wps.net/checkv2', headers=header).json()
    try:
        user = resp.get('data').get('account')
    except:
        user = ''
    if not user:
        return user
    else:
        return user


@app.get("/favicon.ico")  # 设置icon
async def get_favicon():
   return {"file": '/docs/wps_logo.png'}


@app.middleware("https")
async def check_authentication(request: Request, call_next):
    if request.url.path == '/gradio/api/predict' or request.url.path == '/gradio/reset':
        return await call_next(request)
    cookie = request.cookies.get('ovsmgr_sid', '')
    user = check_cookie(cookie)
    if not user:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)
    # request.client.host = ''
    return await call_next(request)


@app.get('/')
async def homepage(request: Request):
    cookie = request.cookies.get('ovsmgr_sid', '')
    user = check_cookie(cookie)
    if user:
        return RedirectResponse(url='/gradio')
    else:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)



if __name__ == '__main__':
    pass

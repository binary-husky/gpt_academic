#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :

import requests

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import json

app = FastAPI()

def check_cookie(cookie):
    header = {
        'Cookie': f"ovsmgr_sid={cookie}",
        "Origin": 'https://kso-chatbot-cc.4wps.net/'
    }
    resp = requests.get(url='https://ovsmgr-api.4wps.net/checkv2', headers=header)
    if resp.json().get('code') != 'error':
        return True
    else:
        return False


@app.get('/')
async def homepage(request: Request):
    cookie = request.cookies.get('ovsmgr_sid', '')
    user = check_cookie(cookie)
    if user:
        return RedirectResponse(url='/gradio')
    else:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)


@app.get('/gradio')
async def homepage(request: Request):
    cookie = request.cookies.get('ovsmgr_sid', '')
    user = check_cookie(cookie)
    if user:
        return RedirectResponse(url='/gradio')
    else:
        new_website_url = "https://console.4wps.net/#/login"  # 新网站的URL
        return RedirectResponse(new_website_url)


if __name__ == '__main__':
    check_cookie('')

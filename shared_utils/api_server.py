# encoding: utf-8
# @Time   : 2024/3/3
# @Author : Spike
# @Descr   :
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from typing import List, Literal
from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from toolbox import get_conf
from yarl import URL
import httpx

CUSTOM_PATH, AUTHENTICATION = get_conf('CUSTOM_PATH', 'AUTHENTICATION')


async def homepage(request: Request):
    return RedirectResponse(url=CUSTOM_PATH)


async def logout():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie('access-token')
    response.delete_cookie('access-token-unsecure')
    return response


async def get_favicon():
    favicon_path = './docs/logo.png'
    return RedirectResponse(url=f'{CUSTOM_PATH}file={favicon_path}')


async def authentication(request: Request, call_next):
    """
    https 中间件，用于检查用户登陆状态、文件鉴权等
    """
    if AUTHENTICATION:
        url = URL(request.url.path)
        try:
            index = url.raw_parts.index('private_upload')
        except ValueError:
            index = False
        if isinstance(index, int):
            async with httpx.AsyncClient() as client:
                res = await client.get(str(request.base_url) + f'{CUSTOM_PATH}user',
                                       cookies=request.cookies)
                res_user = res.text[1:-1]
                if url.raw_parts[index + 1] != res_user:
                    return JSONResponse({'Error': "You can't download other people's files."})
    # 这里可以实现单点登陆鉴权
    # login_status = check_cookie(cookie)
    # if not login_status:
    #     new_website_url = ''  # 鉴权网站的URL
    return await call_next(request)


def mount_app_routes(app: FastAPI):
    """
    挂载app的路由
    """
    if CUSTOM_PATH != '/':
        app.get(path='/', tags=['Gradio Mount'], summary='重定向到Gradio二级目录')(homepage)

    app.get(path='/favicon.ico', tags=['Gradio Mount'], summary='获取网站icon')(get_favicon)

    app.get(path='/logout', tags=['Gradio Mount'], summary='退出登陆')(logout)


def create_app():
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="!secret")
    app.middleware('https')(authentication)

    mount_app_routes(app)

    return app

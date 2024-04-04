# encoding: utf-8
# @Time   : 2024/3/3
# @Author : Spike

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from typing import List, Literal
from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from toolbox import get_conf
from yarl import URL

CUSTOM_PATH, AUTHENTICATION, PATH_PRIVATE_UPLOAD = get_conf('CUSTOM_PATH', 'AUTHENTICATION', 'PATH_PRIVATE_UPLOAD')

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

async def get_user(request: Request):
    import httpx
    async with httpx.AsyncClient() as client:
        res = await client.get(
            str(request.base_url) + f'{CUSTOM_PATH}user', cookies=request.cookies
        )
        res_user = res.text[1:-1]
    return res_user

async def authentication(request: Request, call_next):
    """
    https 中间件，用于检查用户登陆状态、文件鉴权等
    """
    if len(AUTHENTICATION) > 0:
        url = URL(request.url.path)
        print("/".join(url.raw_parts))
        if len(url.raw_parts) >=2 and url.raw_parts[1].startswith(f'file={PATH_PRIVATE_UPLOAD}'):
            if len(url.raw_parts) >=3:
                if url.raw_parts[2] != await get_user(request):
                    return JSONResponse({'Error': "You can't download other people's files."})
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
    # app.add_middleware(AuthenticationMiddleware, backend=authentication)
    app.middleware('https')(authentication)
    mount_app_routes(app)
    return app


# 测试：ssl
# 测试：auth
# 测试：ip & port
# 测试：文件上传
# 测试：文件下载
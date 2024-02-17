# encoding: utf-8
# @Time   : 2023/8/2
# @Author : Spike
# @Descr   :
from fastapi import FastAPI
from common.api_server import gradio
from starlette.middleware.sessions import SessionMiddleware


def create_app():
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="!secret")
    app.middleware('https')(gradio.check_authentication)

    mount_app_routes(app)

    return app


def mount_app_routes(app: FastAPI):
    app.get(path='/', summary='')(gradio.homepage)

    app.get(path='/favicon.icon', summary='')(gradio.get_favicon)

    app.get(path='/logout', summary='')(gradio.logout)




if __name__ == '__main__':
    pass

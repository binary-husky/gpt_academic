import os

def _authorize_user(path_or_url, request, gradio_app):
    from toolbox import get_conf, default_user_name
    PATH_PRIVATE_UPLOAD, PATH_LOGGING = get_conf('PATH_PRIVATE_UPLOAD', 'PATH_LOGGING')
    sensitive_path = None
    if path_or_url.startswith(PATH_LOGGING):
        sensitive_path = PATH_LOGGING
    if path_or_url.startswith(PATH_PRIVATE_UPLOAD):
        sensitive_path = PATH_PRIVATE_UPLOAD
    if sensitive_path:
        token = request.cookies.get("access-token") or request.cookies.get("access-token-unsecure")
        user = gradio_app.tokens.get(token) # get user
        allowed_users = [user, 'autogen', default_user_name]  # three user path that can be accessed
        for user_allowed in allowed_users:
            if path_or_url.startswith(os.path.join(sensitive_path, user_allowed)):
                return True
        return False # "越权访问!"
    return True

def start_app(app_block, CONCURRENT_COUNT, AUTHENTICATION, PORT, SSL_KEYFILE, SSL_CERTFILE):
    import uvicorn
    import fastapi
    import gradio as gr
    from fastapi import FastAPI
    from gradio.routes import App
    from toolbox import get_conf
    CUSTOM_PATH = get_conf('CUSTOM_PATH')

    # --- --- configurate gradio app block --- ---
    app_block:gr.Blocks
    app_block.queue(concurrency_count=CONCURRENT_COUNT)
    app_block.ssl_verify = False
    app_block.auth_message = '请登录'
    app_block.favicon_path = os.path.join(os.path.dirname(__file__), "docs/logo.png")
    app_block.auth = AUTHENTICATION if len(AUTHENTICATION) != 0 else None
    app_block.blocked_paths = ["config.py", "config_private.py", "docker-compose.yml", "Dockerfile", "{PATH_LOGGING}/admin"]
    app_block.dev_mode = False
    app_block.config = app_block.get_config_file()
    app_block.validate_queue_settings()
    gradio_app = App.create_app(app_block)

    # --- --- replace gradio endpoint to forbid access to sensitive files --- ---
    if len(AUTHENTICATION) > 0:
        dependencies = []
        endpoint = None
        for route in list(gradio_app.router.routes):
            if route.path == "/file/{path:path}":
                gradio_app.router.routes.remove(route)
            if route.path == "/file={path_or_url:path}":
                dependencies = route.dependencies
                endpoint = route.endpoint
                gradio_app.router.routes.remove(route)
        @gradio_app.get("/file/{path:path}", dependencies=dependencies)
        @gradio_app.head("/file={path_or_url:path}", dependencies=dependencies)
        @gradio_app.get("/file={path_or_url:path}", dependencies=dependencies)
        async def file(path_or_url: str, request: fastapi.Request):
            if len(AUTHENTICATION) > 0:
                if not _authorize_user(path_or_url, request, gradio_app): "越权访问!"
            return await endpoint(path_or_url, request)

    # --- --- app_lifespan --- ---
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def app_lifespan(app):
        async def startup_gradio_app():
            if gradio_app.get_blocks().enable_queue:
                gradio_app.get_blocks().startup_events()
        async def shutdown_gradio_app():
            pass
        await startup_gradio_app() # startup logic here
        yield  # The application will serve requests after this point
        await shutdown_gradio_app() # cleanup/shutdown logic here

    # --- --- FastAPI --- ---
    app = FastAPI(lifespan=app_lifespan)
    app.mount(CUSTOM_PATH, gradio_app)

    # --- --- uvicorn.Config --- ---
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="warning",
        ssl_keyfile=None if SSL_KEYFILE == "" else SSL_KEYFILE,
        ssl_certfile=None if SSL_CERTFILE == "" else SSL_CERTFILE,
    )
    server = uvicorn.Server(config)
    server.run()
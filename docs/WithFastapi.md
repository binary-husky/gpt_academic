# Running with fastapi

We currently support fastapi in order to solve sub-path deploy issue.

1. change CUSTOM_PATH setting in `config.py`

``` sh
nano config.py
```

2. Edit main.py

```diff
    auto_opentab_delay()
    - demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION, favicon_path="docs/logo.png")
    + demo.queue(concurrency_count=CONCURRENT_COUNT)

    - # 如果需要在二级路径下运行
    - # CUSTOM_PATH, = get_conf('CUSTOM_PATH')
    - # if CUSTOM_PATH != "/": 
    - #     from toolbox import run_gradio_in_subpath
    - #     run_gradio_in_subpath(demo, auth=AUTHENTICATION, port=PORT, custom_path=CUSTOM_PATH)
    - # else: 
    - #     demo.launch(server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION, favicon_path="docs/logo.png")

    + 如果需要在二级路径下运行
    + CUSTOM_PATH, = get_conf('CUSTOM_PATH')
    + if CUSTOM_PATH != "/": 
    +     from toolbox import run_gradio_in_subpath
    +     run_gradio_in_subpath(demo, auth=AUTHENTICATION, port=PORT, custom_path=CUSTOM_PATH)
    + else: 
    +     demo.launch(server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION, favicon_path="docs/logo.png")

if __name__ == "__main__":
    main()
```


3. Go!

``` sh
python main.py
```

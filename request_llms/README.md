P.S. 如果您按照以下步骤成功接入了新的大模型，欢迎发Pull Requests（如果您在自己接入新模型的过程中遇到困难，欢迎加README底部QQ群联系群主）


# 如何接入其他本地大语言模型

1. 复制`request_llms/bridge_llama2.py`，重命名为你喜欢的名字

2. 修改`load_model_and_tokenizer`方法，加载你的模型和分词器（去该模型官网找demo，复制粘贴即可）

3. 修改`llm_stream_generator`方法，定义推理模型（去该模型官网找demo，复制粘贴即可）

4. 命令行测试
    - 修改`tests/test_llms.py`（聪慧如您，只需要看一眼该文件就明白怎么修改了）
    - 运行`python tests/test_llms.py`

5. 测试通过后，在`request_llms/bridge_all.py`中做最后的修改，把你的模型完全接入到框架中（聪慧如您，只需要看一眼该文件就明白怎么修改了）

6. 修改`LLM_MODEL`配置，然后运行`python main.py`，测试最后的效果


# 如何接入其他在线大语言模型

1. 复制`request_llms/bridge_zhipu.py`，重命名为你喜欢的名字

2. 修改`predict_no_ui_long_connection`

3. 修改`predict`

4. 命令行测试
    - 修改`tests/test_llms.py`（聪慧如您，只需要看一眼该文件就明白怎么修改了）
    - 运行`python tests/test_llms.py`

5. 测试通过后，在`request_llms/bridge_all.py`中做最后的修改，把你的模型完全接入到框架中（聪慧如您，只需要看一眼该文件就明白怎么修改了）

6. 修改`LLM_MODEL`配置，然后运行`python main.py`，测试最后的效果

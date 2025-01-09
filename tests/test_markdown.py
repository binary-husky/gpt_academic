md = """
You can use the following Python script to rename files matching the pattern '* - 副本.tex' to '* - wushiguang.tex' in a directory:

```python
import os

# Directory containing the files
directory = 'Tex/'

for filename in os.listdir(directory):
    if filename.endswith(' - 副本.tex'):
        new_filename = filename.replace(' - 副本.tex', ' - wushiguang.tex')
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
```

Replace 'Tex/' with the actual directory path where your files are located before running the script.
"""


md = """
Following code including wrapper

```python:wrapper.py
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{decide}
    C --> D[Keep]
    C --> E[Edit Definition]
    E --> B
    D --> F[Save Image and Code]
    F --> B



```

<details>
<summary><b>My section header in bold</b></summary>

Any folded content here. It requires an empty line just above it.

</details>

"""

md ="""

在这种场景中，您希望机器 B 能够通过轮询机制来间接地“请求”机器 A，而实际上机器 A 只能主动向机器 B 发出请求。这是一种典型的客户端-服务器轮询模式。下面是如何实现这种机制的详细步骤：

### 机器 B 的实现

1. **安装 FastAPI 和必要的依赖库**：
   ```bash
   pip install fastapi uvicorn
   ```

2. **创建 FastAPI 服务**：
   ```python
   from fastapi import FastAPI
   from fastapi.responses import JSONResponse
   from uuid import uuid4
   from threading import Lock
   import time

   app = FastAPI()

   # 字典用于存储请求和状态
   requests = {}
   process_lock = Lock()

"""
def validate_path():
    import os, sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory
from toolbox import markdown_convertion
# from shared_utils.advanced_markdown_format import markdown_convertion_for_file
from shared_utils.advanced_markdown_format import close_up_code_segment_during_stream
# with open("gpt_log/default_user/shared/2024-04-22-01-27-43.zip.extract/translated_markdown.md", "r", encoding="utf-8") as f:
    # md = f.read()
md = close_up_code_segment_during_stream(md)
html = markdown_convertion(md)
# print(html)
with open("test.html", "w", encoding="utf-8") as f:
    f.write(html)


# TODO: 列出10个经典名著
md = """
作为您的写作和编程助手，我可以为您提供以下服务：

1. 写作：
    - 帮助您撰写文章、报告、散文、故事等。
    - 提供写作建议和技巧。
    - 协助您进行文案策划和内容创作。

2. 编程：
    - 帮助您解决编程问题，提供编程思路和建议。
    - 协助您编写代码，包括但不限于 Python、Java、C++ 等。
    - 为您解释复杂的技术概念，让您更容易理解。

3. 项目支持：
    - 协助您规划项目进度和任务分配。
    - 提供项目管理和协作建议。
    - 在项目实施过程中提供支持，确保项目顺利进行。

4. 学习辅导：
    - 帮助您巩固编程基础，提高编程能力。
    - 提供计算机科学、数据科学、人工智能等相关领域的学习资源和建议。
    - 解答您在学习过程中遇到的问题，让您更好地掌握知识。

5. 行业动态和趋势分析：
    - 为您提供业界最新的新闻和技术趋势。
    - 分析行业动态，帮助您了解市场发展和竞争态势。
    - 为您制定技术战略提供参考和建议。

请随时告诉我您的需求，我会尽力提供帮助。如果您有任何问题或需要解答的议题，请随时提问。
"""

def validate_path():
    import os, sys
    dir_name = os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) +  '/..')
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)
validate_path() # validate path so you can run from base directory
from toolbox import markdown_convertion

html = markdown_convertion(md)
print(html)
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(html)
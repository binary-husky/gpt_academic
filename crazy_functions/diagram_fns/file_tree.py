import os
from textwrap import indent
from loguru import logger

class FileNode:
    def __init__(self, name, build_manifest=False):
        self.name = name
        self.children = []
        self.is_leaf = False
        self.level = 0
        self.parenting_ship = []
        self.comment = ""
        self.comment_maxlen_show = 50
        self.build_manifest = build_manifest
        self.manifest = {}

    @staticmethod
    def add_linebreaks_at_spaces(string, interval=10):
        return '\n'.join(string[i:i+interval] for i in range(0, len(string), interval))

    def sanitize_comment(self, comment):
        if len(comment) > self.comment_maxlen_show: suf = '...'
        else: suf = ''
        comment = comment[:self.comment_maxlen_show]
        comment = comment.replace('\"', '').replace('`', '').replace('\n', '').replace('`', '').replace('$', '')
        comment = self.add_linebreaks_at_spaces(comment, 10)
        return '`' + comment + suf + '`'

    def add_file(self, file_path, file_comment):
        directory_names, file_name = os.path.split(file_path)
        current_node = self
        level = 1
        if directory_names == "":
            new_node = FileNode(file_name)
            self.manifest[file_path] = new_node
            current_node.children.append(new_node)
            new_node.is_leaf = True
            new_node.comment = self.sanitize_comment(file_comment)
            new_node.level = level
            current_node = new_node
        else:
            dnamesplit = directory_names.split(os.sep)
            for i, directory_name in enumerate(dnamesplit):
                found_child = False
                level += 1
                for child in current_node.children:
                    if child.name == directory_name:
                        current_node = child
                        found_child = True
                        break
                if not found_child:
                    new_node = FileNode(directory_name)
                    current_node.children.append(new_node)
                    new_node.level = level - 1
                    current_node = new_node
            term = FileNode(file_name)
            self.manifest[file_path] = term
            term.level = level
            term.comment = self.sanitize_comment(file_comment)
            term.is_leaf = True
            current_node.children.append(term)

    def print_files_recursively(self, level=0, code="R0"):
        logger.info('    '*level + self.name + ' ' + str(self.is_leaf) + ' ' + str(self.level))
        for j, child in enumerate(self.children):
            child.print_files_recursively(level=level+1, code=code+str(j))
            self.parenting_ship.extend(child.parenting_ship)
            p1 = f"""{code}[\"🗎{self.name}\"]""" if self.is_leaf else f"""{code}[[\"📁{self.name}\"]]"""
            p2 = """ --> """
            p3 = f"""{code+str(j)}[\"🗎{child.name}\"]""" if child.is_leaf else f"""{code+str(j)}[[\"📁{child.name}\"]]"""
            edge_code = p1 + p2 + p3
            if edge_code in self.parenting_ship:
                continue
            self.parenting_ship.append(edge_code)
        if self.comment != "":
            pc1 = f"""{code}[\"🗎{self.name}\"]""" if self.is_leaf else f"""{code}[[\"📁{self.name}\"]]"""
            pc2 = f""" -.-x """
            pc3 = f"""C{code}[\"{self.comment}\"]:::Comment"""
            edge_code = pc1 + pc2 + pc3
            self.parenting_ship.append(edge_code)


MERMAID_TEMPLATE = r"""
```mermaid
flowchart LR
    %% <gpt_academic_hide_mermaid_code> 一个特殊标记，用于在生成mermaid图表时隐藏代码块
    classDef Comment stroke-dasharray: 5 5
    subgraph {graph_name}
{relationship}
    end
```
"""

def build_file_tree_mermaid_diagram(file_manifest, file_comments, graph_name):
    # Create the root node
    file_tree_struct = FileNode("root")
    # Build the tree structure
    for file_path, file_comment in zip(file_manifest, file_comments):
        file_tree_struct.add_file(file_path, file_comment)
    file_tree_struct.print_files_recursively()
    cc = "\n".join(file_tree_struct.parenting_ship)
    ccc = indent(cc, prefix=" "*8)
    return MERMAID_TEMPLATE.format(graph_name=graph_name, relationship=ccc)

if __name__ == "__main__":
    # File manifest
    file_manifest = [
        "cradle_void_terminal.ipynb",
        "tests/test_utils.py",
        "tests/test_plugins.py",
        "tests/test_llms.py",
        "config.py",
        "build/ChatGLM-6b-onnx-u8s8/chatglm-6b-int8-onnx-merged/model_weights_0.bin",
        "crazy_functions/latex_fns/latex_actions.py",
        "crazy_functions/latex_fns/latex_toolbox.py"
    ]
    file_comments = [
        "根据位置和名称，可能是一个模块的初始化文件根据位置和名称，可能是一个模块的初始化文件根据位置和名称，可能是一个模块的初始化文件",
        "包含一些用于文本处理和模型微调的函数和装饰器包含一些用于文本处理和模型微调的函数和装饰器包含一些用于文本处理和模型微调的函数和装饰器",
        "用于构建HTML报告的类和方法用于构建HTML报告的类和方法用于构建HTML报告的类和方法",
        "包含了用于文本切分的函数，以及处理PDF文件的示例代码包含了用于文本切分的函数，以及处理PDF文件的示例代码包含了用于文本切分的函数，以及处理PDF文件的示例代码",
        "用于解析和翻译PDF文件的功能和相关辅助函数用于解析和翻译PDF文件的功能和相关辅助函数用于解析和翻译PDF文件的功能和相关辅助函数",
        "是一个包的初始化文件，用于初始化包的属性和导入模块是一个包的初始化文件，用于初始化包的属性和导入模块是一个包的初始化文件，用于初始化包的属性和导入模块",
        "用于加载和分割文件中的文本的通用文件加载器用于加载和分割文件中的文本的通用文件加载器用于加载和分割文件中的文本的通用文件加载器",
        "包含了用于构建和管理向量数据库的函数和类包含了用于构建和管理向量数据库的函数和类包含了用于构建和管理向量数据库的函数和类",
    ]
    logger.info(build_file_tree_mermaid_diagram(file_manifest, file_comments, "项目文件树"))
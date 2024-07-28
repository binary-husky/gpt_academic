import ast

class CommentRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # 移除函数的文档字符串
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        # 移除类的文档字符串
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        # 移除模块的文档字符串
        if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        self.generic_visit(node)
        return node
    

def remove_python_comments(source_code):
    # 解析源代码为 AST
    tree = ast.parse(source_code)
    # 移除注释
    transformer = CommentRemover()
    tree = transformer.visit(tree)
    # 将处理后的 AST 转换回源代码
    return ast.unparse(tree)

# 示例使用
if __name__ == "__main__":
    with open("source.py", "r", encoding="utf-8") as f:
        source_code = f.read()

    cleaned_code = remove_python_comments(source_code)

    with open("cleaned_source.py", "w", encoding="utf-8") as f:
        f.write(cleaned_code)
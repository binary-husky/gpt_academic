from pathlib import Path
from crazy_functions.doc_fns.read_fns.unstructured_all.paper_structure_extractor import PaperStructureExtractor

def extract_and_save_as_markdown(paper_path, output_path=None):
    """
    提取论文结构并保存为Markdown格式

    参数:
        paper_path: 论文文件路径
        output_path: 输出的Markdown文件路径，如果不指定，将使用与输入相同的文件名但扩展名为.md

    返回:
        保存的Markdown文件路径
    """
    # 创建提取器
    extractor = PaperStructureExtractor()

    # 解析文件路径
    paper_path = Path(paper_path)

    # 如果未指定输出路径，使用相同文件名但扩展名为.md
    if output_path is None:
        output_path = paper_path.with_suffix('.md')
    else:
        output_path = Path(output_path)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"正在处理论文: {paper_path}")

    try:
        # 提取论文结构
        paper = extractor.extract_paper_structure(paper_path)

        # 生成Markdown内容
        markdown_content = extractor.generate_markdown(paper)

        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"已成功保存Markdown文件: {output_path}")

        # 打印摘要信息
        print("\n论文摘要信息:")
        print(f"标题: {paper.metadata.title}")
        print(f"作者: {', '.join(paper.metadata.authors)}")
        print(f"关键词: {', '.join(paper.keywords)}")
        print(f"章节数: {len(paper.sections)}")
        print(f"图表数: {len(paper.figures)}")
        print(f"表格数: {len(paper.tables)}")
        print(f"公式数: {len(paper.formulas)}")
        print(f"参考文献数: {len(paper.references)}")

        return output_path

    except Exception as e:
        print(f"处理论文时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

# 使用示例
if __name__ == "__main__":
    # 替换为实际的论文文件路径
    sample_paper = "crazy_functions/doc_fns/read_fns/paper/2501.12599v1.pdf"

    # 可以指定输出路径，也可以使用默认路径
    # output_file = "/path/to/output/paper_structure.md"
    # extract_and_save_as_markdown(sample_paper, output_file)

    # 使用默认输出路径（与输入文件同名但扩展名为.md）
    extract_and_save_as_markdown(sample_paper)

    # # 批量处理多个论文的示例
    # paper_dir = Path("/path/to/papers/folder")
    # output_dir = Path("/path/to/output/folder")
    #
    # # 确保输出目录存在
    # output_dir.mkdir(parents=True, exist_ok=True)
    #
    # # 处理目录中的所有PDF文件
    # for paper_file in paper_dir.glob("*.pdf"):
    #     output_file = output_dir / f"{paper_file.stem}.md"
    #     extract_and_save_as_markdown(paper_file, output_file)

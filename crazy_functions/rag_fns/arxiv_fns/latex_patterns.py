from dataclasses import dataclass


@dataclass
class LaTeXPatterns:
    """LaTeX模式存储类，用于集中管理所有LaTeX相关的正则表达式模式"""
    special_envs = {
        'math': [
            # 基础数学环境
            r'\\begin{(equation|align|gather|eqnarray|multline|flalign|alignat)\*?}.*?\\end{\1\*?}',
            r'\$\$.*?\$\$',
            r'\$[^$]+\$',
            # 矩阵环境
            r'\\begin{(matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|smallmatrix)\*?}.*?\\end{\1\*?}',
            # 数组环境
            r'\\begin{(array|cases|aligned|gathered|split)\*?}.*?\\end{\1\*?}',
            # 其他数学环境
            r'\\begin{(subequations|math|displaymath)\*?}.*?\\end{\1\*?}'
        ],

        'table': [
            # 基础表格环境
            r'\\begin{(table|tabular|tabularx|tabulary|longtable)\*?}.*?\\end{\1\*?}',
            # 复杂表格环境
            r'\\begin{(tabu|supertabular|xtabular|mpsupertabular)\*?}.*?\\end{\1\*?}',
            # 自定义表格环境
            r'\\begin{(threeparttable|tablefootnote)\*?}.*?\\end{\1\*?}',
            # 表格注释环境
            r'\\begin{(tablenotes)\*?}.*?\\end{\1\*?}'
        ],

        'figure': [
            # 图片环境
            r'\\begin{figure\*?}.*?\\end{figure\*?}',
            r'\\begin{(subfigure|wrapfigure)\*?}.*?\\end{\1\*?}',
            # 图片插入命令
            r'\\includegraphics(\[.*?\])?\{.*?\}',
            # tikz 图形环境
            r'\\begin{(tikzpicture|pgfpicture)\*?}.*?\\end{\1\*?}',
            # 其他图形环境
            r'\\begin{(picture|pspicture)\*?}.*?\\end{\1\*?}'
        ],

        'algorithm': [
            # 算法环境
            r'\\begin{(algorithm|algorithmic|algorithm2e|algorithmicx)\*?}.*?\\end{\1\*?}',
            r'\\begin{(lstlisting|verbatim|minted|listing)\*?}.*?\\end{\1\*?}',
            # 代码块环境
            r'\\begin{(code|verbatimtab|verbatimwrite)\*?}.*?\\end{\1\*?}',
            # 伪代码环境
            r'\\begin{(pseudocode|procedure)\*?}.*?\\end{\1\*?}'
        ],

        'list': [
            # 列表环境
            r'\\begin{(itemize|enumerate|description)\*?}.*?\\end{\1\*?}',
            r'\\begin{(list|compactlist|bulletlist)\*?}.*?\\end{\1\*?}',
            # 自定义列表环境
            r'\\begin{(tasks|todolist)\*?}.*?\\end{\1\*?}'
        ],

        'theorem': [
            # 定理类环境
            r'\\begin{(theorem|lemma|proposition|corollary)\*?}.*?\\end{\1\*?}',
            r'\\begin{(definition|example|proof|remark)\*?}.*?\\end{\1\*?}',
            # 其他证明环境
            r'\\begin{(axiom|property|assumption|conjecture)\*?}.*?\\end{\1\*?}'
        ],

        'box': [
            # 文本框环境
            r'\\begin{(tcolorbox|mdframed|framed|shaded)\*?}.*?\\end{\1\*?}',
            r'\\begin{(boxedminipage|shadowbox)\*?}.*?\\end{\1\*?}',
            # 强调环境
            r'\\begin{(important|warning|info|note)\*?}.*?\\end{\1\*?}'
        ],

        'quote': [
            # 引用环境
            r'\\begin{(quote|quotation|verse|abstract)\*?}.*?\\end{\1\*?}',
            r'\\begin{(excerpt|epigraph)\*?}.*?\\end{\1\*?}'
        ],

        'bibliography': [
            # 参考文献环境
            r'\\begin{(thebibliography|bibliography)\*?}.*?\\end{\1\*?}',
            r'\\begin{(biblist|citelist)\*?}.*?\\end{\1\*?}'
        ],

        'index': [
            # 索引环境
            r'\\begin{(theindex|printindex)\*?}.*?\\end{\1\*?}',
            r'\\begin{(glossary|acronym)\*?}.*?\\end{\1\*?}'
        ]
    }
    # 章节模式
    section_patterns = [
        # 基础章节命令
        r'\\chapter\{([^}]+)\}',
        r'\\section\{([^}]+)\}',
        r'\\subsection\{([^}]+)\}',
        r'\\subsubsection\{([^}]+)\}',
        r'\\paragraph\{([^}]+)\}',
        r'\\subparagraph\{([^}]+)\}',

        # 带星号的变体(不编号)
        r'\\chapter\*\{([^}]+)\}',
        r'\\section\*\{([^}]+)\}',
        r'\\subsection\*\{([^}]+)\}',
        r'\\subsubsection\*\{([^}]+)\}',
        r'\\paragraph\*\{([^}]+)\}',
        r'\\subparagraph\*\{([^}]+)\}',

        # 特殊章节
        r'\\part\{([^}]+)\}',
        r'\\part\*\{([^}]+)\}',
        r'\\appendix\{([^}]+)\}',

        # 前言部分
        r'\\frontmatter\{([^}]+)\}',
        r'\\mainmatter\{([^}]+)\}',
        r'\\backmatter\{([^}]+)\}',

        # 目录相关
        r'\\tableofcontents',
        r'\\listoffigures',
        r'\\listoftables',

        # 自定义章节命令
        r'\\addchap\{([^}]+)\}',  # KOMA-Script类
        r'\\addsec\{([^}]+)\}',  # KOMA-Script类
        r'\\minisec\{([^}]+)\}',  # KOMA-Script类

        # 带可选参数的章节命令
        r'\\chapter\[([^]]+)\]\{([^}]+)\}',
        r'\\section\[([^]]+)\]\{([^}]+)\}',
        r'\\subsection\[([^]]+)\]\{([^}]+)\}'
    ]

    # 包含模式
    include_patterns = [
        r'\\(input|include|subfile)\{([^}]+)\}'
    ]

    metadata_patterns = {
        # 标题相关
        'title': [
            r'\\title\{([^}]+)\}',
            r'\\Title\{([^}]+)\}',
            r'\\doctitle\{([^}]+)\}',
            r'\\subtitle\{([^}]+)\}',
            r'\\chapter\*?\{([^}]+)\}',  # 第一章可能作为标题
            r'\\maketitle\s*\\section\*?\{([^}]+)\}'  # 第一节可能作为标题
        ],

        # 摘要相关
        'abstract': [
            r'\\begin{abstract}(.*?)\\end{abstract}',
            r'\\abstract\{([^}]+)\}',
            r'\\begin{摘要}(.*?)\\end{摘要}',
            r'\\begin{Summary}(.*?)\\end{Summary}',
            r'\\begin{synopsis}(.*?)\\end{synopsis}',
            r'\\begin{abstracten}(.*?)\\end{abstracten}'  # 英文摘要
        ],

        # 作者信息
        'author': [
            r'\\author\{([^}]+)\}',
            r'\\Author\{([^}]+)\}',
            r'\\authorinfo\{([^}]+)\}',
            r'\\authors\{([^}]+)\}',
            r'\\author\[([^]]+)\]\{([^}]+)\}',  # 带附加信息的作者
            r'\\begin{authors}(.*?)\\end{authors}'
        ],

        # 日期相关
        'date': [
            r'\\date\{([^}]+)\}',
            r'\\Date\{([^}]+)\}',
            r'\\submitdate\{([^}]+)\}',
            r'\\publishdate\{([^}]+)\}',
            r'\\revisiondate\{([^}]+)\}'
        ],

        # 关键词
        'keywords': [
            r'\\keywords\{([^}]+)\}',
            r'\\Keywords\{([^}]+)\}',
            r'\\begin{keywords}(.*?)\\end{keywords}',
            r'\\key\{([^}]+)\}',
            r'\\begin{关键词}(.*?)\\end{关键词}'
        ],

        # 机构/单位
        'institution': [
            r'\\institute\{([^}]+)\}',
            r'\\institution\{([^}]+)\}',
            r'\\affiliation\{([^}]+)\}',
            r'\\organization\{([^}]+)\}',
            r'\\department\{([^}]+)\}'
        ],

        # 学科/主题
        'subject': [
            r'\\subject\{([^}]+)\}',
            r'\\Subject\{([^}]+)\}',
            r'\\field\{([^}]+)\}',
            r'\\discipline\{([^}]+)\}'
        ],

        # 版本信息
        'version': [
            r'\\version\{([^}]+)\}',
            r'\\revision\{([^}]+)\}',
            r'\\release\{([^}]+)\}'
        ],

        # 许可证/版权
        'license': [
            r'\\license\{([^}]+)\}',
            r'\\copyright\{([^}]+)\}',
            r'\\begin{license}(.*?)\\end{license}'
        ],

        # 联系方式
        'contact': [
            r'\\email\{([^}]+)\}',
            r'\\phone\{([^}]+)\}',
            r'\\address\{([^}]+)\}',
            r'\\contact\{([^}]+)\}'
        ],

        # 致谢
        'acknowledgments': [
            r'\\begin{acknowledgments}(.*?)\\end{acknowledgments}',
            r'\\acknowledgments\{([^}]+)\}',
            r'\\thanks\{([^}]+)\}',
            r'\\begin{致谢}(.*?)\\end{致谢}'
        ],

        # 项目/基金
        'funding': [
            r'\\funding\{([^}]+)\}',
            r'\\grant\{([^}]+)\}',
            r'\\project\{([^}]+)\}',
            r'\\support\{([^}]+)\}'
        ],

        # 分类号/编号
        'classification': [
            r'\\classification\{([^}]+)\}',
            r'\\serialnumber\{([^}]+)\}',
            r'\\id\{([^}]+)\}',
            r'\\doi\{([^}]+)\}'
        ],

        # 语言
        'language': [
            r'\\documentlanguage\{([^}]+)\}',
            r'\\lang\{([^}]+)\}',
            r'\\language\{([^}]+)\}'
        ]
    }
    latex_only_patterns = {
        # 文档类和包引入
        r'\\documentclass(\[.*?\])?\{.*?\}',
        r'\\usepackage(\[.*?\])?\{.*?\}',
        # 常见的文档设置命令
        r'\\setlength\{.*?\}\{.*?\}',
        r'\\newcommand\{.*?\}(\[.*?\])?\{.*?\}',
        r'\\renewcommand\{.*?\}(\[.*?\])?\{.*?\}',
        r'\\definecolor\{.*?\}\{.*?\}\{.*?\}',
        # 页面设置相关
        r'\\pagestyle\{.*?\}',
        r'\\thispagestyle\{.*?\}',
        # 其他常见的设置命令
        r'\\bibliographystyle\{.*?\}',
        r'\\bibliography\{.*?\}',
        r'\\setcounter\{.*?\}\{.*?\}',
        # 字体和文本设置命令
        r'\\makeFNbottom',
        r'\\@setfontsize\\[A-Z]+\{.*?\}\{.*?\}',  # 匹配字体大小设置
        r'\\renewcommand\\[A-Z]+\{\\@setfontsize\\[A-Z]+\{.*?\}\{.*?\}\}',
        r'\\renewcommand\{?\\thefootnote\}?\{\\fnsymbol\{footnote\}\}',
        r'\\renewcommand\\footnoterule\{.*?\}',
        r'\\color\{.*?\}',

        # 页面和节标题设置
        r'\\setcounter\{secnumdepth\}\{.*?\}',
        r'\\renewcommand\\@biblabel\[.*?\]\{.*?\}',
        r'\\renewcommand\\@makefntext\[.*?\](\{.*?\})*',
        r'\\renewcommand\{?\\figurename\}?\{.*?\}',

        # 字体样式设置
        r'\\sectionfont\{.*?\}',
        r'\\subsectionfont\{.*?\}',
        r'\\subsubsectionfont\{.*?\}',

        # 间距和布局设置
        r'\\setstretch\{.*?\}',
        r'\\setlength\{\\skip\\footins\}\{.*?\}',
        r'\\setlength\{\\footnotesep\}\{.*?\}',
        r'\\setlength\{\\jot\}\{.*?\}',
        r'\\hrule\s+width\s+.*?\s+height\s+.*?',

        # makeatletter 和 makeatother
        r'\\makeatletter\s*',
        r'\\makeatother\s*',
        r'\\footnotetext\{[^}]*\$\^{[^}]*}\$[^}]*\}',  # 带有上标的脚注
        # r'\\footnotetext\{[^}]*\}',  # 普通脚注
        # r'\\footnotetext\{.*?(?:\$\^{.*?}\$)?.*?(?:email\s*:\s*[^}]*)?.*?\}',  # 带有邮箱的脚注
        # r'\\footnotetext\{.*?(?:ESI|DOI).*?\}',  # 带有 DOI 或 ESI 引用的脚注
        # 文档结构命令
        r'\\begin\{document\}',
        r'\\end\{document\}',
        r'\\maketitle',
        r'\\printbibliography',
        r'\\newpage',

        # 输入文件命令
        r'\\input\{[^}]*\}',
        r'\\input\{.*?\.tex\}',  # 特别匹配 .tex 后缀的输入

        # 脚注相关
        # r'\\footnotetext\[\d+\]\{[^}]*\}',  # 带编号的脚注

        # 致谢环境
        r'\\begin\{ack\}',
        r'\\end\{ack\}',
        r'\\begin\{ack\}[^\n]*(?:\n.*?)*?\\end\{ack\}',  # 匹配整个致谢环境及其内容

        # 其他文档控制命令
        r'\\renewcommand\{\\thefootnote\}\{\\fnsymbol\{footnote\}\}',
    }
    math_envs = [
        # 基础数学环境
        (r'\\begin{equation\*?}.*?\\end{equation\*?}', 'equation'),  # 单行公式
        (r'\\begin{align\*?}.*?\\end{align\*?}', 'align'),  # 多行对齐公式
        (r'\\begin{gather\*?}.*?\\end{gather\*?}', 'gather'),  # 多行居中公式
        (r'\$\$.*?\$\$', 'display'),  # 行间公式
        (r'\$.*?\$', 'inline'),  # 行内公式

        # 矩阵环境
        (r'\\begin{matrix}.*?\\end{matrix}', 'matrix'),  # 基础矩阵
        (r'\\begin{pmatrix}.*?\\end{pmatrix}', 'pmatrix'),  # 圆括号矩阵
        (r'\\begin{bmatrix}.*?\\end{bmatrix}', 'bmatrix'),  # 方括号矩阵
        (r'\\begin{vmatrix}.*?\\end{vmatrix}', 'vmatrix'),  # 竖线矩阵
        (r'\\begin{Vmatrix}.*?\\end{Vmatrix}', 'Vmatrix'),  # 双竖线矩阵
        (r'\\begin{smallmatrix}.*?\\end{smallmatrix}', 'smallmatrix'),  # 小号矩阵

        # 数组环境
        (r'\\begin{array}.*?\\end{array}', 'array'),  # 数组
        (r'\\begin{cases}.*?\\end{cases}', 'cases'),  # 分段函数

        # 多行公式环境
        (r'\\begin{multline\*?}.*?\\end{multline\*?}', 'multline'),  # 多行单个公式
        (r'\\begin{split}.*?\\end{split}', 'split'),  # 拆分长公式
        (r'\\begin{alignat\*?}.*?\\end{alignat\*?}', 'alignat'),  # 对齐环境带间距控制
        (r'\\begin{flalign\*?}.*?\\end{flalign\*?}', 'flalign'),  # 完全左对齐

        # 特殊数学环境
        (r'\\begin{subequations}.*?\\end{subequations}', 'subequations'),  # 子公式编号
        (r'\\begin{gathered}.*?\\end{gathered}', 'gathered'),  # 居中对齐组
        (r'\\begin{aligned}.*?\\end{aligned}', 'aligned'),  # 内部对齐组

        # 定理类环境
        (r'\\begin{theorem}.*?\\end{theorem}', 'theorem'),  # 定理
        (r'\\begin{lemma}.*?\\end{lemma}', 'lemma'),  # 引理
        (r'\\begin{proof}.*?\\end{proof}', 'proof'),  # 证明

        # 数学模式中的表格环境
        (r'\\begin{tabular}.*?\\end{tabular}', 'tabular'),  # 表格
        (r'\\begin{array}.*?\\end{array}', 'array'),  # 数组

        # 其他专业数学环境
        (r'\\begin{CD}.*?\\end{CD}', 'CD'),  # 交换图
        (r'\\begin{boxed}.*?\\end{boxed}', 'boxed'),  # 带框公式
        (r'\\begin{empheq}.*?\\end{empheq}', 'empheq'),  # 强调公式

        # 化学方程式环境 (需要加载 mhchem 包)
        (r'\\begin{reaction}.*?\\end{reaction}', 'reaction'),  # 化学反应式
        (r'\\ce\{.*?\}', 'chemequation'),  # 化学方程式

        # 物理单位环境 (需要加载 siunitx 包)
        (r'\\SI\{.*?\}\{.*?\}', 'SI'),  # 物理单位
        (r'\\si\{.*?\}', 'si'),  # 单位

        # 补充环境
        (r'\\begin{equation\+}.*?\\end{equation\+}', 'equation+'),  # breqn包的自动换行公式
        (r'\\begin{dmath\*?}.*?\\end{dmath\*?}', 'dmath'),  # breqn包的显示数学模式
        (r'\\begin{dgroup\*?}.*?\\end{dgroup\*?}', 'dgroup'),  # breqn包的公式组
    ]

    # 示例使用函数

    # 使用示例

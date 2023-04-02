# chatgpt-academic项目自译解报告
（Author补充：以下分析均由本项目调用ChatGPT一键生成，如果有不准确的地方，全怪GPT😄）

## [0/18] 程序摘要: functional_crazy.py

这是一个功能扩展的程序，文件名为 `functional_crazy.py`。代码的主要功能是通过提供一系列函数插件，增强程序的功能，让用户可以通过界面中的按钮，快速调用对应的函数插件实现相应的操作。代码中使用了 `HotReload` 函数插件，可以在不重启程序的情况下更新函数插件的代码，让其生效。同时，通过 `UserVisibleLevel` 变量的设置，可以控制哪些插件会在UI界面显示出来。函数插件列表包括了以下功能：解析项目本身、解析一个Python项目、解析一个C++项目头文件、解析一个C++项目、读取文章并生成摘要、批量生成函数注释、全项目切换成英文、批量总结PDF文档、批量总结PDF文档pdfminer、批量总结Word文档、高阶功能模板函数、以及其他未经充分测试的函数插件。

## [1/18] 程序摘要: main.py

该程序是一个基于Gradio构建的对话生成模型的Web界面示例，包含了以下主要功能：

1.加载模型并对用户输入进行响应；
2.通过调用外部函数库来获取用户的输入，并在模型生成的过程中进行处理；
3.支持用户上传本地文件，供外部函数库调用；
4.支持停止当前的生成过程；
5.保存用户的历史记录，并将其记录在本地日志文件中，以供后续分析和使用。

该程序需要依赖于一些外部库和软件包，如Gradio、torch等。用户需要确保这些依赖项已经安装，并且在运行该程序前对config_private.py配置文件进行相应的修改。

## [2/18] 程序摘要: functional.py

该文件定义了一个名为“functional”的函数，函数的作用是返回一个包含多个字典（键值对）的字典，每个键值对表示一种功能。该字典的键值由功能名称和对应的数据组成。其中的每个字典都包含4个键值对，分别为“Prefix”、“Suffix”、“Color”和“PreProcess”，分别表示前缀、后缀、按钮颜色和预处理函数。如果某些键值对没有给出，那么程序中默认相应的值，如按钮颜色默认为“secondary”等。每个功能描述了不同的学术润色/翻译/其他服务，如“英语学术润色”、“中文学术润色”、“查找语法错误”等。函数还引用了一个名为“clear_line_break”的函数，用于预处理修改前的文本。

## [3/18] 程序摘要: show_math.py

该程序文件名为show_math.py，主要用途是将Markdown和LaTeX混合格式转换成带有MathML的HTML格式。该程序通过递归地处理LaTeX和Markdown混合段落逐一转换成HTML/MathML标记出来，并在LaTeX公式创建中进行错误处理。在程序文件中定义了3个变量，分别是incomplete，convError和convert，其中convert函数是用来执行转换的主要函数。程序使用正则表达式进行LaTeX格式和Markdown段落的分割，从而实现转换。如果在Latex转换过程中发生错误，程序将输出相应的错误信息。

## [4/18] 程序摘要: predict.py

本程序文件的文件名为"./predict.py"，主要包含三个函数：

1. predict：正常对话时使用，具备完备的交互功能，不可多线程；
2. predict_no_ui：高级实验性功能模块调用，不会实时显示在界面上，参数简单，可以多线程并行，方便实现复杂的功能逻辑；
3. predict_no_ui_long_connection：在实验过程中发现调用predict_no_ui处理长文档时，和openai的连接容易断掉，这个函数用stream的方式解决这个问题，同样支持多线程。

其中，predict函数用于基础的对话功能，发送至chatGPT，流式获取输出，根据点击的哪个按钮，进行对话预处理等额外操作；predict_no_ui函数用于payload比较大的情况，或者用于实现多线、带嵌套的复杂功能；predict_no_ui_long_connection实现调用predict_no_ui处理长文档时，避免连接断掉的情况，支持多线程。

## [5/18] 程序摘要: check_proxy.py

该程序文件名为check_proxy.py，主要功能是检查代理服务器的可用性并返回代理服务器的地理位置信息或错误提示。具体实现方式如下：

首先使用requests模块向指定网站（https://ipapi.co/json/）发送GET请求，请求结果以JSON格式返回。如果代理服务器参数(proxies)是有效的且没有指明'https'代理，则用默认字典值'无'替代。

然后，程序会解析返回的JSON数据，并根据数据中是否包含国家名字字段来判断代理服务器的地理位置。如果有国家名字字段，则将其打印出来并返回代理服务器的相关信息。如果没有国家名字字段，但有错误信息字段，则返回其他错误提示信息。

在程序执行前，程序会先设置环境变量no_proxy，并使用toolbox模块中的get_conf函数从配置文件中读取代理参数。

最后，检测程序会输出检查结果并返回对应的结果字符串。

## [6/18] 程序摘要: config_private.py

本程序文件名为`config_private.py`，其功能为配置私有信息以便在主程序中使用。主要功能包括：

- 配置OpenAI API的密钥和API URL
- 配置是否使用代理，如果使用代理配置代理地址和端口
- 配置发送请求的超时时间和失败重试次数的限制
- 配置并行使用线程数和用户名密码
- 提供检查功能以确保API密钥已经正确设置

其中，需要特别注意的是：最后一个检查功能要求在运行之前必须将API密钥正确设置，否则程序会直接退出。

## [7/18] 程序摘要: config.py

该程序文件是一个配置文件，用于配置OpenAI的API参数和优化体验的相关参数，具体包括以下几个步骤：

1.设置OpenAI的API密钥。

2.选择是否使用代理，如果使用则需要设置代理地址和端口等参数。

3.设置请求OpenAI后的超时时间、网页的端口、重试次数、选择的OpenAI模型、API的网址等。

4.设置并行使用的线程数和用户名密码。

该程序文件的作用为在使用OpenAI API时进行相关参数的配置，以保证请求的正确性和速度，并且优化使用体验。

## [8/18] 程序摘要: theme.py

该程序是一个自定义Gradio主题的Python模块。主题文件名为"./theme.py"。程序引入了Gradio模块，并定义了一个名为"adjust_theme()"的函数。该函数根据输入值调整Gradio的默认主题，返回一个包含所需自定义属性的主题对象。主题属性包括颜色、字体、过渡、阴影、按钮边框和渐变等。主题颜色列表包括石板色、灰色、锌色、中性色、石头色、红色、橙色、琥珀色、黄色、酸橙色、绿色、祖母绿、青蓝色、青色、天蓝色、蓝色、靛蓝色、紫罗兰色、紫色、洋红色、粉红色和玫瑰色。如果Gradio版本较旧，则不能自定义字体和颜色。

## [9/18] 程序摘要: toolbox.py

该程序文件包含了一系列函数，用于实现聊天程序所需的各种功能，如预测对话、将对话记录写入文件、将普通文本转换为Markdown格式文本、装饰器函数CatchException和HotReload等。其中一些函数用到了第三方库，如Python-Markdown、mdtex2html、zipfile、tarfile、rarfile和py7zr。除此之外，还有一些辅助函数，如get_conf、clear_line_break和extract_archive等。主要功能包括：

1. 导入markdown、mdtex2html、threading、functools等模块。
2. 定义函数predict_no_ui_but_counting_down，用于生成对话。
3. 定义函数write_results_to_file，用于将对话记录生成Markdown文件。
4. 定义函数regular_txt_to_markdown，将普通文本转换为Markdown格式的文本。
5. 定义装饰器函数CatchException，用于捕获函数执行异常并返回生成器。
6. 定义函数report_execption，用于向chatbot中添加错误信息。
7. 定义函数text_divide_paragraph，用于将文本按照段落分隔符分割开，生成带有段落标签的HTML代码。
8. 定义函数markdown_convertion，用于将Markdown格式的文本转换为HTML格式。
9. 定义函数format_io，用于将输入和输出解析为HTML格式。
10. 定义函数find_free_port，用于返回当前系统中可用的未使用端口。
11. 定义函数extract_archive，用于解压归档文件。
12. 定义函数find_recent_files，用于查找最近创建的文件。
13. 定义函数on_file_uploaded，用于处理上传文件的操作。
14. 定义函数on_report_generated，用于处理生成报告文件的操作。


## [10/18] 程序摘要: crazy_functions/生成函数注释.py

该程序文件是一个Python脚本，文件名为“生成函数注释.py”，位于“./crazy_functions/”目录下。该程序实现了一个批量生成函数注释的功能，可以对指定文件夹下的所有Python和C++源代码文件中的所有函数进行注释，使用Markdown表格输出注释结果。

该程序引用了predict.py和toolbox.py两个模块，其中predict.py实现了一个基于GPT模型的文本生成功能，用于生成函数注释，而toolbox.py实现了一些工具函数，包括异常处理函数、文本写入函数等。另外，该程序还定义了两个函数，一个是“生成函数注释”函数，用于处理单个文件的注释生成；另一个是“批量生成函数注释”函数，用于批量处理多个文件的注释生成。

## [11/18] 程序摘要: crazy_functions/读文章写摘要.py

这个程序文件是一个名为“读文章写摘要”的函数。该函数的输入包括文章的文本内容、top_p（生成文本时选择最可能的词语的概率阈值）、temperature（控制生成文本的随机性的因子）、对话历史等参数，以及一个聊天机器人和一个系统提示的文本。该函数的主要工作是解析一组.tex文件，然后生成一段学术性语言的中文和英文摘要。在解析过程中，该函数使用一个名为“toolbox”的模块中的辅助函数和一个名为“predict”的模块中的函数来执行GPT-2模型的推理工作，然后将结果返回给聊天机器人。另外，该程序还包括一个名为“fast_debug”的bool型变量，用于调试和测试。

## [12/18] 程序摘要: crazy_functions/代码重写为全英文_多线程.py

该程序文件实现了一个多线程操作，用于将指定目录下的所有 Python 文件中的中文转化为英文，并将转化后的文件存入另一个目录中。具体实现过程如下：

1. 集合目标文件路径并清空历史记录。
2. 循环目标文件，对每个文件启动一个线程进行任务操作。
3. 各个线程同时开始执行任务函数，并在任务完成后将转化后的文件写入指定目录，最终生成一份任务执行报告。

## [13/18] 程序摘要: crazy_functions/高级功能函数模板.py

该程序文件名为高级功能函数模板.py，它包含了一个名为“高阶功能模板函数”的函数，这个函数可以作为开发新功能函数的模板。该函数引用了predict.py和toolbox.py文件中的函数。在该函数内部，它首先清空了历史记录，然后对于今天和今天以后的四天，它问用户历史中哪些事件发生在这些日期，并列举两条事件并发送相关的图片。在向用户询问问题时，使用了GPT进行响应。由于请求GPT需要一定的时间，所以函数会在重新显示状态之前等待一段时间。在每次与用户的互动中，使用yield关键字生成器函数来输出聊天机器人的当前状态，包括聊天消息、历史记录和状态（'正常'）。最后，程序调用write_results_to_file函数将聊天的结果写入文件，以供后续的评估和分析。

## [14/18] 程序摘要: crazy_functions/总结word文档.py

该程序文件名为总结word文档.py，主要功能是批量总结Word文档。具体实现过程是解析docx格式和doc格式文件，生成文件内容，然后使用自然语言处理工具对文章内容做中英文概述，最后给出建议。该程序需要依赖python-docx和pywin32，如果没有安装，会给出安装建议。

## [15/18] 程序摘要: crazy_functions/批量总结PDF文档pdfminer.py

该程序文件名为pdfminer.py，位于./crazy_functions/目录下。程序实现了批量读取PDF文件，并使用pdfminer解析PDF文件内容。此外，程序还根据解析得到的文本内容，调用机器学习模型生成对每篇文章的概述，最终生成全文摘要。程序中还对模块依赖进行了导入检查，若缺少依赖，则会提供安装建议。

## [16/18] 程序摘要: crazy_functions/解析项目源代码.py

这个程序文件中包含了几个函数，分别是：

1. `解析源代码(file_manifest, project_folder, top_p, temperature, chatbot, history, systemPromptTxt)`：通过输入文件路径列表对程序文件进行逐文件分析，根据分析结果做出整体功能和构架的概括，并生成包括每个文件功能的markdown表格。
2. `解析项目本身(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)`：对当前文件夹下的所有Python文件及其子文件夹进行逐文件分析，并生成markdown表格。
3. `解析一个Python项目(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)`：对指定路径下的所有Python文件及其子文件夹进行逐文件分析，并生成markdown表格。
4. `解析一个C项目的头文件(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)`：对指定路径下的所有头文件进行逐文件分析，并生成markdown表格。
5. `解析一个C项目(txt, top_p, temperature, chatbot, history, systemPromptTxt, WEB_PORT)`：对指定路径下的所有.h、.cpp、.c文件及其子文件夹进行逐文件分析，并生成markdown表格。

程序中还包含了一些辅助函数和变量，如CatchException装饰器函数，report_execption函数、write_results_to_file函数等。在执行过程中还会调用其他模块中的函数，如toolbox模块的函数和predict模块的函数。

## [17/18] 程序摘要: crazy_functions/批量总结PDF文档.py

这个程序文件是一个名为“批量总结PDF文档”的函数插件。它导入了predict和toolbox模块，并定义了一些函数，包括is_paragraph_break，normalize_text和clean_text。这些函数是对输入文本进行预处理和清洗的功能函数。主要的功能函数是解析PDF，它打开每个PDF文件并将其内容存储在file_content变量中，然后传递给聊天机器人，以产生一句话的概括。在解析PDF文件之后，该函数连接了所有文件的摘要，以产生一段学术语言和英文摘要。最后，函数批量处理目标文件夹中的所有PDF文件，并输出结果。

## 根据以上你自己的分析，对程序的整体功能和构架做出概括。然后用一张markdown表格整理每个文件的功能。

该程序是一个聊天机器人，使用了OpenAI的GPT语言模型以及一些特殊的辅助功能去处理各种学术写作和科研润色任务。整个程序由一些函数组成，每个函数都代表了不同的学术润色/翻译/其他服务。

下面是程序中每个文件的功能列表：

| 文件名 | 功能 |
|--------|--------|
| functional_crazy.py | 实现高级功能函数模板和其他一些辅助功能函数 |
| main.py | 程序的主要入口，负责程序的启动和UI的展示 |
| functional.py | 定义各种功能按钮的颜色和响应函数 |
| show_math.py | 解析LaTeX文本，将其转换为Markdown格式 |
| predict.py | 基础的对话功能，用于与chatGPT进行交互 |
| check_proxy.py | 检查代理设置的正确性 |
| config_private.py | 配置程序的API密钥和其他私有信息 |
| config.py | 配置OpenAI的API参数和程序的其他属性 |
| theme.py | 设置程序主题样式 |
| toolbox.py | 存放一些辅助函数供程序使用 |
| crazy_functions/生成函数注释.py | 生成Python文件中所有函数的注释 |
| crazy_functions/读文章写摘要.py | 解析文章文本，生成中英文摘要 |
| crazy_functions/代码重写为全英文_多线程.py | 将中文代码内容转化为英文 |
| crazy_functions/高级功能函数模板.py | 实现高级功能函数模板 |
| crazy_functions/总结word文档.py | 解析Word文件，生成文章内容的概要 |
| crazy_functions/批量总结PDF文档pdfminer.py | 解析PDF文件，生成文章内容的概要（使用pdfminer库） |
| crazy_functions/批量总结PDF文档.py | 解析PDF文件，生成文章内容的概要（使用PyMuPDF库） |
| crazy_functions/解析项目源代码.py | 解析C/C++源代码，生成markdown表格 |
| crazy_functions/批量总结PDF文档.py | 对PDF文件进行批量摘要生成 |

总的来说，该程序提供了一系列的学术润色和翻译的工具，支持对各种类型的文件进行分析和处理。同时也提供了对话式用户界面，便于用户使用和交互。


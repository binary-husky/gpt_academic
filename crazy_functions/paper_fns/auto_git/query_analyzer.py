from typing import Dict, List
from dataclasses import dataclass
import re

@dataclass
class SearchCriteria:
    """搜索条件"""
    query_type: str  # 查询类型: repo/code/user/topic
    main_topic: str  # 主题
    sub_topics: List[str]  # 子主题列表
    language: str  # 编程语言
    min_stars: int  # 最少星标数
    github_params: Dict  # GitHub搜索参数
    original_query: str = ""  # 原始查询字符串
    repo_id: str = ""  # 特定仓库ID或名称

class QueryAnalyzer:
    """查询分析器"""

    # 响应索引常量
    BASIC_QUERY_INDEX = 0
    GITHUB_QUERY_INDEX = 1

    def __init__(self):
        self.valid_types = {
            "repo": ["repository", "project", "library", "framework", "tool"],
            "code": ["code", "snippet", "implementation", "function", "class", "algorithm"],
            "user": ["user", "developer", "organization", "contributor", "maintainer"],
            "topic": ["topic", "category", "tag", "field", "area", "domain"]
        }

    def analyze_query(self, query: str, chatbot: List, llm_kwargs: Dict):
        """分析查询意图"""
        from crazy_functions.crazy_utils import \
            request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency as request_gpt

        # 1. 基本查询分析
        type_prompt = f"""请分析这个与GitHub相关的查询，并严格按照以下XML格式回答：

查询: {query}

说明:
1. 你的回答必须使用下面显示的XML标签，不要有任何标签外的文本
2. 从以下选项中选择查询类型: repo/code/user/topic
   - repo: 用于查找仓库、项目、框架或库
   - code: 用于查找代码片段、函数实现或算法
   - user: 用于查找用户、开发者或组织
   - topic: 用于查找主题、类别或领域相关项目
3. 识别主题和子主题
4. 识别首选编程语言(如果有)
5. 确定最低星标数(如果适用)

必需格式:
<query_type>此处回答</query_type>
<main_topic>此处回答</main_topic>
<sub_topics>子主题1, 子主题2, ...</sub_topics>
<language>此处回答</language>
<min_stars>此处回答</min_stars>

示例回答:

1. 仓库查询:
查询: "查找有至少1000颗星的Python web框架"
<query_type>repo</query_type>
<main_topic>web框架</main_topic>
<sub_topics>后端开发, HTTP服务器, ORM</sub_topics>
<language>Python</language>
<min_stars>1000</min_stars>

2. 代码查询:
查询: "如何用JavaScript实现防抖函数"
<query_type>code</query_type>
<main_topic>防抖函数</main_topic>
<sub_topics>事件处理, 性能优化, 函数节流</sub_topics>
<language>JavaScript</language>
<min_stars>0</min_stars>"""

        # 2. 生成英文搜索条件
        github_prompt = f"""Optimize the following GitHub search query:

Query: {query}

Task: Convert the natural language query into an optimized GitHub search query.
Please use English, regardless of the language of the input query.

Available search fields and filters:
1. Basic fields:
   - in:name - Search in repository names
   - in:description - Search in repository descriptions
   - in:readme - Search in README files
   - in:topic - Search in topics
   - language:X - Filter by programming language
   - user:X - Repositories from a specific user
   - org:X - Repositories from a specific organization

2. Code search fields:
   - extension:X - Filter by file extension
   - path:X - Filter by path
   - filename:X - Filter by filename

3. Metric filters:
   - stars:>X - Has more than X stars
   - forks:>X - Has more than X forks
   - size:>X - Size greater than X KB
   - created:>YYYY-MM-DD - Created after a specific date
   - pushed:>YYYY-MM-DD - Updated after a specific date

4. Other filters:
   - is:public/private - Public or private repositories
   - archived:true/false - Archived or not archived
   - license:X - Specific license
   - topic:X - Contains specific topic tag

Examples:

1. Query: "Find Python machine learning libraries with at least 1000 stars"
<query>machine learning in:description language:python stars:>1000</query>

2. Query: "Recently updated React UI component libraries"
<query>UI components library in:readme in:description language:javascript topic:react pushed:>2023-01-01</query>

3. Query: "Open source projects developed by Facebook"
<query>org:facebook is:public</query>

4. Query: "Depth-first search implementation in JavaScript"
<query>depth first search in:file language:javascript</query>

Please analyze the query and answer using only the XML tag:
<query>Provide the optimized GitHub search query, using appropriate fields and operators</query>"""

        # 3. 生成中文搜索条件
        chinese_github_prompt = f"""优化以下GitHub搜索查询:

查询: {query}

任务: 将自然语言查询转换为优化的GitHub搜索查询语句。
为了搜索中文内容，请提取原始查询的关键词并使用中文形式，同时保留GitHub特定的搜索语法为英文。

可用的搜索字段和过滤器:
1. 基本字段:
   - in:name - 在仓库名称中搜索
   - in:description - 在仓库描述中搜索
   - in:readme - 在README文件中搜索
   - in:topic - 在主题中搜索
   - language:X - 按编程语言筛选
   - user:X - 特定用户的仓库
   - org:X - 特定组织的仓库

2. 代码搜索字段:
   - extension:X - 按文件扩展名筛选
   - path:X - 按路径筛选
   - filename:X - 按文件名筛选

3. 指标过滤器:
   - stars:>X - 有超过X颗星
   - forks:>X - 有超过X个分支
   - size:>X - 大小超过X KB
   - created:>YYYY-MM-DD - 在特定日期后创建
   - pushed:>YYYY-MM-DD - 在特定日期后更新

4. 其他过滤器:
   - is:public/private - 公开或私有仓库
   - archived:true/false - 已归档或未归档
   - license:X - 特定许可证
   - topic:X - 含特定主题标签

示例:

1. 查询: "找有关机器学习的Python库，至少1000颗星"
<query>机器学习 in:description language:python stars:>1000</query>

2. 查询: "最近更新的React UI组件库"
<query>UI 组件库 in:readme in:description language:javascript topic:react pushed:>2023-01-01</query>

3. 查询: "微信小程序开发框架"
<query>微信小程序 开发框架 in:name in:description in:readme</query>

请分析查询并仅使用XML标签回答:
<query>提供优化的GitHub搜索查询，使用适当的字段和运算符，保留中文关键词</query>"""

        try:
            # 构建提示数组
            prompts = [
                type_prompt,
                github_prompt,
                chinese_github_prompt,
            ]

            show_messages = [
                "分析查询类型...",
                "优化英文GitHub搜索参数...",
                "优化中文GitHub搜索参数...",
            ]

            sys_prompts = [
                "你是一个精通GitHub生态系统的专家，擅长分析与GitHub相关的查询。",
                "You are a GitHub search expert, specialized in converting natural language queries into optimized GitHub search queries in English.",
                "你是一个GitHub搜索专家，擅长处理查询并保留中文关键词进行搜索。",
            ]

            # 使用同步方式调用LLM
            responses = yield from request_gpt(
                inputs_array=prompts,
                inputs_show_user_array=show_messages,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history_array=[[] for _ in prompts],
                sys_prompt_array=sys_prompts,
                max_workers=3
            )

            # 从收集的响应中提取我们需要的内容
            extracted_responses = []
            for i in range(len(prompts)):
                if (i * 2 + 1) < len(responses):
                    response = responses[i * 2 + 1]
                    if response is None:
                        raise Exception(f"Response {i} is None")
                    if not isinstance(response, str):
                        try:
                            response = str(response)
                        except:
                            raise Exception(f"Cannot convert response {i} to string")
                    extracted_responses.append(response)
                else:
                    raise Exception(f"未收到第 {i + 1} 个响应")

            # 解析基本信息
            query_type = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "query_type")
            if not query_type:
                print(
                    f"Debug - Failed to extract query_type. Response was: {extracted_responses[self.BASIC_QUERY_INDEX]}")
                raise Exception("无法提取query_type标签内容")
            query_type = query_type.lower()

            main_topic = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "main_topic")
            if not main_topic:
                print(f"Debug - Failed to extract main_topic. Using query as fallback.")
                main_topic = query

            query_type = self._normalize_query_type(query_type, query)

            # 提取子主题
            sub_topics = []
            sub_topics_text = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "sub_topics")
            if sub_topics_text:
                sub_topics = [topic.strip() for topic in sub_topics_text.split(",")]

            # 提取语言
            language = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "language")

            # 提取最低星标数
            min_stars = 0
            min_stars_text = self._extract_tag(extracted_responses[self.BASIC_QUERY_INDEX], "min_stars")
            if min_stars_text and min_stars_text.isdigit():
                min_stars = int(min_stars_text)

            # 解析GitHub搜索参数 - 英文
            english_github_query = self._extract_tag(extracted_responses[self.GITHUB_QUERY_INDEX], "query")

            # 解析GitHub搜索参数 - 中文
            chinese_github_query = self._extract_tag(extracted_responses[2], "query")

            # 构建GitHub参数
            github_params = {
                "query": english_github_query,
                "chinese_query": chinese_github_query,
                "sort": "stars",  # 默认按星标排序
                "order": "desc",  # 默认降序
                "per_page": 30,   # 默认每页30条
                "page": 1         # 默认第1页
            }

            # 检查是否为特定仓库查询
            repo_id = ""
            if "repo:" in english_github_query or "repository:" in english_github_query:
                repo_match = re.search(r'(repo|repository):([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)', english_github_query)
                if repo_match:
                    repo_id = repo_match.group(2)

            print(f"Debug - 提取的信息:")
            print(f"查询类型: {query_type}")
            print(f"主题: {main_topic}")
            print(f"子主题: {sub_topics}")
            print(f"语言: {language}")
            print(f"最低星标数: {min_stars}")
            print(f"英文GitHub参数: {english_github_query}")
            print(f"中文GitHub参数: {chinese_github_query}")
            print(f"特定仓库: {repo_id}")

            # 更新返回的 SearchCriteria，包含中英文查询
            return SearchCriteria(
                query_type=query_type,
                main_topic=main_topic,
                sub_topics=sub_topics,
                language=language,
                min_stars=min_stars,
                github_params=github_params,
                original_query=query,
                repo_id=repo_id
            )

        except Exception as e:
            raise Exception(f"分析查询失败: {str(e)}")

    def _normalize_query_type(self, query_type: str, query: str) -> str:
        """规范化查询类型"""
        if query_type in ["repo", "code", "user", "topic"]:
            return query_type

        query_lower = query.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return type_name

        query_type_lower = query_type.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_type_lower:
                    return type_name

        return "repo"  # 默认返回repo类型

    def _extract_tag(self, text: str, tag: str) -> str:
        """提取标记内容"""
        if not text:
            return ""

        # 标准XML格式（处理多行和特殊字符）
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # 备用模式
        patterns = [
            rf"<{tag}>\s*([\s\S]*?)\s*</{tag}>",  # 标准XML格式
            rf"<{tag}>([\s\S]*?)(?:</{tag}>|$)",  # 未闭合的标签
            rf"[{tag}]([\s\S]*?)[/{tag}]",  # 方括号格式
            rf"{tag}:\s*(.*?)(?=\n\w|$)",  # 冒号格式
            rf"<{tag}>\s*(.*?)(?=<|$)"  # 部分闭合
        ]

        # 尝试所有模式
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:  # 确保提取的内容不为空
                    return content

        # 如果所有模式都失败，返回空字符串
        return ""

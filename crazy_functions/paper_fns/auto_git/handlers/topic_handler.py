from typing import List, Dict, Any
from .base_handler import BaseHandler
from ..query_analyzer import SearchCriteria
import asyncio

class TopicHandler(BaseHandler):
    """主题搜索处理器"""

    def __init__(self, github, llm_kwargs=None):
        super().__init__(github, llm_kwargs)

    async def handle(
        self,
        criteria: SearchCriteria,
        chatbot: List[List[str]],
        history: List[List[str]],
        system_prompt: str,
        llm_kwargs: Dict[str, Any],
        plugin_kwargs: Dict[str, Any],
    ) -> str:
        """处理主题搜索请求，返回最终的prompt"""

        search_params = self._get_search_params(plugin_kwargs)

        # 搜索主题
        topics = await self._search_bilingual_topics(
            english_query=criteria.github_params["query"],
            chinese_query=criteria.github_params["chinese_query"],
            per_page=search_params['max_repos']
        )

        if not topics:
            # 尝试用主题搜索仓库
            search_query = criteria.github_params["query"]
            chinese_search_query = criteria.github_params["chinese_query"]
            if "topic:" not in search_query:
                search_query += " topic:" + criteria.main_topic.replace(" ", "-")
            if "topic:" not in chinese_search_query:
                chinese_search_query += " topic:" + criteria.main_topic.replace(" ", "-")

            repos = await self._search_bilingual_repositories(
                english_query=search_query,
                chinese_query=chinese_search_query,
                language=criteria.language,
                min_stars=criteria.min_stars,
                per_page=search_params['max_repos']
            )

            if not repos:
                return self._generate_apology_prompt(criteria)

            # 获取仓库详情
            enhanced_repos = await self._get_repo_details(repos[:10])
            self.ranked_repos = enhanced_repos

            if not enhanced_repos:
                return self._generate_apology_prompt(criteria)

            # 构建基于主题的仓库列表prompt
            current_time = self._get_current_time()
            final_prompt = f"""当前时间: {current_time}

基于用户对主题"{criteria.main_topic}"的查询，我找到了以下相关GitHub仓库。

主题相关仓库:
{self._format_repos(enhanced_repos)}

请提供:

1. 主题综述:
   - "{criteria.main_topic}"主题的概述和重要性
   - 该主题在技术领域中的应用和发展趋势
   - 主题相关的主要技术栈和知识体系

2. 仓库分析:
   - 按功能、技术栈或应用场景对仓库进行分类
   - 每个仓库在该主题领域的定位和贡献
   - 不同仓库间的技术路线对比

3. 学习路径建议:
   - 初学者入门该主题的推荐仓库和学习顺序
   - 进阶学习的关键仓库和技术要点
   - 实际应用中的最佳实践选择

4. 技术生态分析:
   - 该主题下的主流工具和库
   - 社区活跃度和维护状况
   - 与其他相关技术的集成方案

重要提示:
- 主题"{criteria.main_topic}"是用户查询的核心，请围绕此主题展开分析
- 注重仓库质量评估和使用建议
- 提供基于事实的客观技术分析
- 在介绍仓库时使用<a href='链接地址' target='_blank'>链接文本</a>格式，确保链接在新窗口打开
- 考虑不同技术水平用户的需求

使用markdown格式提供清晰的分节回复。
"""
            return final_prompt

        # 如果找到了主题，则获取主题下的热门仓库
        topic_repos = []
        for topic in topics[:5]:  # 增加到5个主题
            topic_name = topic.get('name', '')
            if topic_name:
                # 搜索该主题下的仓库
                repos = await self._search_repositories(
                    query=f"topic:{topic_name}",
                    language=criteria.language,
                    min_stars=criteria.min_stars,
                    per_page=20  # 每个主题最多20个仓库
                )

                if repos:
                    for repo in repos:
                        repo['topic_source'] = topic_name
                        topic_repos.append(repo)

        if not topic_repos:
            return self._generate_apology_prompt(criteria)

        # 获取前N个仓库的详情
        enhanced_repos = await self._get_repo_details(topic_repos[:search_params['max_details']])
        self.ranked_repos = enhanced_repos

        if not enhanced_repos:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = f"""当前时间: {current_time}

基于用户对"{criteria.main_topic}"主题的查询，我找到了以下相关GitHub主题和仓库。

主题相关仓库:
{self._format_topic_repos(enhanced_repos)}

请提供:

1. 主题概述:
   - 对"{criteria.main_topic}"相关主题的介绍和技术背景
   - 这些主题在软件开发中的重要性和应用范围
   - 主题间的关联性和技术演进路径

2. 精选仓库分析:
   - 每个主题下最具代表性的仓库详解
   - 仓库的技术亮点和创新点
   - 使用场景和技术成熟度评估

3. 技术趋势分析:
   - 基于主题和仓库活跃度的技术发展趋势
   - 新兴解决方案和传统方案的对比
   - 未来可能的技术方向预测

4. 实践建议:
   - 不同应用场景下的最佳仓库选择
   - 学习路径和资源推荐
   - 实际项目中的应用策略

重要提示:
- 将分析重点放在主题的技术内涵和价值上
- 突出主题间的关联性和技术演进脉络
- 提供基于数据(星标数、更新频率等)的客观分析
- 考虑不同技术背景用户的需求
- 所有链接请使用<a href='链接地址' target='_blank'>链接文本</a>格式，确保链接在新窗口打开

使用markdown格式提供清晰的分节回复。
"""

        return final_prompt

    def _format_topic_repos(self, repos: List[Dict]) -> str:
        """按主题格式化仓库列表"""
        # 按主题分组
        topics_dict = {}
        for repo in repos:
            topic = repo.get('topic_source', '其他')
            if topic not in topics_dict:
                topics_dict[topic] = []
            topics_dict[topic].append(repo)

        # 格式化输出
        formatted = []
        for topic, topic_repos in topics_dict.items():
            formatted.append(f"## 主题: {topic}\n")

            for i, repo in enumerate(topic_repos, 1):
                # 构建仓库URL
                repo_url = repo.get('html_url', '')

                # 构建引用
                reference = (
                    f"{i}. **{repo.get('full_name', '')}**\n"
                    f"   - 描述: {repo.get('description', 'N/A')}\n"
                    f"   - 语言: {repo.get('language', 'N/A')}\n"
                    f"   - 星标: {repo.get('stargazers_count', 0)}\n"
                    f"   - Fork数: {repo.get('forks_count', 0)}\n"
                    f"   - 更新时间: {repo.get('updated_at', 'N/A')[:10]}\n"
                    f"   - URL: <a href='{repo_url}' target='_blank'>{repo_url}</a>\n"
                )

                # 添加主题标签(如果有)
                if repo.get('topics'):
                    topics_str = ", ".join(repo.get('topics'))
                    reference += f"   - 主题标签: {topics_str}\n"

                # 添加README摘要(如果有)
                if repo.get('readme_excerpt'):
                    # 截断README，只取前200个字符
                    readme_short = repo.get('readme_excerpt')[:200].replace('\n', ' ')
                    reference += f"   - README摘要: {readme_short}...\n"

                formatted.append(reference)

            formatted.append("\n")  # 主题之间添加空行

        return "\n".join(formatted)

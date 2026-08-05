from typing import List, Dict, Any
from .base_handler import BaseHandler
from ..query_analyzer import SearchCriteria
import asyncio

class CodeSearchHandler(BaseHandler):
    """代码搜索处理器"""

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
        """处理代码搜索请求，返回最终的prompt"""

        search_params = self._get_search_params(plugin_kwargs)

        # 搜索代码
        code_results = await self._search_bilingual_code(
            english_query=criteria.github_params["query"],
            chinese_query=criteria.github_params["chinese_query"],
            language=criteria.language,
            per_page=search_params['max_repos']
        )

        if not code_results:
            return self._generate_apology_prompt(criteria)

        # 获取代码文件内容
        enhanced_code_results = await self._get_code_details(code_results[:search_params['max_details']])
        self.ranked_repos = [item["repository"] for item in enhanced_code_results if "repository" in item]

        if not enhanced_code_results:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = f"""当前时间: {current_time}

基于用户对{criteria.main_topic}的查询，我找到了以下代码示例。

代码搜索结果:
{self._format_code_results(enhanced_code_results)}

请提供:

1. 对于搜索的"{criteria.main_topic}"主题的综合解释:
   - 概念和原理介绍
   - 常见实现方法和技术
   - 最佳实践和注意事项

2. 对每个代码示例:
   - 解释代码的主要功能和实现方式
   - 分析代码质量、可读性和效率
   - 指出代码中的亮点和潜在改进空间
   - 说明代码的适用场景

3. 代码实现比较:
   - 不同实现方法的优缺点
   - 性能和可维护性分析
   - 适用不同场景的实现建议

4. 学习建议:
   - 理解和使用这些代码需要的背景知识
   - 如何扩展或改进所展示的代码
   - 进一步学习相关技术的资源

重要提示:
- 深入解释代码的核心逻辑和实现思路
- 提供专业、技术性的分析
- 优先关注代码的实现质量和技术价值
- 当代码实现有问题时，指出并提供改进建议
- 对于复杂代码，分解解释其组成部分
- 根据用户查询的具体问题提供针对性答案
- 所有链接请使用<a href='链接地址' target='_blank'>链接文本</a>格式，确保链接在新窗口打开

使用markdown格式提供清晰的分节回复。
"""

        return final_prompt

    async def _get_code_details(self, code_results: List[Dict]) -> List[Dict]:
        """获取代码详情"""
        enhanced_results = []

        for item in code_results:
            try:
                repo = item.get('repository', {})
                file_path = item.get('path', '')
                repo_name = repo.get('full_name', '')

                if repo_name and file_path:
                    owner, repo_name = repo_name.split('/')

                    # 获取文件内容
                    file_content = await self.github.get_file_content(owner, repo_name, file_path)
                    if file_content and "decoded_content" in file_content:
                        item['code_content'] = file_content["decoded_content"]

                        # 获取仓库基本信息
                        repo_details = await self.github.get_repo(owner, repo_name)
                        if repo_details:
                            item['repository'] = repo_details

                enhanced_results.append(item)
            except Exception as e:
                print(f"获取代码详情时出错: {str(e)}")
                enhanced_results.append(item)  # 添加原始信息

        return enhanced_results

    def _format_code_results(self, code_results: List[Dict]) -> str:
        """格式化代码搜索结果"""
        formatted = []

        for i, item in enumerate(code_results, 1):
            # 构建仓库信息
            repo = item.get('repository', {})
            repo_name = repo.get('full_name', 'N/A')
            repo_url = repo.get('html_url', '')
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language', 'N/A')

            # 构建文件信息
            file_path = item.get('path', 'N/A')
            file_url = item.get('html_url', '')

            # 构建代码内容
            code_content = item.get('code_content', '')
            if code_content:
                # 只显示前30行代码
                code_lines = code_content.split("\n")
                if len(code_lines) > 30:
                    displayed_code = "\n".join(code_lines[:30]) + "\n... (代码太长已截断) ..."
                else:
                    displayed_code = code_content
            else:
                displayed_code = "(代码内容获取失败)"

            reference = (
                f"### {i}. {file_path} (在 {repo_name} 中)\n\n"
                f"- **仓库**: <a href='{repo_url}' target='_blank'>{repo_name}</a> (⭐ {stars}, 语言: {language})\n"
                f"- **文件路径**: <a href='{file_url}' target='_blank'>{file_path}</a>\n\n"
                f"```{language.lower()}\n{displayed_code}\n```\n\n"
            )

            formatted.append(reference)

        return "\n".join(formatted)

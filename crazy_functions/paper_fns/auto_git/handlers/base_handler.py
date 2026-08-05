from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..query_analyzer import SearchCriteria
from ..sources.github_source import GitHubSource
import asyncio
import re
from datetime import datetime

class BaseHandler(ABC):
    """处理器基类"""

    def __init__(self, github: GitHubSource, llm_kwargs: Dict = None):
        self.github = github
        self.llm_kwargs = llm_kwargs or {}
        self.ranked_repos = []  # 存储排序后的仓库列表

    def _get_search_params(self, plugin_kwargs: Dict) -> Dict:
        """获取搜索参数"""
        return {
            'max_repos': plugin_kwargs.get('max_repos', 150),  # 最大仓库数量，从30改为150
            'max_details': plugin_kwargs.get('max_details', 80),  # 最多展示详情的仓库数量，新增参数
            'search_multiplier': plugin_kwargs.get('search_multiplier', 3),  # 检索倍数
            'min_stars': plugin_kwargs.get('min_stars', 0),  # 最少星标数
        }

    @abstractmethod
    async def handle(
            self,
            criteria: SearchCriteria,
            chatbot: List[List[str]],
            history: List[List[str]],
            system_prompt: str,
            llm_kwargs: Dict[str, Any],
            plugin_kwargs: Dict[str, Any],
    ) -> str:
        """处理查询"""
        pass

    async def _search_repositories(self, query: str, language: str = None, min_stars: int = 0,
                                sort: str = "stars", per_page: int = 30) -> List[Dict]:
        """搜索仓库"""
        try:
            # 构建查询字符串
            if min_stars > 0 and "stars:>" not in query:
                query += f" stars:>{min_stars}"

            if language and "language:" not in query:
                query += f" language:{language}"

            # 执行搜索
            result = await self.github.search_repositories(
                query=query,
                sort=sort,
                per_page=per_page
            )

            if result and "items" in result:
                return result["items"]
            return []
        except Exception as e:
            print(f"仓库搜索出错: {str(e)}")
            return []

    async def _search_bilingual_repositories(self, english_query: str, chinese_query: str, language: str = None, min_stars: int = 0,
                                sort: str = "stars", per_page: int = 30) -> List[Dict]:
        """同时搜索中英文仓库并合并结果"""
        try:
            # 搜索英文仓库
            english_results = await self._search_repositories(
                query=english_query,
                language=language,
                min_stars=min_stars,
                sort=sort,
                per_page=per_page
            )

            # 搜索中文仓库
            chinese_results = await self._search_repositories(
                query=chinese_query,
                language=language,
                min_stars=min_stars,
                sort=sort,
                per_page=per_page
            )

            # 合并结果，去除重复项
            merged_results = []
            seen_repos = set()

            # 优先添加英文结果
            for repo in english_results:
                repo_id = repo.get('id')
                if repo_id and repo_id not in seen_repos:
                    seen_repos.add(repo_id)
                    merged_results.append(repo)

            # 添加中文结果（排除重复）
            for repo in chinese_results:
                repo_id = repo.get('id')
                if repo_id and repo_id not in seen_repos:
                    seen_repos.add(repo_id)
                    merged_results.append(repo)

            # 按星标数重新排序
            merged_results.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)

            return merged_results[:per_page]  # 返回合并后的前per_page个结果
        except Exception as e:
            print(f"双语仓库搜索出错: {str(e)}")
            return []

    async def _search_code(self, query: str, language: str = None, per_page: int = 30) -> List[Dict]:
        """搜索代码"""
        try:
            # 构建查询字符串
            if language and "language:" not in query:
                query += f" language:{language}"

            # 执行搜索
            result = await self.github.search_code(
                query=query,
                per_page=per_page
            )

            if result and "items" in result:
                return result["items"]
            return []
        except Exception as e:
            print(f"代码搜索出错: {str(e)}")
            return []

    async def _search_bilingual_code(self, english_query: str, chinese_query: str, language: str = None, per_page: int = 30) -> List[Dict]:
        """同时搜索中英文代码并合并结果"""
        try:
            # 搜索英文代码
            english_results = await self._search_code(
                query=english_query,
                language=language,
                per_page=per_page
            )

            # 搜索中文代码
            chinese_results = await self._search_code(
                query=chinese_query,
                language=language,
                per_page=per_page
            )

            # 合并结果，去除重复项
            merged_results = []
            seen_files = set()

            # 优先添加英文结果
            for item in english_results:
                # 使用文件URL作为唯一标识
                file_url = item.get('html_url', '')
                if file_url and file_url not in seen_files:
                    seen_files.add(file_url)
                    merged_results.append(item)

            # 添加中文结果（排除重复）
            for item in chinese_results:
                file_url = item.get('html_url', '')
                if file_url and file_url not in seen_files:
                    seen_files.add(file_url)
                    merged_results.append(item)

            # 对结果进行排序，优先显示匹配度高的结果
            # 由于无法直接获取匹配度，这里使用仓库的星标数作为替代指标
            merged_results.sort(key=lambda x: x.get('repository', {}).get('stargazers_count', 0), reverse=True)

            return merged_results[:per_page]  # 返回合并后的前per_page个结果
        except Exception as e:
            print(f"双语代码搜索出错: {str(e)}")
            return []

    async def _search_users(self, query: str, per_page: int = 30) -> List[Dict]:
        """搜索用户"""
        try:
            result = await self.github.search_users(
                query=query,
                per_page=per_page
            )

            if result and "items" in result:
                return result["items"]
            return []
        except Exception as e:
            print(f"用户搜索出错: {str(e)}")
            return []

    async def _search_bilingual_users(self, english_query: str, chinese_query: str, per_page: int = 30) -> List[Dict]:
        """同时搜索中英文用户并合并结果"""
        try:
            # 搜索英文用户
            english_results = await self._search_users(
                query=english_query,
                per_page=per_page
            )

            # 搜索中文用户
            chinese_results = await self._search_users(
                query=chinese_query,
                per_page=per_page
            )

            # 合并结果，去除重复项
            merged_results = []
            seen_users = set()

            # 优先添加英文结果
            for user in english_results:
                user_id = user.get('id')
                if user_id and user_id not in seen_users:
                    seen_users.add(user_id)
                    merged_results.append(user)

            # 添加中文结果（排除重复）
            for user in chinese_results:
                user_id = user.get('id')
                if user_id and user_id not in seen_users:
                    seen_users.add(user_id)
                    merged_results.append(user)

            # 按关注者数量进行排序
            merged_results.sort(key=lambda x: x.get('followers', 0), reverse=True)

            return merged_results[:per_page]  # 返回合并后的前per_page个结果
        except Exception as e:
            print(f"双语用户搜索出错: {str(e)}")
            return []

    async def _search_topics(self, query: str, per_page: int = 30) -> List[Dict]:
        """搜索主题"""
        try:
            result = await self.github.search_topics(
                query=query,
                per_page=per_page
            )

            if result and "items" in result:
                return result["items"]
            return []
        except Exception as e:
            print(f"主题搜索出错: {str(e)}")
            return []

    async def _search_bilingual_topics(self, english_query: str, chinese_query: str, per_page: int = 30) -> List[Dict]:
        """同时搜索中英文主题并合并结果"""
        try:
            # 搜索英文主题
            english_results = await self._search_topics(
                query=english_query,
                per_page=per_page
            )

            # 搜索中文主题
            chinese_results = await self._search_topics(
                query=chinese_query,
                per_page=per_page
            )

            # 合并结果，去除重复项
            merged_results = []
            seen_topics = set()

            # 优先添加英文结果
            for topic in english_results:
                topic_name = topic.get('name')
                if topic_name and topic_name not in seen_topics:
                    seen_topics.add(topic_name)
                    merged_results.append(topic)

            # 添加中文结果（排除重复）
            for topic in chinese_results:
                topic_name = topic.get('name')
                if topic_name and topic_name not in seen_topics:
                    seen_topics.add(topic_name)
                    merged_results.append(topic)

            # 可以按流行度进行排序（如果有）
            if merged_results and 'featured' in merged_results[0]:
                merged_results.sort(key=lambda x: x.get('featured', False), reverse=True)

            return merged_results[:per_page]  # 返回合并后的前per_page个结果
        except Exception as e:
            print(f"双语主题搜索出错: {str(e)}")
            return []

    async def _get_repo_details(self, repos: List[Dict]) -> List[Dict]:
        """获取仓库详细信息"""
        enhanced_repos = []

        for repo in repos:
            try:
                # 获取README信息
                owner = repo.get('owner', {}).get('login') if repo.get('owner') is not None else None
                repo_name = repo.get('name')

                if owner and repo_name:
                    readme = await self.github.get_repo_readme(owner, repo_name)
                    if readme and "decoded_content" in readme:
                        # 提取README的前1000个字符作为摘要
                        repo['readme_excerpt'] = readme["decoded_content"][:1000] + "..."

                    # 获取语言使用情况
                    languages = await self.github.get_repository_languages(owner, repo_name)
                    if languages:
                        repo['languages_detail'] = languages

                    # 获取最新发布版本
                    releases = await self.github.get_repo_releases(owner, repo_name, per_page=1)
                    if releases and len(releases) > 0:
                        repo['latest_release'] = releases[0]

                    # 获取主题标签
                    topics = await self.github.get_repo_topics(owner, repo_name)
                    if topics and "names" in topics:
                        repo['topics'] = topics["names"]

                enhanced_repos.append(repo)
            except Exception as e:
                print(f"获取仓库 {repo.get('full_name')} 详情时出错: {str(e)}")
                enhanced_repos.append(repo)  # 添加原始仓库信息

        return enhanced_repos

    def _format_repos(self, repos: List[Dict]) -> str:
        """格式化仓库列表"""
        formatted = []

        for i, repo in enumerate(repos, 1):
            # 构建仓库URL
            repo_url = repo.get('html_url', '')

            # 构建完整的引用
            reference = (
                f"{i}. **{repo.get('full_name', '')}**\n"
                f"   - 描述: {repo.get('description', 'N/A')}\n"
                f"   - 语言: {repo.get('language', 'N/A')}\n"
                f"   - 星标: {repo.get('stargazers_count', 0)}\n"
                f"   - Fork数: {repo.get('forks_count', 0)}\n"
                f"   - 更新时间: {repo.get('updated_at', 'N/A')[:10]}\n"
                f"   - 创建时间: {repo.get('created_at', 'N/A')[:10]}\n"
                f"   - URL: <a href='{repo_url}' target='_blank'>{repo_url}</a>\n"
            )

            # 添加主题标签(如果有)
            if repo.get('topics'):
                topics_str = ", ".join(repo.get('topics'))
                reference += f"   - 主题标签: {topics_str}\n"

            # 添加最新发布版本(如果有)
            if repo.get('latest_release'):
                release = repo.get('latest_release')
                reference += f"   - 最新版本: {release.get('tag_name', 'N/A')} ({release.get('published_at', 'N/A')[:10]})\n"

            # 添加README摘要(如果有)
            if repo.get('readme_excerpt'):
                # 截断README，只取前300个字符
                readme_short = repo.get('readme_excerpt')[:300].replace('\n', ' ')
                reference += f"   - README摘要: {readme_short}...\n"

            formatted.append(reference)

        return "\n".join(formatted)

    def _generate_apology_prompt(self, criteria: SearchCriteria) -> str:
        """生成道歉提示"""
        return f"""很抱歉，我们未能找到与"{criteria.main_topic}"相关的GitHub项目。

可能的原因：
1. 搜索词过于具体或冷门
2. 星标数要求过高
3. 编程语言限制过于严格

建议解决方案：
   1. 尝试使用更通用的关键词
   2. 降低最低星标数要求
   3. 移除或更改编程语言限制
请根据以上建议调整后重试。"""

    def _get_current_time(self) -> str:
        """获取当前时间信息"""
        now = datetime.now()
        return now.strftime("%Y年%m月%d日")

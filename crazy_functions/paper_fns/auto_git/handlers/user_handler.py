from typing import List, Dict, Any
from .base_handler import BaseHandler
from ..query_analyzer import SearchCriteria
import asyncio

class UserSearchHandler(BaseHandler):
    """用户搜索处理器"""

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
        """处理用户搜索请求，返回最终的prompt"""

        search_params = self._get_search_params(plugin_kwargs)

        # 搜索用户
        users = await self._search_bilingual_users(
            english_query=criteria.github_params["query"],
            chinese_query=criteria.github_params["chinese_query"],
            per_page=search_params['max_repos']
        )

        if not users:
            return self._generate_apology_prompt(criteria)

        # 获取用户详情和仓库
        enhanced_users = await self._get_user_details(users[:search_params['max_details']])
        self.ranked_repos = []  # 添加用户top仓库进行展示

        for user in enhanced_users:
            if user.get('top_repos'):
                self.ranked_repos.extend(user.get('top_repos'))

        if not enhanced_users:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = f"""当前时间: {current_time}

基于用户对{criteria.main_topic}的查询，我找到了以下GitHub用户。

GitHub用户搜索结果:
{self._format_users(enhanced_users)}

请提供:

1. 用户综合分析:
   - 各开发者的专业领域和技术专长
   - 他们在GitHub开源社区的影响力
   - 技术实力和项目质量评估

2. 对每位开发者:
   - 其主要贡献领域和技术栈
   - 代表性项目及其价值
   - 编程风格和技术特点
   - 在相关领域的影响力

3. 项目推荐:
   - 针对用户查询的最有价值项目
   - 值得学习和借鉴的代码实践
   - 不同用户项目的相互补充关系

4. 如何学习和使用:
   - 如何从这些开发者项目中学习
   - 最适合入门学习的项目
   - 进阶学习的路径建议

重要提示:
- 关注开发者的技术专长和核心贡献
- 分析其开源项目的技术价值
- 根据用户的原始查询提供相关建议
- 避免过度赞美或主观评价
- 基于事实数据(项目数、星标数等)进行客观分析
- 所有链接请使用<a href='链接地址' target='_blank'>链接文本</a>格式，确保链接在新窗口打开

使用markdown格式提供清晰的分节回复。
"""

        return final_prompt

    async def _get_user_details(self, users: List[Dict]) -> List[Dict]:
        """获取用户详情和仓库"""
        enhanced_users = []

        for user in users:
            try:
                username = user.get('login')

                if username:
                    # 获取用户详情
                    user_details = await self.github.get_user(username)
                    if user_details:
                        user.update(user_details)

                    # 获取用户仓库
                    repos = await self.github.get_user_repos(
                        username,
                        sort="stars",
                        per_page=10  # 增加到10个仓库
                    )
                    if repos:
                        user['top_repos'] = repos

                enhanced_users.append(user)
            except Exception as e:
                print(f"获取用户 {user.get('login')} 详情时出错: {str(e)}")
                enhanced_users.append(user)  # 添加原始信息

        return enhanced_users

    def _format_users(self, users: List[Dict]) -> str:
        """格式化用户列表"""
        formatted = []

        for i, user in enumerate(users, 1):
            # 构建用户信息
            username = user.get('login', 'N/A')
            name = user.get('name', username)
            profile_url = user.get('html_url', '')
            bio = user.get('bio', '无简介')
            followers = user.get('followers', 0)
            public_repos = user.get('public_repos', 0)
            company = user.get('company', '未指定')
            location = user.get('location', '未指定')
            blog = user.get('blog', '')

            user_info = (
                f"### {i}. {name} (@{username})\n\n"
                f"- **简介**: {bio}\n"
                f"- **关注者**: {followers} | **公开仓库**: {public_repos}\n"
                f"- **公司**: {company} | **地点**: {location}\n"
                f"- **个人网站**: {blog}\n"
                f"- **GitHub**: <a href='{profile_url}' target='_blank'>{username}</a>\n\n"
            )

            # 添加用户的热门仓库
            top_repos = user.get('top_repos', [])
            if top_repos:
                user_info += "**热门仓库**:\n\n"
                for repo in top_repos:
                    repo_name = repo.get('name', '')
                    repo_url = repo.get('html_url', '')
                    repo_desc = repo.get('description', '无描述')
                    repo_stars = repo.get('stargazers_count', 0)
                    repo_language = repo.get('language', '未指定')

                    user_info += (
                        f"- <a href='{repo_url}' target='_blank'>{repo_name}</a> - ⭐ {repo_stars}, {repo_language}\n"
                        f"  {repo_desc}\n\n"
                    )

            formatted.append(user_info)

        return "\n".join(formatted)

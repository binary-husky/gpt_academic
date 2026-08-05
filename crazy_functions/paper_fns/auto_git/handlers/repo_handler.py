from typing import List, Dict, Any
from .base_handler import BaseHandler
from ..query_analyzer import SearchCriteria
import asyncio

class RepositoryHandler(BaseHandler):
    """仓库搜索处理器"""

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
        """处理仓库搜索请求，返回最终的prompt"""

        search_params = self._get_search_params(plugin_kwargs)

        # 如果是特定仓库查询
        if criteria.repo_id:
            try:
                owner, repo = criteria.repo_id.split('/')
                repo_details = await self.github.get_repo(owner, repo)
                if repo_details:
                    # 获取推荐的相似仓库
                    similar_repos = await self.github.get_repo_recommendations(criteria.repo_id, limit=5)

                    # 添加详细信息
                    all_repos = [repo_details] + similar_repos
                    enhanced_repos = await self._get_repo_details(all_repos)

                    self.ranked_repos = enhanced_repos

                    # 构建最终的prompt
                    current_time = self._get_current_time()
                    final_prompt = self._build_repo_detail_prompt(enhanced_repos[0], enhanced_repos[1:], current_time)
                    return final_prompt
                else:
                    return self._generate_apology_prompt(criteria)
            except Exception as e:
                print(f"处理特定仓库时出错: {str(e)}")
                return self._generate_apology_prompt(criteria)

        # 一般仓库搜索
        repos = await self._search_bilingual_repositories(
            english_query=criteria.github_params["query"],
            chinese_query=criteria.github_params["chinese_query"],
            language=criteria.language,
            min_stars=criteria.min_stars,
            per_page=search_params['max_repos']
        )

        if not repos:
            return self._generate_apology_prompt(criteria)

        # 获取仓库详情
        enhanced_repos = await self._get_repo_details(repos[:search_params['max_details']])  # 使用max_details参数
        self.ranked_repos = enhanced_repos

        if not enhanced_repos:
            return self._generate_apology_prompt(criteria)

        # 构建最终的prompt
        current_time = self._get_current_time()
        final_prompt = f"""当前时间: {current_time}

基于用户对{criteria.main_topic}的兴趣，以下是相关的GitHub仓库。

可供推荐的GitHub仓库:
{self._format_repos(enhanced_repos)}

请提供:
1. 按功能、用途或成熟度对仓库进行分组

2. 对每个仓库：
   - 简要描述其主要功能和用途
   - 分析其技术特点和优势
   - 说明其适用场景和使用难度
   - 指出其与同类产品相比的独特优势
   - 解释其星标数量和活跃度代表的意义

3. 使用建议：
   - 新手最适合入门的仓库
   - 生产环境中最稳定可靠的选择
   - 最新技术栈或创新方案的代表
   - 学习特定技术的最佳资源

4. 相关资源：
   - 学习这些项目需要的前置知识
   - 项目间的关联和技术栈兼容性
   - 可能的使用组合方案

重要提示:
- 重点解释为什么每个仓库值得关注
- 突出项目间的关联性和差异性
- 考虑用户不同水平的需求(初学者vs专业人士)
- 在介绍项目时，使用<a href='链接' target='_blank'>文本</a>格式，确保链接在新窗口打开
- 根据仓库的活跃度、更新频率、维护状态提供使用建议
- 仅基于提供的信息，不要做无根据的猜测
- 在信息缺失或不明确时，坦诚说明

使用markdown格式提供清晰的分节回复。
"""

        return final_prompt

    def _build_repo_detail_prompt(self, main_repo: Dict, similar_repos: List[Dict], current_time: str) -> str:
        """构建仓库详情prompt"""

        # 提取README摘要
        readme_content = "未提供"
        if main_repo.get('readme_excerpt'):
            readme_content = main_repo.get('readme_excerpt')

        # 构建语言分布
        languages = main_repo.get('languages_detail', {})
        lang_distribution = []
        if languages:
            total = sum(languages.values())
            for lang, bytes_val in languages.items():
                percentage = (bytes_val / total) * 100
                lang_distribution.append(f"{lang}: {percentage:.1f}%")

        lang_str = "未知"
        if lang_distribution:
            lang_str = ", ".join(lang_distribution)

        # 构建最终prompt
        prompt = f"""当前时间: {current_time}

## 主要仓库信息

### {main_repo.get('full_name')}

- **描述**: {main_repo.get('description', '未提供')}
- **星标数**: {main_repo.get('stargazers_count', 0)}
- **Fork数**: {main_repo.get('forks_count', 0)}
- **Watch数**: {main_repo.get('watchers_count', 0)}
- **Issues数**: {main_repo.get('open_issues_count', 0)}
- **语言分布**: {lang_str}
- **许可证**: {main_repo.get('license', {}).get('name', '未指定') if main_repo.get('license') is not None else '未指定'}
- **创建时间**: {main_repo.get('created_at', '')[:10]}
- **最近更新**: {main_repo.get('updated_at', '')[:10]}
- **主题标签**: {', '.join(main_repo.get('topics', ['无']))}
- **GitHub链接**: <a href='{main_repo.get('html_url')}' target='_blank'>链接</a>

### README摘要:
{readme_content}

## 类似仓库:
{self._format_repos(similar_repos)}

请提供以下内容:

1. **项目概述**
   - 详细解释{main_repo.get('name', '')}项目的主要功能和用途
   - 分析其技术特点、架构和实现原理
   - 讨论其在所属领域的地位和影响力
   - 评估项目成熟度和稳定性

2. **优势与特点**
   - 与同类项目相比的独特优势
   - 显著的技术创新或设计模式
   - 值得学习或借鉴的代码实践

3. **使用场景**
   - 最适合的应用场景
   - 潜在的使用限制和注意事项
   - 入门门槛和学习曲线评估
   - 产品级应用的可行性分析

4. **资源与生态**
   - 相关学习资源推荐
   - 配套工具和库的建议
   - 社区支持和活跃度评估

5. **类似项目对比**
   - 与列出的类似项目的详细对比
   - 不同场景下的最佳选择建议
   - 潜在的互补使用方案

提示：所有链接请使用<a href='链接地址' target='_blank'>链接文本</a>格式，确保链接在新窗口打开。

请以专业、客观的技术分析角度回答，使用markdown格式提供结构化信息。
"""
        return prompt

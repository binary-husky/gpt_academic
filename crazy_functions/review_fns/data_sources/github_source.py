import aiohttp
import asyncio
import base64
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Union, Any

class GitHubSource:
    """GitHub API实现"""

    # 默认API密钥列表 - 可以放置多个GitHub令牌
    API_KEYS = [
        "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    ]

    def __init__(self, api_key: Optional[Union[str, List[str]]] = None):
        """初始化GitHub API客户端

        Args:
            api_key: GitHub个人访问令牌或令牌列表
        """
        if api_key is None:
            self.api_keys = self.API_KEYS
        elif isinstance(api_key, str):
            self.api_keys = [api_key]
        else:
            self.api_keys = api_key

        self._initialize()

    def _initialize(self) -> None:
        """初始化客户端，设置默认参数"""
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHub-API-Python-Client"
        }

        # 如果有可用的API密钥，随机选择一个
        if self.api_keys:
            selected_key = random.choice(self.api_keys)
            self.headers["Authorization"] = f"Bearer {selected_key}"
            print(f"已随机选择API密钥进行认证")
        else:
            print("警告: 未提供API密钥，将受到GitHub API请求限制")

    async def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Any:
        """发送API请求

        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            endpoint: API端点
            params: URL参数
            data: 请求体数据

        Returns:
            解析后的响应JSON
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{self.base_url}{endpoint}"

            # 为调试目的打印请求信息
            print(f"请求: {method} {url}")
            if params:
                print(f"参数: {params}")

            # 发送请求
            request_kwargs = {}
            if params:
                request_kwargs["params"] = params
            if data:
                request_kwargs["json"] = data

            async with session.request(method, url, **request_kwargs) as response:
                response_text = await response.text()

                # 检查HTTP状态码
                if response.status >= 400:
                    print(f"API请求失败: HTTP {response.status}")
                    print(f"响应内容: {response_text}")
                    return None

                # 解析JSON响应
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"JSON解析错误: {response_text}")
                    return None

    # ===== 用户相关方法 =====

    async def get_user(self, username: Optional[str] = None) -> Dict:
        """获取用户信息

        Args:
            username: 指定用户名，不指定则获取当前授权用户

        Returns:
            用户信息字典
        """
        endpoint = "/user" if username is None else f"/users/{username}"
        return await self._request("GET", endpoint)

    async def get_user_repos(self, username: Optional[str] = None, sort: str = "updated",
                            direction: str = "desc", per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取用户的仓库列表

        Args:
            username: 指定用户名，不指定则获取当前授权用户
            sort: 排序方式 (created, updated, pushed, full_name)
            direction: 排序方向 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            仓库列表
        """
        endpoint = "/user/repos" if username is None else f"/users/{username}/repos"
        params = {
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def get_user_starred(self, username: Optional[str] = None,
                              per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取用户星标的仓库

        Args:
            username: 指定用户名，不指定则获取当前授权用户
            per_page: 每页结果数量
            page: 页码

        Returns:
            星标仓库列表
        """
        endpoint = "/user/starred" if username is None else f"/users/{username}/starred"
        params = {
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    # ===== 仓库相关方法 =====

    async def get_repo(self, owner: str, repo: str) -> Dict:
        """获取仓库信息

        Args:
            owner: 仓库所有者
            repo: 仓库名

        Returns:
            仓库信息
        """
        endpoint = f"/repos/{owner}/{repo}"
        return await self._request("GET", endpoint)

    async def get_repo_branches(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取仓库的分支列表

        Args:
            owner: 仓库所有者
            repo: 仓库名
            per_page: 每页结果数量
            page: 页码

        Returns:
            分支列表
        """
        endpoint = f"/repos/{owner}/{repo}/branches"
        params = {
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def get_repo_commits(self, owner: str, repo: str, sha: Optional[str] = None,
                              path: Optional[str] = None, per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取仓库的提交历史

        Args:
            owner: 仓库所有者
            repo: 仓库名
            sha: 特定提交SHA或分支名
            path: 文件路径筛选
            per_page: 每页结果数量
            page: 页码

        Returns:
            提交列表
        """
        endpoint = f"/repos/{owner}/{repo}/commits"
        params = {
            "per_page": per_page,
            "page": page
        }
        if sha:
            params["sha"] = sha
        if path:
            params["path"] = path

        return await self._request("GET", endpoint, params=params)

    async def get_commit_details(self, owner: str, repo: str, commit_sha: str) -> Dict:
        """获取特定提交的详情

        Args:
            owner: 仓库所有者
            repo: 仓库名
            commit_sha: 提交SHA

        Returns:
            提交详情
        """
        endpoint = f"/repos/{owner}/{repo}/commits/{commit_sha}"
        return await self._request("GET", endpoint)

    # ===== 内容相关方法 =====

    async def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Dict:
        """获取文件内容

        Args:
            owner: 仓库所有者
            repo: 仓库名
            path: 文件路径
            ref: 分支名、标签名或提交SHA

        Returns:
            文件内容信息
        """
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {}
        if ref:
            params["ref"] = ref

        response = await self._request("GET", endpoint, params=params)
        if response and isinstance(response, dict) and "content" in response:
            try:
                # 解码Base64编码的文件内容
                content = base64.b64decode(response["content"].encode()).decode()
                response["decoded_content"] = content
            except Exception as e:
                print(f"解码文件内容时出错: {str(e)}")

        return response

    async def get_directory_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> List[Dict]:
        """获取目录内容

        Args:
            owner: 仓库所有者
            repo: 仓库名
            path: 目录路径
            ref: 分支名、标签名或提交SHA

        Returns:
            目录内容列表
        """
        # 注意：此方法与get_file_content使用相同的端点，但对于目录会返回列表
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {}
        if ref:
            params["ref"] = ref

        return await self._request("GET", endpoint, params=params)

    # ===== Issues相关方法 =====

    async def get_issues(self, owner: str, repo: str, state: str = "open",
                        sort: str = "created", direction: str = "desc",
                        per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取仓库的Issues列表

        Args:
            owner: 仓库所有者
            repo: 仓库名
            state: Issue状态 (open, closed, all)
            sort: 排序方式 (created, updated, comments)
            direction: 排序方向 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            Issues列表
        """
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """获取特定Issue的详情

        Args:
            owner: 仓库所有者
            repo: 仓库名
            issue_number: Issue编号

        Returns:
            Issue详情
        """
        endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}"
        return await self._request("GET", endpoint)

    async def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """获取Issue的评论

        Args:
            owner: 仓库所有者
            repo: 仓库名
            issue_number: Issue编号

        Returns:
            评论列表
        """
        endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
        return await self._request("GET", endpoint)

    # ===== Pull Requests相关方法 =====

    async def get_pull_requests(self, owner: str, repo: str, state: str = "open",
                               sort: str = "created", direction: str = "desc",
                               per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取仓库的Pull Request列表

        Args:
            owner: 仓库所有者
            repo: 仓库名
            state: PR状态 (open, closed, all)
            sort: 排序方式 (created, updated, popularity, long-running)
            direction: 排序方向 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            Pull Request列表
        """
        endpoint = f"/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict:
        """获取特定Pull Request的详情

        Args:
            owner: 仓库所有者
            repo: 仓库名
            pr_number: Pull Request编号

        Returns:
            Pull Request详情
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return await self._request("GET", endpoint)

    async def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """获取Pull Request中修改的文件

        Args:
            owner: 仓库所有者
            repo: 仓库名
            pr_number: Pull Request编号

        Returns:
            修改文件列表
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/files"
        return await self._request("GET", endpoint)

    # ===== 搜索相关方法 =====

    async def search_repositories(self, query: str, sort: str = "stars",
                                 order: str = "desc", per_page: int = 30, page: int = 1) -> Dict:
        """搜索仓库

        Args:
            query: 搜索关键词
            sort: 排序方式 (stars, forks, updated)
            order: 排序顺序 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            搜索结果
        """
        endpoint = "/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def search_code(self, query: str, sort: str = "indexed",
                         order: str = "desc", per_page: int = 30, page: int = 1) -> Dict:
        """搜索代码

        Args:
            query: 搜索关键词
            sort: 排序方式 (indexed)
            order: 排序顺序 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            搜索结果
        """
        endpoint = "/search/code"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def search_issues(self, query: str, sort: str = "created",
                           order: str = "desc", per_page: int = 30, page: int = 1) -> Dict:
        """搜索Issues和Pull Requests

        Args:
            query: 搜索关键词
            sort: 排序方式 (created, updated, comments)
            order: 排序顺序 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            搜索结果
        """
        endpoint = "/search/issues"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def search_users(self, query: str, sort: str = "followers",
                          order: str = "desc", per_page: int = 30, page: int = 1) -> Dict:
        """搜索用户

        Args:
            query: 搜索关键词
            sort: 排序方式 (followers, repositories, joined)
            order: 排序顺序 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            搜索结果
        """
        endpoint = "/search/users"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    # ===== 组织相关方法 =====

    async def get_organization(self, org: str) -> Dict:
        """获取组织信息

        Args:
            org: 组织名称

        Returns:
            组织信息
        """
        endpoint = f"/orgs/{org}"
        return await self._request("GET", endpoint)

    async def get_organization_repos(self, org: str, type: str = "all",
                                    sort: str = "created", direction: str = "desc",
                                    per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取组织的仓库列表

        Args:
            org: 组织名称
            type: 仓库类型 (all, public, private, forks, sources, member, internal)
            sort: 排序方式 (created, updated, pushed, full_name)
            direction: 排序方向 (asc, desc)
            per_page: 每页结果数量
            page: 页码

        Returns:
            仓库列表
        """
        endpoint = f"/orgs/{org}/repos"
        params = {
            "type": type,
            "sort": sort,
            "direction": direction,
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    async def get_organization_members(self, org: str, per_page: int = 30, page: int = 1) -> List[Dict]:
        """获取组织成员列表

        Args:
            org: 组织名称
            per_page: 每页结果数量
            page: 页码

        Returns:
            成员列表
        """
        endpoint = f"/orgs/{org}/members"
        params = {
            "per_page": per_page,
            "page": page
        }
        return await self._request("GET", endpoint, params=params)

    # ===== 更复杂的操作 =====

    async def get_repository_languages(self, owner: str, repo: str) -> Dict:
        """获取仓库使用的编程语言及其比例

        Args:
            owner: 仓库所有者
            repo: 仓库名

        Returns:
            语言使用情况
        """
        endpoint = f"/repos/{owner}/{repo}/languages"
        return await self._request("GET", endpoint)

    async def get_repository_stats_contributors(self, owner: str, repo: str) -> List[Dict]:
        """获取仓库的贡献者统计

        Args:
            owner: 仓库所有者
            repo: 仓库名

        Returns:
            贡献者统计信息
        """
        endpoint = f"/repos/{owner}/{repo}/stats/contributors"
        return await self._request("GET", endpoint)

    async def get_repository_stats_commit_activity(self, owner: str, repo: str) -> List[Dict]:
        """获取仓库的提交活动

        Args:
            owner: 仓库所有者
            repo: 仓库名

        Returns:
            提交活动统计
        """
        endpoint = f"/repos/{owner}/{repo}/stats/commit_activity"
        return await self._request("GET", endpoint)

async def example_usage():
    """GitHubSource使用示例"""
    # 创建客户端实例（可选传入API令牌）
    # github = GitHubSource(api_key="your_github_token")
    github = GitHubSource()

    try:
        # 示例1：搜索热门Python仓库
        print("\n=== 示例1：搜索热门Python仓库 ===")
        repos = await github.search_repositories(
            query="language:python stars:>1000",
            sort="stars",
            order="desc",
            per_page=5
        )

        if repos and "items" in repos:
            for i, repo in enumerate(repos["items"], 1):
                print(f"\n--- 仓库 {i} ---")
                print(f"名称: {repo['full_name']}")
                print(f"描述: {repo['description']}")
                print(f"星标数: {repo['stargazers_count']}")
                print(f"Fork数: {repo['forks_count']}")
                print(f"最近更新: {repo['updated_at']}")
                print(f"URL: {repo['html_url']}")

        # 示例2：获取特定仓库的详情
        print("\n=== 示例2：获取特定仓库的详情 ===")
        repo_details = await github.get_repo("microsoft", "vscode")
        if repo_details:
            print(f"名称: {repo_details['full_name']}")
            print(f"描述: {repo_details['description']}")
            print(f"星标数: {repo_details['stargazers_count']}")
            print(f"Fork数: {repo_details['forks_count']}")
            print(f"默认分支: {repo_details['default_branch']}")
            print(f"开源许可: {repo_details.get('license', {}).get('name', '无')}")
            print(f"语言: {repo_details['language']}")
            print(f"Open Issues数: {repo_details['open_issues_count']}")

        # 示例3：获取仓库的提交历史
        print("\n=== 示例3：获取仓库的最近提交 ===")
        commits = await github.get_repo_commits("tensorflow", "tensorflow", per_page=5)
        if commits:
            for i, commit in enumerate(commits, 1):
                print(f"\n--- 提交 {i} ---")
                print(f"SHA: {commit['sha'][:7]}")
                print(f"作者: {commit['commit']['author']['name']}")
                print(f"日期: {commit['commit']['author']['date']}")
                print(f"消息: {commit['commit']['message'].splitlines()[0]}")

        # 示例4：搜索代码
        print("\n=== 示例4：搜索代码 ===")
        code_results = await github.search_code(
            query="filename:README.md language:markdown pytorch in:file",
            per_page=3
        )
        if code_results and "items" in code_results:
            print(f"共找到: {code_results['total_count']} 个结果")
            for i, item in enumerate(code_results["items"], 1):
                print(f"\n--- 代码 {i} ---")
                print(f"仓库: {item['repository']['full_name']}")
                print(f"文件: {item['path']}")
                print(f"URL: {item['html_url']}")

        # 示例5：获取文件内容
        print("\n=== 示例5：获取文件内容 ===")
        file_content = await github.get_file_content("python", "cpython", "README.rst")
        if file_content and "decoded_content" in file_content:
            content = file_content["decoded_content"]
            print(f"文件名: {file_content['name']}")
            print(f"大小: {file_content['size']} 字节")
            print(f"内容预览: {content[:200]}...")

        # 示例6：获取仓库使用的编程语言
        print("\n=== 示例6：获取仓库使用的编程语言 ===")
        languages = await github.get_repository_languages("facebook", "react")
        if languages:
            print(f"React仓库使用的编程语言:")
            for lang, bytes_of_code in languages.items():
                print(f"- {lang}: {bytes_of_code} 字节")

        # 示例7：获取组织信息
        print("\n=== 示例7：获取组织信息 ===")
        org_info = await github.get_organization("google")
        if org_info:
            print(f"名称: {org_info['name']}")
            print(f"描述: {org_info.get('description', '无')}")
            print(f"位置: {org_info.get('location', '未指定')}")
            print(f"公共仓库数: {org_info['public_repos']}")
            print(f"成员数: {org_info.get('public_members', 0)}")
            print(f"URL: {org_info['html_url']}")

        # 示例8：获取用户信息
        print("\n=== 示例8：获取用户信息 ===")
        user_info = await github.get_user("torvalds")
        if user_info:
            print(f"名称: {user_info['name']}")
            print(f"公司: {user_info.get('company', '无')}")
            print(f"博客: {user_info.get('blog', '无')}")
            print(f"位置: {user_info.get('location', '未指定')}")
            print(f"公共仓库数: {user_info['public_repos']}")
            print(f"关注者数: {user_info['followers']}")
            print(f"URL: {user_info['html_url']}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio

    # 运行示例
    asyncio.run(example_usage())

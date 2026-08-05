import aiohttp
import asyncio
from typing import List, Dict, Optional
import re
import random
import time

class WikipediaAPI:
    """维基百科API调用实现"""

    def __init__(self, language: str = "zh", user_agent: str = None,
                 max_concurrent: int = 5, request_delay: float = 0.5):
        """
        初始化维基百科API客户端

        Args:
            language: 语言代码 (zh: 中文, en: 英文, ja: 日文等)
            user_agent: 用户代理信息，如果为None将使用默认值
            max_concurrent: 最大并发请求数
            request_delay: 请求间隔时间(秒)
        """
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
        self.user_agent = user_agent or "WikipediaAPIClient/1.0 (chatscholar@163.com)"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        # 添加并发控制
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.request_delay = request_delay
        self.last_request_time = 0

    async def _make_request(self, url, params=None):
        """
        发起API请求，包含并发控制和请求延迟

        Args:
            url: 请求URL
            params: 请求参数

        Returns:
            API响应数据
        """
        # 使用信号量控制并发
        async with self.semaphore:
            # 添加请求间隔
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.request_delay:
                await asyncio.sleep(self.request_delay - time_since_last_request)

            # 设置随机延迟，避免规律性请求
            jitter = random.uniform(0, 0.2)
            await asyncio.sleep(jitter)

            # 记录本次请求时间
            self.last_request_time = time.time()

            # 发起请求
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 429:  # Too Many Requests
                            retry_after = int(response.headers.get('Retry-After', 5))
                            print(f"达到请求限制，等待 {retry_after} 秒后重试...")
                            await asyncio.sleep(retry_after)
                            return await self._make_request(url, params)

                        if response.status != 200:
                            print(f"API请求失败: HTTP {response.status}")
                            print(f"响应内容: {await response.text()}")
                            return None

                        return await response.json()
            except aiohttp.ClientError as e:
                print(f"请求错误: {str(e)}")
                return None

    async def search(self, query: str, limit: int = 10, namespace: int = 0) -> List[Dict]:
        """
        搜索维基百科文章

        Args:
            query: 搜索关键词
            limit: 返回结果数量
            namespace: 命名空间 (0表示文章, 14表示分类等)

        Returns:
            搜索结果列表
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": limit,
            "srnamespace": namespace,
            "srprop": "snippet|titlesnippet|sectiontitle|categorysnippet|size|wordcount|timestamp|redirecttitle"
        }

        data = await self._make_request(self.base_url, params)
        if not data:
            return []

        search_results = data.get("query", {}).get("search", [])
        return search_results

    async def get_page_content(self, title: str, section: Optional[int] = None) -> Dict:
        """
        获取维基百科页面内容

        Args:
            title: 页面标题
            section: 特定章节编号(可选)

        Returns:
            页面内容字典
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = {
                "action": "parse",
                "page": title,
                "format": "json",
                "prop": "text|langlinks|categories|links|templates|images|externallinks|sections|revid|displaytitle|iwlinks|properties"
            }

            # 如果指定了章节，只获取该章节内容
            if section is not None:
                params["section"] = section

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    print(f"API请求失败: HTTP {response.status}")
                    return {}

                data = await response.json()
                if "error" in data:
                    print(f"API错误: {data['error'].get('info', '未知错误')}")
                    return {}

                return data.get("parse", {})

    async def get_summary(self, title: str, sentences: int = 3) -> str:
        """
        获取页面摘要

        Args:
            title: 页面标题
            sentences: 返回的句子数量

        Returns:
            页面摘要文本
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = {
                "action": "query",
                "prop": "extracts",
                "exintro": "1",
                "exsentences": sentences,
                "explaintext": "1",
                "titles": title,
                "format": "json"
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    print(f"API请求失败: HTTP {response.status}")
                    return ""

                data = await response.json()
                pages = data.get("query", {}).get("pages", {})
                # 获取第一个页面ID的内容
                for page_id in pages:
                    return pages[page_id].get("extract", "")
                return ""

    async def get_random_articles(self, count: int = 1, namespace: int = 0) -> List[Dict]:
        """
        获取随机文章

        Args:
            count: 需要的随机文章数量
            namespace: 命名空间

        Returns:
            随机文章列表
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = {
                "action": "query",
                "list": "random",
                "rnlimit": count,
                "rnnamespace": namespace,
                "format": "json"
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    print(f"API请求失败: HTTP {response.status}")
                    return []

                data = await response.json()
                return data.get("query", {}).get("random", [])

    async def login(self, username: str, password: str) -> bool:
        """
        使用维基百科账户登录

        Args:
            username: 维基百科用户名
            password: 维基百科密码

        Returns:
            登录是否成功
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # 获取登录令牌
            params = {
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }

            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    print(f"获取登录令牌失败: HTTP {response.status}")
                    return False

                data = await response.json()
                login_token = data.get("query", {}).get("tokens", {}).get("logintoken")

                if not login_token:
                    print("获取登录令牌失败")
                    return False

                # 使用令牌登录
                login_params = {
                    "action": "login",
                    "lgname": username,
                    "lgpassword": password,
                    "lgtoken": login_token,
                    "format": "json"
                }

                async with session.post(self.base_url, data=login_params) as login_response:
                    login_data = await login_response.json()

                    if login_data.get("login", {}).get("result") == "Success":
                        print(f"登录成功: {username}")
                        return True
                    else:
                        print(f"登录失败: {login_data.get('login', {}).get('reason', '未知原因')}")
                        return False

    async def setup_oauth(self, consumer_token: str, consumer_secret: str,
                       access_token: str = None, access_secret: str = None) -> bool:
        """
        设置OAuth认证

        Args:
            consumer_token: 消费者令牌
            consumer_secret: 消费者密钥
            access_token: 访问令牌（可选）
            access_secret: 访问密钥（可选）

        Returns:
            设置是否成功
        """
        try:
            # 需要安装 mwoauth 库: pip install mwoauth
            import mwoauth
            import requests_oauthlib

            # 设置OAuth
            self.consumer_token = consumer_token
            self.consumer_secret = consumer_secret

            if access_token and access_secret:
                # 如果已有访问令牌
                self.auth = requests_oauthlib.OAuth1(
                    consumer_token,
                    consumer_secret,
                    access_token,
                    access_secret
                )
                print("OAuth设置成功")
                return True
            else:
                # 需要获取访问令牌（这通常需要用户在网页上授权）
                print("请在开发环境中完成以下OAuth授权流程:")

                # 创建消费者
                consumer = mwoauth.Consumer(
                    consumer_token, consumer_secret
                )

                # 初始化握手
                redirect, request_token = mwoauth.initiate(
                    f"https://{self.language}.wikipedia.org/w/index.php",
                    consumer
                )

                print(f"请访问此URL授权应用: {redirect}")
                # 这里通常会提示用户访问URL并输入授权码
                # 实际应用中需要实现适当的授权流程
                return False
        except ImportError:
            print("请安装 mwoauth 库: pip install mwoauth")
            return False
        except Exception as e:
            print(f"设置OAuth时发生错误: {str(e)}")
            return False

async def example_usage():
    """演示WikipediaAPI的使用方法"""
    # 创建默认中文维基百科API客户端
    wiki_zh = WikipediaAPI(language="zh")

    try:
        # 示例1: 基本搜索
        print("\n=== 示例1: 搜索维基百科 ===")
        results = await wiki_zh.search("人工智能", limit=3)

        for i, result in enumerate(results, 1):
            print(f"\n--- 结果 {i} ---")
            print(f"标题: {result.get('title')}")
            snippet = result.get('snippet', '')
            # 清理HTML标签
            snippet = re.sub(r'<.*?>', '', snippet)
            print(f"摘要: {snippet}")
            print(f"字数: {result.get('wordcount')}")
            print(f"大小: {result.get('size')} 字节")

        # 示例2: 获取页面摘要
        print("\n=== 示例2: 获取页面摘要 ===")
        summary = await wiki_zh.get_summary("深度学习", sentences=2)
        print(f"深度学习摘要: {summary}")

        # 示例3: 获取页面内容
        print("\n=== 示例3: 获取页面内容 ===")
        content = await wiki_zh.get_page_content("机器学习")
        if content and "text" in content:
            text = content["text"].get("*", "")
            # 移除HTML标签以便控制台显示
            clean_text = re.sub(r'<.*?>', '', text)
            print(f"机器学习页面内容片段: {clean_text[:200]}...")

            # 显示页面包含的分类数量
            categories = content.get("categories", [])
            print(f"分类数量: {len(categories)}")

            # 显示页面包含的链接数量
            links = content.get("links", [])
            print(f"链接数量: {len(links)}")

        # 示例4: 获取特定章节内容
        print("\n=== 示例4: 获取特定章节内容 ===")
        # 获取引言部分(通常是0号章节)
        intro_content = await wiki_zh.get_page_content("人工智能", section=0)
        if intro_content and "text" in intro_content:
            intro_text = intro_content["text"].get("*", "")
            clean_intro = re.sub(r'<.*?>', '', intro_text)
            print(f"人工智能引言内容片段: {clean_intro[:200]}...")

        # 示例5: 获取随机文章
        print("\n=== 示例5: 获取随机文章 ===")
        random_articles = await wiki_zh.get_random_articles(count=2)
        print("随机文章:")
        for i, article in enumerate(random_articles, 1):
            print(f"{i}. {article.get('title')}")

            # 显示随机文章的简短摘要
            article_summary = await wiki_zh.get_summary(article.get('title'), sentences=1)
            print(f"   摘要: {article_summary[:100]}...")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio

    # 运行示例
    asyncio.run(example_usage())

from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from loguru import logger
import PyPDF2
import io


class SciHub:
    # 更新的镜像列表，包含更多可用的镜像
    MIRRORS = [
        'https://sci-hub.se/',
        'https://sci-hub.st/',
        'https://sci-hub.ru/',
        'https://sci-hub.wf/',
        'https://sci-hub.ee/',
        'https://sci-hub.ren/',
        'https://sci-hub.tf/',
        'https://sci-hub.si/',
        'https://sci-hub.do/',
        'https://sci-hub.hkvisa.net/',
        'https://sci-hub.mksa.top/',
        'https://sci-hub.shop/',
        'https://sci-hub.yncjkj.com/',
        'https://sci-hub.41610.org/',
        'https://sci-hub.automic.us/',
        'https://sci-hub.et-fine.com/',
        'https://sci-hub.pooh.mu/',
        'https://sci-hub.bban.top/',
        'https://sci-hub.usualwant.com/',
        'https://sci-hub.unblockit.kim/'
    ]

    def __init__(self, doi: str, path: Path, url=None, timeout=60, use_proxy=True):
        self.timeout = timeout
        self.path = path
        self.doi = str(doi)
        self.use_proxy = use_proxy
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.payload = {
            'sci-hub-plugin-check': '',
            'request': self.doi
        }
        self.url = url if url else self.MIRRORS[0]
        self.proxies = {
            "http": "socks5h://localhost:10880",
            "https": "socks5h://localhost:10880",
        } if use_proxy else None

    def _test_proxy_connection(self):
        """测试代理连接是否可用"""
        if not self.use_proxy:
            return True

        try:
            # 测试代理连接
            test_response = requests.get(
                'https://httpbin.org/ip',
                proxies=self.proxies,
                timeout=10
            )
            if test_response.status_code == 200:
                logger.info("代理连接测试成功")
                return True
        except Exception as e:
            logger.warning(f"代理连接测试失败: {str(e)}")
            return False
        return False

    def _check_pdf_validity(self, content):
        """检查PDF文件是否有效"""
        try:
            # 使用PyPDF2检查PDF是否可以正常打开和读取
            pdf = PyPDF2.PdfReader(io.BytesIO(content))
            if len(pdf.pages) > 0:
                return True
            return False
        except Exception as e:
            logger.error(f"PDF文件无效: {str(e)}")
            return False

    def _send_request(self):
        """发送请求到Sci-Hub镜像站点"""
        # 首先测试代理连接
        if self.use_proxy and not self._test_proxy_connection():
            logger.warning("代理连接不可用，切换到直连模式")
            self.use_proxy = False
            self.proxies = None

        last_exception = None
        working_mirrors = []

        # 先测试哪些镜像可用
        logger.info("正在测试镜像站点可用性...")
        for mirror in self.MIRRORS:
            try:
                test_response = requests.get(
                    mirror,
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=10
                )
                if test_response.status_code == 200:
                    working_mirrors.append(mirror)
                    logger.info(f"镜像 {mirror} 可用")
                    if len(working_mirrors) >= 5:  # 找到5个可用镜像就够了
                        break
            except Exception as e:
                logger.debug(f"镜像 {mirror} 不可用: {str(e)}")
                continue

        if not working_mirrors:
            raise Exception("没有找到可用的镜像站点")

        logger.info(f"找到 {len(working_mirrors)} 个可用镜像，开始尝试下载...")

        # 使用可用的镜像进行下载
        for mirror in working_mirrors:
            try:
                res = requests.post(
                    mirror,
                    headers=self.headers,
                    data=self.payload,
                    proxies=self.proxies,
                    timeout=self.timeout
                )
                if res.ok:
                    logger.info(f"成功使用镜像站点: {mirror}")
                    self.url = mirror  # 更新当前使用的镜像
                    time.sleep(1)  # 降低等待时间以提高效率
                    return res
            except Exception as e:
                logger.error(f"尝试镜像 {mirror} 失败: {str(e)}")
                last_exception = e
                continue

        if last_exception:
            raise last_exception
        raise Exception("所有可用镜像站点均无法完成下载")

    def _extract_url(self, response):
        """从响应中提取PDF下载链接"""
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            # 尝试多种方式提取PDF链接
            pdf_element = soup.find(id='pdf')
            if pdf_element:
                content_url = pdf_element.get('src')
            else:
                # 尝试其他可能的选择器
                pdf_element = soup.find('iframe')
                if pdf_element:
                    content_url = pdf_element.get('src')
                else:
                    # 查找直接的PDF链接
                    pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x)
                    if pdf_links:
                        content_url = pdf_links[0].get('href')
                    else:
                        raise AttributeError("未找到PDF链接")

            if content_url:
                content_url = content_url.replace('#navpanes=0&view=FitH', '').replace('//', '/')
                if not content_url.endswith('.pdf') and 'pdf' not in content_url.lower():
                    raise AttributeError("找到的链接不是PDF文件")
        except AttributeError:
            logger.error(f"未找到论文 {self.doi}")
            return None

        current_mirror = self.url.rstrip('/')
        if content_url.startswith('/'):
            return current_mirror + content_url
        elif content_url.startswith('http'):
            return content_url
        else:
            return 'https:/' + content_url

    def _download_pdf(self, pdf_url):
        """下载PDF文件并验证其完整性"""
        try:
            # 尝试不同的下载方式
            download_methods = [
                # 方法1：直接下载
                lambda: requests.get(pdf_url, proxies=self.proxies, timeout=self.timeout),
                # 方法2：添加 Referer 头
                lambda: requests.get(pdf_url, proxies=self.proxies, timeout=self.timeout,
                                   headers={**self.headers, 'Referer': self.url}),
                # 方法3：使用原始域名作为 Referer
                lambda: requests.get(pdf_url, proxies=self.proxies, timeout=self.timeout,
                                   headers={**self.headers, 'Referer': pdf_url.split('/downloads')[0] if '/downloads' in pdf_url else self.url})
            ]

            for i, download_method in enumerate(download_methods):
                try:
                    logger.info(f"尝试下载方式 {i+1}/3...")
                    response = download_method()
                    if response.status_code == 200:
                        content = response.content
                        if len(content) > 1000 and self._check_pdf_validity(content):  # 确保文件不是太小
                            logger.info(f"PDF下载成功，文件大小: {len(content)} bytes")
                            return content
                        else:
                            logger.warning("下载的文件可能不是有效的PDF")
                    elif response.status_code == 403:
                        logger.warning(f"访问被拒绝 (403 Forbidden)，尝试其他下载方式")
                        continue
                    else:
                        logger.warning(f"下载失败，状态码: {response.status_code}")
                        continue
                except Exception as e:
                    logger.warning(f"下载方式 {i+1} 失败: {str(e)}")
                    continue

            # 如果所有方法都失败，尝试构造替代URL
            try:
                logger.info("尝试使用替代镜像下载...")
                # 从原始URL提取关键信息
                if '/downloads/' in pdf_url:
                    file_part = pdf_url.split('/downloads/')[-1]
                    alternative_mirrors = [
                        f"https://sci-hub.se/downloads/{file_part}",
                        f"https://sci-hub.st/downloads/{file_part}",
                        f"https://sci-hub.ru/downloads/{file_part}",
                        f"https://sci-hub.wf/downloads/{file_part}",
                        f"https://sci-hub.ee/downloads/{file_part}",
                        f"https://sci-hub.ren/downloads/{file_part}",
                        f"https://sci-hub.tf/downloads/{file_part}"
                    ]

                    for alt_url in alternative_mirrors:
                        try:
                            response = requests.get(
                                alt_url,
                                proxies=self.proxies,
                                timeout=self.timeout,
                                headers={**self.headers, 'Referer': alt_url.split('/downloads')[0]}
                            )
                            if response.status_code == 200:
                                content = response.content
                                if len(content) > 1000 and self._check_pdf_validity(content):
                                    logger.info(f"使用替代镜像成功下载: {alt_url}")
                                    return content
                        except Exception as e:
                            logger.debug(f"替代镜像 {alt_url} 下载失败: {str(e)}")
                            continue

            except Exception as e:
                logger.error(f"所有下载方式都失败: {str(e)}")

            return None

        except Exception as e:
            logger.error(f"下载PDF文件失败: {str(e)}")
            return None

    def fetch(self):
        """获取论文PDF，包含重试和验证机制"""
        for attempt in range(2):  # 最多重试3次
            try:
                logger.info(f"开始第 {attempt + 1} 次尝试下载论文: {self.doi}")

                # 获取PDF下载链接
                response = self._send_request()
                pdf_url = self._extract_url(response)
                if pdf_url is None:
                    logger.warning(f"第 {attempt + 1} 次尝试：未找到PDF下载链接")
                    continue

                logger.info(f"找到PDF下载链接: {pdf_url}")

                # 下载并验证PDF
                pdf_content = self._download_pdf(pdf_url)
                if pdf_content is None:
                    logger.warning(f"第 {attempt + 1} 次尝试：PDF下载失败")
                    continue

                # 保存PDF文件
                pdf_name = f"{self.doi.replace('/', '_').replace(':', '_')}.pdf"
                pdf_path = self.path.joinpath(pdf_name)
                pdf_path.write_bytes(pdf_content)

                logger.info(f"成功下载论文: {pdf_name}，文件大小: {len(pdf_content)} bytes")
                return str(pdf_path)

            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                if attempt < 2:  # 不是最后一次尝试
                    wait_time = (attempt + 1) * 3  # 递增等待时间
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                continue

        raise Exception(f"无法下载论文 {self.doi}，所有重试都失败了")

# Usage Example
if __name__ == '__main__':
    # 创建一个用于保存PDF的目录
    save_path = Path('./downloaded_papers')
    save_path.mkdir(exist_ok=True)

    # DOI示例
    sample_doi = '10.3897/rio.7.e67379'  # 这是一篇Nature的论文DOI

    try:
        # 初始化SciHub下载器，先尝试使用代理
        logger.info("尝试使用代理模式...")
        downloader = SciHub(doi=sample_doi, path=save_path, use_proxy=True)

        # 开始下载
        result = downloader.fetch()
        print(f"论文已保存到: {result}")

    except Exception as e:
        print(f"使用代理模式失败: {str(e)}")
        try:
            # 如果代理模式失败，尝试直连模式
            logger.info("尝试直连模式...")
            downloader = SciHub(doi=sample_doi, path=save_path, use_proxy=False)
            result = downloader.fetch()
            print(f"论文已保存到: {result}")
        except Exception as e2:
            print(f"直连模式也失败: {str(e2)}")
            print("建议检查网络连接或尝试其他DOI")

import logging
import tarfile
from pathlib import Path
from typing import Optional, Dict

import requests


class ArxivDownloader:
    """用于下载arXiv论文源码的下载器"""

    def __init__(self, root_dir: str = "./papers", proxies: Optional[Dict[str, str]] = None):
        """
        初始化下载器
        
        Args:
            root_dir: 保存下载文件的根目录
            proxies: 代理服务器设置，例如 {"http": "http://proxy:port", "https": "https://proxy:port"}
        """
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(exist_ok=True)
        self.proxies = proxies

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _download_and_extract(self, arxiv_id: str) -> str:
        """
        下载并解压arxiv论文源码
        
        Args:
            arxiv_id: arXiv论文ID，例如"2103.00020"
            
        Returns:
            str: 解压后的文件目录路径
            
        Raises:
            RuntimeError: 当下载失败时抛出
        """
        paper_dir = self.root_dir / arxiv_id
        tar_path = paper_dir / f"{arxiv_id}.tar.gz"

        # 检查缓存
        if paper_dir.exists() and any(paper_dir.iterdir()):
            logging.info(f"Using cached version for {arxiv_id}")
            return str(paper_dir)

        paper_dir.mkdir(exist_ok=True)

        urls = [
            f"https://arxiv.org/src/{arxiv_id}",
            f"https://arxiv.org/e-print/{arxiv_id}"
        ]

        for url in urls:
            try:
                logging.info(f"Downloading from {url}")
                response = requests.get(url, proxies=self.proxies)
                if response.status_code == 200:
                    tar_path.write_bytes(response.content)
                    with tarfile.open(tar_path, 'r:gz') as tar:
                        tar.extractall(path=paper_dir)
                    return str(paper_dir)
            except Exception as e:
                logging.warning(f"Download failed for {url}: {e}")
                continue

        raise RuntimeError(f"Failed to download paper {arxiv_id}")

    def download_paper(self, arxiv_id: str) -> str:
        """
        下载指定的arXiv论文
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            str: 论文文件所在的目录路径
        """
        return self._download_and_extract(arxiv_id)


def main():
    """测试下载功能"""
    # 配置代理（如果需要）
    proxies = {
        "http": "http://your-proxy:port",
        "https": "https://your-proxy:port"
    }

    # 创建下载器实例（如果不需要代理，可以不传入proxies参数）
    downloader = ArxivDownloader(root_dir="./downloaded_papers", proxies=None)

    # 测试下载一篇论文（这里使用一个示例ID）
    try:
        paper_id = "2103.00020"  # 这是一个示例ID
        paper_dir = downloader.download_paper(paper_id)
        print(f"Successfully downloaded paper to: {paper_dir}")

        # 检查下载的文件
        paper_path = Path(paper_dir)
        if paper_path.exists():
            print("Downloaded files:")
            for file in paper_path.rglob("*"):
                if file.is_file():
                    print(f"- {file.relative_to(paper_path)}")
    except Exception as e:
        print(f"Error downloading paper: {e}")


if __name__ == "__main__":
    main()

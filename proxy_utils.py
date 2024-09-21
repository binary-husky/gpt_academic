# proxy_utils.py

import ipaddress
from urllib.parse import urlparse
from toolbox import get_conf

# 从配置中读取 NO_PROXY_URLS
NO_PROXY_URLS = get_conf('NO_PROXY_URLS') or [] 

def is_private_ip(ip_address):
    """
    检查给定的IP地址是否为私有IP。

    支持IPv4和IPv6。
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        if ip.version == 4:
            # 私有IPv4范围包括环回地址
            private_ranges = [
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
                ipaddress.ip_network('192.168.0.0/16'),
                ipaddress.ip_network('169.254.0.0/16'),  # 链路本地
                ipaddress.ip_network('127.0.0.0/8'),      # 环回
            ]
            return any(ip in private_range for private_range in private_ranges)
        elif ip.version == 6:
            # 检查ULA（Unique Local Address）fc00::/7和环回地址::1/128
            return ((int(ip) >> 121) == 0b1111110) or (ip == ipaddress.IPv6Address('::1'))
        return False
    except ValueError:
        return False


def should_use_proxy(url):
    """
    决定是否应该对给定的URL使用代理。

    判断依据：
    1. URL是否在NO_PROXY_URLS列表中匹配。
    2. URL的主机名是否为私有IP。

    如果不满足上述条件，则使用代理。
    """
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        if not hostname:
            # 如果无法解析主机名，默认使用代理
            return True

        # 检查主机名是否匹配NO_PROXY_URLS中的任何模式
        for pattern in NO_PROXY_URLS:
            # 精确匹配
            if hostname == pattern:
                return False
            # 域名/子域名匹配
            if pattern.startswith('.') and hostname.endswith(pattern):
                return False
            # 通配符匹配
            if pattern.startswith('*') and hostname.endswith(pattern[1:]):
                return False
            # IP范围匹配
            try:
                ip = ipaddress.ip_address(hostname)
                network = ipaddress.ip_network(pattern, strict=False)
                if ip in network:
                    return False
            except ValueError:
                pass  # 不是IP地址或无效的网络，继续检查下一个模式

        # 检查是否为私有IP
        if is_private_ip(hostname):
            return False

        # 如果以上条件都不满足，则使用代理
        return True
    except Exception:
        # 如果解析URL或其他错误，默认使用代理
        return True


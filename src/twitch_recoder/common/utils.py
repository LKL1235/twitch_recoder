"""
Twitch录制器工具模块
"""

import re

from twitch_recoder.config.my_config import config

def get_proxies() -> dict | None:
    """获取代理配置

    Returns:
        dict | None: 代理配置字典,如果没有配置代理则返回None
    """
    if config.proxy and config.proxy.strip():
        proxy_url = config.proxy.strip()
        return {'http': proxy_url, 'https': proxy_url}
    return None


def extract_resolution_width(resolution_str: str) -> int:
    """
    从分辨率字符串中提取宽度值

    Args:
        resolution_str (str): 分辨率字符串，如 "1920x1080"

    Returns:
        int: 宽度值，如果解析失败则返回0
    """
    if not resolution_str:
        return 0

    try:
        width = int(resolution_str.split("x")[0])
        return width
    except (ValueError, IndexError):
        return 0


def format_bandwidth(bandwidth: int) -> str:
    """
    格式化带宽显示

    Args:
        bandwidth (int): 带宽值（bps）

    Returns:
        str: 格式化后的带宽字符串
    """
    if bandwidth >= 1_000_000_000:  # 1 Gbps
        return f"{bandwidth / 1_000_000_000:.2f} Gbps"
    elif bandwidth >= 1_000_000:  # 1 Mbps
        return f"{bandwidth / 1_000_000:.2f} Mbps"
    elif bandwidth >= 1_000:  # 1 Kbps
        return f"{bandwidth / 1_000:.2f} Kbps"
    else:
        return f"{bandwidth} bps"


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除或替换非法字符

    Args:
        filename (str): 原始文件名

    Returns:
        str: 清理后的文件名
    """
    # 移除或替换Windows文件名中的非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, "_", filename)

    # 移除前后空格
    sanitized = sanitized.strip()

    # 如果文件名为空，使用默认名称
    if not sanitized:
        sanitized = "twitch_stream"

    return sanitized
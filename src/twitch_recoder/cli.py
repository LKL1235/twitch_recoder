#!/usr/bin/env python3
"""
Twitch录制器命令行入口点

可以直接运行此脚本来使用命令行功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from twitch_recoder.main import cli


def entry_point():
    cli()


if __name__ == "__main__":
    entry_point()

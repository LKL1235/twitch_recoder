# Twitch录制器模块

这是一个模块化的Twitch流媒体录制器，提供Twitch流媒体解析、排序和录制功能。

## 模块结构

```
twitch-recoder/
├── __init__.py          # 模块初始化文件
├── main.py              # 主程序入口
├── twitch_api.py        # Twitch API相关功能
├── m3u8_parser.py       # M3U8播放列表解析
├── stream_sorter.py     # 流媒体排序功能
├── config.py            # 配置管理
├── utils.py             # 工具函数
├── example.py           # 使用示例
└── README.md            # 本文档
```

## 功能特性

- **Twitch API集成**: 自动获取访问令牌和签名
- **M3U8解析**: 解析播放列表，提取流媒体信息
- **智能排序**: 按分辨率、帧率和带宽智能排序
- **配置管理**: 集中管理API配置和参数
- **工具函数**: 提供用户名验证、带宽格式化等实用功能
- **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
pip install requests loguru click
```

## 使用方法

### 基本使用

```python
from twitch_recoder import main

# 运行主程序
main()
```

### 命令行使用

```bash
# 使用默认用户名
python -m twitch_recoder.main

# 指定用户名
python -m twitch_recoder.main --uid your_username

# 使用短参数
python -m twitch_recoder.main -u your_username

# 显示详细日志
python -m twitch_recoder.main -u your_username -v

# 只显示错误信息
python -m twitch_recoder.main -u your_username -q

# 查看帮助
python -m twitch_recoder.main --help
```

### 单独使用模块

```python
from twitch_recoder.twitch_api import get_token_and_sign, get_m3u8_url
from twitch_recoder.m3u8_parser import parse_m3u8_url
from twitch_recoder.stream_sorter import get_best_stream

# 获取访问令牌
uid = "your_twitch_username"
token, sign = get_token_and_sign(uid)

if token and sign:
    # 获取M3U8播放列表
    m3u8_content = get_m3u8_url(uid, token, sign)
    
    # 解析流媒体信息
    streams = parse_m3u8_url(m3u8_content)
    
    # 获取最佳流媒体
    best_stream = get_best_stream(streams)
    print(f"最佳流媒体: {best_stream}")
```

### 运行示例

```bash
cd src/twitch-recoder

# 运行主程序
python main.py

# 运行命令行版本
python cli.py

# 或者作为模块运行
python -m twitch_recoder.main
```

## 模块详解

### 1. twitch_api.py

处理与Twitch API的交互：

- `get_token_and_sign(uid)`: 获取访问令牌和签名
- `get_m3u8_url(uid, token, sign)`: 获取M3U8播放列表

### 2. m3u8_parser.py

解析M3U8播放列表：

- `parse_m3u8_url(m3u8_content)`: 解析播放列表内容
- `display_stream_info(streams, title)`: 格式化显示流媒体信息

### 3. stream_sorter.py

流媒体排序和选择：

- `sort_streams(streams)`: 智能排序流媒体
- `get_best_stream(streams)`: 获取最佳质量流媒体

### 4. config.py

集中管理配置信息：

- API端点URL
- 请求头和参数
- GraphQL查询语句

### 5. utils.py

提供工具函数：

- `validate_twitch_username(username)`: 验证用户名格式
- `format_bandwidth(bandwidth)`: 格式化带宽显示
- `extract_resolution_width(resolution)`: 提取分辨率宽度
- `sanitize_filename(filename)`: 清理文件名

### 6. main.py

主程序入口：

- `main()`: 主程序入口点（支持命令行参数）
- `process_twitch_stream(uid)`: 处理Twitch流媒体的核心逻辑

### 7. cli.py

命令行入口点：

- 独立的命令行脚本，可以直接运行

## 配置说明

主要配置在 `config.py` 文件中：

- `TWITCH_GQL_URL`: GraphQL API端点
- `TWITCH_USHER_URL`: 流媒体获取端点
- `DEFAULT_HEADERS`: 默认请求头
- `DEFAULT_PARAMS`: 默认请求参数

## 错误处理

模块包含完善的错误处理：

- 网络请求异常处理
- 用户名格式验证
- API响应状态检查
- 详细的日志记录

## 日志配置

使用 `loguru` 进行日志管理：

- DEBUG级别：详细的调试信息
- INFO级别：一般信息
- ERROR级别：错误信息

## 注意事项

1. **API限制**: 请遵守Twitch的API使用限制
2. **认证信息**: 当前使用硬编码的认证信息，生产环境请使用环境变量
3. **网络连接**: 需要稳定的网络连接访问Twitch服务
4. **法律合规**: 请确保遵守相关法律法规和Twitch的服务条款

## 扩展功能

可以基于现有模块扩展：

- 录制功能：集成ffmpeg进行视频录制
- 质量监控：实时监控流媒体质量
- 批量处理：支持多个频道同时处理
- 数据库存储：保存流媒体信息到数据库

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

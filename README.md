# Twitch录制器 (Twitch Recoder)

一个用于录制Twitch直播流的Python工具，支持多线程并发录制多个频道，具有智能任务管理和优雅关闭机制。

## 🚀 主要特性

- 🎥 **多频道并发录制**: 支持同时录制多个Twitch频道
- 🔄 **双任务管理器**: 独立的process和recode任务管理器
- 📊 **智能任务调度**: 自动检测频道状态，避免重复录制
- 🛡️ **优雅关闭**: 支持信号处理和任务清理
- 📁 **自动文件管理**: 智能文件命名和目录管理
- ⚙️ **灵活配置**: JSON配置文件支持
- ⌨️ **快捷键支持**: Ctrl+P查看任务状态
- 🔍 **实时监控**: 详细的任务状态跟踪和日志记录

## 📋 系统要求

- Python 3.10+
- FFmpeg (需要预先安装并添加到系统PATH)
- Windows/Linux/macOS

## 🛠️ 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd twitch_recoder

# 安装依赖
pip install -e .
```

### 依赖安装

```bash
pip install requests loguru click keyboard
```

## ⚙️ 配置

### 配置文件结构

在 `config/config.json` 文件中配置要录制的频道：

```json
{
    "uids": ["mande", "xqc", "rogue", "xzylas"],
    "data_path": "data",
    "shutdown_timeout": 10,
    "max_time_limit": 3600,
    "proxy": null
}
```

### 配置参数说明

- `uids`: 要录制的Twitch频道UID列表
- `data_path`: 录制文件保存路径
- `shutdown_timeout`: 关闭超时时间（秒）
- `max_time_limit`: 最大录制时间限制（秒）
- `proxy`: 代理设置（可选）

## 🚀 使用方法

### 基本使用

```bash
# 使用默认配置文件
python -m twitch_recoder

# 指定配置文件
python -m twitch_recoder --config config/my_config.json

# 显示详细日志
python -m twitch_recoder --verbose

# 只显示错误信息
python -m twitch_recoder --quiet
```

### 命令行选项

- `-c, --config`: 指定配置文件路径
- `-v, --verbose`: 显示详细日志（DEBUG级别）
- `-q, --quiet`: 只显示错误信息（ERROR级别）

### 快捷键

- `Ctrl+P`: 查看当前所有任务状态
- `Ctrl+C`: 优雅关闭程序

## 🏗️ 架构设计

### 双任务管理器架构

系统使用两个独立的任务管理器：

- **Process Task Manager**: 处理频道UID解析和流媒体信息获取
- **Recode Task Manager**: 处理实际的录制任务执行

### 任务流程

1. **频道检测**: 定期检查配置的UID列表
2. **状态验证**: 检查频道是否已开播
3. **流媒体获取**: 获取最佳质量的流媒体信息
4. **录制任务创建**: 为每个有效流创建录制任务
5. **并发录制**: 多线程并发执行录制任务
6. **状态监控**: 实时跟踪任务状态和进度

### 任务状态管理

系统维护完整的任务生命周期：

```python
class TaskStatus(Enum):
    QUEUED = "queued"           # 排队中
    RUNNING = "running"         # 运行中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败
    SHUTDOWN = "shutdown"       # 已关闭
```

## 📁 项目结构

```
twitch_recoder/
├── config/                     # 配置文件
│   └── config.json
├── data/                       # 录制文件存储
├── src/
│   └── twitch_recoder/
│       ├── api/               # Twitch API接口
│       │   └── twitch_api.py
│       ├── cli.py            # 命令行接口
│       ├── common/           # 通用工具
│       │   ├── m3u8_parser.py
│       │   ├── stream_sorter.py
│       │   ├── taskManager.py
│       │   └── utils.py
│       ├── config/           # 配置管理
│       │   └── my_config.py
│       ├── core/             # 核心录制逻辑
│       │   ├── process.py
│       │   └── recoder.py
│       ├── types/            # 类型定义
│       │   ├── errors.py
│       │   └── typeinfo.py
│       ├── __init__.py
│       └── main.py          # 主程序入口
├── pyproject.toml            # 项目配置
├── README.md
└── version.txt
```

## 🔧 核心模块

### TaskManager (任务管理器)

- 任务创建、启动、停止、状态跟踪
- 自动清理已完成任务
- 任务队列管理和负载均衡

### Twitch API

- 频道状态检测
- 流媒体信息获取
- 最佳质量流选择

### 录制引擎

- FFmpeg集成
- 多格式支持
- 错误处理和重试机制

## 📊 监控和调试

### 日志级别

- `--verbose`: DEBUG级别，包含详细执行信息
- 默认: INFO级别，显示主要操作信息
- `--quiet`: ERROR级别，只显示错误信息

### 任务状态查看

使用 `Ctrl+P` 快捷键或查看日志来监控任务状态：

```
INFO - 所有的process任务: [Task(task_id=process_mande, uid=mande, status=RUNNING)]
INFO - 所有的recode任务: [Task(task_id=recode_mande_123456, uid=mande, status=RUNNING)]
```

## 🚨 故障排除

### 常见问题

1. **FFmpeg未找到**
   ```
   确保FFmpeg已安装并添加到系统PATH
   Windows: 下载FFmpeg并添加到环境变量
   Linux: sudo apt install ffmpeg
   macOS: brew install ffmpeg
   ```

2. **权限错误**
   ```
   检查data_path目录的写入权限
   确保程序有足够的磁盘空间
   ```

3. **网络连接问题**
   ```
   检查网络连接
   配置代理设置（如需要）
   验证Twitch服务可用性
   ```

4. **频道未开播**
   ```
   程序会自动跳过未开播的频道
   这是正常行为，无需担心
   ```

### 调试技巧

- 使用 `--verbose` 参数获取详细日志
- 检查配置文件格式是否正确
- 验证UID是否有效
- 监控磁盘空间使用情况

## 🔄 高级功能

### 自动任务清理

系统会自动清理已完成的任务，避免内存泄漏：

```python
# 自动清理已完成任务
process_task_manager.clear_completed_tasks()
recode_task_manager.clear_completed_tasks()
```

### 智能重复检测

避免为同一频道创建重复任务：

```python
# 检查是否已有运行中的任务
if process_task or recode_task:
    continue  # 跳过已有任务的频道
```

### 优雅关闭

支持多种关闭方式：

- `Ctrl+C` (SIGINT)
- `SIGTERM` 信号
- 程序异常退出

## 📈 性能优化

### 并发控制

- 每个频道独立任务管理
- 避免重复任务创建
- 智能任务调度

### 资源管理

- 自动清理已完成任务
- 内存使用优化
- 磁盘空间监控

## 🔮 扩展功能

### 自定义录制参数

可以修改 `recoder.py` 中的FFmpeg参数：

```python
# 调整缓冲区大小
bufsize = "20000k"

# 修改超时设置
rw_timeout = "100000000"
```

### 添加新功能

- 支持更多视频格式
- 自定义录制质量
- 集成其他流媒体平台

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如果遇到问题，请：

1. 查看日志输出
2. 检查配置文件
3. 验证系统要求
4. 提交Issue描述问题

---

**注意**: 请确保遵守Twitch的服务条款和当地法律法规。本工具仅用于个人学习和研究目的。

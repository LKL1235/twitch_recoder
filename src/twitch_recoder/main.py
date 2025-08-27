import json
import os
import time
import click
import signal
import sys
import keyboard
from loguru import logger
from twitch_recoder.common.taskManager import process_task_manager, recode_task_manager
from twitch_recoder.config.my_config import DEFAULT_CONFIG
from twitch_recoder.core.process import process


def main(config_path: str, verbose: bool, quiet: bool, data_path: str = "data"):
    """Twitch录制器 - 获取和解析Twitch流媒体信息"""
    # 配置日志级别
    if quiet:
        logger.remove()
        logger.add(lambda msg: print(msg), level="ERROR")
    elif verbose:
        logger.remove()
        logger.add(lambda msg: print(msg), level="DEBUG")
    else:
        logger.remove()
        logger.add(lambda msg: print(msg), level="INFO")

    if not os.path.exists(config_path) and not os.path.isfile(config_path):
        logger.error(f"配置文件不存在: {config_path}, 生成默认配置文件:config/config.json")
        os.makedirs("config", exist_ok=True)
        with open("config/config.json", "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return
    from twitch_recoder.config.my_config import ConfigReader, config

    config_reader = ConfigReader(config_path)
    config_reader.load_config()
    if not config:
        logger.error(f"配置文件读取失败: {config_path}")
        return

    logger.info(f"开始处理Twitch频道: {config_path}")

    # 设置信号处理器
    def signal_handler(signum, frame):
        """处理中断信号"""
        logger.info(f"收到信号 {signum}，正在优雅关闭...")
        process_task_manager.shutdown()
        recode_task_manager.shutdown()
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    def on_ctrl_p():
        """当按下Ctrl+P时显示任务状态"""
        logger.info(f"所有的process任务: {process_task_manager.get_all_tasks()}")
        logger.info(f"所有的recode任务: {recode_task_manager.get_all_tasks()}")

    # 注册快捷键
    keyboard.add_hotkey('ctrl+p', on_ctrl_p)

    try:
        logger.info("启动所有任务...")
        while True:
            process()
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        # 显示当前任务状态
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生未预期的错误: {e}")
        sys.exit(1)
    finally:
        process_task_manager.shutdown()
        recode_task_manager.shutdown()


@click.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="配置文件路径")
@click.option("--verbose", "-v", is_flag=True, help="显示详细日志")
@click.option("--quiet", "-q", is_flag=True, help="只显示错误信息")
def cli(config: str, verbose: bool, quiet: bool):
    main(config, verbose, quiet)


if __name__ == "__main__":
    main("config/config.json", False, False)

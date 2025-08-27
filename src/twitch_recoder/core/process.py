from datetime import datetime
import time
import os
from loguru import logger
from twitch_recoder.api.twitch_api import process_twitch_stream
from twitch_recoder.core.recoder import recode
from twitch_recoder.config.my_config import config
from twitch_recoder.common.taskManager import TaskStatus, TaskType, Task, process_task_manager, recode_task_manager
from twitch_recoder.types.errors import NetWorkErr, OfflineErr


def process_single_uid(uid: str) -> bool:
    """处理单个UID的录制任务"""

    try:
        best_stream = process_twitch_stream(uid)
    except OfflineErr:
        logger.error(f"频道 {uid} 未开播")
        return False
    except NetWorkErr as e:
        logger.error(f"{uid} 获取流媒体信息失败: {e}")
        return False

    if not best_stream or not best_stream.url:
        logger.error(f"{uid} 获取流媒体信息失败: {best_stream}")
        return False

    # 确保nickname是字符串类型
    nickname = str(best_stream.nickname) if best_stream.nickname else str(best_stream.uid)
    resolution = str(best_stream.resolution) if best_stream.resolution else "unknown"
    frame_rate = str(best_stream.frame_rate) if best_stream.frame_rate else "unknown"

    # 生成录制任务ID
    recode_task_id = f"recode_{uid}_{int(time.time())}"

    os.makedirs(config.data_path, exist_ok=True)
    streamer_name = nickname
    save_file_name = f"{streamer_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    save_file_path = os.path.join(config.data_path, save_file_name)

    task = Task(
        task_id=recode_task_id,
        uid=uid,
        task_type=TaskType.RECODE,
        func=recode,
        args=(best_stream.url, config.proxy, save_file_path, nickname, config.max_time_limit),
    )
    recode_task_manager.add_task(task)
    task.start()

    logger.info(f"已提交录制任务, UID:{uid}, {resolution}:{frame_rate}, save_path: {save_file_path}")
    return True


def process():
    """主处理函数 - 为每个UID创建处理任务"""
    if not config.uids:
        logger.error("配置中没有UID")
        return False
    logger.info("清除已完成任务")
    process_task_manager.clear_completed_tasks()
    recode_task_manager.clear_completed_tasks()
    this_time_process_uids = []
    for uid in config.uids:
        # 检查是否存在process任务
        process_task = process_task_manager.find_task_by_uid(uid)
        recode_task = recode_task_manager.find_task_by_uid(uid)
        if process_task or recode_task:
            continue
        # 如果没有/已经完成对应uid的process任务，则创建process任务
        task = Task(
            task_id=f"process_{uid}",
            uid=uid,
            task_type=TaskType.PROCESS,
            func=process_single_uid,
            args=(uid,),
        )
        process_task_manager.add_task(task)
        task.start()
        this_time_process_uids.append(uid)

    logger.info(f"没有正在运行的{this_time_process_uids}任务, 已创建")
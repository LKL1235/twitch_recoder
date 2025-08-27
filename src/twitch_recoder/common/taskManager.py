from enum import Enum
import threading
import time
from typing import Optional, Callable

from loguru import logger


class TaskType(Enum):
    PROCESS = "process"
    RECODE = "recode"


class TaskStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SHUTDOWN = "shutdown"


class Task(threading.Thread):
    def __init__(self, task_id: str, uid: str, task_type: TaskType, func: Callable, *args, **kwargs):
        # 调用父类构造函数
        super().__init__(name=f"Task-{task_id}")

        self.task_id = task_id
        self.uid = uid
        self.task_type = task_type
        self.func = func
        # 处理参数：如果传入的是args参数，直接使用；否则收集所有位置参数
        if 'args' in kwargs:
            self.args = kwargs.pop('args')
        else:
            self.args = args

        self.kwargs = kwargs

        # 任务状态
        self.status = TaskStatus.QUEUED
        self.result: Optional[bool] = None
        self.error_message: Optional[str] = None

        # 时间戳
        self.create_time = time.time()
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # 控制标志
        self._stop_event = threading.Event()

    def run(self):
        """线程执行的主要方法"""
        try:
            # 更新状态为运行中
            self.status = TaskStatus.RUNNING
            self.start_time = time.time()

            # 执行任务函数
            self.result = self.func(*self.args, **self.kwargs)

            # 更新状态为完成
            self.status = TaskStatus.COMPLETED

        except Exception as e:
            # 处理异常
            self.status = TaskStatus.FAILED
            self.result = False
            self.error_message = str(e)

        finally:
            # 记录结束时间
            self.end_time = time.time()

    def stop(self):
        """停止任务"""
        self._stop_event.set()
        self.status = TaskStatus.SHUTDOWN

    def is_stopped(self) -> bool:
        """检查任务是否被停止"""
        return self._stop_event.is_set()

    def get_duration(self) -> Optional[float]:
        """获取任务执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return None

    def __str__(self):
        return f"Task(task_id={self.task_id}, uid={self.uid}, task_type={self.task_type}, status={self.status}, result={self.result})"

    def __repr__(self):
        return self.__str__()


class TaskManager:
    def __init__(self):
        self.tasks: list[Task] = []

    def start_all(self):
        for task in self.tasks:
            task.start()

    def shutdown(self):
        for task in self.tasks:
            task.stop()

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def remove_task(self, task: Task):
        self.tasks.remove(task)

    def find_task_by_uid(self, uid: str) -> Optional[Task]:
        for task in self.tasks:
            if task.uid == uid:
                return task
        return None

    def is_task_running(self, task: Task) -> bool:
        return task and (task.status == TaskStatus.RUNNING or task.status == TaskStatus.QUEUED)

    def clear_completed_tasks(self):
        to_remove_tasks = []
        for task in self.tasks:
            if task.status != TaskStatus.RUNNING and task.status != TaskStatus.QUEUED:
                to_remove_tasks.append(task)
        for task in to_remove_tasks:
            logger.debug(
                f"移除已完成{task.task_type}任务,task_id={task.task_id}, uid={task.uid}, status={task.status}"
            )
            self.remove_task(task)


    def get_all_tasks(self) -> list[Task]:
        return self.tasks

    def get_running_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.RUNNING]

    def get_completed_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]

    def get_failed_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.FAILED]

    def get_queued_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.QUEUED]

    def get_shutdown_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.SHUTDOWN]

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        task = self.get_task(task_id)
        return task.status if task else None


process_task_manager = TaskManager()
recode_task_manager = TaskManager()

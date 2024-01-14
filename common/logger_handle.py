# encoding: utf-8
# @Time   : 2023/12/6
# @Author : Spike
# @Descr   :
import logging
import sys
import os
import json
import time
from loguru import logger
from typing import cast
from types import FrameType
from common.path_handle import init_path


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(),
        )


def init_config():
    LOGGER_NAMES = ("uvicorn.asgi", "uvicorn.access", "uvicorn")

    # change handler for default uvicorn logger
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]


format_ = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
          "<level>{level}</level> | " \
          "<cyan>{process.name}:{process.id}</cyan> | " \
          "<cyan>{thread.name}</cyan> | " \
          "<cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
          "<level>{message}</level>"

logger.remove()
logger.add(sys.stdout, format=format_, colorize=True)
log_name = f"Fast_{time.strftime('%Y-%m-%d', time.localtime()).replace('-', '_')}.log"
log_path = os.path.join(init_path.logs_path, log_name)
logger.add(log_path,  # 写入目录指定文件
           format=format_,
           encoding='utf-8',
           retention='7 days',  # 设置历史保留时长
           backtrace=True,  # 回溯
           diagnose=True,  # 诊断
           enqueue=True,  # 异步写入
           rotation="00:00",  # 每日更新时间
           colorize=True,
           # rotation="5kb",  # 切割，设置文件大小，rotation="12:00"，rotation="1 week"
           # filter="my_module"  # 过滤模块
           # compression="zip"   # 文件压缩
           )

if __name__ == '__main__':
    pass

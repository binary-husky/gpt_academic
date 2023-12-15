#! .\venv\
# encoding: utf-8
# @Time   : 2023/12/6
# @Author : Spike
# @Descr   :
import sys
from loguru import logger


format_ = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
         "<level>{level}</level> | "
         "<cyan>{process.name}:{process.id}</cyan> | "
         "<cyan>{thread.name}</cyan> | "
         "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
         ":<cyan>{line}</cyan> "
         "<level>{message}</level>")

logger.remove()
logger.add(sys.stdout, format=format_, level='INFO')
# logger.add(lambda e: error_handel(e), format=format, level='ERROR')

if __name__ == '__main__':
    logger.catch()
    logger.debug('123123123')
    logger.info('123213')
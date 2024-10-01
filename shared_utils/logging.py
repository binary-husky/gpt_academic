from loguru import logger
import logging
import sys
import os

def chat_log_filter(record):
    return "chat_msg" in record["extra"]

def not_chat_log_filter(record):
    return "chat_msg" not in record["extra"]

def formatter_with_clip(record):
    # Note this function returns the string to be formatted, not the actual message to be logged
    # record["extra"]["serialized"] = "555555"
    max_len = 12
    record['function_x'] = record['function'].center(max_len)
    if len(record['function_x']) > max_len:
        record['function_x'] = ".." + record['function_x'][-(max_len-2):]
    record['line_x'] = str(record['line']).ljust(3)
    return '<green>{time:HH:mm}</green> | <cyan>{function_x}</cyan>:<cyan>{line_x}</cyan> | <level>{message}</level>\n'

def setup_logging(PATH_LOGGING):
    
    admin_log_path = os.path.join(PATH_LOGGING, "admin")
    os.makedirs(admin_log_path, exist_ok=True)
    sensitive_log_path = os.path.join(admin_log_path, "chat_secrets.log")
    regular_log_path = os.path.join(admin_log_path, "console_log.log")
    logger.remove()
    logger.configure(
        levels=[dict(name="WARNING", color="<g>")],
    )

    logger.add(
        sys.stderr, 
        format=formatter_with_clip,
        # format='<green>{time:HH:mm}</green> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
        filter=(lambda record: not chat_log_filter(record)),
        colorize=True,
        enqueue=True
    )

    logger.add(
        sensitive_log_path, 
        format='<green>{time:MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
        rotation="10 MB",
        filter=chat_log_filter,
        enqueue=True, 
    )

    logger.add(
        regular_log_path, 
        format='<green>{time:MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
        rotation="10 MB",
        filter=not_chat_log_filter,
        enqueue=True, 
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.warning(f"所有对话记录将自动保存在本地目录{sensitive_log_path}, 请注意自我隐私保护哦！")


# logger.bind(chat_msg=True).info("This message is logged to the file!")
# logger.debug(f"debug message")
# logger.info(f"info message")
# logger.success(f"success message")
# logger.error(f"error message")
# logger.add("special.log", filter=lambda record: "special" in record["extra"])
# logger.debug("This message is not logged to the file")

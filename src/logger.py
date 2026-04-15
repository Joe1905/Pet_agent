import logging
import datetime
import os

from string_manager import StringManager


class SaveLogger:
    @staticmethod
    def setup_custom_logger(log_file="app.log"):
        """配置自定义日志记录器"""
        # 创建日志目录（如果不存在）
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建日志记录器
        logger = logging.getLogger("CustomLogger")
        logger.setLevel(logging.DEBUG)  # 设置最低日志级别

        # 格式化日志内容（包含自定义信息）
        log_format = logging.Formatter(
            '%(log_time)s - %(user)s - %(message)s'
        )

        # 创建文件处理器，将日志写入文件
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(log_format)

        # 添加处理器到日志记录器
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def to_logger(log_contents:list):
        strings = StringManager()
        # print(strings.get("logger.log_enter_str"))
        if log_contents is None or len(log_contents) == 0:
            return
        start_time = log_contents[0][1].strftime(strings.get("logger.log_file_name"))
        # 初始化日志记录器
        logger = SaveLogger.setup_custom_logger(f"logs/{start_time}.txt")

        # 记录日志
        for action in log_contents:
            message = action[0]  # 第一个元素是message
            log_time = action[1]  # 第二个元素是时间
            user = "robot" if action[2] == 2 else "mine"
            # 使用extra参数传递自定义字段
            logger.info(
                message,
                extra={
                    "user": user,
                    "log_time": log_time.strftime(strings.get("messageUi.time_table"))  # 传递时间到日志格式中
                }
            )


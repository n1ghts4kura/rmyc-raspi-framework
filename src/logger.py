#
# logger.py
#
# @author n1ghts4kura
# @date 2025/9/28
#

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ColorFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
        'BOLD': '\033[1m',        # 粗体
        'DIM': '\033[2m'          # 暗色
    }
    
    def format(self, record):
        # 获取颜色
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        bold = self.COLORS['BOLD']
        dim = self.COLORS['DIM']
        
        # 格式化时间
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建日志消息
        log_message = (
            f"{dim}[{timestamp}]{reset} "
            f"{color}{bold}[{record.levelname:>8}]{reset} "
            f"{dim}{record.name}:{record.lineno}{reset} "
            f"- {record.getMessage()}"
        )
        
        # 如果有异常信息，添加异常堆栈
        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"
            
        return log_message


class Logger:
    """日志管理器类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = "FrameworkLogger", level: LogLevel = LogLevel.INFO, 
                 enable_color: bool = True):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
            enable_color: 是否启用彩色输出
        """
        if self._initialized:
            return
            
        self.name = name
        self.level = level
        self.enable_color = enable_color
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # 清除已有处理器
        self.logger.handlers.clear()
        
        # 设置控制台处理器
        self._setup_console_handler()
        
        self._initialized = True
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level.value)
        
        if self.enable_color:
            formatter = ColorFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def set_level(self, level: LogLevel):
        """
        设置日志级别
        
        Args:
            level: 新的日志级别
        """
        self.level = level
        self.logger.setLevel(level.value)
        
        # 更新控制台处理器级别
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level.value)
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """异常日志（自动包含异常堆栈）"""
        self.logger.exception(message, *args, **kwargs)


# 全局变量控制日志级别
DEBUG_MODE = True  # 设置为 False 则只输出 INFO 及以上级别的日志

# 根据调试模式设置日志级别
LOG_LEVEL = LogLevel.DEBUG if DEBUG_MODE else LogLevel.INFO

# 创建全局日志器实例
logger = Logger(
    name="Framework",
    level=LOG_LEVEL,
    enable_color=True
)


def set_debug_mode(debug: bool):
    """
    设置调试模式
    
    Args:
        debug: True为调试模式，False为正常模式
    """
    global DEBUG_MODE
    DEBUG_MODE = debug
    level = LogLevel.DEBUG if debug else LogLevel.INFO
    logger.set_level(level)


def get_logger() -> Logger:
    """获取日志器实例"""
    return logger


# 便捷函数
def debug(message: str, *args, **kwargs):
    """调试日志"""
    logger.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """信息日志"""
    logger.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """警告日志"""
    logger.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """错误日志"""
    logger.error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """严重错误日志"""
    logger.critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """异常日志"""
    logger.exception(message, *args, **kwargs)

__all__ = [
    "set_debug_mode",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "get_logger",
]
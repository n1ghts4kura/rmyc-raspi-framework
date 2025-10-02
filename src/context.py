#
# context.py
# 全局上下文单例类
#
# @author n1ghts4kura
#

import threading
import typing as t
from bot.game_msg import GameMsgDictType

class GlobalContext:
    """
    全局上下文单例类
    
    用于存储和管理框架运行时的全局状态信息。
    采用线程安全的单例模式，确保全局只有一个上下文实例。
    
    属性:
        last_game_msg_dict: 最后接收到的游戏消息字典
    
    用法:
        >>> from context import GlobalContext
        >>> ctx = GlobalContext.get_instance()
        >>> ctx.last_game_msg_dict = {"keys": ["w", "a"]}
        >>> print(ctx.last_game_msg_dict)
    """
    
    _instance: t.Optional['GlobalContext'] = None
    _instance_lock = threading.Lock()
    
    def __new__(cls):
        """实现单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            with cls._instance_lock:
                # 双重检查锁定
                if cls._instance is None:
                    cls._instance = super(GlobalContext, cls).__new__(cls)
                    cls._instance._singleton_initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化全局上下文"""
        # 避免重复初始化
        if self._singleton_initialized:
            return
        
        self._singleton_initialized = True
        
        # 游戏消息相关
        self._last_game_msg_dict: GameMsgDictType = GameMsgDictType()
        self._game_msg_lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'GlobalContext':
        """
        获取 GlobalContext 单例实例。
        
        Returns:
            GlobalContext: 单例实例
        
        Example:
            >>> ctx = GlobalContext.get_instance()
        """
        if cls._instance is None:
            return cls()
        return cls._instance
    
    @property
    def last_game_msg_dict(self) -> GameMsgDictType:
        """
        获取最后接收到的游戏消息字典（线程安全）。
        
        Returns:
            GameMsgDictType: 游戏消息字典
        """
        with self._game_msg_lock:
            return self._last_game_msg_dict
    
    @last_game_msg_dict.setter
    def last_game_msg_dict(self, value: GameMsgDictType) -> None:
        """
        设置最后接收到的游戏消息字典（线程安全）。
        
        Args:
            value: 游戏消息字典
        """
        with self._game_msg_lock:
            self._last_game_msg_dict = value
    
# base.py
# 技能基类
#
# @author n1ghts4kura
# @date 25-12-7
#

import threading as t
from typing import Callable

from src import logger


class BaseSkill:
    """
    单个技能的基本实现
    """

    def __init__(
        self,
        binding_key: str,
        invoke_func: Callable[..., None],
        name: str | None = None
    ):
        """
        Args:
            binding_key (str): 绑定的按键
            invoke_func (Callable[..., None]): 调用的函数
            name (str | None, optional): 技能名称. 若为None则默认为"[按键]".
        """

        # 技能本体设计
        self.binding_key: int = ord(binding_key if binding_key.islower() else binding_key.lower()) # 绑定的按键 (统一小写)
        self.invoke_func: Callable[["BaseSkill", ], None] = invoke_func # 调用的函数

        # 技能状态
        self.thread: t.Thread | None = None # 运行的线程
        self.enabled: bool = False # 技能是否启用

        # 技能标识
        self.name: str = f"[{binding_key}]" if not name else name


    def invoke(self) -> None:
        """
        调用技能
        """
        self.thread = t.Thread(target=self.invoke_func, args=(self, ), daemon=True)
        self.thread.start()

        self.enabled = True
        logger.debug(f"技能 {self.name} 已启用")


    def cancel(self) -> None:
        """
        取消技能
        """
        if self.thread is not None and self.thread.is_alive():
            logger.debug(f"技能 {self.name} 正在取消中...")
            self.thread.join(timeout=5) # 等待线程结束 timeout参数效果=无
        self.enabled = False
        logger.debug(f"技能 {self.name} 已取消")


    def __str__(self) -> str:
        return f"技能 {self.name} (绑定按键: {self.binding_key}, 启用状态: {self.enabled})"


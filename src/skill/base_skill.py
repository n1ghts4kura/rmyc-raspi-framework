#
# skill.py
#
# @author n1ghts4kura
#

import threading as t
from typing import Callable

import logger as LOG


class BaseSkill:
    """
    单个技能的基本实现
    """

    def __init__(
        self,
        binding_key: str,
        invoke_func: Callable[..., None],
        invoke_args: list | Callable[..., list] | None = None,

        name: str | None = None
    ):
        """
        Args:
            binding_key (str): 绑定的按键
            invoke_func (Callable[..., None]): 调用的函数
            invoke_args (list | Callable[None, list] | None, optional): 调用函数的参数. 可以是固定的列表或动态获取的参数.
            name (str | None, optional): 技能名称. 若为None则默认为"[按键]".
        """

        # 技能本体设计
        self.binding_key: str = binding_key if binding_key.islower() else binding_key.lower() # 绑定的按键 (统一小写)
        self.invoke_func: Callable[["BaseSkill", ], None] = invoke_func # 调用的函数
        self.invoke_args: list | Callable[..., list] = invoke_args if invoke_args is not None else [] # 调用函数的参数

        # 技能状态
        self.thread: t.Thread | None = None # 运行的线程
        self.enabled: bool = False # 技能是否启用
        self.errored: bool = False # 技能是否出错

        # 技能标识
        self.name: str = f"[{binding_key}]" if not name else name


    def async_invoke(self) -> None:
        """
        异步调用技能
        """
        args = [self, ]
        if callable(self.invoke_args):
            args += self.invoke_args()
        else:
            args += self.invoke_args
        
        self.thread = t.Thread(target=self.invoke_func, args=args)
        self.thread.start()

        self.enabled = True
        self.errored = False
        LOG.debug(f"技能 {self.name} 已启用")


    def async_cancel(self) -> None:
        """
        异步取消技能
        """
        if self.thread is not None and self.thread.is_alive():
            LOG.debug(f"技能 {self.name} 正在取消中...")
            self.thread.join(timeout=5) # 等待线程结束 timeout参数效果=无
        self.enabled = False
        LOG.debug(f"技能 {self.name} 已取消")


    def set_errored(self, errored: bool = True) -> None:
        """
        设置技能错误状态（给技能调用函数用的）
        """

        self.errored = errored
        if errored:
            LOG.error(f"技能 {self.name} 出错")
        else:
            LOG.debug(f"技能 {self.name} 错误状态已清除")


    def __str__(self) -> str:
        return f"技能 {self.name} (绑定按键: {self.binding_key}, 启用状态: {self.enabled}, 错误状态: {self.errored})"

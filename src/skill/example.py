#
# example_skill.py
#
# @author n1ghts4kura
#

import time

from src.skill.base import BaseSkill
from src import logger
from src.uart.blaster import blaster_fire


def example_action(skill: BaseSkill, *args, **kwargs) -> None:
    """
    示例技能动作
    当按下 w 键时执行
    """

    logger.info("你好呀 我是example action.") 
    time.sleep(3)
    logger.info("SHOOT!!")
    blaster_fire()

skill = BaseSkill(
    binding_key="w", # **用小写字母注册！**
    invoke_func=example_action,
    name="示例技能"
)
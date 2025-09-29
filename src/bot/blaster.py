#
# robot/blaster.py
# 控制机器人发射器
#
# @author n1ghts4kura
#

import conn as serial

def set_blaster_bead(num: int) -> None:
    """
    设置单次发射量
    Args:
        num (int): 发射量，范围[1, 5]
    Raises:
        ValueError: 如果num不在范围[1, 5]内则抛出异常
    """
    if not (1 <= num <= 5):
        raise ValueError("num must be in range [1, 5]")

    serial.write_serial(f"blaster bead {num};")

def blaster_fire() -> None:
    """
    发射子弹
    """
    serial.write_serial("blaster fire;")

__all__ = ["set_blaster_bead", "blaster_fire"]

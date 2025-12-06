# blaster.py
# 枪管模块
#
# @author n1ghts4kura
# @date 25-12-6
#

from . import conn

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

    conn.writeline(f"blaster bead {num};")


def blaster_fire() -> None:
    """
    发射子弹
    """
    conn.writeline("blaster fire;")


__all__ = ["set_blaster_bead", "blaster_fire"]

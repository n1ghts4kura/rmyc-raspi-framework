# dataholder.py
# 串口数据管理模块
#
# @author n1ghts4kura
# @date 25-12-6
#

import threading
from queue import Queue
from dataclasses import dataclass

from . import conn
from src import logger


@dataclass
class GameData:
    """
    赛事数据
    """

    cmd_id:      int       # ???
    length:      int       # 数据包长度
    mouse_press: int       # 鼠标按键 1:左键 2:右键 4:中键
    mouse_x:     int       # 鼠标移动距离 [-100, 100]
    mouse_y:     int       # 鼠标移动距离 [-100, 100]
    seq:         int       # 序列号 ???
    key_num:     int       # 识别到的 键盘按下的按键数量 [0, 3]
    keys:        list[int] # 识别到的 键盘按下的按键 ord 值列表

class DataHolder:
    """
    串口数据管理类 单例类
    """

    def __init__(self):

        # 总数据队列
        self.data: Queue[str] = Queue()

        # 赛事数据
        self._game_data_list: list[GameData] = []

    
    # === 数据处理机制 ===

    def process_line(self, line: str) -> None:
        """
        处理单行数据

        Args:
            line (str): 单行数据
        """

        # === 赛事数据 ===
        # eg: game msg push [0, 6, 1, 0, 0, 255, 1, 199]
        if line.startswith("game msg push"):
            data = line.strip().split("[")[-1].strip("]").split(",") # 提取数据
            data = [int(i.strip()) for i in data]                    # 转为整数

            self._game_data_list.append(
                GameData(
                    cmd_id      = data[0],
                    length      = data[1],
                    mouse_press = data[2],
                    mouse_x     = data[3],
                    mouse_y     = data[4],
                    seq         = data[5],
                    key_num     = data[6],
                    keys        = data[7:7+data[6]]
                )
            )

            # 处理掉一部分*旧的*数据，避免内存占用过高
            if len(self._game_data_list) > 30:
                self._game_data_list = self._game_data_list[-10:] # 保留最新的 10 条数据 (虽然除了最新的 1 条数据，其他的都没什么用处)
        # === 过滤 "ok;" "Already in SDK mode;" 数据 ===
        elif line.startswith("ok;") or line.startswith("Already in SDK mode;"):
            pass
        # === ... ===
        # === 其他数据 ===
        else:
            self.data.put(line) # 放入总数据队列

    
    def fetch_and_process(self) -> None:
        """
        从串口处获取数据 并进行处理
        """

        lines = conn.readall()
        
        for line in lines:
            logger.info(f"分析了一条串口数据: {line}")
            self.process_line(line)

    
    # === 数据管理机制 ===

    @property
    def game_data(self) -> GameData | None:
        """
        获取最新的赛事数据

        Returns:
            GameData | None: 最新的赛事数据，若无数据则返回 None
        """

        if len(self._game_data_list) == 0:
            return None
        else:
            return self._game_data_list[-1]
    
    @property
    def pressed_keys(self) -> list[int]:
        """
        获取最新的键盘按键信息

        Returns:
            list[int]: 键盘按键 ord 值列表，若无数据则返回空列表
        """

        game_data = self.game_data

        if game_data is None:
            return []
        else:
            return game_data.keys


    # === 单例类机制 ===
    # 单例类设计
    _instance: 'DataHolder | None' = None
    _instance_lock = threading.Lock() # 线程锁 防止多个线程同时访问该类造成问题

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super(DataHolder, cls).__new__(cls)
        return cls._instance

        
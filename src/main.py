#
# main.py
#
# @author n1ghts4kura
#

import time
import typing

import logger as LOG
from bot.conn import open_serial, start_serial_worker, get_serial_command_nowait, close_serial
from bot.sdk import enter_sdk_mode, exit_sdk_mode
from bot.game_msg import game_msg_process, GameMsgDictType

# 技能
from skill.manager import SkillManager
from skill.example_skill import skill as example_skill

def main():
    try: 
        LOG.info("Framework 启动中...")

        # 端口配置
        LOG.info("正在打开串口...")
        result = open_serial()
        if not result:
            LOG.error("串口打开失败！请检查连接后重试。")
            return
        LOG.info("串口已打开。")
        start_serial_worker()
        exit_sdk_mode()

        # 技能配置
        LOG.info("正在配置技能...")
        global skill_manager
        skill_manager = SkillManager()
        skill_manager.add_skill(example_skill)

        # 上下文
        global last_game_msg_dict
        last_game_msg_dict = GameMsgDictType()

        LOG.info("正式启动前倒计时 5s")
        enter_sdk_mode()
        time.sleep(5)
        LOG.info("启动.")

        # 开始主循环
        while True:
            line = get_serial_command_nowait()
            if not line:
                continue
                
            LOG.debug(f"收到数据: {line.strip()}")
            if line.startswith("game msg push"):
                last_game_msg_dict = game_msg_process(line)
                LOG.info(f"获取到赛事消息: {last_game_msg_dict}")

            for key in last_game_msg_dict.get("keys", []):
                result = skill_manager.change_skill_state(key)
                if result:
                    # LOG.info(f"按键 {key} 触发技能状态变更是否成功: {result}")
                    pass
                else:
                    LOG.debug(f"按键 {key} 未绑定任何技能。")

    except Exception as e:
        exit_sdk_mode()
        close_serial()

        LOG.exception(str(e))
        LOG.error("异常退出.")

if __name__ == "__main__":
    main()

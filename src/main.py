#
# main.py
#
# @author n1ghts4kura
#

import time

import logger as LOG
from context import GlobalContext
from recognizer import Recognizer
from bot.conn import open_serial, start_serial_worker, get_serial_command_nowait, close_serial
from bot.sdk import enter_sdk_mode, exit_sdk_mode
from bot.game_msg import game_msg_process

# 技能
from skill.manager import SkillManager
from skill.example_skill import skill as example_skill

def main():
    try: 
        LOG.info("Framework 启动中...")

        # 初始化识别器
        LOG.info("正在初始化识别器...")
        recog = Recognizer.get_instance()
        recog.wait_until_initialized()
        LOG.info("识别器初始化完成")

        # 端口配置
        LOG.info("正在打开串口...")
        result = open_serial()
        if not result:
            LOG.error("串口打开失败！请检查连接后重试")
            return
        LOG.info("串口已打开")
        start_serial_worker()
        exit_sdk_mode()

        # 技能配置
        LOG.info("正在配置技能...")
        skill_manager = SkillManager()
        skill_manager.add_skill(example_skill)

        # 全局上下文
        ctx = GlobalContext.get_instance()

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
                ctx.last_game_msg_dict = game_msg_process(line)
                LOG.info(f"获取到赛事消息: {ctx.last_game_msg_dict}")

            for key in ctx.last_game_msg_dict.get("keys", []):
                if skill_manager.get_skill_enabled_state(key):
                    skill_manager.cancel_skill_by_key(key)
                else:
                    skill_manager.invoke_skill_by_key(key, game_msg_dict=ctx.last_game_msg_dict)

    except Exception as e:
        LOG.exception(str(e))
        LOG.error("异常退出.")
    finally:
        exit_sdk_mode()
        close_serial()

if __name__ == "__main__":
    main()

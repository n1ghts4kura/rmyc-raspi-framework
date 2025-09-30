import bot
import logger as LOG
import time
import sys

LOG.info("连接机器人...")
result =  bot.conn.init_serial()
LOG.info(f"连接结果: {result}")
if not result:
    sys.exit(-1)

bot.sdk.exit_sdk_mode()
bot.sdk.enter_sdk_mode()
time.sleep(1)
bot.blaster.blaster_fire()
time.sleep(3)
LOG.info("===开始测试===")

# blaster module

try:
    LOG.info("1. 发射器模块测试 五秒五连发")
    for i in range(5):
        bot.blaster.blaster_fire()
        time.sleep(1)

    LOG.info("2. 发射器模块测试 一次五联发")
    bot.blaster.set_blaster_bead(5)
    bot.blaster.blaster_fire()

    time.sleep(5)

    # chassis module

    LOG.info("3. 底盘模块测试 底盘3维度移动")
    bot.chassis.set_chassis_speed_3d(1.5, 2, 180)
    time.sleep(3)
    bot.chassis.set_chassis_speed_3d(0, 0, 0)

    time.sleep(2)

    LOG.info("4. 底盘模块测试 底盘轮子单独调速")
    bot.chassis.set_chassis_wheel_speed(100, 100, 300, 300)
    time.sleep(3)
    bot.chassis.set_chassis_wheel_speed(0, 0, 0, 0)

    time.sleep(2)

    LOG.info("5. 底盘模块测试 底盘移动距离")
    bot.chassis.chassis_move(3, 1.7, 270, 2, 200)
    time.sleep(10)
    bot.conn.write_serial("command;")
    # 2025/9/28 这一步耗时很久 不知道为什么

    # gimbal module

    LOG.info("6. 云台模块测试 控制云台相对运动 & 调整云台运动速度")
    bot.gimbal.set_gimbal_speed(360, 180)
    bot.gimbal.move_gimbal(20, 50, None, None)
    time.sleep(5)

    LOG.info("7. 云台模块测试 控制云台回中")
    bot.gimbal.set_gimbal_recenter()
    time.sleep(5)

    LOG.info("8. 云台模块测试 控制云台绝对运动 & 调整云台运动速度")
    bot.gimbal.set_gimbal_speed(0, 0) # ignore me plz
    bot.gimbal.move_gimbal_absolute(-20, 90, 180, 360)
    time.sleep(3)
    bot.gimbal.move_gimbal_absolute(20, 0, 90, None)
    time.sleep(5)
    bot.gimbal.set_gimbal_recenter()

    time.sleep(2)

    # robot module
    # 我不想测这个了。date 2025/9/28

    LOG.info("===测试结束===")
    time.sleep(1)
    sys.exit(0)
except Exception as e:
    LOG.exception(str(e))

bot.sdk.exit_sdk_mode()
sys.exit(0)

#!/usr/bin/env python3
#
# tools/test_serial.py
# 串口通信高层API测试脚本
#
# 用途：测试 src/bot/ 中所有硬件控制模块的高层API
# 使用：python tools/test_serial.py
#
# @author AI Assistant
# @date 2025/10/09
#

import sys
import time
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logger as LOG
from bot.conn import open_serial, close_serial, start_serial_worker, get_serial_command_nowait
from bot import sdk, gimbal, chassis, blaster, robot

os.system("sudo chmod 777 /dev/ttyUSB0")


def test_sdk_module():
    """测试 SDK 模块"""
    LOG.info("=" * 50)
    LOG.info("【SDK 模块测试】")
    LOG.info("=" * 50)
    
    LOG.info("1. 退出 SDK 模式")
    sdk.exit_sdk_mode()
    time.sleep(1)
    
    # 清空接收缓冲区，避免旧数据干扰
    while get_serial_command_nowait():
        pass
    
    LOG.info("2. 进入 SDK 模式")
    sdk.enter_sdk_mode()
    
    # ⭐ 关键：等待并验证下位机响应
    LOG.info("   等待下位机确认...")
    max_wait = 5  # 最多等待 5 秒
    start_time = time.time()
    success = False
    
    while time.time() - start_time < max_wait:
        response = get_serial_command_nowait()
        if response:
            LOG.info(f"   收到响应: {response.strip()}")
            if "ok" in response.lower():
                success = True
                break
        time.sleep(0.1)
    
    if success:
        LOG.info("✅ SDK 模式进入成功")
    else:
        LOG.error("❌ SDK 模式进入失败！后续测试可能无效")
        LOG.error("   提示：检查串口连接、波特率、下位机状态")
        return
    
    time.sleep(1)  # 额外等待，确保 SDK 模式稳定
    LOG.info("✅ SDK 模块测试完成")


def test_gimbal_module():
    """测试云台模块"""

    LOG.info("=" * 50)
    LOG.info("【云台模块测试】")
    LOG.info("=" * 50)
    
    # ⭐ 关键：在测试开始时确保正确模式
    LOG.info("0. 设置机器人模式为 free（云台控制必需）")
    robot.set_robot_mode("free")
    time.sleep(1.5)  # 给足够时间让模式生效
    
    LOG.info("1. 云台回中")
    gimbal.set_gimbal_recenter()
    time.sleep(5) # 等待回中完成
    
    LOG.info("2. 设置云台速度")
    gimbal.set_gimbal_speed(pitch=180, yaw=180)
    time.sleep(5) # 等待速度设置生效
    
    LOG.info("3. 云台相对旋转 - Pitch 向上 15°")
    gimbal.rotate_gimbal(pitch=15, yaw=None, vpitch=90, vyaw=None)
    time.sleep(2)
    
    LOG.info("4. 云台相对旋转 - Pitch 向下 15°")
    gimbal.rotate_gimbal(pitch=-15, yaw=None, vpitch=90, vyaw=None)
    time.sleep(2)
    
    LOG.info("5. 云台相对旋转 - Yaw 向右 30°")
    gimbal.rotate_gimbal(pitch=None, yaw=30, vpitch=None, vyaw=90)
    time.sleep(2)
    
    LOG.info("6. 云台相对旋转 - Yaw 向左 30°")
    gimbal.rotate_gimbal(pitch=None, yaw=-30, vpitch=None, vyaw=90)
    time.sleep(2)
    
    LOG.info("7. 云台协同控制 - Pitch + Yaw 同时移动")
    gimbal.rotate_gimbal(pitch=10, yaw=20, vpitch=90, vyaw=90)
    time.sleep(3)
    
    LOG.info("8. 云台回中")
    gimbal.set_gimbal_recenter()
    time.sleep(3)
    
    LOG.info("9. 云台绝对位置控制 - 测试 360° 旋转")
    LOG.info("   步骤 1: Yaw 50°")
    gimbal.rotate_gimbal_absolute(pitch=None, yaw=50, vpitch=None, vyaw=90)
    time.sleep(2)
    LOG.info("   步骤 2: Yaw 100°")
    gimbal.rotate_gimbal_absolute(pitch=None, yaw=100, vpitch=None, vyaw=90)
    time.sleep(2)
    LOG.info("   步骤 3: Yaw 150°")
    gimbal.rotate_gimbal_absolute(pitch=None, yaw=150, vpitch=None, vyaw=90)
    time.sleep(2)
    LOG.info("   步骤 4: Yaw -150° (测试反向)")
    gimbal.rotate_gimbal_absolute(pitch=None, yaw=-150, vpitch=None, vyaw=90)
    time.sleep(2)
    
    LOG.info("10. 云台回中")
    gimbal.set_gimbal_recenter()
    time.sleep(3)
    
    LOG.info("11. 云台挂起")
    gimbal.set_gimbal_suspend()
    time.sleep(2)
    
    LOG.info("12. 云台恢复")
    gimbal.set_gimbal_resume()
    time.sleep(2)
    
    LOG.info("✅ 云台模块测试完成")


def test_chassis_module():
    """测试底盘模块"""
    LOG.info("=" * 50)
    LOG.info("【底盘模块测试】")
    LOG.info("=" * 50)
    
    LOG.info("1. 底盘 3D 速度控制 - 前进")
    chassis.set_chassis_speed_3d(speed_x=0.5, speed_y=0, speed_z=0)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("2. 底盘 3D 速度控制 - 后退")
    chassis.set_chassis_speed_3d(speed_x=-0.5, speed_y=0, speed_z=0)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("3. 底盘 3D 速度控制 - 左平移")
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=-0.5, speed_z=0)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("4. 底盘 3D 速度控制 - 右平移")
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0.5, speed_z=0)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("5. 底盘 3D 速度控制 - 顺时针旋转")
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=100)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("6. 底盘 3D 速度控制 - 逆时针旋转")
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=-100)
    time.sleep(2)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("7. 底盘 3D 速度控制 - 组合运动 (前进 + 右平移 + 旋转)")
    chassis.set_chassis_speed_3d(speed_x=0.5, speed_y=-0.3, speed_z=50)
    time.sleep(3)
    chassis.set_chassis_speed_3d(speed_x=0, speed_y=0, speed_z=0)  # 停止
    time.sleep(1)
    
    LOG.info("8. 底盘轮子单独调速 - 测试")
    chassis.set_chassis_wheel_speed(w1=200, w2=200, w3=200, w4=200)
    time.sleep(2)
    chassis.set_chassis_wheel_speed(w1=0, w2=0, w3=0, w4=0)  # 停止
    time.sleep(1)
    
    LOG.info("9. 底盘移动到指定位置 (注意：此操作耗时较长)")
    LOG.info("   移动参数: x=0.5m, y=0.3m, vxy=0.5m/s, z=90°, vz=90°/s")
    chassis.chassis_move(distance_x=0.5, distance_y=0.3, degree_z=90, speed_xy=0.5, speed_z=90)
    LOG.info("   等待底盘移动完成...")
    time.sleep(8)  # 根据实际移动时间调整
    
    LOG.info("✅ 底盘模块测试完成")


def test_blaster_module():
    """测试发射器模块"""
    LOG.info("=" * 50)
    LOG.info("【发射器模块测试】")
    LOG.info("=" * 50)
    
    LOG.info("1. 单次发射 (默认 1 颗)")
    blaster.blaster_fire()
    time.sleep(2)
    
    LOG.info("2. 设置发射数量为 3 颗")
    blaster.set_blaster_bead(3)
    time.sleep(0.5)
    
    LOG.info("3. 发射 3 颗")
    blaster.blaster_fire()
    time.sleep(3)
    
    LOG.info("4. 连续发射测试 (5 次单发)")
    for i in range(5):
        LOG.info(f"   第 {i+1} 次发射")
        blaster.blaster_fire()
        time.sleep(1)
    
    LOG.info("5. 设置发射数量为 5 颗并发射")
    blaster.set_blaster_bead(5)
    time.sleep(0.5)
    blaster.blaster_fire()
    time.sleep(5)
    
    LOG.info("✅ 发射器模块测试完成")


# def test_robot_module():
#     """测试机器人模块"""
#     LOG.info("=" * 50)
#     LOG.info("【机器人模块测试】")
#     LOG.info("=" * 50)
    
#     LOG.info("1. 设置机器人模式为 free (自由模式)")
#     result = robot.set_robot_mode("free")
#     LOG.info(f"   设置结果: {result}")
#     time.sleep(2)
    
#     LOG.info("2. 设置机器人模式为 chassis_lead (底盘优先)")
#     result = robot.set_robot_mode("chassis_lead")
#     LOG.info(f"   设置结果: {result}")
#     time.sleep(2)
    
#     LOG.info("3. 设置机器人模式为 gimbal_lead (云台优先)")
#     result = robot.set_robot_mode("gimbal_lead")
#     LOG.info(f"   设置结果: {result}")
#     time.sleep(2)
    
#     LOG.info("4. 恢复为 free 模式")
#     result = robot.set_robot_mode("free")
#     LOG.info(f"   设置结果: {result}")
#     time.sleep(2)
    
#     LOG.info("✅ 机器人模块测试完成")


def main():
    """主测试流程"""
    LOG.info("=" * 60)
    LOG.info("  串口通信高层 API 测试脚本")
    LOG.info("  测试范围: SDK / 云台 / 底盘 / 发射器 / 机器人模块")
    LOG.info("=" * 60)
    
    # 1. 初始化串口连接
    LOG.info("\n【初始化串口连接】")
    result = open_serial()
    if not result:
        LOG.error("❌ 串口打开失败！请检查连接")
        sys.exit(1)
    LOG.info("✅ 串口打开成功")
    
    # 2. 启动后台接收线程
    LOG.info("启动串口后台接收线程...")
    start_serial_worker()
    time.sleep(1)
    
    try:

        robot.set_robot_mode("free")
        time.sleep(1)

        # 3. SDK 模块测试
        test_sdk_module()
        time.sleep(2)
        
        # 4. 云台模块测试
        test_gimbal_module()
        time.sleep(2)
        
        # 5. 底盘模块测试
        test_chassis_module()
        time.sleep(2)
        
        # 6. 发射器模块测试
        test_blaster_module()
        time.sleep(2)
        
        # 7. 机器人模块测试
        # test_robot_module()
        # time.sleep(2)
        
        # 测试完成
        LOG.info("\n" + "=" * 60)
        LOG.info("  🎉 所有模块测试完成！")
        LOG.info("=" * 60)
        
    except KeyboardInterrupt:
        LOG.warning("\n⚠️ 用户中断测试")
    except Exception as e:
        LOG.exception(f"❌ 测试过程中发生异常: {e}")
    finally:
        # 清理资源
        LOG.info("\n【清理资源】")
        LOG.info("退出 SDK 模式...")
        sdk.exit_sdk_mode()
        time.sleep(1)
        
        LOG.info("关闭串口连接...")
        close_serial()
        
        LOG.info("✅ 资源清理完成")
        LOG.info("\n测试脚本已退出")


if __name__ == "__main__":
    main()

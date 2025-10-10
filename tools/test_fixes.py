#!/usr/bin/env python3
"""
快速测试脚本 - 验证 Bug 修复
测试内容:
1. open_serial() 连接验证
2. set_gimbal_speed(0, 0) 不阻塞
3. set_gimbal_recenter() 正确回中
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import logger as LOG
from bot import conn, gimbal, sdk
import time

def test_connection():
    """测试连接验证"""
    LOG.info("=" * 60)
    LOG.info("【测试 1: 连接验证】")
    LOG.info("=" * 60)
    
    # open_serial 现在会自动启动线程并验证响应
    result = conn.open_serial()
    
    if result:
        LOG.info("✅ 连接验证通过!")
    else:
        LOG.error("❌ 连接验证失败!")
        sys.exit(1)

def test_gimbal_speed_zero():
    """测试 set_gimbal_speed(0, 0) 不阻塞"""
    LOG.info("\n" + "=" * 60)
    LOG.info("【测试 2: set_gimbal_speed(0, 0) 阻塞问题】")
    LOG.info("=" * 60)
    
    LOG.info("进入 SDK 模式...")
    sdk.enter_sdk_mode()
    time.sleep(1)
    
    LOG.info("调用 gimbal.set_gimbal_speed(0, 0, delay=True)...")
    start = time.time()
    gimbal.set_gimbal_speed(0, 0, delay=True)
    elapsed = time.time() - start
    
    LOG.info(f"⏱️  耗时: {elapsed:.2f} 秒")
    
    if elapsed < 1:
        LOG.info("✅ 测试通过! (预期: <1秒, 实际: {:.2f}秒)".format(elapsed))
    else:
        LOG.error(f"❌ 测试失败! 耗时过长: {elapsed:.2f}秒")

def test_gimbal_recenter():
    """测试云台回中"""
    LOG.info("\n" + "=" * 60)
    LOG.info("【测试 3: 云台回中功能】")
    LOG.info("=" * 60)
    
    LOG.info("先转动云台...")
    gimbal.rotate_gimbal(pitch=20, yaw=30, vpitch=180, vyaw=180, delay=True)
    time.sleep(1)
    
    LOG.info("调用云台回中...")
    start = time.time()
    gimbal.set_gimbal_recenter(delay=True)
    elapsed = time.time() - start
    
    LOG.info(f"⏱️  耗时: {elapsed:.2f} 秒")
    
    if 0.5 < elapsed < 2:
        LOG.info("✅ 测试通过! (预期: 0.5-2秒, 实际: {:.2f}秒)".format(elapsed))
    else:
        LOG.warning(f"⚠️  耗时异常: {elapsed:.2f}秒 (预期 0.5-2秒)")

def main():
    LOG.info("�� 开始测试 Bug 修复...")
    
    try:
        test_connection()
        test_gimbal_speed_zero()
        test_gimbal_recenter()
        
        LOG.info("\n" + "=" * 60)
        LOG.info("🎉 所有测试完成!")
        LOG.info("=" * 60)
        
    except KeyboardInterrupt:
        LOG.warning("\n⚠️ 测试被中断")
    except Exception as e:
        LOG.exception(f"❌ 测试失败: {e}")
    finally:
        sdk.exit_sdk_mode()
        conn.close_serial()

if __name__ == "__main__":
    main()

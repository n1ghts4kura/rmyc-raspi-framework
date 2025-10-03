"""
自瞄技能模块 - 技能系统集成。

本模块将自瞄功能封装为技能系统可调度的 Skill，支持按键触发、自动超时回中。

按键绑定：
    - 'z' 键：切换自瞄开关

工作流程：
    1. 按下 'z' 键启动自瞄
    2. 循环调用 aim_step() 进行目标跟踪
    3. 连续 12 帧无目标时自动回中并继续等待
    4. 再次按下 'z' 键停止自瞄

典型使用：
    from skill.auto_aim_skill import auto_aim_skill
    from skill.manager import SkillManager
    
    skill_manager = SkillManager()
    skill_manager.add_skill(auto_aim_skill)
"""

import time
import logger as LOG
import config
from recognizer import Recognizer
from skill.base_skill import BaseSkill
from aimassistant.pipeline import aim_step_v1, recenter_gimbal


def auto_aim_action(skill: BaseSkill, **kwargs):
    """
    自瞄技能的主执行函数。
    
    功能说明：
        - 循环调用 aim_step() 尝试瞄准目标
        - 跟踪连续无目标的帧数
        - 超过阈值时调用 recenter_gimbal() 回中
        - 通过 skill.enabled 检查技能状态
    
    Args:
        skill: BaseSkill 实例（用于检查 enabled 状态）
        **kwargs: 关键字参数
            - recognizer (Recognizer): 视觉识别器实例（必需）
    
    异常处理：
        - 捕获所有异常并记录日志
        - 异常发生后函数退出，线程自然结束
    """
    # 提取 recognizer 参数
    recognizer = kwargs.get("recognizer")
    if recognizer is None:
        LOG.error("自瞄技能启动失败：缺少 recognizer 参数")
        return
    
    try:
        LOG.info("自瞄技能已启动")
        lost_frames = 0  # 连续无目标的帧数计数器
        
        while skill.enabled:
            # 执行一次自瞄步骤
            success = aim_step_v1(recognizer)
            
            if success:
                # 成功瞄准，重置丢失计数器
                lost_frames = 0
            else:
                # 未检测到目标，递增计数器
                lost_frames += 1
                
                # 超过阈值时触发回中
                if lost_frames >= config.AIM_LOST_TARGET_TIMEOUT_FRAMES:
                    LOG.info(f"连续 {lost_frames} 帧无目标，执行回中")
                    recenter_gimbal()
                    lost_frames = 0  # 回中后重置计数器
            
            # 短暂休眠以匹配视觉识别频率
            time.sleep(1.0 / config.AIM_CONTROL_FREQUENCY)
        
        LOG.info("自瞄技能已停止")
        
    except Exception as e:
        LOG.exception(f"自瞄技能发生异常: {e}")
        # 异常后线程自然退出，enabled 状态由 SkillManager 的 cancel() 管理


# 创建技能实例（绑定 'z' 键）
auto_aim_skill = BaseSkill(
    binding_key="z",
    invoke_func=auto_aim_action,
    name="自动瞄准"
)

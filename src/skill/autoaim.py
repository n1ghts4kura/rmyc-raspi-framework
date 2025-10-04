#
# skill/autoaim.py
# 自瞄模块
#
# @author n1ghts4kura
# @date 2025/10/3
#


import time
import logger as LOG
import config
from recognizer import Recognizer
from skill.base_skill import BaseSkill
from bot.gimbal import set_gimbal_recenter, rotate_gimbal
from aimassistant.pipeline import aim_step_v1


def auto_aim_action(skill: BaseSkill):
    """
    自瞄技能的主执行函数。

    Args:
        skill: BaseSkill 实例（用于检查 enabled 状态）
    
    功能说明：
        - 循环调用 aim_step() 尝试瞄准目标
        - 跟踪连续无目标的帧数
        - 超过阈值时触发云台旋转搜索（持续固定方向旋转）
        - 通过 skill.enabled 检查技能状态
    
    搜索策略：
        - 当连续 N 帧无目标时，云台开始持续旋转搜索
        - 旋转角度根据相机 FOV 和推理速度动态计算
        - 每帧旋转固定角度，持续搜索直到重新检测到目标
    
    异常处理：
        - 捕获所有异常并记录日志
        - 异常发生后函数退出，线程自然结束
    """

    # 提取 recognizer 参数
    recognizer = Recognizer.get_instance()
    
    try:
        LOG.info("自瞄技能已启动")
        lost_frames = 0  # 连续无目标的帧数计数器
        
        # 计算自适应搜索角度
        # 获取实际推理 FPS（从 recognizer 状态中读取）
        status = recognizer.get_status()
        actual_fps = status.get('inference_fps', 4.0)  # 默认 4 FPS
        
        # 计算搜索步进角度
        # 公式：min(视野角度 × 覆盖率, 云台速度 / 推理FPS)
        # 含义：在推理间隔内，云台旋转的角度应该覆盖部分视野，避免漏掉目标
        search_step_angle = min(
            config.CAMERA_FOV_HORIZONTAL * config.AIM_SEARCH_FOV_COVERAGE,
            config.GIMBAL_SPEED / actual_fps
        )
        
        LOG.info(
            f"自瞄搜索参数: 推理FPS={actual_fps:.2f}, "
            f"搜索角度={search_step_angle:.1f}°, "
            f"视野覆盖={config.AIM_SEARCH_FOV_COVERAGE*100:.0f}%"
        )
        
        while skill.enabled:
            # 执行一次自瞄步骤
            success = aim_step_v1(recognizer)
            
            if success:
                # 成功瞄准，重置丢失计数器
                lost_frames = 0
            else:
                # 未检测到目标，递增计数器
                lost_frames += 1
                
                # 超过阈值时触发旋转搜索
                if lost_frames >= config.AIM_LOST_TARGET_TIMEOUT_FRAMES:
                    # 持续旋转搜索（每帧固定角度）
                    yaw_angle = search_step_angle * config.AIM_SEARCH_DIRECTION
                    rotate_gimbal(
                        pitch=None,  # 不改变 pitch
                        yaw=yaw_angle,
                        vpitch=None,
                        vyaw=config.GIMBAL_SPEED
                    )
                    LOG.debug(f"搜索模式：旋转 {yaw_angle:.1f}° (累计 {lost_frames} 帧无目标)")
            
            # 短暂休眠以匹配控制频率
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

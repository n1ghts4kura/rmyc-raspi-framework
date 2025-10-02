#
# manager.py
#
# @author n1ghts4kura
#

from skill.base_skill import BaseSkill
import logger as LOG

class SkillManager:
    """
    技能管理

    当按下某个绑定键时，调用对应的技能；若再次按下该键，则取消该技能。
    """

    def __init__(self) -> None:
        self.skills: list[BaseSkill] = []


    def add_skill(self, skill: BaseSkill) -> None:
        """
        添加技能

        Args:
            skill (BaseSkill): 要添加的技能实例
        Raises:
            ValueError: 如果绑定键已被其他技能使用
        """

        # 检查绑定键位是否重复
        for existing_skill in self.skills:
            if existing_skill.binding_key == skill.binding_key:
                LOG.error(f"无法添加技能 {skill.name}: 绑定键 {skill.binding_key} 已被技能 {existing_skill.name} 使用")
                raise ValueError(f"绑定键 {skill.binding_key} 已被使用")

        self.skills.append(skill)

        LOG.info(f"技能已添加: {skill.name}")

    
    def get_skill_enabled_state(self, binding_key: str) -> bool:
        """
        获取技能启用状态

        Args:
            binding_key (str): 绑定键
        Returns:
            bool: 技能是否启用
        """

        for skill in self.skills:
            if skill.binding_key == binding_key:
                return skill.enabled

        # LOG.info(f"无法获取绑定按键 {binding_key} 的技能状态")
        return False


    def invoke_skill_by_key(self, binding_key: str, *args, **kwargs) -> bool:
        """
        通过绑定键调用技能
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                skill.invoke(*args, **kwargs)
                LOG.info(f"技能 {skill.name} 已通过按键 {binding_key} 调用")
                return True

        LOG.warning(f"无法启动绑定按键 {binding_key} 的技能")
        return False


    def cancel_skill_by_key(self, binding_key: str) -> bool:
        """
        通过绑定键取消技能
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                skill.cancel()
                LOG.info(f"技能 {skill.name} 已通过按键 {binding_key} 取消")
                return True

        LOG.warning(f"无法取消绑定按键 {binding_key} 的技能")
        return False

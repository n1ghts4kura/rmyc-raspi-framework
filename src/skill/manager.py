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
    """

    def __init__(self) -> None:
        self.skills: list[BaseSkill] = []

    def add_skill(self, skill: BaseSkill) -> None:
        """
        添加技能
        """
        self.skills.append(skill)

        LOG.debug(f"技能已添加: {skill.name}")

    def invoke_skill_by_key(self, binding_key: str) -> bool:
        """
        通过绑定键调用技能
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                skill.async_invoke()
                LOG.debug(f"技能 {skill.name} 已通过按键 {binding_key} 调用")
                return True

        LOG.debug(f"无法启动绑定按键 {binding_key} 的技能")
        return False

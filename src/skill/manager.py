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
        """

        # 检查绑定键位是否重复
        for existing_skill in self.skills:
            if existing_skill.binding_key == skill.binding_key:
                LOG.error(f"无法添加技能 {skill.name}: 绑定键 {skill.binding_key} 已被技能 {existing_skill.name} 使用")
                raise ValueError(f"绑定键 {skill.binding_key} 已被使用")

        self.skills.append(skill)

        LOG.info(f"技能已添加: {skill.name}")


    def change_skill_state(self, binding_key: str) -> bool:
        """
        切换技能状态（调用或取消）
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                if skill.enabled:
                    return self._cancel_skill_by_key(binding_key)
                else:
                    return self._invoke_skill_by_key(binding_key)

        # LOG.debug(f"无法找到绑定按键 {binding_key} 的技能")
        return False


    def _invoke_skill_by_key(self, binding_key: str) -> bool:
        """
        通过绑定键调用技能
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                skill.async_invoke()
                LOG.info(f"技能 {skill.name} 已通过按键 {binding_key} 调用")
                return True

        LOG.info(f"无法启动绑定按键 {binding_key} 的技能")
        return False


    def _cancel_skill_by_key(self, binding_key: str) -> bool:
        """
        通过绑定键取消技能
        """
        for skill in self.skills:
            if skill.binding_key == binding_key:
                skill.async_cancel()
                LOG.info(f"技能 {skill.name} 已通过按键 {binding_key} 取消")
                return True

        LOG.info(f"无法取消绑定按键 {binding_key} 的技能")
        return False

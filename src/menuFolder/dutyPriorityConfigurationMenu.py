import numpy
import regex

import src
import tcod

class DutyPriorityConfigurationMenu(src.menues.SubMenu):
    def __init__(self,character,partner):
        self.type = "DutyPriorityConfigurationMenu"
        self.selected_duty = None
        self.character = character
        self.partner = partner
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):

        # exit menu
        if key in ("esc",):
            if self.followUp:
                self.callIndirect(self.followUp)
            self.done = True
            return True

        # get sorted duties
        duties = self._get_sorted_duties()
        if not self.selected_duty:
            self.selected_duty = duties[0]

        # handle general keypresses
        if key in ("w",):
            index = duties.index(self.selected_duty)
            index -= 1
            if index < 0:
                index = len(duties)-1
            self.selected_duty = duties[index]
        if key in ("s",):
            index = duties.index(self.selected_duty)
            index += 1
            if index >= len(duties):
                index = 0
            self.selected_duty = duties[index]
        if key in ("a",):
            priority = self.partner.dutyPriorities.get(self.selected_duty,1)
            priority -= 1
            if priority < 1:
                priority = 1
            self.partner.dutyPriorities[self.selected_duty] = priority
        if key in ("d",):
            priority = self.partner.dutyPriorities.get(self.selected_duty,1)
            priority += 1
            self.partner.dutyPriorities[self.selected_duty] = priority

        return False

    def getTitle(self):
        return "GROUNDSKEEPER DUTY PRIORITY CONFIGURATION"

    def render(self,size=None):
        duties = self._get_sorted_duties()
        text = []
        text.extend(["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You ask the groundskeeper to change its working priorities."),"""

The groundskeepers duties and its priorities are listed bellow.
High priority task will done before low priority tasks.
A high number indicates a high priority.


"""])
        for duty in duties:
            if duty == self.selected_duty:
                text.append(f"=> ")
            else:
                text.append(f"*  ")
            text.append(f"{duty}: {self.partner.dutyPriorities[duty]}\n")
        text.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),["""
press """,src.interaction.ActionMeta(payload="w",content="w"),"/",src.interaction.ActionMeta(payload="s",content="s"),""" to move cursor
""",src.interaction.ActionMeta(payload="a",content="press a to decrease priority"),"""
""",src.interaction.ActionMeta(payload="d",content="press a to increase priority"),"""
"""]))

        return text

    def _get_sorted_duties(self):
        duties = self.partner.duties[:]
        duties.sort()
        duties.sort(key=lambda duty: self.partner.dutyPriorities.get(duty,1), reverse=True)
        return duties

    def get_command_to_select_duty(self,target_duty):
        duties = self._get_sorted_duties()
        current_index = None
        target_index = None
        counter = 0
        for duty in duties:
            if duty == target_duty:
                target_index = counter
            if duty == self.selected_duty:
                current_index = counter
            counter += 1

        if current_index is None or target_index is None:
            return None
        return "s"*(target_index-current_index)+"w"*(current_index-target_index)

# register the menu type
src.menues.add_menu(DutyPriorityConfigurationMenu)

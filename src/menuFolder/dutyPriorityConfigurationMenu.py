import src

class DutyPriorityConfigurationMenu(src.menues.SubMenu):
    '''
    the menu to configure the duty priorities of a NPC
    '''
    _quest_descriptions = {
            "resource gathering": """Collecting Scrap from scrap fields""",
            "machine operation": """Using machines like ScrapCompactors""",
            "storage management": """Ensuring items are stacked and some storage is free""",
            "hauling": """Carrying items between stockpiles within rooms""",
            "maggot gathering": """Collecting VatMaggots from Trees""",
            "metal working": """Producing items at a MetalWorkingBench""",
            "painting": """Painting markers and draw floor plans""",
            "praying": """Praying and sacrifice""",
            "resource fetching": """Carrying items between stockpiles between rooms""",
            "room building": """Building new rooms""",
            "scavenging": """Collecting items from outside the base""",
            "scrap hammering": """Hammering Scrap into MetalBars""",
            "cleaning": """Ensuring that the walkinspaces are traversable""",
            "machine placing": """Placing items on build sites""",
            "manufacturing": """Producing items at ManufacturingTables""",
            "mold farming": """Farming and harvest mold""",
        }
    def __init__(self,character,partner):
        self.type = "DutyPriorityConfigurationMenu"
        self.selected_duty = None
        self.character = character
        self.partner = partner
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        '''
        handle keypresses
        '''

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
        if key in ("w","up",):
            index = duties.index(self.selected_duty)
            index -= 1
            if index < 0:
                index = len(duties)-1
            self.selected_duty = duties[index]
        if key in ("s","down",):
            index = duties.index(self.selected_duty)
            index += 1
            if index >= len(duties):
                index = 0
            self.selected_duty = duties[index]
        if key in ("a","left",):
            priority = self.partner.dutyPriorities.get(self.selected_duty,1)
            priority -= 1
            if priority < 1:
                priority = 1
            self.partner.dutyPriorities[self.selected_duty] = priority
            self.partner.changed("changedDutyPriority",{"duty":self.selected_duty,"character":self.partner})
        if key in ("d","right",):
            priority = self.partner.dutyPriorities.get(self.selected_duty,1)
            priority += 1
            self.partner.dutyPriorities[self.selected_duty] = priority
            self.partner.changed("changedDutyPriority",{"duty":self.selected_duty,"character":self.partner})

        return False

    def getTitle(self):
        '''
        generates the menu title
        '''
        return "DUTY PRIORITY CONFIGURATION"

    def render(self,size=None):
        '''
        generate the text representation of the menu
        '''

        # set up helper variables
        text = []

        # show general description
        text.extend(["""
""",(src.interaction.highlighted_ui_attr,f"You ask {self.partner.name} to change its working priorities."),"""

The clones duties and its priorities are listed below.
High priority tasks will done before low priority tasks.
A high number indicates a high priority.


"""])

        # generate the list of duties
        duties = self._get_sorted_duties()
        for duty in duties:
            if duty == self.selected_duty:
                text.append(f"=> ")
            else:
                text.append(f"*  ")
            text.append(f"{duty}: {self.partner.dutyPriorities.get(duty,1)}\n")

        # show a descrition for the selected duty
        description = self._quest_descriptions.get(self.selected_duty)
        if description:
            text.append("\n\n")
            text.append(description)
            text.append("\n\n")

        # show the general usage instructions
        text.append((src.interaction.shadowed_ui_attr,["""
press """,src.interaction.ActionMeta(payload="w",content="w"),"/",src.interaction.ActionMeta(payload="s",content="s"),""" to move cursor
""",src.interaction.ActionMeta(payload="a",content="press a to decrease priority"),"""
""",src.interaction.ActionMeta(payload="d",content="press a to increase priority"),"""
"""]))

        # return the generated text
        return text

    def _get_sorted_duties(self):
        '''
        returns the duties sorted in a specific way
        '''
        duties = self.partner.duties[:]
        duties.sort()
        duties.sort(key=lambda duty: self.partner.dutyPriorities.get(duty,1), reverse=True)
        return duties

    def get_command_to_select_duty(self,target_duty):
        '''
        generate a series of keystrokes to select a certain duty
        '''

        # get the indices
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

        # return the actual command
        if current_index is None or target_index is None:
            return None
        return "s"*(target_index-current_index)+"w"*(current_index-target_index)

# register the menu type
src.menues.add_menu(DutyPriorityConfigurationMenu)

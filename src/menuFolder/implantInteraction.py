import src

class ImplantInteraction(src.menues.SubMenu):
    """
    a menu showing a text
    """

    type = "ImplantInteraction"

    def __init__(self,character):
        """
        initialise internal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.character = character
        self.submenu = None

    def getTitle(self):
        return "IMPLANT INTERACTION"

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        if key == "esc":
            return True

        if key == "q":
            character.add_submenu(src.menuFolder.questMenu.QuestMenu(char=character))
            return True

        if src.gamestate.gamestate.stern.get("first_reachout_done") == None:
            src.gamestate.gamestate.stern["first_reachout_done"] = False
        else:
            src.gamestate.gamestate.stern["first_reachout_done"] = True

        if self.submenu:
            if self.submenu.tag == "implant_meta_action_selection":
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection == "abort quest":
                    character.clear_quests()
            else:
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection:
                    task_type = self.submenu.extraInfo.get("task_type")

                    if selection == "yes":
                        if src.gamestate.gamestate.stern.get("first_quest_assign") == None:
                            src.gamestate.gamestate.stern["first_quest_assign"] = True
                        if src.gamestate.gamestate.stern["first_quest_assign"]:
                            src.gamestate.gamestate.stern["first_quest_assign"] = False
                            character.showTextMenu("""
You can see the quest description and general instructions in the quest menu.
""")

                        terrain = character.getHomeTerrain()
                        groundskeepers_place = None
                        for room in terrain.rooms:
                            if room.tag != "the groundskeepers place":
                                continue
                            groundskeepers_place = room

                        quest = None
                        if task_type == "escape_lab":
                            quest = src.quests.questMap["EscapeLab"]()
                        elif task_type == "reach_shelter":
                            quest = src.quests.questMap["GoToTile"](targetPosition=groundskeepers_place.getPosition())
                        elif task_type == "free_groundskeeper":
                            quest = src.quests.questMap["ActivateItem"](targetPosition=(6,6,0),targetPositionBig=groundskeepers_place.getPosition())
                        elif task_type == "fix_groundskeeper":
                            quest = src.quests.questMap["FixGroundskeeper"]()
                        elif task_type == "help_groundskeeper":
                            quest = src.quests.questMap["HelpGroundskeeper"]()
                        elif task_type == "wait_explosion":
                            quest = src.quests.questMap["WatchLabBurn"]()
                        elif task_type == "kill_spiderling":
                            quest = src.quests.questMap["SecureTile"](toSecure=(7,5,0),endWhenCleared=True,reason="clear the path",simpleAttacksOnly=True,noHeal=True)
                        elif task_type == "explore":
                            quest = src.quests.questMap["StoryExploreHomeTerrain"](lifetime=500)
                        if quest:
                            character.assignQuest(quest)
                        else:
                            character.notify("failed generating quest")

                    if selection == "skip":
                        if task_type == "wait_explosion":
                            src.gamestate.gamestate.stern["skipped_explosion"] = True
                        self.submenu = None

                    if self.submenu:
                        character.changed("completed implant interaction")
                        self.done = True
                        return True
                if self.submenu:
                    return False

        implant_intro_text = ""
        if not src.gamestate.gamestate.stern["first_reachout_done"]:
            implant_intro_text = """
You must be confused.

I'm your implant and i'm here to help you.
You can contact me any time by pressing tab.
"""

        if len(character.quests) > 0 and not character.quests[0].type == "ReachOutStory":
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You already have an active quest."),"""

Press q to open the quest menu and see the quest description.
I also try to calcuate the keystrokes needed to solve the quest.
This suggested action is shown on the left side of the screen.

What do you want to do?
"""]
            options = [("abort quest","abort active quest"),("continue","continue")]
            self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
            self.submenu.handleKey(key, noRender, character)
            self.submenu.tag = "implant_meta_action_selection"
            return False

        if character.container.tag == "the architects tomb":    
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Hello!"),f"""

{implant_intro_text}

The machinery around you is burning and exploding.
So i recommend leaving the room before you get hurt.

The exit is on the north side, you can move by pressing the wasd keys.
You can move my clicking on the map as well.

Big items like the machinery will block your movement.


""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Shall i assign you a quest to leave the room to avoid the explosion?"""),"""
"""]
            options = [("yes","yes"),("no","no")]
            self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
            self.submenu.handleKey(key, noRender, character)
            self.submenu.extraInfo["task_type"] = "escape_lab"
            return False

        terrain = character.getHomeTerrain()

        # wait for lab to burn down
        if not src.gamestate.gamestate.stern.get("skipped_explosion"):
            tombCandidates = terrain.getRoomByPosition((7,7,0))
            if tombCandidates and tombCandidates[0].tag == "the architects tomb":
                base_text = ["""
You made it out of the burning room.
We are safe for a second, but the room will explode soon.

Watch the room burn down.
You can pass time by pressing the "." key.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Shall i assign you a quest to watch the room explode?"""),"""
"""]
                extraDescriptions = {}
                options = [("yes","yes"),("no","no"),("skip","skip")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "wait_explosion"
                return False

        # wake builder
        wakeable_builder = False
        groundskeepers_place = None
        for room in terrain.rooms:
            if room.tag != "the groundskeepers place":
                continue
            groundskeepers_place = room
            items = room.getItemsByType("StasisTank")
            if not items:
                continue
            wakeable_builder = True
        if wakeable_builder: 

            # kill enemy
            if character.getBigPosition() == (7,6,0) and terrain.getCharactersOnTile((7,5,0)):
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""
{implant_intro_text}
You are outside and need to find shelter.

There is shelter to the north,
but """,(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""there is an enemy blocking your path."""),"""
kill the enemy. Enemy are shown with red edges.

The simplest way to fight enemies is to walk against them.
This will trigger an attack.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to kill the enemy?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "kill_spiderling"
                return False


            # go inside
            if not character.container.isRoom:
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

{implant_intro_text}

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""You are outside and need to find shelter."""),"""
The old groundskeepers place is nearby.
Go there.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to find shelter?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "reach_shelter"
                return False

            if not character.container.tag == "the groundskeepers place":
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


Explore the rooms and try to find something useful.

There is a StasisTank in the groundskeepers place. Look there.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to go to the groundskeepers place?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "reach_shelter"
                return False

            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


There is a StasisTank in this room. 
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""It should contain a survivior."""),"""
That could be useful for us.

Free the survivor.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to free the survivor?"""),"""
"""]
            options = [("yes","yes"),("no","no")]
            self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
            self.submenu.handleKey(key, noRender, character)
            self.submenu.extraInfo["task_type"] = "free_groundskeeper"
            return False

        groundsKeeper = None
        for check_character in terrain.getAllCharacters():
            if not check_character.faction == character.faction:
                continue
            if check_character == character:
                continue
            groundsKeeper = check_character
        
        if groundsKeeper:
            if not groundsKeeper.registers.get("startedWorking"):
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""The groundskeeper lives."""),"""
This could be very useful.

It doesn't work though.
Find out why.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to talk to the survivor?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "fix_groundskeeper"
                return False

            if not groundsKeeper.registers.get("gotPainter"):
                # help groundskeeper set up
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

The groundskeeper is working now,
but it seems to missing something very essential.

Check if you can help out.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to help to groundskeeper?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "help_groundskeeper"
                return False

            if groundskeepers_place.floorPlan:
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

The groundskeeper seems to be busy.
We cannot help right now.

I think we should explore the ruins around us a bit.

There are many useful items around.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to explore the environment?"""),"""
"""]
                options = [("yes","yes"),("no","no")]
                self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
                self.submenu.handleKey(key, noRender, character)
                self.submenu.extraInfo["task_type"] = "explore"
                return False

            # help groundskeeper set up
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

The groundskeeper is working now.
It will start to rebuild its working area.

Help it get set up.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to help to groundskeeper?"""),"""
"""]
            options = [("yes","yes"),("no","no")]
            self.submenu = src.menuFolder.selectionMenu.SelectionMenu(base_text,options=options)
            self.submenu.handleKey(key, noRender, character)
            self.submenu.extraInfo["task_type"] = "help_groundskeeper"
            return False
        1/0

    def render(self):
        if self.submenu:
            return self.submenu.render()
        else:
            return ["""something went wrong"""]

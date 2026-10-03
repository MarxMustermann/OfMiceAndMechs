import src

# bad code: uses global function to render
class UIConfigMenu(src.menues.SubMenu):
    """
    the submenue to help configuring the UI
    """

    type = "UIConfigMenu"

    def __init__(self,character):
        self.skipKeypress = True
        super().__init__()
        self.index = 0
        self.character = character
        self.menu_creation = False
        self.menu_to_add = None

    def getTitle(self):
        return "UI CONFIGURATION"

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # handle menu creation
        if self.menu_creation:
            if key in ("q",):
                self.menu_to_add = src.menues.menuMap["QuestMenu"](char=character)
            if key in ("i",):
                self.menu_to_add = src.menues.menuMap["InventoryMenu"](char=character)
            if key in ("v",):
                self.menu_to_add = src.menues.menuMap["CharacterInfoMenu"](char=character)
            if key in ("x",):
                self.menu_to_add = src.menues.menuMap["MessagesMenu"](char=character)
            if self.menu_to_add:
                self.menu_to_add.sidebared = True
            self.menu_creation = False
            return False

        if self.menu_to_add:
            if key in ("lESC",):
                self.character.rememberedMenu.append(self.menu_to_add)
            if key in ("rESC",):
                self.character.rememberedMenu2.append(self.menu_to_add)
            self.menu_to_add = None
            return False

        if self.skipKeypress:
            self.skipKeypress = False
            key = "~"

        # exit the submenu
        if key in ("esc"," ",):
            return True

        # remove sidebared menues
        if key in ("lESC",):
            if self.character.rememberedMenu:
                self.character.rememberedMenu.pop()
        if key in ("rESC",):
            if self.character.rememberedMenu2:
                self.character.rememberedMenu2.pop()
        if key in ("j","J",):
            self.menu_creation = True
        if key in ("C","R",):
            self.character.rememberedMenu = []
            self.character.rememberedMenu2 = []
        if key in ("R",):
            menu = src.menues.menuMap["QuestMenu"](char=character)
            menu.sidebared = True
            self.character.rememberedMenu.append(menu)

            menu = src.menues.menuMap["InventoryMenu"](char=character)
            menu.sidebared = True
            self.character.rememberedMenu2.append(menu)

            menu = src.menues.menuMap["MessagesMenu"](char=character)
            menu.sidebared = True
            self.character.rememberedMenu2.append(menu)

        return False

    def render(self,size=None):
        txt = []
        left_UI = []
        right_UI = []
        infos = ["What do you want to do?",""]
        commands = [
                        src.interaction.ActionMeta(payload=["C"],content="press C to reset UI"),
                        src.interaction.ActionMeta(payload=["R"],content="press R to reset UI"),
                        src.interaction.ActionMeta(payload=["j"],content="press j to add UI element"),
                        src.interaction.ActionMeta(payload=["lESC"],content="press escape + left shift to remove top UI element from the left"),
                        src.interaction.ActionMeta(payload=["rESC"],content="press escape + right shift to remove top UI element from the right"),
                        src.interaction.ActionMeta(payload=["esc"],content="press esc to close menu"),
                   ]
        if self.menu_creation:
            infos = ["What do menu do you want to add?",""]
            commands = [
                            src.interaction.ActionMeta(payload=["q"],content="press q to add quest menu"),
                            src.interaction.ActionMeta(payload=["i"],content="press i to add inventory"),
                            src.interaction.ActionMeta(payload=["v"],content="press v to add character information"),
                            src.interaction.ActionMeta(payload=["x"],content="press x to add message log"),
                       ]
        if self.menu_to_add:
            infos = [self.menu_to_add.getTitle(),"","Where do you want to add the menu?",""]
            commands = [
                        src.interaction.ActionMeta(payload=["lESC"],content="press escape + left shift to add UI element to the left"),
                        src.interaction.ActionMeta(payload=["rESC"],content="press escape + right shift to add UI element to the right"),
                       ]
        for menu in reversed(self.character.rememberedMenu):
            left_UI.append(menu.getTitle())
        for menu in reversed(self.character.rememberedMenu2):
            right_UI.append(menu.getTitle())

        num_rows = max(len(left_UI),len(right_UI),len(commands)+len(infos))
        for i in range(0,num_rows):
            left_text = ""
            if i < len(left_UI):
                left_text = left_UI[i]
            txt.append(left_text.ljust(20," "))
            center_witdh = 80
            center_text = ""
            if i < len(infos):
                center_text = infos[i]
            elif i < len(commands)+len(infos):
                center_text = (src.interaction.disabled_ui_attr,commands[i-len(infos)])
            spacer_size = center_witdh-len(src.interaction.stringifyUrwid(center_text))
            txt.append(" "*(spacer_size//2))
            txt.append(center_text)
            txt.append(" "*(spacer_size-(spacer_size//2)))
            right_text = ""
            if i < len(right_UI):
                right_text = right_UI[i]
            txt.append(right_text.rjust(20," "))
            txt.append("\n")
        return txt
        txt = []
        txt.append((src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"#000"),"press a/d to move cursor\n"))
        title = ""
        color = "#666"
        if self.index == 0:
            color = "#fff"
            title = "overview"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"\n[ overview ] "))
        color = "#666"
        if self.index == 1:
            color = "#fff"
            title = "implant"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"[ implant ] "))
        color = "#666"
        if self.index == 2:
            color = "#fff"
            title = "keybindings"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"[ keybindings ] "))
        color = "#666"
        if self.index == 3:
            color = "#fff"
            title = "submenues"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"[ submenues ] "))
        color = "#666"
        if self.index == 4:
            color = "#fff"
            title = "user interface"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"[ user interface ]\n"))

        txt.append("\n")
        txt.append("\n")
        txt.append((src.interaction.urwid.AttrSpec("#aa5", "#000"),f"== {title} =="))
        txt.append("\n")
        txt.append("\n")

        if self.index == 0:
            txt.append("\n")
            txt.append("This is the help menu. It covers various topics.\n\npress a and d to switch between the topics\n")
            txt.append("press esc to close this menu")
        if self.index == 1:
            txt.append("\n")
            txt.append("The implant is your main help in this game.\n")
            txt.append("It will guide you from start to end and will always show you what keys to press to progress.\n")
            txt.append("On easy difficuly you can finish the game by blindly typing down the keys shown.\n")
            txt.append("The keys to press are shown on the left side of the screen as \"suggested action\".\n\n")
            txt.append("You are very welcome to not do what the implant suggests.\n")
            txt.append("The implants instructions will try to adapt as good as it can.\n")
            txt.extend(["""

Instructions on how to complete your quests will be shown on the left side on the screen.
Keep in mind that capital letters have to be pressed as shift+letter.
Capital letters will be shown in blueish tint.

For example:

if the suggested action is \" """,(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"C"),""" w x":

    press shift+c then
    press w then
    press x
""",])

        if self.index == 2:
            txt.append("\n= movement =\n\n")
            txt.append("  w/a/s/d - move north/east/south/west (up/left/down/right)\n")
            txt.extend(["  ",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"W"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"A"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"S"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"D")," - special move north/east/south/west\n"])
            txt.append("\n= wait =\n\n")
            txt.extend(["  ./",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),":"),"/,/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),";")," - wait 1 turn / 0.1 turn / enemy approach / enemy nearby\n"])
            txt.append("\n= item interaction =\n\n")
            txt.extend(["  j/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"J")," - activate items\n"])
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"those are the day to day normal interactions, like using a machine\n"))
            txt.extend(["  c/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"C")," - complex activate items\n"])
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"those are the more absurd enteractions, like unbolting or configuring a machine\n"))
            txt.extend(["  k/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"K")," - pick up item\n"])
            txt.extend(["  l/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"L")," - drop item\n"])
            txt.append("\n")
            txt.append("  lowercase keys work on the square you stand on or the last item you bumped into\n")
            txt.append("  uppercase keys open a secondary menu for selection what to interact with\n")
            txt.append("\n= fighting =\n\n")
            txt.append("  w/a/s/d - attack north/east/south/west\n")
            txt.extend(["  ",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"W"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"A"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"S"),"/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"D")," - alternate attack north/east/south/west\n"])
            txt.append("  f       - shoot\n")
            txt.append("  m       - attack enemy on the same square\n")

        if self.index == 3:
            txt.append("\n")
            txt.append("tab - implant interaction\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"allows you to get in contact with your implant\n"))
            txt.append("o   - observe\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"get descriptions of things around you\n"))
            txt.extend([(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"O"),"   - observe alternates\n"])
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"get information about your environment\n"))
            txt.extend(["e/",(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"E")," - examine nearby items\n"])
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"examane an item closer\n"))
            txt.append("q   - open quests\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"shows current quests and allows you to change them\n"))
            txt.extend([(src.interaction.urwid.AttrSpec(src.interaction.upper_case_letter_color,"#000"),"Q"),"   - open advanced quest menu\n"])
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"allows you to create quest\n"))
            txt.append("i   - open inventory\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"shows what item you carry\n"))
            txt.append("x   - open message log\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"shows what happened the last turns\n"))
            txt.append("v   - open character overview\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"shows your characters stats\n"))
            txt.append("p   - cast magic\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"allows you to use the arcane power\n"))
            txt.append("g   - open action menu\n")
            txt.append((src.interaction.urwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"allows you to do special actions\n"))
            txt.append("\n\nPress esc to close submenues.\nSome menues can be docked/undocked by pressing esc+rCTRL or esc+lCTRL.")

        if self.index == 4:
            txt.append("\n")
            txt.append("ESC      - open main menu\n")
            txt.append("F11      - toggle fullscreen\n")
            txt.append("ctrl +/- - zoom in/out\n")
            txt.append("\n")
            txt.append("\n")

        if self.index > 1:
            txt.append("\n")
            txt.append("\n")
            txt.append("\n")
            txt.append("sadly the controls cannot be changed at the moment\n")
            txt.append("if you have issues with the character running into walls, tap the keys instead of holding them")
        txt.append("\n")

        return txt

# register the menu type
src.menues.add_menu(UIConfigMenu)

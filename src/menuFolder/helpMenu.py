import src

# bad code: uses global function to render
class HelpMenu(src.subMenu.SubMenu):
    """
    the help submenue
    """

    type = "HelpMenu"

    def __init__(self):
        self.skipKeypress = True
        super().__init__()
        src.interaction.send_tracking_ping("opened_help_menu")
        self.index = 0

    def getTitle(self):
        return "HELP"

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        character.changed("opened help menu",{})

        if self.skipKeypress:
            self.skipKeypress = False
            key = "~"

        # exit the submenu
        if key in ("esc"," ","?","z"):
            character.changed("closedHelp")
            return True

        if key in ("s","down",):
            self.index += 1
        if key in ("w","up",):
            self.index -= 1

        if self.index < 0:
            self.index = 3
        if self.index > 3:
            self.index = 0

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.render()))

        return False

    def render(self):
        txt = []
        txt.append("press w/s to move cursor\n")
        title = ""
        color = "#666"
        if self.index == 0:
            color = "#fff"
            title = "implant"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"\n== implant ="))
        color = "#666"
        if self.index == 1:
            color = "#fff"
            title = "keybindings"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"\n= keybindings ="))
        color = "#666"
        if self.index == 2:
            color = "#fff"
            title = "user interface"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"= user interface ="))
        color = "#666"
        if self.index == 3:
            color = "#fff"
            title = "submenues"
        txt.append((src.interaction.urwid.AttrSpec(color, "#000"),"= submenues==\n"))

        txt.append((src.interaction.urwid.AttrSpec("#fff", "#000"),f"\n\n== {title} ==\n"))
        if self.index == 0:
            txt.append("\n")
            txt.append("The implant is your main help in this game.\n")
            txt.append("It will guide you from start to end and will always show you what keys to press to progress.\n")
            txt.append("On easy difficuly you can finish the game by blindly typing down the keys shown.\n")
            txt.append("The keys to press are shown on the left side of the screen as \"suggested action\".\n\n")
            txt.append("You are very welcome to not do what the implant suggests.\n")
            txt.append("The implants instructions will try to adpapt as good as it can.\n")

        if self.index == 1:
            txt.append("\n  = movement =\n\n")
            txt.append("w/a/s/d - move north/east/south/west (up/left/down/right)\n")
            txt.append("use shift for special movement\n")
            txt.append("\n  = wait =\n\n")
            txt.append("./:/,/; - wait 1 turn / 0.1 turn / enemy approach / enemy nearby\n")
            txt.append("\n  = item interaction =\n\n")
            txt.append("j/J - activate items\n")
            txt.append("c/C - complex activate items\n")
            txt.append("k/K - pick up item\n")
            txt.append("l/L -  drop item\n")
            txt.append("\n")
            txt.append("lowercase keys work on the square you stand on or the last item you bumped into\n")
            txt.append("uppercase keys open a secondary menu for selection what to interact with\n")
            txt.append("\n  = fighting =\n\n")
            txt.append("w/a/s/d - attack north/east/south/west\n")
            txt.append("use shift for alternate attacks\n")
            txt.append("f - shoot\n")
            txt.append("m - attack enemy on the same square\n")
        if self.index == 2:
            txt.append("\n")
            txt.append("o: observe\n")
            txt.append("O: observe alternates\n")
            txt.append("e/E - examine nearby items\n")
            txt.append("q: open quests\n")
            txt.append("Q: open advanced quest menu\n")
            txt.append("i: open inventory\n")
            txt.append("x: open message log\n")
            txt.append("v: open character overwiev\n")
            txt.append("p: cast magic\n")

        if self.index == 3:
            txt.append("\n")
            txt.append("F11: toggle fullscreen\n")
            txt.append("ctrl +/-: zoom in/out\n")
            txt.append("\n")
            txt.append("\n")
        txt.append("\n")
        txt.append("\n")
        txt.append("\n")
        txt.append("sadly the controls cannot be changed at the moment\n")
        txt.append("if you have issues with the character running into walls, tap the keys instead of holding them\n")

        return txt

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

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.render()))

        return False

    def render(self):
        txt = ""
        txt += "\n== keybindings ==\n\n"
        txt += "\n= movement =\n"
        txt += " w/a/s/d - move north/east/south/west (up/left/down/right)\n"
        txt += " use shift for special movement\n"
        txt += "\n= wait =\n"
        txt += " ./:/,/; - wait 1 turn / 0.1 turn / enemy approach / enemy nearby\n"
        txt += "\n= item interaction =\n"
        txt += " j/J - activate items\n"
        txt += " c/C - complex activate items\n"
        txt += " k/K - pick up item\n"
        txt += " l/L -  drop item\n"
        txt += " e/E - examine item\n"
        txt += "\n"
        txt += "lowercase keys work on the square you stand on or the last item you bumped into\n"
        txt += "uppercase keys open a secondary menu for selection what to interact with\n"
        txt += "\n= fighting =\n"
        txt += " w/a/s/d - attack north/east/south/west\n"
        txt += " use shift for alternate attacks\n"
        txt += " f - shoot\n"
        txt += " m - attack enemy on the same square\n"
        txt += "\n= user interface =\n"
        txt += " o: observe\n"
        txt += " q: open quests\n"
        txt += " Q: open advanced quest menu\n"
        txt += " i: show inventory\n"
        txt += " F11: toggle fullscreen\n"
        txt += " ctrl +/-: zoom in/out\n"
        txt += "\n"
        txt += "sadly the controls cannot be changed at the moment\n"
        txt += "if you have issues with the character running into walls, tap the keys instead of holding them\n"
        txt += "\n"
        txt += ""

        return txt

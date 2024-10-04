
import SubMenu

from src.interaction import header, main, urwid


# bad code: uses global function to render
class HelpMenu(SubMenu):
    """
    the help submenue
    """

    type = "HelpMenu"

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," "):
            character.changed("closedHelp")
            return True

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))

        txt = ""
        txt += "\n= movement =\n"
        txt += " w/a/s/d: move north/east/south/west (up/left/down/right)\n"
        txt += " W/A/S/D: dash north/east/south/west (up/left/down/right)\n"
        txt += " .: wait\n"
        txt += "\n= item interaction =\n"
        txt += " j/J: activate items\n"
        txt += " c/C: complex activate items\n"
        txt += " k/K: pick up item\n"
        txt += " l/L: drop item\n"
        txt += " e/E: examine item\n"
        txt += "\n"
        txt += "lowercase keys work on the square you stand on or the last item you bumped into\n"
        txt += "uppercase keys open a secondary menu\n"
        txt += "\n= fighting =\n"
        txt += " w/a/s/d: attack north/east/south/west (up/left/down/right)\n"
        txt += " W/A/S/D: advanced attack north/east/south/west (up/left/down/right)\n"
        txt += "\n= user interface =\n"
        txt += " q: open quests\n"
        txt += " Q: open advanced quest menu\n"
        txt += " i: show inventory\n"
        txt += " t: set information to render\n"
        txt += " r: show room menu\n"
        txt += "\n"
        txt += "sadly the controls cannot be changed at the moment\n"
        txt += "if you have issues with the character running into wall, tap the keys instead of holding them\n"
        txt += "\n"
        txt += ""

        main.set_text((urwid.AttrSpec("default", "default"), txt))

        return False

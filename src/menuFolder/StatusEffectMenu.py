import json

import src

# bad code: should be abstracted
# bad code: uses global function to render
class StatusEffectMenu(src.SubMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "StatusEffectMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()

    def render(self,char):
        if char.dead:
            return ""

        text = "KatzeKatzeKatze"

        return text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        if key == "e":

            return True

        # exit the submenu
        if key == "esc":
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        char = self.char

        text = self.render(char)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ncharacter overview"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None

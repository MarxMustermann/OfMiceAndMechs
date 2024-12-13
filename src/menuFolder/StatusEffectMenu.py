import json

import src

# bad code: should be abstracted
# bad code: uses global function to render
class StatusEffectMenu(src.SubMenu.SubMenu):
    """
    menu to show the players attributes
    """

    type = "StatusEffectMenu"

    def __init__(self, char=None,cursor=0):
        self.char = char
        self.cursor = cursor
        super().__init__()

    def render(self,char):
        if char.dead:
            return ""

        if not char.statusEffects:
            text = "no status effects"
        else:
            text = []
            index = 0
            for statusEffect in char.statusEffects:
                text.append(f"== {statusEffect.type} ({statusEffect.getShortCode()}) ==")
                if index == self.cursor:
                    text.append(f"\n\n{statusEffect.getDescription()}\n")
                text.append(f"\n")
                index += 1

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

        if key == "w":
            self.cursor -= 1 
        if self.cursor < 0:
            self.cursor = len(character.statusEffects)-1

        if key == "s":
            self.cursor += 1 
        if self.cursor >= len(character.statusEffects):
            self.cursor = 0

        if key == "esc":
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

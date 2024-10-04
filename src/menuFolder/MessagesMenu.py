import src

from src.menuFolder.SubMenu import SubMenu

class MessagesMenu(SubMenu):
    def render(self,char):
        if self.scrollIndex:
            return "\n".join(reversed(char.messages[-46-self.scrollIndex:-self.scrollIndex]))
        return "\n".join(reversed(char.messages[-46:]))

    type = "MessagesMenu"

    def __init__(self, char=None):
        self.char = char
        self.scrollIndex = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key == "a" and self.scrollIndex > 0:
            self.scrollIndex -= 1
        if key == "d":
            self.scrollIndex += 1
        if key == "esc":
            character.changed("closedMessages")
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        char = self.char

        text = f"press a/d to scroll\noldest message on top - skipping {self.scrollIndex} messages\n\n"+self.render(char)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "messages"))
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), [text]))
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
        return None

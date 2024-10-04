
from src.menuFolder.SubMenu import SubMenu

from src.interaction import footer, header, main, urwid


class InputMenu(SubMenu):
    """
    menu to get a string input from the user
    """

    type = "InputMenu"

    def __init__(self, query="", ignoreFirst=False, targetParamName="text",stealAllKeys=False):
        """
        initialise internal state

        Parameters:
            query: the text to be shown along with the input prompt
            ignoreFirst: flag to ignore first keypress
        """

        self.query = query
        self.text = ""
        super().__init__()
        self.footerText = "enter the text press enter to confirm"
        self.firstHit = True
        self.ignoreFirst = ignoreFirst
        self.escape = False
        self.position = 0
        self.targetParamName = targetParamName
        self.stealAllKeys = stealAllKeys
        self.done = False

    def handleKey(self, key, noRender=False, character = None):
        """
        gather the input keystrokes

        Parameters:
            key: the key pressed
            noRender: a flag to skip rendering
        Returns:
            returns True when done
        """

        if key == "enter" and not self.escape:
            if self.followUp:
                self.callIndirect(self.followUp,extraParams={self.targetParamName:self.text})
            self.done = True
            return True

        if self.ignoreFirst and self.firstHit:
            pass
        elif key == "\\" and not self.escape:
            self.escape = True
        elif key == "backspace" and not self.escape:
            if self.position:
                self.text = (
                    self.text[0: self.position - 1] + self.text[self.position:]
                )
                self.position -= 1
        elif key == "delete" and not self.escape:
            if self.position < len(self.text):
                self.text = (
                    self.text[0: self.position] + self.text[self.position + 1:]
                )
        elif key == "~":
            pass
        elif key == "+" or key == "*":
            return None
        elif key == "left":
            self.position -= 1
        elif key == "right":
            self.position += 1
        else:
            if key == "enter":
                key = "\n"
            if len(self.text):
                self.text = (
                    self.text[0: self.position] + key + self.text[self.position:]
                )
            else:
                self.text = key
            self.position += 1
            self.escape = False

        if len(self.text):
            text = self.text[0: self.position] + "█" + self.text[self.position:]
        else:
            text = "█"

        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), "\ntext input\n\n"))
            footer.set_text((urwid.AttrSpec("default", "default"), "\ntext input\n\n"))

            self.persistentText = (
                urwid.AttrSpec("default", "default"),
                "\n" + self.query + "\n\n" + text,
            )

            # show the render
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        if self.firstHit:
            self.firstHit = False

        return False

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
        header.set_text((urwid.AttrSpec("default", "default"), "messages"))
        main.set_text((urwid.AttrSpec("default", "default"), [text]))
        header.set_text((urwid.AttrSpec("default", "default"), ""))
        return None

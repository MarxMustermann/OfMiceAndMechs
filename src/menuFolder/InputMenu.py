import src
import tcod
class InputMenu(src.SubMenu.SubMenu):
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

        if key == "esc":
            self.done = True
            return True
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
        elif key == "ctrl v":
            self.text +=tcod.sdl.sys._get_clipboard()
            self.position = len(self.text) + 1
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
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ntext input\n\n"))
            src.interaction.footer.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\ntext input\n\n"))

            self.persistentText = (
                src.interaction.urwid.AttrSpec("default", "default"),
                "\n" + self.query + "\n\n" + text,
            )

            # show the render
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        if self.firstHit:
            self.firstHit = False

        return False

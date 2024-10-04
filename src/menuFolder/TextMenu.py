
from src.menuFolder.SubMenu import SubMenu

import src

class TextMenu(SubMenu):
    """
    a menu showing a text
    """

    type = "TextMenu"

    def __init__(self, text=""):
        """
        initialise internal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.text = text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in (
            "esc",
            "enter",
            "space",
            " ",
        ):
            if self.followUp:
                self.callIndirect(self.followUp)
            return True

        if not noRender:
            # show info
            src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), ""))
            self.persistentText = self.text
            src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), self.persistentText))

        return False

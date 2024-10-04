
from src.menuFolder.SubMenu import SubMenu

from src.interaction import header, main, urwid


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
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = self.text
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

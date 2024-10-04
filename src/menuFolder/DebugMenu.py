import collections

import SubMenu

import src
from src.interaction import commandChars, header, main, urwid
from src.menuFolder.SelectionMenu import SelectionMenu


class DebugMenu(SubMenu):
    """
    menu offering minimal debug ability
    (actually does nothing)
    """

    def __init__(self):
        """
        initialise internal state
        """

        self.type = "DebugMenu"
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        """
        show some debug output
        (actually does nothing)

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """
        self.persistentText = ["debug"]

        # exit submenu
        if key == "esc":
            return True
        return None

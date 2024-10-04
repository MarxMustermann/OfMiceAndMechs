
from src.menuFolder.SubMenu import SubMenu

from src.interaction import header


# bad code: this does nothing the Submenu doesn't do
class SelectionMenu(SubMenu):
    """
    does a simple selection and terminates
    """

    def __init__(self, text="", options=None, default=None, targetParamName="selection",extraDescriptions=None, selected=None):
        """
        set up the selection

        Parameters:
            text: the text to show next to the selection
            options: the options to select from
            default: the default value
            targetParamName: name of the parameter the selection should be stored in
        """

        if not options:
            options = []

        self.type = "SelectionMenu"
        super().__init__(default=default,targetParamName=targetParamName)
        self.setOptions(text, options)

        if selected:
            counter = 0
            for option in options:
                counter += 1
                if option[0] == selected:
                    self.selectionIndex = counter

        self.extraDescriptions = extraDescriptions

    def handleKey(self, key, noRender=False, character = None):
        """
        handles a keypress

        Parameters:
            key: the key pressed
            noRender: flag for skipping rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            self.selection = None
            if self.followUp:
                self.callIndirect(self.followUp,extraParams={self.targetParamName:None})
            return True
        if not noRender and header:
            header.set_text("")

        # let superclass handle the actual selection
        if not self.getSelection():
            super().handleKey(key, noRender=noRender, character=character)

        # stop when done
        return bool(self.getSelection())

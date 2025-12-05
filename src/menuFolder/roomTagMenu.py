import src

class RoomTagMenu(src.subMenu.SubMenu):
    """
    """

    type = "RoomTagMenu"
    def __init__(self, room):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.room = room
        self.submenu = None

    def handleKey(self, key, noRender=False, character = None):

        if self.submenu:
            self.submenu.handleKey(key, noRender, character)
            if self.submenu.done:
                self.room.tag = self.submenu.text
                self.done = True
                return True
            return False


        self.submenu = src.menuFolder.inputMenu.InputMenu(f"input the new tag. current tag is {self.room.tag}:")
        self.submenu.handleKey("~", noRender, character)
        return False

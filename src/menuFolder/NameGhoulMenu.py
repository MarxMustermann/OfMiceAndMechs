
from src.menuFolder.SubMenu import SubMenu

class NameGhoulMenu(SubMenu):
    def __init__(self,npc=None):
        self.npc = npc
        self.type = "NameGhoulMenu"
        self.subMenu = None
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        if self.subMenu:
            subMenuDone = self.subMenu.handleKey(key, noRender=noRender, character=character)
            if not subMenuDone:
                return False
            key = "~"

        # exit the submenu
        if key == "esc":
            return True

        if not self.subMenu:
            self.subMenu = src.menuFolder.InputMenu.InputMenu("enter the new name for this Ghoul")
            self.handleKey("~", noRender=noRender, character=character)
            return False
        self.npc.name = self.subMenu.text
        self.subMenu = None

        return True

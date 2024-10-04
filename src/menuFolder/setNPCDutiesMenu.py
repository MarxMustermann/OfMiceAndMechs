
import SubMenu


class setNPCDutiesMenu(SubMenu):
    def __init__(self,npc=None):
        self.npc = npc
        self.type = "setNPCDutiesMenu"

    def handleKey(self, key, noRender=False, character = None):
        if self.subMenu:
            subMenuDone = self.subMenu.handleKey(key, noRender=noRender, character=character)
            if not subMenuDone:
                return False
            key = "~"

        # exit the submenu
        if key == "esc":
            return True
        return None

        # set primary duty
        # set secondary duty
        # set tertiary duty

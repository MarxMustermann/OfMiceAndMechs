
from src.menuFolder.SubMenu import SubMenu

from src.interaction import header, main, urwid


class ImplantConnection(SubMenu):
    type = "ImplantConnection"

    def __init__(self, connectionTarget):
        super().__init__()
        self.connectionTarget = connectionTarget
        self.submenu = None
        self.sidebared = False

    def handleKey(self, key, noRender=False, character = None):
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = f"implant connection to {self.connectionTarget.type}"
            self.persistentText += "\n\n"
            self.persistentText += "press j to use connection\n"
            self.persistentText += "press x to close connection\n"
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        if self.submenu and self.submenu.done:
            self.submenu = None
            return False

        if self.submenu:
            self.submenu.handleKey(key, noRender, character)
            return False

        if key in ("x",):
            self.done = True
            return True
        if character and key in ("ESC","lESC",):
            character.rememberedMenu.append(self)
            return True
        if character and key in ("rESC",):
            character.rememberedMenu2.append(self)
            return True

        if character and key in ("j",):
            self.connectionTarget.apply(character)
            character.rememberedMenu.append(self)

        return False

    def render(self, char):
        return f"implant connection to {self.connectionTarget.type}"

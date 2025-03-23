import src


class WarningMenu(src.subMenu.SubMenu):
    def __init__(self, text, onReturn=None):
        self.text = text
        self.onReturn = onReturn
        self.stealAllKeys = False  # HACK

    def handleKey(self, key, noRender=False, character=None):
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\Warning\n\n"))

        src.interaction.main.set_text(
            (
                src.interaction.urwid.AttrSpec("default", "default"),
                self.text,
            )
        )
        # exit submenu
        if key in ("enter", "j", "esc"):
            if self.onReturn:
                self.onReturn()
            return True
        return False

import src


class ConfirmMenu(src.subMenu.SubMenu):
    def __init__(self, text, onConfirm, onCancel=None):
        self.text = text
        self.onConfirm = onConfirm
        self.onCancel = onCancel
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("a", "d", "left", "right"):
            self.index += 1 if key in ("d", "right") else -1

        if self.index == -1:
            self.index = 1

        if self.index == 2:
            self.index = 0

        change_event = key in ("enter", "j")

        src.interaction.header.set_text(
            (src.interaction.urwid.AttrSpec("default", "default"), "\n\nConfirm Actions\n\n")
        )
        text = self.text + "\n\n\n"

        for i, t in enumerate(["Accept", "Cancel"]):
            if i == self.index:
                text += f">{t}<"
            else:
                text += t
            if i == 0:
                text += " " * max(len(max(self.text.splitlines(), key=len)) - 10, 6)

        text += "\n\n"

        src.interaction.main.set_text(
            (
                src.interaction.urwid.AttrSpec("default", "default"),
                text,
            )
        )

        if change_event:
            if self.index == 0:
                self.onConfirm()
            else:
                self.onCancel()
            return True
        # exit submenu

        if key == "esc":
            if self.onCancel:
                self.onCancel()
            return True
        return False

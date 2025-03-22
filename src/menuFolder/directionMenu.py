import src
from src.helpers import clamp


class DirectionMenu(src.subMenu.SubMenu):
    def __init__(self, text, current_dir, dirChosen):
        self.type = "DirectionMenu"
        if current_dir:
            self.dir = current_dir
        else:
            self.dir = (0, 0)

        self.text = text
        self.dirChosen = dirChosen
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("s", "down"):
            self.dir = (0, 1, 0)
        elif key in ("w", "up"):
            self.dir = (0, -1, 0)
        elif key in ("d", "right"):
            self.dir = (1, 0, 0)
        elif key in ("a", "left"):
            self.dir = (-1, 0, 0)


        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDirection\n\n"))
        text = ""

        text += self.text + "\n\n"

        N = " N " if self.dir != (0, -1, 0) else ">N<"
        W = " W " if self.dir != (-1, 0, 0) else ">W<"
        E = " E " if self.dir != (1, 0, 0) else ">E<"
        S = " S " if self.dir != (0, 1, 0) else ">S<"

        text += f"            {N}            " + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += f"{W}----------+----------{E}" + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += r"             |             " + "\n"
        text += f"            {S}            " + "\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        if key in ("enter", "j"):
            self.dirChosen(self.dir)
            return True

        # exit submenu
        return key == "esc"

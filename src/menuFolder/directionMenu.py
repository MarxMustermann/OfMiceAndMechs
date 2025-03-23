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

        North = " North " if self.dir != (0, -1, 0) else ">North<"
        West = " West " if self.dir != (-1, 0, 0) else ">West<"
        East = " East " if self.dir != (1, 0, 0) else ">East<"
        South = " South " if self.dir != (0, 1, 0) else ">South<"

        text += f"             {North}             " + "\n"
        text += r"                                 " + "\n"
        text += r"                ^                " + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += f"{West}<---------+--------->{East}" + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += r"                |                " + "\n"
        text += r"                v                " + "\n"
        text += r"                                 " + "\n"
        text += f"             {South}             " + "\n"

        text += "\n\n\nPress x to use all four directions"
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        if key in ("enter", "j"):
            self.dirChosen(self.dir)
            return True

        if key == "x":
            self.dirChosen(None)
            return True

        # exit submenu
        return key == "esc"

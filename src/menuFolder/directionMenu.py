import src
from src.helpers import clamp


class DirectionMenu(src.subMenu.SubMenu):
    def __init__(self, text, current_dir, dirChosen):
        self.type = "DirectionMenu"
        if current_dir:
            self.x_index = current_dir[0] + 1
            self.y_index = current_dir[1] + 1
        else:
            self.x_index = 0
            self.y_index = 0
        self.text = text
        self.dirChosen = dirChosen
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("w", "s", "up", "down"):
            if key in ("s", "down") and self.y_index + 1 == 1 and self.x_index == 1:
                self.y_index = 2
            elif key in ("w", "up") and self.y_index - 1 == 1 and self.x_index == 1:
                self.y_index = 0
            else:
                self.y_index += 1 if key in ("s", "down") else -1

        if key in ("d", "right", "a", "left"):
            if key in ("d", "right") and self.x_index + 1 == 1 and self.y_index == 1:
                self.x_index = 2
            elif key in ("a", "left") and self.x_index - 1 == 1 and self.y_index == 1:
                self.x_index = 0
            else:
                self.x_index += 1 if key in ("d", "right") else -1

        self.x_index = clamp(self.x_index, 0, 2)
        self.y_index = clamp(self.y_index, 0, 2)

        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDirection\n\n"))
        text = ""

        text += self.text + "\n\n"

        offset_index = (self.x_index, self.y_index)

        NW = " NW " if offset_index != (0, 0) else ">NW<"
        N = " N " if offset_index != (1, 0) else ">N<"
        NE = " NE " if offset_index != (2, 0) else ">NE<"
        W = " W " if offset_index != (0, 1) else ">W<"
        E = " E " if offset_index != (2, 1) else ">E<"
        SW = " SW " if offset_index != (0, 2) else ">SW<"
        S = " S " if offset_index != (1, 2) else ">S<"
        SE = " SE " if offset_index != (2, 2) else ">SE<"

        text += f"  {NW}      {N}     {NE}   " + "\n"
        text += r"      \      |      /      " + "\n"
        text += r"        \    |    /        " + "\n"
        text += r"          \  |  /          " + "\n"
        text += r"            \|/            " + "\n"
        text += f"{W}----------+----------{E}" + "\n"
        text += r"            /|\            " + "\n"
        text += r"          /  |  \          " + "\n"
        text += r"        /    |    \        " + "\n"
        text += r"      /      |      \      " + "\n"
        text += f"   {SW}     {S}     {SE}   " + "\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        if key in ("enter", "j"):
            self.dirChosen(([-1, 0, 1][self.x_index], [-1, 0, 1][self.y_index], 0))
            return True

        # exit submenu
        return key == "esc"

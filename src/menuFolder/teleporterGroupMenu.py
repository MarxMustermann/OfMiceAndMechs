from decimal import Decimal as D
from functools import partial

import src
import src.helpers
import src.menuFolder
import src.menuFolder.confirmMenu
import src.menuFolder.inputMenu
import src.menuFolder.textMenu
import src.menuFolder.warningMenu


class TeleporterGroupMenu(src.subMenu.SubMenu):
    def __init__(self, teleporter):
        self.type = "TeleporterGroupMenu"
        self.value = D("87.5") if not teleporter.group else teleporter.group
        self.teleporter = teleporter
        super().__init__()

    def handleKey(self, key: str, noRender=False, character=None):
        step = D("0.1")
        if key.lower() in ("d", "a", "right", "left"):
            if key[0].isupper():
                step = D("1")
            self.value += step if key.lower() in ("d", "right") else -step

        self.value = src.helpers.clamp(self.value, D(87.5), D(108))
        change_event = key in ("enter", "j")

        src.interaction.header.set_text(
            (src.interaction.urwid.AttrSpec("default", "default"), "\n\nTeleportGroupMenu\n\n")
        )
        text = ""

        if change_event:
            self.teleporter.removeFromGroup()
            self.teleporter.group = self.value
            self.teleporter.addToGroup()
            return True

        if key == "x":
            self.teleporter.removeFromGroup()
            self.teleporter.group = None
            return True

        if key == "i":
            character.macroState["submenue"] = src.menuFolder.inputMenu.InputMenu("enter frequency")
            character.macroState["submenue"].followUp = {
                "container": self,
                "method": "setGroup",
                "params": {"character": character},
            }
            return True
        text = ""
        width = 20
        points = []

        for x in range(width):
            for y in range(width):
                if y == 0 or y == width - 1 or x == 0 or x == width - 1:
                    text += "* "
                    points.append((x, y))
                else:
                    text += "  "
            text += "\n"

        new_var = (self.value - D(87.5)) / (D(108) - D(87.5))
        points.sort(key=partial(src.helpers.clockwiseangle_and_distance, (width / 2, width / 2)))
        target = points[len(points) - 1 - int(len(points) * new_var)]

        lines = text.splitlines()

        def d(x, y):
            l = list(lines[int(y)])
            l[int(x * 2)] = "."
            lines[int(y)] = "".join(l)

        src.helpers.drawLine(width / 2, width / 2, target[0], target[1], d)
        text = "\n".join(lines)
        v = str(self.value)
        text += "\n" + "  " * int(width / 2 - len(v) / 2) + v
        src.interaction.main.set_text(
            (
                src.interaction.urwid.AttrSpec("default", "default"),
                text
                + "\n\npress a d to change the frequency\npress shift to change with bigger steps\nyou can press i to enter manually"
                "\nyou can press x to turn the teleporter off",
            )
        )
        # exit submenu
        return key == "esc"

    def setGroup(self, params):
        try:
            output = D(params["text"])
            if D(87.5) <= output and output <= D(108):
                self.teleporter.removeFromGroup()
                self.teleporter.group = output
                self.teleporter.addToGroup()
        except:
            params["character"].macroState["submenue"] = src.menuFolder.textMenu.TextMenu("Wrong input for Frequency")

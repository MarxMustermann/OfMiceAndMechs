import json

from src.menuFolder.SubMenu import SubMenu

from src.interaction import header, main, settings, urwid


def clamp(n, min, max):
    if n < min:
        return min
    if n > max:
        return max
    return n


class SettingMenu(SubMenu):
    type = "SettingMenu"
    setting_options = ["set sound volume"]

    def __init__(self, default=None, targetParamName="selection"):
        self.index = 0
        super().__init__(default, targetParamName)

    def handleKey(self, key, noRender=False, character=None):
        if key in ("esc", " "):
            with open("config/globalSettings.json", "w") as f:
                json.dump(settings, f)
            return True
        change_value = False
        if key in ("a", "d"):
            change_value = True
        if key in ("w", "s"):
            self.index += 1 if key == "s" else -1
            self.index = clamp(self.index, 0, len(self.options))

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nsettings\n\n"))
        text = ""

        for setting in self.setting_options:
            match setting:
                case "set sound volume":
                    if change_value:
                        settings["sound"] += -1 if key == "a" else +1
                        settings["sound"] = clamp(settings["sound"], 0, 32)
                    text += setting + ":"
                    text += " " + settings["sound"] * "║"
                    text += (32 - settings["sound"]) * "|"

        main.set_text((urwid.AttrSpec("default", "default"), text))

        return False

import json

import src
from src.menuFolder.SubMenu import SubMenu


class SettingMenu(SubMenu):
    type = "SettingMenu"
    setting_options = ["set sound volume"]

    def __init__(self, default=None, targetParamName="selection"):
        self.index = 0
        super().__init__(default, targetParamName)

    def handleKey(self, key, noRender=False, character=None):
        if key in ("esc", " "):
            with open("config/globalSettings.json", "w") as f:
                json.dump(src.interaction.settings, f)
            return True
        change_value = False
        if key in ("a", "d"):
            change_value = True
        if key in ("w", "s"):
            self.index += 1 if key == "s" else -1
            self.index = src.helpers.clamp(self.index, 0, len(self.options))

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nsettings\n\n"))
        text = ""

        for setting in self.setting_options:
            match setting:
                case "set sound volume":
                    if change_value:
                        src.interaction.settings["sound"] += -1 if key == "a" else +1
                        src.interaction.settings["sound"] = src.helpers.clamp(src.interaction.settings["sound"], 0, 32)
                    text += setting + ":"
                    text += " " + src.interaction.settings["sound"] * "║"
                    text += (32 - src.interaction.settings["sound"]) * "|"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        return False

import json

import src
from src.menuFolder.SubMenu import SubMenu


class SettingMenu(SubMenu):
    type = "SettingMenu"
    setting_options = ["set sound volume","toggle fullscreen"]

    def __init__(self, default=None, targetParamName="selection"):
        self.index = 0
        super().__init__(default, targetParamName)

    def handleKey(self, key, noRender=False, character=None):
        if key in ("esc", " "):
            with open("config/globalSettings.json", "w") as f:
                json.dump(src.interaction.settings, f)
            return True
        change_event = False
        if key in ("a", "d"):
            change_event = True
        if key in ("w", "s"):
            self.index += 1 if key == "s" else -1
            self.index = src.helpers.clamp(self.index, 0, len(self.setting_options)-1)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nsettings\n\n"))
        text = ""

        for i,setting in enumerate(self.setting_options):
            change_value = change_event and self.index == i
            text+= ">" if self.index == i else ""
            match setting:
                case "set sound volume":
                    if change_value:
                        src.interaction.settings["sound"] += -1 if key == "a" else +1
                        src.interaction.settings["sound"] = src.helpers.clamp(src.interaction.settings["sound"], 0, 32)
                    text += setting + ":"
                    text += " " + src.interaction.settings["sound"] * "║"
                    text += (32 - src.interaction.settings["sound"]) * "|"
                case "toggle fullscreen":
                    if change_value:
                        src.interaction.settings["fullscreen"] = not src.interaction.settings["fullscreen"]
                        import tcod
                        tcod.lib.SDL_SetWindowFullscreen(
                            src.interaction.tcodContext.sdl_window_p,
                            tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP if src.interaction.settings["fullscreen"] else 0,
                        )
                    text += setting + ":    "
                    text += "On" if src.interaction.settings["fullscreen"] else "Off"
            text+="\n"
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        return False

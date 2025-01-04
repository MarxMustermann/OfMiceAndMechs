import json

import src

class SettingMenu(src.subMenu.SubMenu):
    type = "SettingMenu"
    setting_options = ["auto save","enable sound","set sound volume","toggle fullscreen"]

    def __init__(self, default=None, targetParamName="selection"):
        self.index = 0
        super().__init__(default, targetParamName)

    def handleKey(self, key, noRender=False, character=None):
        if key in ("esc", " "):
            with open("config/globalSettings.json", "w") as f:
                json.dump(src.interaction.settings, f)
            return True
        change_event = False
        if key in ("a", "d","left","right"):
            change_event = True
        if key in ("w", "s","up","down"):
            self.index += 1 if key in ("s","down") else -1
            self.index = src.helpers.clamp(self.index, 0, len(self.setting_options)-1)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nsettings\n\n"))
        text = ""

        for i,setting in enumerate(self.setting_options):
            if change_event and self.index == i:
                match setting:
                    case "enable sound":
                        src.interaction.settings["sound"] = 32 if src.interaction.settings["sound"] == 0 else 0
                    case "set sound volume":
                        src.interaction.settings["sound"] += -1 if key == "a" else +1
                        src.interaction.settings["sound"] = src.helpers.clamp(src.interaction.settings["sound"], 0, 32)
                        src.interaction.changeVolume()
                    case "toggle fullscreen":
                        src.interaction.settings["fullscreen"] = not src.interaction.settings["fullscreen"]
                        import tcod
                        tcod.lib.SDL_SetWindowFullscreen(
                            src.interaction.tcodContext.sdl_window_p,
                            tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP if src.interaction.settings["fullscreen"] else 0,
                        )
                    case "auto save":
                        src.interaction.settings["auto save"] = not src.interaction.settings.get("auto save",False)
        for i,setting in enumerate(self.setting_options):
            text+= ">" if self.index == i else ""
            match setting:
                case "enable sound":
                    text += setting + ": "
                    text += "Off" if src.interaction.settings["sound"] == 0 else "On"
                case "set sound volume":
                    text += setting + ":"
                    text += " " + src.interaction.settings["sound"] * "║"
                    text += (32 - src.interaction.settings["sound"]) * "|"
                case "toggle fullscreen":
                    text += setting + ":    "
                    text += "On" if src.interaction.settings["fullscreen"] else "Off"
                case "auto save":
                    text+= "auto save:    "
                    text += "On" if src.interaction.settings.get("auto save") else "Off"
            text+="\n"
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        return False

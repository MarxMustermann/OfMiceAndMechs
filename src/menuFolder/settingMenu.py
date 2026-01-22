import json

import src

class SettingMenu(src.subMenu.SubMenu):
    type = "SettingMenu"
    setting_options = ["auto save", "sound", "set sound volume", "fullscreen", "change npc rendering"]

    def __init__(self, default=None, targetParamName="selection"):
        self.index = 0
        super().__init__(default, targetParamName)

    def handleKey(self, key, noRender=False, character=None):
        if key in ("esc", " "):
            with open("config/globalSettings.json", "w") as f:
                json.dump(src.interaction.settings, f)
            return True
        change_event = False
        if key in ("a", "d", "left", "right", "j", "enter"):
            change_event = True
        if key in ("w", "s","up","down"):
            if key in ("s","down"):
                change_amount = 1
            else:
                change_amount = -1
            self.index += change_amount
            self.index = src.helpers.clamp(self.index, 0, len(self.setting_options)-1)

        # show info
        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nsettings\n\n"))

        for i,setting in enumerate(self.setting_options):
            if change_event and self.index == i:
                match setting:
                    case "sound":
                        src.interaction.settings["sound"] = 32 if src.interaction.settings["sound"] == 0 else 0
                    case "set sound volume":
                        src.interaction.settings["sound"] += -1 if key in ("a","left") else +1
                        src.interaction.settings["sound"] = src.helpers.clamp(src.interaction.settings["sound"], 0, 32)
                        src.interaction.changeVolume()
                    case "fullscreen":
                        src.interaction.settings["fullscreen"] = not src.interaction.settings["fullscreen"]
                        src.interaction.sdl_window.fullscreen = src.interaction.settings["fullscreen"]
                    case "auto save":
                        src.interaction.settings["auto save"] = not src.interaction.settings.get("auto save",False)

                    case "change npc rendering":
                        character.macroState["submenue"] = src.menuFolder.changeViewsMenu.ChangeViewsMenu()

        text = self.render()
        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        return False

    def render(self):
        text = ""
        for i,setting in enumerate(self.setting_options):
            if self.index == i:
                text+= "> "
            match setting:
                case "sound":
                    text += setting + ":               "
                    if src.interaction.settings["sound"] == 0:
                        text += "Off"
                    else:
                        text += "On"
                case "set sound volume":
                    text += setting + ":   "
                    text += " " + src.interaction.settings["sound"] * "║"
                    text += (32 - src.interaction.settings["sound"]) * "|"
                case "fullscreen":
                    text += setting + ":          "
                    if src.interaction.settings["fullscreen"]:
                        text += "On"
                    else:
                        text += "Off"
                case "auto save":
                    text+= "auto save:           "
                    if src.interaction.settings.get("auto save"):
                        text += "On"
                    else:
                        text += "Off"
                case "change npc rendering":
                    text += "change npc rendering"

            text+="\n"
        return text

import collections

import src

class DebugMenu(src.SubMenu.SubMenu):
    """
    menu offering debug ability
    """
    debug_options = ["Execute Code"]

    def __init__(self):
        self.type = "DebugMenu"
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("w", "s"):
            self.index += 1 if key == "s" else -1
            self.index = src.helpers.clamp(self.index, 0, len(self.debug_options) - 1)

        change_event = key in ("enter", "j")

        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDebug\n\n"))
        text = ""

        for i, debug in enumerate(self.debug_options):
            current_change = change_event and self.index == i
            text += ">" if self.index == i else ""
            match debug:
                case "Execute Code":
                    text+= debug
                    if current_change:
                        submenue = src.menuFolder.InputMenu.InputMenu("Type the code to execute",targetParamName="code")
                        character.macroState["submenue"] = submenue
                        character.macroState["submenue"].followUp = {"container":self,"method":"action","params":{"character":character}}
                        return True
            text += "\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        # exit submenu
        return key == "esc"

    def action(self, params):
        character = params["character"]

        if "code" in params:
            try:
                exec(params["code"],{"player":src.gamestate.gamestate.mainChar, "items":src.items.itemMap})
            except Exception as e:
                print("error: " + str(e))
            return

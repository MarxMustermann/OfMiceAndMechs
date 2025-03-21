from functools import partial

import src
import src.menuFolder
import src.menuFolder.confirmMenu
import src.menuFolder.warningMenu


class TeleporterGroupMenu(src.subMenu.SubMenu):
    def __init__(self, teleporter, new_mode):
        self.type = "TeleporterGroupMenu"
        self.index = 0
        self.teleporter = teleporter
        self.new_mode = new_mode
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        groups = src.gamestate.gamestate.teleporterGroups

        if key in ("w", "s", "up", "down"):
            self.index += 1 if key in ("s", "down") else -1

        if self.index == -1:
            self.index = len(groups) - 1

        if self.index == len(groups):
            self.index = 0

        change_event = key in ("enter", "j")

        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDebug\n\n"))
        text = ""

        if key == "c":
            menu = src.menuFolder.inputMenu.InputMenu("input group name")
            character.macroState["submenue"] = menu

            class hack:
                def return_to_current(params):
                    if params["text"] in groups:
                        pass  # TODO error out
                    groups[params["text"]] = ([], [])
                    character.macroState["submenue"] = self

            character.macroState["submenue"].followUp = {"container": hack, "method": "return_to_current", "params": {}}

        if key == "d":
            for i, g_name in enumerate(groups):
                if i == self.index:
                    if g_name != "default":

                        def delete(g_name):
                            groups["default"][0].extend(groups[g_name][0])
                            groups["default"][1].extend(groups[g_name][1])

                            del groups[g_name]

                            character.macroState["submenue"] = self

                        character.macroState["submenue"] = src.menuFolder.confirmMenu.ConfirmMenu(
                            f'are you sure you want to delete group "{g_name}" \n'
                            "all teleporter set to this group will be set to the default group",
                            partial(delete, g_name),
                        )
                        return False
                    else:

                        def return_to_self(s):
                            character.macroState["submenue"] = s

                        character.macroState["submenue"] = src.menuFolder.warningMenu.WarningMenu(
                            "you can't delete the default group", partial(return_to_self, self)
                        )

        for i, g_name in enumerate(groups):
            current_change = change_event and self.index == i
            text += ">" if self.index == i else ""
            text += g_name + "\n"
            if current_change:
                if self.teleporter.bolted:
                    src.gamestate.gamestate.teleporterGroups[self.teleporter.group][self.teleporter.mode].remove(
                        self.teleporter
                    )
                else:
                    self.teleporter.bolted = True

                self.teleporter.group = g_name
                self.teleporter.mode = self.new_mode

                src.gamestate.gamestate.teleporterGroups[g_name][self.teleporter.mode].append(self.teleporter)

                return True

        src.interaction.main.set_text(
            (
                src.interaction.urwid.AttrSpec("default", "default"),
                text + "\npress c to create new group\npress d to delete current group",
            )
        )
        # exit submenu
        return key == "esc"

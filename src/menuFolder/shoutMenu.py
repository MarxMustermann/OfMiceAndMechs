import src
import src.rooms


class ShoutMenu(src.subMenu.SubMenu):
    shout_options = ["Stop and Wait For X tick!!!!!"]

    def __init__(self):
        self.type = "DebugMenu"
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("w", "s", "up", "down"):
            self.index += 1 if key in ("s", "down") else -1

            if self.index == -1:
                self.index = len(self.shout_options) - 1

            if self.index == len(self.shout_options):
                self.index = 0

        change_event = key in ("enter", "j")

        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDebug\n\n"))
        text = ""

        for i, shout in enumerate(self.shout_options):
            current_change = change_event and self.index == i
            text += ">" if self.index == i else ""
            text += shout

            if current_change:
                match shout:
                    case "Stop and Wait For X tick!!!!!":
                        character.macroState["submenue"] = src.menuFolder.inputMenu.InputMenu(
                            "enter tick amount", targetParamName="waitTicks"
                        )
                        character.macroState["submenue"].followUp = {
                            "container": self,
                            "method": "action",
                            "params": {"character": character},
                        }
                        return True
            text += "\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        # exit submenu
        return key == "esc"

    def action(self, params):
        character = params["character"]

        if "waitTicks" in params:
            ticksToWait = int(params["waitTicks"])

            for otherChar in self.getNearbyAllies(character):
                quest = src.quests.questMap["WaitQuest"](lifetime=ticksToWait)
                quest.autoSolve = True
                quest.assignToCharacter(otherChar)
                quest.activate()
                otherChar.assignQuest(quest, active=True)
                otherChar.macroState["commandKeyQueue"] = []

    def getNearbyAllies(self, character):
        container = character.container

        out = []
        if isinstance(container, src.rooms.Room):
            for otherChar in container.characters:
                if otherChar == character:
                    continue
                if (
                    isinstance(otherChar, src.characters.characterMap["Clone"])
                    and not otherChar.dead
                    and character.faction == otherChar.faction
                ):
                    out.append(otherChar)
        else:
            pos = character.getBigPosition()
            otherChars = container.charactersByTile.get(pos, [])
            for otherChar in otherChars:
                if otherChar == character:
                    continue
                if character.faction == otherChar.faction and not otherChar.dead and pos != otherChar.getBigPosition():
                    out.append(otherChar)

        return out

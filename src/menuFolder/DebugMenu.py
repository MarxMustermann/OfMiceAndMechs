import collections

import src

class DebugMenu(src.SubMenu.SubMenu):
    """
    menu offering debug ability
    """
    debug_options = ["Teleport", "Add Mana", "Execute Code"]

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
                case "Add Mana":
                    text+= debug
                    if current_change:
                        terrain = character.getTerrain()
                        terrain.mana += 100
                        return True
                case "Teleport":
                    text += debug
                    if current_change:
                        terrain = character.getTerrain()
                        mapContent = []
                        functionMap = {}

                        for x in range(15):
                            mapContent.append([])
                            for y in range(15):
                                if x not in (0, 14) and y not in (0, 14):
                                    displayChar = "  "
                                elif x != 7 and y != 7:
                                    displayChar = "##"
                                else:
                                    displayChar = "  "
                                mapContent[x].append(displayChar)
                        for x in range(1,14):
                            for y in range(1,14):
                                mapContent[x].append(displayChar)
                                functionMap[(y, x)] = {
                                    "j": {
                                        "function": {
                                            "container": self,
                                            "method": "action",
                                            "params": {"character":character},
                                        },
                                        "description": "move to it",
                                    }
                                }

                        for room in terrain.rooms:
                            mapContent[room.yPosition][room.xPosition] = room.displayChar
                        for scrapField in terrain.scrapFields:
                            mapContent[scrapField[1]][scrapField[0]] = "ss"
                        submenue = src.menuFolder.MapMenu.MapMenu(
                            mapContent=mapContent,
                            functionMap=functionMap,
                            cursor=character.getBigPosition(),
                        )
                        character.macroState["submenue"] = submenue
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

        if "coordinate" in params:
            print(params["coordinate"])
            terrain = character.getTerrain()
            character.container.removeCharacter(character)
            room = terrain.getRoomByPosition(params["coordinate"])
            if len(room):
                room[0].addCharacter(character,7,7)
            else:
                terrain.addCharacter(character,15*params["coordinate"][0]+7,15*params["coordinate"][1]+7)

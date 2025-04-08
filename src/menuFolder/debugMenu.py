import collections
import random

import objgraph
import regex

import src


class DebugMenu(src.subMenu.SubMenu):
    """
    menu offering debug ability
    """

    debug_options = [
        "Teleport",
        "Teleport Terrain",
        "Add Mana",
        "Execute Code",
        "Test Crash",
        "Debug Memory",
        "clear path cache",
        "Get Item",
    ]

    def __init__(self):
        self.type = "DebugMenu"
        self.index = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character=None):
        if key in ("w", "s","up","down"):
            self.index += 1 if key in ("s","down") else -1

            if self.index == -1:
                self.index = len(self.debug_options) - 1

            if self.index == len(self.debug_options):
                self.index = 0

        change_event = key in ("enter", "j")

        src.interaction.header.set_text((src.interaction.urwid.AttrSpec("default", "default"), "\n\nDebug\n\n"))
        text = ""

        for i, debug in enumerate(self.debug_options):
            current_change = change_event and self.index == i
            text += ">" if self.index == i else ""
            text += debug

            match debug:
                case "clear path cache":
                    if current_change:
                        terrain = character.getTerrain()
                        terrain.pathfinderCache = {}
                case "Debug Memory":
                    if current_change:
                        objgraph.show_most_common_types()
                        objgraph.show_growth()
                case "Test Crash":
                    if current_change:
                        1/0
                case "Execute Code":
                    if current_change:
                        submenue = src.menuFolder.inputMenu.InputMenu("Type the code to execute",targetParamName="code")
                        character.macroState["submenue"] = submenue
                        character.macroState["submenue"].followUp = {"container":self,"method":"action","params":{"character":character}}
                        return True
                case "Add Mana":
                    if current_change:
                        terrain = character.getTerrain()
                        terrain.mana += 100
                        return True
                case "Teleport":
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
                        submenue = src.menuFolder.mapMenu.MapMenu(
                            mapContent=mapContent,
                            functionMap=functionMap,
                            cursor=character.getBigPosition(),
                        )
                        character.macroState["submenue"] = submenue
                        return True
                case "Teleport Terrain":
                    if current_change:
                        mapContent = []
                        functionMap = {}
                        for x in range(15):
                            mapContent.append([])
                            for y in range(15):
                                tag: str = src.gamestate.gamestate.terrainMap[x][y].tag
                                if tag:
                                    if tag.endswith("base"):
                                        displayChar = "RB"
                                    elif tag == "lab":
                                        displayChar = "LA"
                                    elif tag == "ruin":
                                        displayChar = "R "
                                    elif tag == "shrine":
                                        displayChar = "S "
                                    else:
                                        displayChar = "  "
                                else:
                                    displayChar = "  "
                                mapContent[x].append(displayChar)
                        for x in range(15):
                            for y in range(15):
                                mapContent[x].append(displayChar)
                                functionMap[(y, x)] = {
                                    "j": {
                                        "function": {
                                            "container": self,
                                            "method": "action",
                                            "params": {"character": character},
                                        },
                                        "description": "move to it",
                                    }
                                }

                        submenue = src.menuFolder.mapMenu.MapMenu(
                            mapContent=mapContent,
                            functionMap=functionMap,
                            cursor=character.getTerrain().getPosition(),
                            applyKey="big_coordinate",
                        )
                        character.macroState["submenue"] = submenue
                        return True
                case "Get Item":
                    if current_change:
                        submenue = src.menuFolder.inputMenu.InputMenu("Type item name to spawn", targetParamName="item")
                        character.macroState["submenue"] = submenue
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

        if "item" in params:
            print(params["item"])
            item_name: str = params["item"].lower()
            m = regex.search("x(\\d+)", item_name)
            if m:
                item_name = item_name.removesuffix("x" + m.group()[1:])

            for key, item_ty in src.items.itemMap.items():
                if key.lower() == item_name:
                    if m:
                        for _ in range(int(m.group()[1:])):
                            character.inventory.append(item_ty())
                    else:
                        character.inventory.append(item_ty())

                    character.addMessage(f"added {item_name}")
                    return

            character.addMessage(f"item ({item_name}) not found")

        if "big_coordinate" in params:
            print(params["big_coordinate"])
            x, y = params["big_coordinate"]
            terrain = character.getTerrain()
            character.container.removeCharacter(character)
            terrain = src.gamestate.gamestate.terrainMap[y][x]
            room = terrain.getRoomByPosition((7, 7))
            if len(room):
                room[0].addCharacter(character, 7, 7)
            else:
                terrain.addCharacter(character, 15 * 7 + 7, 15 * 7 + 7)
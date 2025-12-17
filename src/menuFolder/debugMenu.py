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
        "kill enemies on Terrain",
        "Clear Fog",
        "Add Mana",
        "Get Item",
        "Obtain Glass hearts",
        "Execute Code",
        "Test Crash",
        "Debug Memory",
        "clear path cache",
        "pass time",
        "gain endgame strength",
        "gain full strength",
        "spawn room",
        "toggleQuestExpanding",
        "toggleQuestExpanding2",
        "toggleExpandQ",
        "toggleCommandOnPlus",
        "change personality settings",
        "toggle SDL",
        "fix room state",
        "fix terrain state",
        "take over character on tile",
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
                case "take over character on tile":
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
                        for room in terrain.rooms:
                            mapContent[room.yPosition][room.xPosition] = room.displayChar
                        for scrapField in terrain.scrapFields:
                            mapContent[scrapField[1]][scrapField[0]] = "ss"
                        for x in range(1,14):
                            for y in range(1,14):
                                mapContent[x].append(displayChar)
                                if not terrain.getCharactersOnTile((x,y,0)):
                                    continue
                                mapContent[x][y] = "XX"
                                functionMap[(y, x)] = {
                                    "j": {
                                        "function": {
                                            "container": self,
                                            "method": "takeOverOnTile",
                                            "params": {"character":character},
                                        },
                                        "description": "take over character",
                                    }
                                }

                        submenue = src.menuFolder.mapMenu.MapMenu(
                            mapContent=mapContent,
                            functionMap=functionMap,
                            cursor=character.getBigPosition(),
                        )
                        character.macroState["submenue"] = submenue
                        return True
                    if current_change:
                        terrain = character.getTerrain()
                        terrain.clear_broken_states()
                        return True
                case "fix terrain state":
                    if current_change:
                        terrain = character.getTerrain()
                        terrain.clear_broken_states()
                        return True
                case "fix room state":
                    if current_change:
                        if character.container.isRoom:
                            character.container.clear_broken_states()
                        return True
                case "change personality settings":
                    if current_change:
                        def getValue():
                            settingName = character.macroState["submenue"].selection

                            def setValue():
                                value = character.macroState["submenue"].text
                                if settingName in (
                                    "autoCounterAttack",
                                    "autoFlee",
                                    "abortMacrosOnAttack",
                                    "attacksEnemiesOnContact",
                                ):
                                    if value == "True":
                                        value = True
                                    else:
                                        value = False
                                else:
                                    try:
                                        value = int(value)
                                    except:
                                        return
                                character.personality[settingName] = value

                            if settingName is None:
                                return
                            submenu3 = src.menuFolder.inputMenu.InputMenu("input value")
                            character.macroState["submenue"] = submenu3
                            character.macroState["submenue"].followUp = setValue
                            return

                        options = []
                        for (key, value) in character.personality.items():
                            options.append((key, f"{key}: {value}"))
                        submenu2 = src.menuFolder.selectionMenu.SelectionMenu("select personality setting", options)
                        character.macroState["submenue"] = submenu2
                        character.macroState["submenue"].followUp = getValue
                        return True
                case "toggleQuestExpanding":
                    if current_change:
                        character.autoExpandQuests = not character.autoExpandQuests
                        return True
                case "toggleQuestExpanding2":
                    if current_change:
                        character.autoExpandQuests2 = not character.autoExpandQuests2
                        return True
                case "toggleExpandQ":
                    if current_change:
                        character.autoExpandQ = not character.autoExpandQ
                        return True
                case "toggleCommandOnPlus":
                    if current_change:
                        character.disableCommandsOnPlus = not character.disableCommandsOnPlus
                        return True
                case "gain full strength":
                    if current_change:
                        character.maxHealth = 500
                        character.health = 500
                        character.baseAttackSpeed = 0.10
                        character.movementSpeed = 0.10
                        character.baseDamage = 20
                        character.hasSpecialAttacks = True

                        weapon = src.items.itemMap["Sword"]()
                        weapon.baseDamage = 30
                        character.weapon = weapon
                        armor = src.items.itemMap["Armor"]()
                        armor.armorValue = 8
                        character.armor = armor

                        return True
                case "gain endgame strength":
                    if current_change:
                        character.maxHealth = 370
                        character.health = 370
                        character.baseAttackSpeed = 0.50
                        character.movementSpeed = 0.50
                        character.baseDamage = 20
                        character.hasSpecialAttacks = True

                        weapon = src.items.itemMap["Sword"]()
                        weapon.baseDamage = 30
                        character.weapon = weapon
                        armor = src.items.itemMap["Armor"]()
                        armor.armorValue = 8
                        character.armor = armor

                        return True
                case "kill enemies on Terrain":
                    if current_change:
                        terrain = character.getTerrain()
                        
                        candidates = []
                        candidates.extend(terrain.characters)

                        for room in terrain.rooms:
                            candidates.extend(room.characters)
                        
                        for candidate in candidates[:]:
                            if candidate.faction == character.faction:
                                continue
                            candidate.die("sudden death")

                        return True
                case "Obtain Glass hearts":
                    if current_change:
                        terrain = character.getHomeTerrain()
                        for (godId,godInfo) in src.gamestate.gamestate.gods.items():
                            lastPos = godInfo["lastHeartPos"]
                            godInfo["lastHeartPos"] = (terrain.xPosition,terrain.yPosition)
                        return True
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
                                            "method": "teleport",
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
                case "spawn room":
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
                                functionMap[(y, x)] = {
                                    "j": {
                                        "function": {
                                            "container": self,
                                            "method": "spawnRoom",
                                            "params": {"character":character},
                                        },
                                        "description": "spawn room",
                                    }
                                }

                        for room in terrain.rooms:
                            mapContent[room.yPosition][room.xPosition] = room.displayChar
                            del functionMap[(room.xPosition, room.yPosition)]
                        for scrapField in terrain.scrapFields:
                            mapContent[scrapField[1]][scrapField[0]] = "ss"
                            del functionMap[(scrapField[0], scrapField[1])]

                        submenue = src.menuFolder.mapMenu.MapMenu(
                            mapContent=mapContent,
                            functionMap=functionMap,
                            cursor=character.getBigPosition(),
                        )
                        character.macroState["submenue"] = submenue
                        return True
                case "Teleport Terrain":
                    if current_change:
                        functionMap = {}
                        for x in range(15):
                            for y in range(15):
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

                        submenue = src.menuFolder.terrainMenu.TerrainMenu(
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
                case "Clear Fog":
                    if current_change:
                        for x in range(1, 14):
                            for y in range(1, 14):
                                current_terrain = src.gamestate.gamestate.terrainMap[x][y]
                                character.terrainInfo[current_terrain.getPosition()] = {"tag": current_terrain.tag}
                        return True
                case "pass time":
                    if current_change:
                        submenue = src.menuFolder.inputMenu.InputMenu(
                            "Type amount of ticks to pass", targetParamName="ticks"
                        )
                        character.macroState["submenue"] = submenue
                        character.macroState["submenue"].followUp = {
                            "container": self,
                            "method": "action",
                            "params": {"character": character},
                        }
                case "toggle SDL":
                    if current_change:
                        src.interaction.allow_sdl = not src.interaction.allow_sdl
            text += "\n"

        src.interaction.main.set_text((src.interaction.urwid.AttrSpec("default", "default"), text))

        # exit submenu
        return key == "esc"

    def spawnRoom(self, params):
        '''
        spawn a room
        '''
        character = params["character"]
        src.magic.spawnRoom(character.getTerrain(),"EmptyRoom",params["coordinate"])

    def teleport(self, params):
        '''
        teleport character to a tile 
        '''

        # prepare parameters
        character = params["character"]
        terrain = character.getTerrain()
        position = params["coordinate"]

        # call the background mechanism
        src.magic.teleportToTile(character, position, terrain)

    def takeOverOnTile(self, params):
        character = params["character"]
        terrain = character.getTerrain()
        target_characters = terrain.getCharactersOnTile(params["coordinate"])
        if not target_characters:
            return

        target_character = random.choice(target_characters)
        src.gamestate.gamestate.mainChar = target_character

    def teleportToTerrain(self, params):
        '''
        teleport character to a terrain
        '''
        terrain_position = params["big_coordinate"]
        character = params["character"]

        src.magic.teleportToTerrain(character, terrain_position)

    def action(self, params):
        character = params["character"]

        if "code" in params:
            try:
                exec(params["code"],{"player":src.gamestate.gamestate.mainChar, "items":src.items.itemMap})
            except Exception as e:
                print("error: " + str(e))
            return

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
                            character.addToInventory(item_ty())
                    else:
                        character.addToInventory(item_ty())

                    character.addMessage(f"added {item_name}")
                    return

            character.addMessage(f"item ({item_name}) not found")

        if "big_coordinate" in params:
            self.teleportToTerrain(params)

        if "ticks" in params:
            params["delayTime"] = int(params["ticks"])
            params["action"]= "onDone"

            def onDone(params):
                ticks = params["delayTime"]
                character = params["character"]
                character.addMessage(f"passed {ticks} tick")

            dummy = src.items.Item()
            dummy.onDone = onDone
            dummy.delayedAction(params)

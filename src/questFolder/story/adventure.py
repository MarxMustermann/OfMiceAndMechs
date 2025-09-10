import random

import src

class Adventure(src.quests.MetaQuestSequence):
    '''
    quest to adventure and collect cool stuff
    '''
    type = "Adventure"
    def __init__(self, description="adventure", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.track = []

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step towards solving this quest
        '''

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))
        
        currentTerrain = character.getTerrain()
        if currentTerrain == character.getHomeTerrain():
            for room in character.getTerrain().rooms:
                for item in room.getItemsByType("SwordSharpener"):
                    if item.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["SharpenPersonalSword"]()
                        return ([quest],None)

            for room in character.getTerrain().rooms:
                for item in room.getItemsByType("ArmorReinforcer"):
                    if item.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["ReinforcePersonalArmor"]()
                        return ([quest],None)

            if character.health < character.adjustedMaxHealth:
                readyCoalBurner = False
                for room in currentTerrain.rooms:
                    for coalBurner in room.getItemsByType("CoalBurner"):
                        if not coalBurner.getMoldFeed(character):
                            continue
                        readyCoalBurner = True
                if readyCoalBurner:
                    quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=True)
                    return ([quest],None)

        if not character.weapon or not character.armor:
            quest = src.quests.questMap["Equip"](tryHard=True)
            return ([quest],None)

        try:
            character.lastMapSync
        except:
            character.lastMapSync = None
        if character.getTerrain() == character.getHomeTerrain():
            if (not character.lastMapSync) or src.gamestate.gamestate.tick-character.lastMapSync > 100:
                quest = src.quests.questMap["DoMapSync"]()
                return ([quest],None)
            for item in character.inventory:
                if item.walkable:
                    continue
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)

        if currentTerrain.tag == "shrine":
            # go home directly
            if character.getFreeInventorySpace() < 2:
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)

        if currentTerrain.tag == "ruin":
            if character.getFreeInventorySpace():
                # loot on current terrain
                info = character.terrainInfo[currentTerrain.getPosition()]
                if not info.get("looted"):
                    quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=currentTerrain.getPosition())
                    return ([quest], None)

        if character.searchInventory("Scrap"):
            if not character.container.getItemByPosition(character.getPosition()):
                submenue = character.macroState["submenue"]
                if submenue and not ignoreCommands:
                    if not isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu):
                        return (None,(["esc"],"close the menu"))

                index = 0
                command = ""
                while index < len(character.inventory):
                    if character.inventory[-(1+index)].type != "Scrap":
                        break
                    index += 1
                    command = "l"

                if command:
                    return (None, (command,"drop scrap"))

                index = 0
                command = []
                if not isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu):
                    command.append("i")

                startIndex = 0
                if isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu):
                    startIndex = submenue.cursor

                targetIndex = 0
                for item in character.inventory:
                    if item.type == "Scrap":
                        break
                    targetIndex += 1
                
                command.extend(["s"]*(targetIndex-startIndex))
                command.extend(["w"]*(startIndex-targetIndex))
                command.append("l")

                return (None, (command,"drop scrap"))

        # get all reasonable candidates to move to
        candidates = []
        extraWeight = {}
        for x in range(1,14):
            for y in range(1,14):
                coordinate = (x, y, 0)
                extraWeight[coordinate] = 0
                if coordinate in character.terrainInfo:
                    info = character.terrainInfo[coordinate]
                    if character.getFreeInventorySpace() < 2:
                        extraWeight[coordinate] = 2
                        if not info.get("tag") == "shrine":
                            continue
                    else:
                        if not info.get("tag") == "ruin":
                            continue
                        if info.get("looted"):
                            continue
                candidates.append(coordinate)

        # do special handling of the characters home
        homeCoordinate = (character.registers["HOMETx"], character.registers["HOMETy"], 0)
        if character.getFreeInventorySpace() < 2:
            candidates.append(homeCoordinate)
            extraWeight[coordinate] = 3
        else:
            if homeCoordinate in candidates:
                candidates.remove(homeCoordinate)

        if not len(candidates):
            if dryRun:
                self.fail()
            return (None, None)

        # sort weighted with slight random
        random.shuffle(candidates)
        candidates.sort(key=lambda x: src.helpers.distance_between_points(character.getTerrainPosition(), x)+random.random()-extraWeight[x])
        targetTerrain = candidates[0]

        # move to the actual target terrain
        if character.getFreeInventorySpace() and (targetTerrain != homeCoordinate):
            quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=targetTerrain)
        else:
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=targetTerrain)
        return ([quest], None)

    def generateTextDescription(self):
        '''
        generate a textual description to be shown on the UI
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        
        text = ["""
Go out and adventure{reason}.

track:

"""]
        homeCoordinate = (self.character.registers["HOMETx"], self.character.registers["HOMETy"], 0)
        characterCoordinate = self.character.getTerrain().getPosition()

        rawMap = []
        for y in range(15):
            rawMap.append([])
            for x in range(15):
                if x == 0 or y == 0 or x == 14 or y == 14:
                    rawMap[y].append("~~")
                else:
                    rawMap[y].append("  ")
            rawMap[y].append("\n")

        rawMap[homeCoordinate[1]][homeCoordinate[0]] = "HH"
        rawMap[characterCoordinate[1]][characterCoordinate[0]] = "@@"

        text.extend(rawMap)
        text.extend("\n")
        text.extend("0: Home base\n")
    
        counter = 1
        for item in self.track:
            text.append(f"{counter}: {item}\n")
            counter += 1
        return text

    def handleChangedTerrain(self,extraInfo):
        '''
        keep track of the trail of terrain the character visited
        '''
        terrain = extraInfo["character"].getTerrain()
        pos = terrain.getPosition()
        tag = terrain.tag
        self.track.append({"pos":pos,"tag":tag})

    def assignToCharacter(self, character):
        '''
        listen to the character changing the terrain
        '''
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        '''
        check and end quest if completed
        '''
        if not character:
            return False

        currentTerrain = character.getTerrain()
        if not currentTerrain.xPosition == character.registers["HOMETx"]:
            return False
        if not currentTerrain.yPosition == character.registers["HOMETy"]:
            return False

        if not character.getFreeInventorySpace() < 2:
            return False

        self.postHandler()
        return True

# register the quest type
src.quests.addType(Adventure)

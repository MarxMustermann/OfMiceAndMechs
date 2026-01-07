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
        Parameters:
            character:       the character doing the quest
            ignoreCommands:  whether to generate commands or not
            dryRun:          flag to be stateless or not
        Returns:
            the activity to run as next step
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # ensure good health
        if character.is_low_health():
            if character.canHeal():
                quest = src.quests.questMap["Heal"](reason="be in good health")
                return ([quest],None)
            return self._solver_trigger_fail(dryRun,"low health")

        # enter rooms properly
        if character.getBigPosition()[0] == 0:
            return (None, ("d","enter the terrain"))
        if character.getBigPosition()[0] == 14:
            return (None, ("a","enter the terrain"))
        if character.getBigPosition()[1] == 0:
            return (None, ("s","enter the terrain"))
        if character.getBigPosition()[1] == 14:
            return (None, ("w","enter the terrain"))

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](reason="defend yourself")
            return ([quest],None)

        # consume memories
        if character.searchInventory("MemoryFragment"):
            quest = src.quests.questMap["ConsumeItem"](itemType="MemoryFragment",description="extract memories",reason="gain insight or mana")
            return ([quest],None)
        
        # prepare for adventure
        currentTerrain = character.getTerrain()
        if currentTerrain == character.getHomeTerrain():
            
            # upgrade equipment
            for room in character.getTerrain().rooms:
                for item in room.getItemsByType("SwordSharpener"):
                    if item.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["SharpenPersonalSword"](reason="be able to cut deeper")
                        return ([quest],None)
            for room in character.getTerrain().rooms:
                for item in room.getItemsByType("ArmorReinforcer"):
                    if item.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["ReinforcePersonalArmor"](reason="be able to tank more hits")
                        return ([quest],None)

            # heal
            if character.health < character.adjustedMaxHealth:
                readyCoalBurner = False
                for room in currentTerrain.rooms:
                    for coalBurner in room.getItemsByType("CoalBurner",needsBolted=True):
                        if not coalBurner.getMoldFeed(character):
                            continue
                        readyCoalBurner = True
                if readyCoalBurner:
                    quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=True,reason="be in good health")
                    return ([quest],None)

            # ensure traps are clean
            for room in currentTerrain.rooms:
                if not room.tag == "trapRoom":
                    continue
                numItems = 0
                for item in room.itemsOnFloor:
                    if item.bolted == False:
                        if item.getPosition() not in room.walkingSpace:
                            continue
                        if room.getItemByPosition(item.getPosition())[0].bolted:
                            continue
                        numItems += 1
                if numItems > 4:
                    quest = src.quests.questMap["ClearTile"](targetPositionBig=room.getPosition(),reason="increase chances the traps will work")
                    return ([quest],None)

            # ensure not beeing encombered
            for item in character.inventory:
                if item.walkable:
                    continue
                quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="get rid of big items")
                return ([quest],None)
            if character.getFreeInventorySpace(ignoreTypes=["Bolt"]) < 5:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="make space for loot")
                return ([quest],None)

            # fetch ammo
            if character.getFreeInventorySpace():
                for room in currentTerrain.rooms:
                    if not room.getNonEmptyOutputslots("Bolt"):
                        continue
                    quest = src.quests.questMap["FetchItems"](toCollect="Bolt",reason="have some ammo to shoot")
                    return ([quest],None)

            # sync map
            if (not character.lastMapSync) or src.gamestate.gamestate.tick-character.lastMapSync > 100:
                quest = src.quests.questMap["DoMapSync"](reason="allow the base to remember if you die")
                return ([quest],None)

        # ensure basic equipment
        if not character.weapon or not character.armor:
            quest = src.quests.questMap["Equip"](tryHard=True,reason="not be defenseless")
            return ([quest],None)

        # go home directly if convinient
        if currentTerrain.tag == "shrine":
            if character.getFreeInventorySpace(ignoreTypes=["Bolt"]) < 2:
                quest = src.quests.questMap["GoHome"](reason="bring home loot")
                return ([quest],None)

        # interact with most menus
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if not isinstance(submenue,src.menuFolder.inventoryMenu.InventoryMenu):
                return (None,(["esc"],"close the menu"))

        # clear inventory from scrap
        if character.searchInventory("Scrap"):

            # find usable drop spots
            drop_offset = None
            for check_offet in ((0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
                check_position = character.getPosition(offset=check_offet)
                items = character.container.getItemByPosition(check_position)
                if len(items) > 1:
                    continue
                if items and items[0].type != "Scrap":
                    continue
                if items and not character.container.getPositionWalkable(items[0].getPosition()):
                    continue
                drop_offset = check_offet
                break

            # go to drop spot
            move_command = None
            if drop_offset == (1,0,0):
                move_command = "d"
            if drop_offset == (-1,0,0):
                move_command = "a"
            if drop_offset == (0,1,0):
                move_command = "s"
            if drop_offset == (0,-1,0):
                move_command = "w"
            if move_command:
                if character.macroState.get("submenue"):
                    return (None, (["esc"],"close menu"))
                return (None, (move_command,"go to drop spot"))

            # drop scrap that can be easily dropped
            if drop_offset == (0,0,0):
                index = 0
                command = ""
                while index < len(character.inventory):
                    if character.inventory[-(1+index)].type != "Scrap":
                        break
                    index += 1
                    command += "l"
                if command:
                    return (None, (command,"drop scrap"))

            # drop items from inventory
            if drop_offset == (0,0,0):
                if submenue:
                    command = submenue.get_command_to_select_item(item_type="Scrap",selectionCommand="l")
                    if command:
                        return (None,(command,"drop scrap"))
                else:
                    return (None, ("i","open inventory menu"))

        # close remaining menus
        if submenue and not ignoreCommands:
            return (None,(["esc"],"close the menu"))

        # loot ruins
        if currentTerrain.tag == "ruin":
            if character.getFreeInventorySpace():
                # loot on current terrain
                info = character.terrainInfo[currentTerrain.getPosition()]
                if not info.get("looted"):
                    quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=currentTerrain.getPosition(),reason="get more loot")
                    return ([quest], None)
        
        # get all reasonable candidates to move to with desirability
        candidates = []
        extraWeight = {}
        for x in range(1,14):
            for y in range(1,14):
                coordinate = (x, y, 0)
                extraWeight[coordinate] = 5
                if coordinate in character.terrainInfo:
                    info = character.terrainInfo[coordinate]
                    if character.getFreeInventorySpace(ignoreTypes=["Bolt"]) < 2:
                        extraWeight[coordinate] = 1
                        if not info.get("tag") == "shrine":
                            continue
                    else:
                        if not info.get("tag") == "ruin":
                            continue
                        if info.get("looted"):
                            continue
                if coordinate == (7,7,0): # avoid endgame dungeon
                    extraWeight[coordinate] = 32000
                candidates.append(coordinate)

        # do special handling of the characters home
        homeCoordinate = (character.registers["HOMETx"], character.registers["HOMETy"], 0)
        if character.getFreeInventorySpace(ignoreTypes=["Bolt"]) < 2:
            candidates.append(homeCoordinate)
            extraWeight[coordinate] = 1
        else:
            if homeCoordinate in candidates:
                candidates.remove(homeCoordinate)

        if not len(candidates):
            self._solver_trigger_fail(dryRun,"no candidates")

        # sort nearest target candidate skewed by desirebility with slight random
        best_candidate = None
        best_distance = None
        current_pos = character.getTerrainPosition()
        for candidate in candidates:
            distance = src.helpers.distance_between_points(current_pos, candidate)
            distance += extraWeight[candidate]
            distance += random.random()
            if best_candidate is None or distance < best_distance:
                best_distance = distance
                best_candidate = candidate
        targetTerrain = best_candidate

        # move to the actual target terrain
        if character.getFreeInventorySpace(ignoreTypes=["Bolt"]) and (targetTerrain != homeCoordinate):
            quest = src.quests.questMap["AdventureOnTerrain"](targetTerrain=targetTerrain,terrainsWeight = extraWeight,reason="gain more nice things")
        else:
            quest = src.quests.questMap["GoToTerrain"](targetTerrain=targetTerrain,reason="reach the target")

        return ([quest], None)

    def generateTextDescription(self):
        '''
        generate a textual description to be shown on the UI
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        
        text = [f"""
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
        for visit in self.track:
            pos = visit["pos"]
            rawMap[pos[1]][pos[0]] = "xx"

        rawMap[homeCoordinate[1]][homeCoordinate[0]] = "HH"
        rawMap[characterCoordinate[1]][characterCoordinate[0]] = "@@"

        text.extend(rawMap)
        text.extend("\n")
        text.extend("0: Home base\n")
    
        counter = 1
        for visit in self.track:
            text.append(f"{counter}: {visit}\n")
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

        self.clearSubQuests()

    def assignToCharacter(self, character):
        '''
        listen to the character changing the terrain
        '''
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
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

        if not character.getFreeInventorySpace(ignoreTypes=["Bolt"]) < 2:
            return False

        if not dryRun:
            self.postHandler()
        return True

# register the quest type
src.quests.addType(Adventure)

import src
import random

class CollectGlassHearts(src.quests.MetaQuestSequence):
    '''
    quest to collect glass hearts
    '''
    type = "CollectGlassHearts"

    def __init__(self, description="collect glass hearts", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.room_building_streak_length = 0

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"close menu"))

        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
            
        terrain = character.getTerrain()

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"]()
            return ([quest],None)

        if terrain.xPosition != character.registers["HOMETx"] or terrain.yPosition != character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        if character.health < character.maxHealth*0.75:
            if not (terrain.xPosition == character.registers["HOMETx"] and
                    terrain.yPosition == character.registers["HOMETy"]):
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)
            else:
                for room in terrain.rooms:
                    items = room.getItemsByType("CoalBurner",needsBolted=True)
                    for item in items:
                        if not item.getMoldFeed(character):
                            continue
                        quest = src.quests.questMap["Heal"](noWaitHeal=True)
                        return ([quest],None)

                quest = src.quests.questMap["BeUsefull"](numTasksToDo=1,failOnIdle=True)
                return ([quest],None)

        if character.flask.uses < 2:
            quest = src.quests.questMap["RefillPersonalFlask"]()
            return ([quest],None)

        # get number of glass hearts
        numGlassHearts = 0
        for room in character.getTerrain().rooms:
            for item in room.itemsOnFloor:
                if not (item.type == "GlassStatue"):
                    continue
                if not item.hasItem:
                    continue
                numGlassHearts += 1

        # count the number of enemies/allies
        npcCount = 0
        enemyCount = 0
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction != character.faction:
                    enemyCount += 1
                    if not room.alarm:
                        quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True,description="kill enemies that breached the defences")
                        return ([quest],None)
                else:
                    if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                        npcCount += 1
        for otherChar in terrain.characters:
            if otherChar.faction != character.faction:
                if otherChar.getBigPosition() in terrain.scrapFields:
                    continue

                enemyCount += 1
                if not terrain.alarm and enemyCount > 2:
                    quest = src.quests.questMap["ReadyBaseDefences"]()
                    return ([quest],None)
            else:
                if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                    npcCount += 1

        if enemyCount:
            quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
            return ([quest],None)


        terrain = character.getTerrain()
        scrapFields = terrain.scrapFields[:]
        for scrapField in scrapFields[:]:
            foundScrap = False
            for item in terrain.itemsByBigCoordinate.get(scrapField,[]):
                if item.type == "Scrap":
                    foundScrap = True
                    break
            if not foundScrap:
                scrapFields.remove(scrapField)

        if not scrapFields:
            terrain = character.getTerrain()
            if terrain.mana >= 20:
                quest = src.quests.questMap["GetEpochReward"](rewardType="spawn scrap",reason="ensure enough scrap is available")
                return ([quest],None)

        if len(character.terrainInfo) < numGlassHearts*3:
            if character.getFreeInventorySpace() < 3:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)

            quest = src.quests.questMap["Adventure"](description="explore the surroundings",reason="get some map awareness")
            return ([quest],None)

        # ensure there is a backup NPC
        if npcCount < numGlassHearts+4:
            hasDispenserCharges = 0
            for room in terrain.rooms:
                for item in room.getItemsByType("GooDispenser",needsBolted=True):
                    if item.charges:
                        hasDispenserCharges += item.charges

            if npcCount < 2:
                for room in terrain.rooms:
                    if not room.tag == "traproom":
                        continue
                    numItems = 0
                    for item in room.itemsOnFloor:
                        if item.bolted == False:
                            numItems += 1
                    if numItems > 4:
                        quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                        return ([quest],None)

            quest = src.quests.questMap["SpawnClone"]()
            return ([quest],None)

        # ensure the siege manager is configured
        if terrain.alarm:
            
            terrain = character.getTerrain()
            siegeManager = None
            for room in terrain.rooms:
                item = room.getItemByType("SiegeManager",needsBolted=True)
                if not item:
                    continue
                
                siegeManager = item

            if siegeManager:
                existingActions = []
                for scheduledAction in siegeManager.getActionList():
                    existingActions.append(scheduledAction[2]["type"])

                if "restrict outside" not in existingActions or "sound alarms" not in existingActions or "unrestrict outside" not in existingActions or "silence alarms" not in existingActions:
                    quest = src.quests.questMap["ConfigureSiegeManager"]()
                    return ([quest],None)

        # ensure there is enough trap rooms
        if numGlassHearts:

            # count trap rooms
            numTrapRooms = 0
            numNonTrapRooms = 0
            for room in character.getTerrain().rooms:
                if room.tag == "trapRoom":
                    numTrapRooms += 1
                else:
                    numNonTrapRooms += 1

            # ensure an appropriate number of trap rooms
            if numTrapRooms < numGlassHearts//2:

                # check to continue building open buildsite when convinent
                forceBuildRoom = False
                for room in terrain.rooms:
                    
                    # ignore non trap rooms
                    if not room.tag in ("traproom","entryRoom",):
                        continue

                    # check for neighbouring buildsites
                    offsets = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
                    roomBuilders = []
                    for offset in offsets:

                        # get room builder
                        roomPos = room.getPosition()
                        checkPos = (roomPos[0]+offset[0], roomPos[1]+offset[1], 0)
                        items = terrain.getItemByPosition((checkPos[0]*15+7,checkPos[1]*15+7,0))
                        if not len(items) == 1 or not items[0].type == "RoomBuilder":
                            continue
                        roomBuilder = items[0]

                        # set flad to force building, if the needed items are in inventory
                        missingItems = roomBuilder.get_missing_items()
                        for (itemType,position) in missingItems:
                            if character.searchInventory(itemType):
                                forceBuildRoom = True

                # either actively build base defences or pass time
                forceAdventure = False
                if self.room_building_streak_length >= 3:
                    forceAdventure = True
                if (random.random() < 0.5 or forceBuildRoom) and not forceAdventure:
                    if not dryRun:
                        self.room_building_streak_length += 1
                    quest = src.quests.questMap["StrengthenBaseDefences"](numTrapRoomsBuild=numGlassHearts//2,numTrapRoomsPlanned=numGlassHearts//2+1,lifetime=random.randint(100,500))
                    return ([quest],None)
                else:
                    if not dryRun:
                        self.room_building_streak_length = 0

                    # ensure at least one Clone has Room building as highest prio
                    foundClone = False
                    for candidate in terrain.getAllCharacters():
                        if not candidate.faction == character.faction:
                            continue
                        if candidate == character:
                            continue
                        if not candidate.getRandomProtisedDuties():
                            continue
                        if not candidate.getRandomProtisedDuties()[0] == "room building":
                            continue
                        foundClone = True
                    if not foundClone:
                        quest = src.quests.questMap["EnsureMaindutyClone"](dutyType="room building")
                        return ([quest],None)

                    # beat people up for fun .... erh to gather ressources
                    quest = src.quests.questMap["Adventure"](description="loot the surroundings",reason="get some useful resources and pass some time")
                    return ([quest],None)

        # ensure the base is set to auto expand
        foundCityPlaner = None
        for room in terrain.rooms:
            items = room.getItemsByType("CityPlaner",needsBolted=True)
            if not items:
                continue
            foundCityPlaner = items[0]
            break

        if foundCityPlaner:
            if not foundCityPlaner.autoExtensionThreashold:
                quest = src.quests.questMap["SetBaseAutoExpansion"](targetLevel=2)
                return ([quest],None)

        # fill empty rooms with life
        if foundCityPlaner and numGlassHearts:
            rooms = foundCityPlaner.getAvailableRooms()
            random.shuffle(rooms)
            if rooms:
                room = rooms[0]

                candidates = ["manufacturingHall","electrifierHall","smokingRoom"]
                random.shuffle(candidates)
                candidates.insert(0,"wallManufacturing")
                candidates.insert(0,"storage")
                for checkRoom in terrain.rooms:
                    if checkRoom.tag in candidates:
                        candidates.remove(checkRoom.tag)
                
                if candidates:
                    quest = src.quests.questMap["AssignFloorPlan"](floorPlanType=candidates[0],roomPosition=room.getPosition())
                    return ([quest],None)

            # ensure an appropriate number of economic rooms
            if numNonTrapRooms < 5+numGlassHearts+1:

                # ensure some walls are in storage
                hasWall = False
                inventoryWallsOnly = False
                if character.searchInventory("Wall"):
                    hasWall = True
                    inventoryWallsOnly = True
                for room in character.getTerrain().rooms:
                    if room.getNonEmptyOutputslots("Wall"):
                        hasWall = True
                        inventoryWallsOnly = False
                        break
                if not hasWall and character.getTerrain().search_item_by_type("Wall"):
                    quest = src.quests.questMap["Scavenge"](toCollect="Wall",lifetime=1000,tryHard=True)
                    return ([quest],None)

                # continue building a planned room
                planned_rooms = foundCityPlaner.plannedRooms[:]
                random.shuffle(planned_rooms)
                if planned_rooms:
                    found_build_site = None
                    for planned_room in planned_rooms[:]:
                        if character.getTerrain().getRoomByPosition(planned_room):
                            planned_rooms.remove(planned_room)
                            break
                        items = character.getTerrain().getItemByPosition((planned_room[0]*15+7,planned_room[1]*15+7,0))
                        if not len(items) == 1:
                            continue
                        if not items[0].type == "RoomBuilder":
                            continue
                        found_build_site = planned_room

                if planned_rooms:
                    if found_build_site:
                        coordinate = found_build_site
                    else:
                        coordinate = random.choice(foundCityPlaner.plannedRooms)
                    tryHard = True
                    if inventoryWallsOnly:
                        tryHard = False
                    quest = src.quests.questMap["BuildRoom"](targetPosition=coordinate,lifetime=1000,tryHard=tryHard,ignoreAlarm=True)
                    return ([quest],None)

        # get statues ready for teleport
        strengthRating = character.getStrengthSelfEstimate()
        readyStatues = {}
        for room in character.getTerrain().rooms:
            for item in room.itemsOnFloor:
                if not (item.type == "GlassStatue"):
                    continue
                if not (item.charges > 4) and not item.hasItem:
                    continue

                readyStatues[item.itemID] = item

        # try to do a dungeon run
        bestDungeon = None
        easiestTooHardDungeon = None
        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue

            if godId in readyStatues:
                if readyStatues[godId].hasItem:
                    continue
                dungeonStrength = 1+(readyStatues[godId].numTeleportsDone/10)
                if readyStatues[godId].numTeleportsDone and strengthRating < dungeonStrength:
                    if not easiestTooHardDungeon or easiestTooHardDungeon > dungeonStrength:
                        easiestTooHardDungeon = dungeonStrength
                    continue

                if not bestDungeon or bestDungeon[0] > readyStatues[godId].numTeleportsDone:
                    bestDungeon = (readyStatues[godId].numTeleportsDone,god,godId)
        if bestDungeon:
            quest = src.quests.questMap["DelveDungeon"](targetTerrain=bestDungeon[1]["lastHeartPos"],itemID=bestDungeon[2])
            return ([quest],None)

        if easiestTooHardDungeon and random.random() < 0.5:
            quest = src.quests.questMap["BecomeStronger"](targetStrength=easiestTooHardDungeon+0.1,lifetime=15*15*15)
            return ([quest],None)

        # unlock more statues
        if len(readyStatues) < 7:
            quest = src.quests.questMap["AppeaseAGod"](targetNumGods=len(readyStatues)+1, lifetime=random.randint(800,1500))
            return ([quest],None)

        # get stronger to be able to complete the unlocked dungeons
        quest = src.quests.questMap["BecomeStronger"](targetStrength=strengthRating+0.1)
        return ([quest],None)

    def generateTextDescription(self):
        try:
             self.room_building_streak_length
        except:
             self.room_building_streak_length = 0
        text = ["""
You reach out to your implant and it answers:

You were not accepted by the Throne as the supreme leader.
As long as you don't control all Glasshearts you can't ascend.
Fetch all GlassHearts, to be able to take the throne and rule the world.

The GlassHearts can be found in dungeons and are guarded.
Those dungeons can be accessed using the GlassStatues in the Temple.

Once you apeased the god of a GlassStatue, it will allow you to teleport to its dungeon.
So apease the gods and obtain their GlassHearts.
"""]
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue

            return False

        if not dryRun:
            self.postHandler()
        return True

    def handleQuestFailure(self,extraParam):
        if extraParam["reason"] == "no job":
            self.subQuests.remove(extraParam["quest"])

            newQuest = src.quests.questMap["Heal"](noVialHeal=True)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return

        super().handleQuestFailure(extraParam)

src.quests.addType(CollectGlassHearts)

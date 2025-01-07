import src
import random

class CollectGlassHearts(src.quests.MetaQuestSequence):
    type = "CollectGlassHearts"

    def __init__(self, description="collect glass hearts", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

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
                enemyCount += 1
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)
            else:
                if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                    npcCount += 1

        # ensure there is a backup NPC
        if npcCount < numGlassHearts+2:
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

            if npcCount < 2 or hasDispenserCharges > 2:
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
                for actionDefintion in siegeManager.schedule.values():
                    existingActions.append(actionDefintion["type"])

                if "restrict outside" not in existingActions or "sound alarms" not in existingActions or "unrestrict outside" not in existingActions or "silence alarms" not in existingActions:
                    quest = src.quests.questMap["ConfigureSiegeManager"]()
                    return ([quest],None)

        if numGlassHearts:

            numTrapRooms = 0
            for room in character.getTerrain().rooms:
                if room.tag == "traproom":
                    numTrapRooms += 1

            if numTrapRooms < numGlassHearts//2:
                quest = src.quests.questMap["StrengthenBaseDefences"](numTrapRoomsBuild=numGlassHearts//2,numTrapRoomsPlanned=numGlassHearts//2+1,lifetime=1000)
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
            quest = src.quests.questMap["AppeaseAGod"](targetNumGods=len(readyStatues)+1, lifetime=1000)
            return ([quest],None)

        # get stronger to be able to complete the unlocked dungeons
        quest = src.quests.questMap["BecomeStronger"](targetStrength=strengthRating+0.1)
        return ([quest],None)

    def generateTextDescription(self):
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

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue

            return False

        self.postHandler()

    def handleQuestFailure(self,extraParam):
        if extraParam["reason"] == "no job":
            self.subQuests.remove(extraParam["quest"])

            newQuest = src.quests.questMap["Heal"](noVialHeal=True)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return

        super().handleQuestFailure(extraParam)

src.quests.addType(CollectGlassHearts)

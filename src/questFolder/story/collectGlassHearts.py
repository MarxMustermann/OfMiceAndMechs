import src

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

        terrain = character.getTerrain()

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

        # count the number of enemies/allies
        npcCount = 0
        enemyCount = 0
        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if otherChar.faction != character.faction:
                enemyCount += 1
            else:
                npcCount += 1
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction != character.faction:
                    enemyCount += 1
                else:
                    npcCount += 1

        # remove all enemies from terrain
        # ? should that only mean hunters ?
        if enemyCount > 0:
            quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
            return ([quest],None)

        # ensure there is a backup NPC
        if npcCount < 2:
            items = terrain.getRoomByPosition((7,8,0))[0].getItemByPosition((2,3,0))
            for item in items:
                if item.type != "GooFlask":
                    continue
                if item.uses < 100:
                    continue
                quest = src.quests.questMap["SpawnClone"]()
                return ([quest],None)

        strengthRating = character.getStrengthSelfEstimate()
        readyStatues = {}
        for room in character.getTerrain().rooms:
            for item in room.itemsOnFloor:
                if not (item.type == "GlassStatue"):
                    continue
                if not (item.charges > 4):
                    continue
                readyStatues[item.itemID] = item


        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue

            if godId in readyStatues:

                if strengthRating < readyStatues[godId].numTeleportsDone:
                    continue

                quest = src.quests.questMap["DelveDungeon"](targetTerrain=god["lastHeartPos"],itemID=godId,suicidal=True)
                return ([quest],None)

        if len(readyStatues) < 7:
            quest = src.quests.questMap["AppeaseAGod"](targetNumGods=len(readyStatues)+1)
            return ([quest],None)

        quest = src.quests.questMap["BecomeStronger"]()
        return ([quest],None)

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

You were not accepted by the Throne as the supreme leader.
As long as you don't control all Glasshearts you can't ascend.
Fetch all GlassHearts and rule the world.

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

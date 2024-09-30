import src


class CollectGlassHearts(src.quests.MetaQuestSequenceV2):
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
                        quest = src.quests.questMap["Heal"]()
                        return ([quest],None)
                quest = src.quests.questMap["BeUsefull"](numTasksToDo=1)
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
            quest = src.quests.questMap["ClearTerrain"]()
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
                quest = src.quests.questMap["DelveDungeon"](targetTerrain=god["lastHeartPos"],itemID=godId,suicidal=True)
                return ([quest],None)

        quest = src.quests.questMap["AppeaseAGod"]()
        return ([quest],None)


    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

You have control over the base now, but your ressources are limited.
You need to use magic to keep the base runnning in the long term.

The GlassStatues in the temple allow you to cast magic.
This will use up the mana of the area.

The mana will slowly regenerate, but there is a faster way.
The GlassStatues are missing their hearts.
Obtain their GlassHeart and make them whole.

This will give you 3 advantages:
1. you will get a immediate mana boost
2. the GlassStatues will generate extra mana each epoch
3. the cost for using magic will be halfed

"""]
        if not self.subQuests:
            text.append("press + to generate a sub quest") 
        else:
            text.append("press d to view sub quest")
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

src.quests.addType(CollectGlassHearts)

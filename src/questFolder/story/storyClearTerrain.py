import src
import random


class StoryClearTerrain(src.quests.MetaQuestSequence):
    type = "StoryClearTerrain"

    def __init__(self, description="secure terrain", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # ensure healing for the clones
        terrain = character.getTerrain()
        for room in terrain.rooms:
            regenerator = room.getItemByType("Regenerator",needsBolted=True)
            if regenerator and not regenerator.activated:
                quest = src.quests.questMap["ActivateRegenerator"]()
                return ([quest],None)

        # count the number of enemies/allies
        terrain = character.getTerrain()
        npcCount = 0
        enemyCount = 0
        snatcherCount = 0
        for otherChar in terrain.characters:
            if otherChar.faction != "city #1":
                enemyCount += 1 
                if otherChar.charType == "Snatcher":
                    snatcherCount += 1 
            else:
                if otherChar.charType == "Ghoul":
                    continue
                npcCount += 1 
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction != "city #1":
                    enemyCount += 1 
                else:
                    if otherChar.charType == "Ghoul":
                        continue
                    npcCount += 1 

        # ensure the character has good health
        if character.health < 80:
            characterHasVial = False
            vials = character.searchInventory("Vial")
            for vial in vials:
                if vial.uses > 0:
                    characterHasFlask = True

            readyCoalBurner = False
            for room in terrain.rooms:
                for coalBurner in room.getItemsByType("CoalBurner"):
                    if not coalBurner.getMoldFeed(character):
                        continue
                    readyCoalBurner = True

            if characterHasVial or readyCoalBurner:
                quest = src.quests.questMap["Heal"](noWaitHeal=True)
                return ([quest],None)

            if not character.getFreeInventorySpace():
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)

            quest = src.quests.questMap["Scavenge"](lifetime=500)
            return ([quest],None)

        # kill snatchers (redundant to GetRank2Promotion)
        if snatcherCount:
            quest = src.quests.questMap["ConfrontSnatchers"]()
            return ([quest],None)

        for room in terrain.rooms:
            if not room.tag == "traproom":
                continue
            hasEnemy = False
            for otherCharacter in room.characters:
                if otherCharacter.faction == character.faction:
                    continue
                hasEnemy = True

            if hasEnemy:
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)

        # check for spider lairs
        targets_found = []
        specialSpiderBlockersFound = []
        for x in range(1,14):
            for y in range(1,14):
                numSpiders = 0
                numSpiderlings = 0

                for otherChar in terrain.charactersByTile.get((x,y,0),[]):
                    if otherChar.charType == "Spider":
                        numSpiders += 1
                    if otherChar.charType == "Spiderling":
                        numSpiderlings += 1

                if numSpiders:
                    targets_found.append(("spider",(x,y,0),numSpiders))
                    pos = (5,8,0)
                    if (x,y,0) == pos:
                        specialSpiderBlockersFound = [pos]
                if numSpiderlings:
                    targets_found.append(("spiderling",(x,y,0),numSpiderlings))

        if targets_found:
            # clear first spider spot
            if specialSpiderBlockersFound:
                quest = src.quests.questMap["BaitSpiders"](targetPositionBig=specialSpiderBlockersFound[0])
                return ([quest],None)

            # select target
            target = random.choice(targets_found)

            # clear spiders
            if target[0] == "spider":
                spider_lair_pos = target[1]

                quest = src.quests.questMap["BaitSpiders"](targetPositionBig=spider_lair_pos)
                return ([quest],None)

            # clear spiderlings
            if target[0] == "spiderling":
                spider_lair_pos = target[1]

                quest = src.quests.questMap["SecureTile"](toSecure=spider_lair_pos,endWhenCleared=True)
                return ([quest],None)

        targets_found = {}
        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            tilePos = otherChar.getBigPosition()
            targets_found[tilePos] = targets_found.get(tilePos,0)+1

        if targets_found:
            target = random.choice(list(targets_found.keys()))
            quest = src.quests.questMap["SecureTile"](toSecure=target,endWhenCleared=True)
            return ([quest],None)

        quest = src.quests.questMap["ClearTerrain"]()
        return ([quest],None)

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

Clear the terrain from all enmies, to be able to get promoted to base commander.
This will allow you to contact main base.

There are several types of enemies, that have different behaviour.
I'll show you how to deal with each of them,
but as long as the enmies die you get the promotion.
So experiment on your own on how to best beat the enemies.

Remember that the base provides you with important ressources and healing.
"""]
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
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

        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            return False

        self.postHandler()

src.quests.addType(StoryClearTerrain)

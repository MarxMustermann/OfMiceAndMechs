import src
import random

class StoryClearTerrain(src.quests.MetaQuestSequence):
    type = "StoryClearTerrain"
    def __init__(self, description="secure terrain", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](suicidal=True,reason="get rid of the enemies")
            return ([quest],None)

        # loot tile
        if not character.getTerrain().alarm and not character.container.isRoom and not character.getBigPosition() == (8,7,0):
            if character.getFreeInventorySpace():
                for item in character.container.itemsByBigCoordinate.get(character.getBigPosition(),[]):
                    if item.bolted:
                        continue
                    if item.type in ("Wall","Scrap","MoldFeed","Bolt"):
                        continue
                    quest = src.quests.questMap["LootRoom"](targetPositionBig=character.getBigPosition(),endWhenFull=True, reason="gather useful items")
                    return ([quest],None)

        # ensure healing for the clones
        terrain = character.getTerrain()
        for room in terrain.rooms:
            regenerator = room.getItemByType("Regenerator",needsBolted=True)
            if regenerator and not regenerator.activated:
                quest = src.quests.questMap["ActivateRegenerator"](reason="ensure all clones can heal")
                return ([quest],None)

        # count the number of enemies/allies
        terrain = character.getTerrain()
        npcCount = 0
        enemyCount = 0
        snatcherCount = 0
        spectreCount = 0
        for otherChar in terrain.characters:
            if otherChar.faction != "city #1":
                enemyCount += 1 
                if otherChar.charType == "Snatcher":
                    snatcherCount += 1 
                if otherChar.charType == "Spectre":
                    spectreCount += 1
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

        # ensure there are backup npcs
        if npcCount < 2:
            quest = src.quests.questMap["SpawnClone"](reason="have some clones in the base")
            return ([quest],None)

        # ensure the character has equipment
        if not character.armor or not character.weapon:
            quest = src.quests.questMap["Equip"](reason="be able to defend yoursef", tryHard=True)
            return ([quest],None)

        # ensure proper weapons
        if character.weapon and character.weapon.type == "Rod":
            quests = [] 
            quests.append(src.quests.questMap["MetalWorking"](toProduce="Sword",reason="have a proper weapon available", tryHard=True))
            quests.append(src.quests.questMap["Equip"](reason="be able to defend yoursef", tryHard=True))
            return (list(reversed(quests)),None)

        # ensure the character has good health
        if character.health < 80:

            # check what resources are available
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

            # heal using available resources
            if characterHasVial or readyCoalBurner:
                quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=True,reason="have energy to fight again")
                return ([quest],None)

            # try to find more healing resources
            if not character.getFreeInventorySpace():
                quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="be able to collect some healing items")
                return ([quest],None)
            if not terrain.alarm:
                quest = src.quests.questMap["Scavenge"](lifetime=500,reason="collect some healing items")
                return ([quest],None)

            # heal any way possible
            quest = src.quests.questMap["Heal"](noVialHeal=True,reason="be able to fight again")
            return ([quest],None)

        # kill snatchers (redundant to GetRank2Promotion)
        if snatcherCount:
            quest = src.quests.questMap["ConfrontSnatchers"](reason="be able to move outside")
            return ([quest],None)

        # handle an ongoing wave
        if spectreCount:
            quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
            return ([quest],None)

        # unrestrict outside movement
        if terrain.alarm:
            quest = src.quests.questMap["LiftOutsideRestrictions"](reason="make the clones to work outside")
            return ([quest],None)

        # defend against waves from areana room
        for room in terrain.rooms:
            if not room.tag == "trapRoom":
                continue
            hasEnemy = False
            for otherCharacter in room.characters:
                if otherCharacter.faction == character.faction:
                    continue
                hasEnemy = True
            if hasEnemy:
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)

        # upgrade equipment if possible
        for room in character.getTerrain().rooms:
            for item in room.getItemsByType("SwordSharpener"):
                if item.readyToBeUsedByCharacter(character,extraIncrease=1):
                    quest1 = src.quests.questMap["SharpenPersonalSword"](reason="be able to cut deeper")
                    quest2 = src.quests.questMap["ClearInventory"](returnToTile=False,reason="have more space for items")
                    return ([quest2,quest1],None)
        for room in character.getTerrain().rooms:
            for item in room.getItemsByType("ArmorReinforcer"):
                if item.readyToBeUsedByCharacter(character,extraIncrease=1):
                    quest1 = src.quests.questMap["ReinforcePersonalArmor"](reason="get hurt less")
                    quest2 = src.quests.questMap["ClearInventory"](returnToTile=False,reason="be able to collect more")
                    return ([quest2,quest1],None)

        # check for spider lairs
        targets_found = []
        specialSpiderBlockersFound = []
        for x in range(1,14):
            for y in range(1,14):
                numSpiders = 0
                numSpiderlings = 0
                for otherChar in terrain.charactersByTile.get((x,y,0),[]):
                    if otherChar.dead or otherChar.getBigPosition() != (x,y,0):
                        terrain.charactersByTile[(x,y,0)].remove(otherChar)
                        break
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

        # clear spider lairs
        if targets_found:

            # clear first spider spot
            if specialSpiderBlockersFound:
                quest = src.quests.questMap["BaitSpiders"](targetPositionBig=specialSpiderBlockersFound[0],reason="get rid of them")
                return ([quest],None)

            # select target
            targets_found.sort(key=lambda x: src.helpers.distance_between_points(x[1],character.getTilePosition()))
            target = targets_found[0]

            reason = "reduce the amount of enemies"

            # clear spiders
            if target[0] == "spider":
                spider_lair_pos = target[1]

                if target[2] > 2:
                    quest = src.quests.questMap["BaitSpiders"](targetPositionBig=spider_lair_pos,reason=reason)
                    return ([quest],None)
                else:
                    quest = src.quests.questMap["SecureTile"](toSecure=spider_lair_pos,endWhenCleared=True,reason=reason)
                    return ([quest],None)

            # clear spiderlings
            if target[0] == "spiderling":
                spider_lair_pos = target[1]

                quest = src.quests.questMap["SecureTile"](toSecure=spider_lair_pos,endWhenCleared=True,reason=reason)
                return ([quest],None)

        # get generic enemy groupings
        targets_found = {}
        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            tilePos = otherChar.getBigPosition()
            targets_found[tilePos] = targets_found.get(tilePos,0)+1

        # attack enemy groupings
        if targets_found:
            targets_pos = list(targets_found.keys())
            targets_pos.sort(key=lambda x: src.helpers.distance_between_points(x,character.getTilePosition()))
            target = targets_pos[0]
            quest = src.quests.questMap["SecureTile"](toSecure=target,endWhenCleared=True,reason="eliminate more enemies")
            return ([quest],None)

        # run the normal quest
        quest = src.quests.questMap["ClearTerrain"](reason="get rid of the last enemies")
        return ([quest],None)

    def generateTextDescription(self):
        reason_string = ""
        if self.reason:
            reason_string = f", {self.reason}"
        text = [f"""
Clear the terrain from all enemies{reason_string}.
This will allow you to contact main base.

There are several types of enemies, that have different behaviour.
I'll show you how to deal with each of them,
but as long as the enemies die you get the promotion.
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

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        terrain = character.getTerrain()
        for otherChar in terrain.characters:
            if otherChar.faction == character.faction:
                continue
            return False
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction == character.faction:
                    continue
                return False

        if not dryRun:
            self.postHandler()
        return True

    def handleQuestFailure(self,extraParam):
        '''
        handle a subquest failing
        '''

        super().handleQuestFailure(extraParam)

        # set up helper variables
        quest = extraParam.get("quest")
        reason = extraParam.get("reason")

        if reason:
            if reason == "no tile path":
                if quest.type == "SecureTile":
                    newQuest = src.quests.questMap["ClearPathToTile"](targetPositionBig=quest.targetPosition, reason="be able to reach the enemy")
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

src.quests.addType(StoryClearTerrain)

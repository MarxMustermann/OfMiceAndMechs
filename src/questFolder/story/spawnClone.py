import src

class SpawnClone(src.quests.MetaQuestSequence):
    type = "SpawnClone"

    def __init__(self, description="spawn clone", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.tryHard = tryHard

    def handleQuestFailure(self,extraParam):
        if extraParam["quest"] not in self.subQuests:
            return

        self.subQuests.remove(extraParam["quest"])
        quest = extraParam["quest"]

        reason = extraParam.get("reason")
        if reason == "no source for item GooFlask":
            if not self.character.getBigPosition() == (7,8,0):
                newQuest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
                self.addQuest(newQuest)
                self.startWatching(newQuest,self.handleQuestFailure,"failed")
                return

            for (coord,itemList) in self.character.getTerrain().itemsByBigCoordinate.items():
                if self.character.getTerrain().getRoomByPosition(coord):
                    continue
                for item in itemList:
                    if not item.type == "GooFlask":
                        continue

                    newQuest = src.quests.questMap["ScavengeTile"](targetPosition=coord,toCollect="GooFlask",tryHard=True)
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

            for room in self.character.getTerrain().rooms:
                for item in room.getItemsByType("GooDispenser"):
                    if item.charges > 0:
                        newQuest = src.quests.questMap["FillFlask"]()
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        newQuest = src.quests.questMap["FetchItems"](toCollect="Flask",tryHard=True,amount=1)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

            if self.character.container.isRoom:
                for item in self.character.container.getItemsByType("GooProducer"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition())
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

                for item in self.character.container.getItemsByType("BioPress"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition())
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

                for item in self.character.container.getItemsByType("BloomShredder"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition())
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

            for room in self.character.getTerrain().rooms:
                if room.getNonEmptyOutputslots("Bloom"):
                    newQuest = src.quests.questMap["FetchItems"](toCollect="Bloom")
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

            # ensure traprooms don't fill up
            for room in self.character.getTerrain().rooms:
                if not room.tag == "traproom":
                    continue
                numItems = 0
                for item in room.itemsOnFloor:
                    if item.bolted == False:
                        numItems += 1
                if numItems > 4:
                    quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                    return ([quest],None)

            # farm for blooms
            newQuest = src.quests.questMap["FarmMold"](tryHard=True)
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            return

        self.fail(reason)

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getBigPosition() == (7,8,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
            return ([quest],None)

        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            return (None,None)

        growthTank = character.container.getItemByType("GrowthTank")
        if not growthTank:
            self.fail(reason="no growth tank found")
            return (None,None)

        if not growthTank.filled and len(growthTank.getFlasks(character)) < 1:
            quest = src.quests.questMap["FetchItems"](toCollect="GooFlask",amount=1)
            return ([quest],None)

        itemPos = growthTank.getPosition()
        if character.getDistance(itemPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=growthTank.getPosition(),reason="to be able to use the growth tank",description="go to growth tank",ignoreEndBlocked=True)
            return ([quest],None)

        if character.macroState.get("itemMarkedLast"):
            if character.macroState["itemMarkedLast"].type == "GrowthTank":
                if character.macroState["itemMarkedLast"].filled:
                    return (None,("j","spawn clone"))
                else:
                    return (None,("j","refill growth tank"))
            else:
                return (None,(".","undo selection"))

        direction = ""
        if character.getPosition(offset=(1,0,0)) == itemPos:
            direction = "d"
        if character.getPosition(offset=(-1,0,0)) == itemPos:
            direction = "a"
        if character.getPosition(offset=(0,1,0)) == itemPos:
            direction = "s"
        if character.getPosition(offset=(0,-1,0)) == itemPos:
            direction = "w"

        if growthTank.filled:
            return (None,(direction+"j","spawn clone"))
        else:
            return (None,(direction+"j","refill growth tank"))

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

The base is a safe place to be now.
But every base as small as it may be should have a crew of at least two.
That way the base can recover in case a fatalaty.

Spawn a clone to have a backup in case of emergencies.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleSpawn, "spawned clone")
        self.startWatching(character,self.noFlask, "no flask")
        super().assignToCharacter(character)

    def noFlask(self,extraInfo=None):
        self.fail("no flask")

    def handleSpawn(self,extraInfo=None):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

src.quests.addType(SpawnClone)

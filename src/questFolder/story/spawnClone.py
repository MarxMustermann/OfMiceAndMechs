import src
import random

class SpawnClone(src.quests.MetaQuestSequence):
    '''
    quest for a NPC to spawn more NPcs
    '''
    type = "SpawnClone"
    def __init__(self, description="spawn clone", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.tryHard = tryHard

    def handleQuestFailure(self,extraParam):
        '''
        try to fix the condition if the quest fails
        '''

        # handle weird edge case
        if extraParam["quest"] not in self.subQuests:
            return

        # remove failed quest
        self.subQuests.remove(extraParam["quest"])

        # set up helper variables
        quest = extraParam["quest"]

        # try to get a goo flask
        reason = extraParam.get("reason")
        if reason == "no source for item GooFlask":

            # go to spawn room (obsolete?)
            if not self.character.getBigPosition() == (7,8,0):
                newQuest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to spawning room",description="go to spawning room")
                self.addQuest(newQuest)
                self.startWatching(newQuest,self.handleQuestFailure,"failed")
                return

            # pick up goo flask from the environment
            for (coord,itemList) in self.character.getTerrain().itemsByBigCoordinate.items():
                if self.character.getTerrain().getRoomByPosition(coord):
                    continue
                is_guarded = False
                for check_character in self.character.getTerrain().getCharactersOnTile(coord):
                    if check_character.faction != self.character.faction:
                        is_guarded = True
                        continue
                if is_guarded:
                    continue
                for item in itemList:
                    if not item.type == "GooFlask":
                        continue
                    newQuest = src.quests.questMap["ScavengeTile"](targetPositionBig=coord,toCollect="GooFlask",tryHard=True, reason="pick up goo flasks")
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

            # refill flask at goo dispenser
            for room in self.character.getTerrain().rooms:
                for item in room.getItemsByType("GooDispenser"):
                    if item.charges > 0:
                        newQuest = src.quests.questMap["FillFlask"](reason="have a full goo flask")
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        newQuest = src.quests.questMap["FetchItems"](toCollect="Flask",tryHard=True,amount=1,reason="have a flask to fill")
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

            # fetch any goo flasks lying around
            for room in self.character.getTerrain().rooms:
                for item in room.getItemsByType("GooFlask"):
                    newQuest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=item.getPosition(),reason="pick up GooFlask")
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

            # produce goo
            if self.character.container.isRoom:
                
                # produce goo
                for item in self.character.container.getItemsByType("GooProducer"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="be able to fill your flask")
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

                # produce goo precursor (PressCake)
                for item in self.character.container.getItemsByType("BioPress"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="be able to produce goo")
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

                # produce goo precursor (BioMass)
                for item in self.character.container.getItemsByType("BloomShredder"):
                    if item.readyToUse():
                        newQuest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="work towards producing goo")
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                        return

            # refill bloom shredder
            bloom_availabe = False
            for room in self.character.getTerrain().rooms:
                if room.getNonEmptyOutputslots("Bloom"):
                    bloom_availabe = True
            if bloom_availabe:
                for room in self.character.getTerrain().rooms:
                    for item in room.getItemsByType("BloomShredder",needsBolted=True):
                        drop_position = item.getPosition(offset=(-1,0,0))
                        if not room.getPositionWalkable(drop_position):
                            continue
                        newQuest = src.quests.questMap["RestockRoom"](toRestock="Bloom",targetPositionBig=room.getPosition(),targetPosition=drop_position,reason="fill the BloomShredders input")
                        self.addQuest(newQuest)
                        newQuest = src.quests.questMap["FetchItems"](toCollect="Bloom",reason="have blooms to feed into the BloomShredder")
                        self.addQuest(newQuest)
                        return

            # ensure traprooms don't fill up
            for room in self.character.getTerrain().rooms:
                if not room.tag == "trapRoom":
                    continue
                numItems = 0
                for item in room.itemsOnFloor:
                    if item.bolted == False:
                        if item.getPosition() not in room.walkingSpace:
                            continue
                        numItems += 1
                if numItems > 4:
                    newQuest = src.quests.questMap["ClearTile"](targetPositionBig=room.getPosition(),reason="maintain trap rooms")
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return

            # get the base state
            hasClone = False
            for other_character in self.character.getTerrain().getAllCharacters():
                if other_character == self.character:
                    continue
                if other_character.faction != self.character.faction:
                    continue
                hasClone = True

            # try to loot goo flasks from the surroundings
            if hasClone and random.random() < 0.5:
                newQuest = src.quests.questMap["Adventure"](lifetime=random.random()*10000+2000,reason="find some goo flasks")
                self.addQuest(newQuest)
                self.startWatching(newQuest,self.handleQuestFailure,"failed")
                return

            # generate more blooms
            newQuest = src.quests.questMap["FarmMold"](tryHard=True,lifetime=1000,reason="obtain some blooms")
            self.addQuest(newQuest)
            self.startWatching(newQuest,self.handleQuestFailure,"failed")
            newQuest = src.quests.questMap["Heal"](noWaitHeal=True,reason="be safe while farming")
            self.addQuest(newQuest)
            return

        # fail recursively
        self.fail(reason)

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        generate the next step towards solving the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)


        # go home
        if not character.isOnHomeTerrain():
            quest = src.quests.questMap["GoHome"](reason="get inside")
            return ([quest],None)

        # enter room fully
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter tile"))
            if character.xPosition%15 == 14:
                return (None,("a","enter tile"))
            if character.yPosition%15 == 0:
                return (None,("s","enter tile"))
            if character.yPosition%15 == 14:
                return (None,("w","enter tile"))
            quest = src.quests.questMap["GoHome"](reason="work from inside")
            return ([quest],None)

        # go to room with growth tank
        growthTank = character.container.getItemByType("GrowthTank")
        if not growthTank:
            for room in character.getTerrain().rooms:
                growthTank = room.getItemByType("GrowthTank")
                if not growthTank:
                    continue
                quest = src.quests.questMap["GoToTile"](targetPosition=growthTank.getBigPosition(),reason="go to spawning room",description="go to spawning room")
                return ([quest],None)
        if not growthTank:
            return self._solver_trigger_fail(dryRun,"no growth tank found")

        if len(growthTank.container.getItemByPosition(growthTank.getPosition(offset=(1,0,0)))) > 1:
            quest = src.quests.questMap["CleanSpace"](targetPosition=growthTank.getPosition(offset=(1,0,0)),targetPositionBig=growthTank.getBigPosition(),abortOnfullInventory=False,reason="clean up the growths tanks output")
            return ([quest],None)

        if not growthTank.filled and len(growthTank.getFlasks(character)) < 1:
            quest = src.quests.questMap["FetchItems"](toCollect="GooFlask",amount=1,reason="be able to spawn a clone")
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

        return (None,(direction+"j","refill growth tank"))

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        return ["""
You reach out to your implant and it answers:

The base is a safe place to be now.
But every base as small as it may be should have a crew of at least two.
That way the base can recover in case a fatalaty.

Spawn a clone to have a backup in case of emergencies.
"""]

    def assignToCharacter(self, character):
        '''
        start listening to events
        '''
        if self.character:
            return

        self.startWatching(character,self.handleSpawn, "spawned clone")
        self.startWatching(character,self.noFlask, "no flask")
        super().assignToCharacter(character)

    def noFlask(self,extraInfo=None):
        '''
        fail if there are no flasks
        '''
        self.fail("no flask")

    def handleSpawn(self,extraInfo=None):
        '''
        end quest if a new character was spawned
        '''
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        never complete without event
        '''
        if not character:
            return False

        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "GrowthTank":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result


# register the quest type
src.quests.addType(SpawnClone)

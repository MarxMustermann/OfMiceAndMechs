import random

import src


class SetUpMachine(src.quests.MetaQuestSequence):
    type = "SetUpMachine"

    def __init__(self, description="set up machine", creator=None, command=None, lifetime=None, itemType=None,tryHard=False,targetPosition=None,targetPositionBig=None,room=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.room = room
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"

        text = f"""
set up a machine to produce {self.itemType}{reason}.

"""

        text += f"""
Set the machine up on position {self.targetPosition} on tile {self.targetPositionBig}
"""

        neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
        text += f"""
{self.itemType} machines are produced by a machine machine.
A blueprint for {self.itemType} is required in the machine machine.
Examine the machine machine for more details.
"""

        if self.tryHard:
            text += f"""
Try as hard as you can to achieve this.
If you don't find a {self.itemType} blueprint, research it.
"""

        return text

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if not self.subQuests:

            itemPlaced = None
            if self.targetPosition:
                if self.targetPositionBig:
                    terrain = character.getTerrain()
                    rooms = terrain.getRoomByPosition(self.targetPositionBig)
                    if rooms:
                        container = rooms[0]
                    else:
                        container = terrain
                else:
                    container = character.container

                if container.isRoom:
                    items = container.getItemByPosition((self.targetPosition[0],self.targetPosition[1],0))
                else:
                    items = container.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))

                if items and items[-1].type == "Machine" and items[-1].toProduce == self.itemType:
                    itemPlaced = items[-1]

            if itemPlaced:
                if itemPlaced.bolted:
                    return (None,None)
                if itemPlaced.container != character.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="go to the tile the Machine is to be placed")
                    return ([quest],None)
                if character.getDistance(itemPlaced.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="go to machine")
                    return ([quest],None)

                directions = [((0,0,0),""),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == itemPlaced.getPosition():
                        return (None,(direction[1]+"cb","bolt down the machine"))


            if character.inventory and character.inventory[-1].type == "Machine" and character.inventory[-1].toProduce == self.itemType:
                if not self.targetPosition:
                    validTargetPosition = False
                    terrain = character.getTerrain()
                    counter = 0
                    while not validTargetPosition and counter < 10:
                        counter += 1
                        targetPosition = (random.randint(3,9),random.randint(3,9),0)
                        cityPlanner = terrain.getRoomByPosition((7,7,0))[0].getItemByPosition((5,2,0))[0]
                        if cityPlanner.generalPurposeRooms:
                            roomPos = random.choice(cityPlanner.generalPurposeRooms)
                            room = terrain.getRoomByPosition(roomPos)[0]
                        else:
                            room = random.choice(terrain.rooms)

                        if room.getItemByPosition(targetPosition) or room.getPaintedByPosition(targetPosition):
                            continue
                        if room.getItemByPosition((targetPosition[0]-1,targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((targetPosition[0]+1,targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((targetPosition[0],targetPosition[1]+1,0)):
                            continue
                        if room.getItemByPosition((targetPosition[0],targetPosition[1]-1,0)):
                            continue

                        validTargetPosition = True
                        break

                    if not validTargetPosition:
                        self.fail("no spot to build machine")
                        return (None,None)

                    self.targetPosition = targetPosition
                    self.targetPositionBig = room.getPosition()

                if character.getBigPosition() != self.targetPositionBig:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="go to the tile the Machine should be placed")
                    return ([quest],None)

                if character.getDistance(self.targetPosition) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="go to the placement spot")
                    return ([quest],None)

                items = character.container.getItemByPosition(self.targetPosition)
                if items:
                    if not character.getFreeInventorySpace():
                        quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="be able to pick up a machine to place")
                        return ([quest],None)

                    quest = src.quests.questMap["CleanSpace"](targetPosition=self.targetPosition,targetPositionBig=character.getBigPosition(),reason="clear the placement spot")
                    return ([quest],None)

                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == self.targetPosition:
                        return (None,("L"+direction[1]+"cb","place the machine"))

            for room in terrain.rooms:
                items = room.getItemsByType("Machine")
                for item in items:
                    if item.bolted:
                        continue
                    if item.toProduce != self.itemType:
                        continue

                    storedItem = False
                    itemPos = item.getPosition()
                    for storageSlot in room.storageSlots:
                        if storageSlot[0] == itemPos:
                            storedItem = True
                    for outputSlot in room.outputSlots:
                        if outputSlot[0] == itemPos:
                            storedItem = True

                    if not storedItem:
                        continue

                    if not character.getFreeInventorySpace():
                        quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="be able to pick up a machine to place")
                        return ([quest],None)

                    newQuest = src.quests.questMap["CleanSpace"](targetPositionBig=room.getPosition(),targetPosition=item.getPosition())
                    return ([newQuest],None)

            machineMachine = None
            bluePrint = None
            for room in character.getTerrain().rooms:
                for item in room.itemsOnFloor:
                    if item.type == "MachineMachine":
                        machineMachine = item
                        continue
                    if item.type == "BluePrint" and item.endProduct == self.itemType:
                        bluePrint = item
                        continue

            if not machineMachine or (src.gamestate.gamestate.tick < machineMachine.coolDownTimer + machineMachine.coolDown):

                newQuest = src.quests.questMap["Machining"](toProduce=self.itemType,amount=1,reason=f"construct a machine that produces {self.itemType}",produceToInventory=True)
                return ([newQuest],None)
                #if not dryRun:
                #    self.fail(reason="no machine machine found")
                #return (None,None)

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(1,0,0)))
            if items and items[-1].type == "Machine":
                if not character.getFreeInventorySpace():
                    quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="be able to pick up a machine to place")
                    return ([quest],None)

                if character.getBigPosition() != (7, 7, 0):
                    quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="go to the tile the Machine to pick up is on")
                    return ([quest],None)

                if character.getDistance(items[-1].getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=items[-1].getPosition(),ignoreEndBlocked=True,reason="go to the Machine to pick up")
                    return ([quest],None)

                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == items[-1].getPosition():
                        counter = 0
                        for endProduct in machineMachine.endProducts:
                            if endProduct == self.itemType:
                                counter += 1
                        return (None,("K"+direction[1],"pick up the machine"))


            if self.itemType in machineMachine.endProducts:
                if character.container != machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition(),reason="go to the tile the MachineMachine is on")
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True,reason="go to the MachineMachine")
                    return ([quest],None)

                items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(-1,0,0)))
                if not items or items[-1].type != "MetalBars":
                    quest = src.quests.questMap["PlaceItem"](targetPosition=machineMachine.getPosition(offset=(-1,0,0)),targetPositionBig=machineMachine.container.getPosition(),itemType="MetalBars",tryHard=self.tryHard,reason="supply the MachineMachine with MetalBars")
                    return ([quest], None)

                if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
                    submenue = character.macroState["submenue"]
                    if submenue.tag == "machineSelection":
                        counter = 1
                        for endProduct in machineMachine.endProducts:
                            if endProduct == self.itemType:
                                break
                            counter += 1

                        offset = counter-submenue.selectionIndex
                        if offset > 0:
                            command = "s"*offset+"j"
                        else:
                            command = "w"*(-offset)+"j"
                        return (None,(command,"to produce the machine"))
                    else:
                        submenue = character.macroState["submenue"]
                        counter = 2
                        command = ""
                        if submenue.selectionIndex > counter:
                            command += "w"*(submenue.selectionIndex-counter)
                        if submenue.selectionIndex < counter:
                            command += "s"*(counter-submenue.selectionIndex)
                        command += "j"
                        return (None,(command,"to start producing a machine"))

                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        return (None,("J"+direction[1],"to activate the epoch artwork"))

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(0,-1,0)))
            placedBlueprintFound = False
            for item in items:
                if item.type == "BluePrint" and item.endProduct == self.itemType:
                    placedBlueprintFound = True
                    break

            if placedBlueprintFound:
                if character.container != machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition(),reason="go to the tile the MachineMachine is on")
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True,reason="go to the MachineMachine")
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        return (None,("J"+direction[1]+"j","load the blueprint"))

            if character.inventory and character.inventory[-1].type == "BluePrint" and character.inventory[-1].endProduct == self.itemType:
                if character.container != machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition(),reason="go to the tile the MachineMachine is on")
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition(offset=(0,-1,0))) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(offset=(0,-1,0)),ignoreEndBlocked=True,reason="go to the MachineMachine")
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition(offset=(0,-1,0)):
                        return (None,("L"+direction[1],"place blueprint"))
                15/0

            if bluePrint:
                if character.container != bluePrint.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=bluePrint.container.getPosition(),reason="go to the tile the blueprint is on")
                    return ([quest],None)
                if character.getPosition() != bluePrint.getPosition():
                    quest = src.quests.questMap["GoToPosition"](targetPosition=bluePrint.getPosition(),reason="go to the BluePrint")
                    return ([quest],None)
                return (None,("k","pick up blueprint"))

            if self.tryHard:
                quest = src.quests.questMap["ResearchBluePrint"](itemType=self.itemType,tryHard=self.tryHard,reason="have a blueprint to load into the MachineMachine")
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest], None)
            if "machining" in character.duties:
                newQuest = src.quests.questMap["Machining"](toProduce=self.itemType,amount=1,reason=f"construct a machine that produces {self.itemType}",produceToInventory=True)
                return ([newQuest],None)
            self.fail(reason="no blueprint for "+self.itemType)
            return (None,None)
        return (None,None)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not self.targetPosition:
            return False

        if not self.targetPositionBig:
            return False

        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            self.fail("targetroom gone")
            return True

        room = rooms[-1]
        items = room.getItemByPosition(self.targetPosition)
        if not items:
            return False

        if items[-1].type == "Machine" and items[-1].toProduce == self.itemType and items[-1].bolted:
            self.postHandler()
            return True

        return False

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room) and renderForTile:
            return []
        elif not renderForTile:
            return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.boltedItem, "boltedItem")
        super().assignToCharacter(character)

    def boltedItem(self,extraInfo):
        self.triggerCompletionCheck(self.character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPositionBig:
            result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

src.quests.addType(SetUpMachine)

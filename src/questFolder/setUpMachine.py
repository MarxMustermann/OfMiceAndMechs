import src
import random

class SetUpMachine(src.quests.MetaQuestSequence):
    type = "SetUpMachine"

    def __init__(self, description="set up machine", creator=None, command=None, lifetime=None, itemType=None,tryHard=False,targetPosition=None,targetPositionBig=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description+" "+itemType
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard

    def generateTextDescription(self):
        text = """
set up a machine to produce %s.

"""%(self.itemType,)

        text += """
Set the machine up on position %s on tile %s
"""%(self.targetPosition,self.targetPositionBig,)
        
        neededItems = src.items.rawMaterialLookup.get(self.itemType,[])[:]
        text += """
%s machines are produced by a machine machine.
A blueprint for %s is required in the machine machine.
Examine the machine machine for more details.
"""%(self.itemType,self.itemType,)

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
If you don't find a %s blueprint, research it.
"""%(self.itemType,)

        return text

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
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

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if character.inventory and character.inventory[-1].type == "Machine":
                if not self.targetPosition:
                    validTargetPosition = False
                    counter = 0
                    while not validTargetPosition and counter < 10:
                        counter += 1
                        self.targetPosition = (random.randint(2,4),random.randint(2,9),0)
                        room = random.choice(character.getTerrain().rooms)

                        if room.getItemByPosition(self.targetPosition):
                            continue
                        if room.getItemByPosition((self.targetPosition[0]-1,self.targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0]+1,self.targetPosition[1],0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0],self.targetPosition[1]+1,0)):
                            continue
                        if room.getItemByPosition((self.targetPosition[0],self.targetPosition[1]-1,0)):
                            continue


                        validTargetPosition = True
                        break

                    if not validTargetPosition:
                        self.fail("no spot to build machine")
                        return (None,None)

                    self.targetPositionBig = room.getPosition()

                if not character.getBigPosition() == self.targetPositionBig:
                    quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
                    return ([quest],None)

                if character.getDistance(self.targetPosition) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True)
                    return ([quest],None)
                
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == self.targetPosition:
                        return (None,("L"+direction[1]+"cb","place the machine"))

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

            if not machineMachine:
                self.fail(reason="no machine machine found")
                return (None,None)

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(1,0,0)))
            if items and items[-1].type == "Machine":
                if character.getDistance(items[-1].getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=items[-1].getPosition(),ignoreEndBlocked=True)
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
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)

                items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(-1,0,0)))
                if not items or not items[-1].type == "MetalBars":
                    quest = src.quests.questMap["PlaceItem"](targetPosition=machineMachine.getPosition(offset=(-1,0,0)),targetPositionBig=machineMachine.container.getPosition(),itemType="MetalBars",tryHard=self.tryHard)
                    return ([quest], None)

                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        counter = 0
                        for endProduct in machineMachine.endProducts:
                            if endProduct == self.itemType:
                                break
                            counter += 1
                        return (None,("J"+direction[1]+"sj"+(counter*"s")+"j","produce the machine"))

            items = machineMachine.container.getItemByPosition(machineMachine.getPosition(offset=(0,-1,0)))
            placedBlueprintFound = False
            for item in items:
                if item.type == "BluePrint" and item.endProduct == self.itemType:
                    placedBlueprintFound = True
                    break

            if placedBlueprintFound:
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(),ignoreEndBlocked=True)
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition():
                        return (None,("J"+direction[1]+"j","load the blueprint"))

            if character.inventory and character.inventory[-1].type == "BluePrint" and character.inventory[-1].endProduct == self.itemType:
                if not character.container == machineMachine.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=machineMachine.container.getPosition())
                    return ([quest],None)
                if character.getDistance(machineMachine.getPosition(offset=(0,-1,0))) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=machineMachine.getPosition(offset=(0,-1,0)),ignoreEndBlocked=True)
                    return ([quest],None)
                directions = [((0,0,0),"."),((0,1,0),"s"),((1,0,0),"d"),((0,-1,0),"w"),((-1,0,0),"a")]
                directionFound = None
                for direction in directions:
                    if character.getPosition(offset=direction[0]) == machineMachine.getPosition(offset=(0,-1,0)):
                        return (None,("L"+direction[1],"place blueprint"))
                15/0

            if bluePrint:
                if not character.container == bluePrint.container:
                    quest = src.quests.questMap["GoToTile"](targetPosition=bluePrint.container.getPosition())
                    return ([quest],None)
                if not character.getPosition() == bluePrint.getPosition():
                    quest = src.quests.questMap["GoToPosition"](targetPosition=bluePrint.getPosition())
                    return ([quest],None)
                return (None,("k","pick up blueprint"))

            if self.tryHard:
                quest = src.quests.questMap["ResearchBluePrint"](itemType=self.itemType,tryHard=self.tryHard)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
                return ([quest], None)
            self.fail(reason="no blueprint for "+self.itemType)
            return (None,None)
        return (None,None)
    
    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not self.targetPosition:
            return False
        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            self.fail("targetroom gone")
            return True

        room = rooms[-1]
        items = room.getItemByPosition(self.targetPosition)
        if not items:
            return False

        if items[-1].type == "Machine" and items[-1].toProduce == self.itemType:
            self.postHandler()
            return True
         
        return False

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(SetUpMachine)

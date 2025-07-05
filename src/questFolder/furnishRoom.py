import random

import src


class FurnishRoom(src.quests.MetaQuestSequence):
    '''
    quest to place items into a room with buildsites

    Parameters:
        description: the description to be shown in the UI
        creator: the entity creating this quest. (obsolete?)
        targetPositionBig: the position of the room to do work in 
        reason: the reason to be shown in the UI
        tryHard: try to complete the quest in any way possible
    '''
    type = "FurnishRoom"
    def __init__(self, description="furnish room", creator=None, targetPositionBig=None,reason=None,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.shortCode = "d"
        self.targetPositionBig = targetPositionBig
        self.reason = reason
        self.type = "FurnishRoom"

    def generateTextDescription(self):
        '''
        generate a text description
        '''
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Build the items needed in room {self.targetPositionBig}{reason}.

the buildsites indicate what needs to be built.

"""
        return out

    def triggerCompletionCheck(self,character=None):
        '''
        check if quest completed and end it

        Parameters:
            character: the character working on the quest
        '''
        
        # continue working if the room has more buildsites to complete or is gone altogether
        rooms = self.character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            return False
        room = rooms[0]
        if room.buildSites:
            return False
        
        # end the quest if nothing is left to do
        self.postHandler()
        return True

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        '''
        generate the next step to complete this quest
        TODO: remove side effects in dry run
        '''

        # do nothing if there is a subquest
        if self.subQuests:
            return (None,None)

        # actually enter the current room
        if not isinstance(character.container,src.rooms.Room):
            command = None
            if character.xPosition%15 == 0:
                command = "d"
            if character.xPosition%15 == 14:
                command = "a"
            if character.yPosition%15 == 0:
                command = "s"
            if character.yPosition%15 == 14:
                command = "w"
            if command:
                return (None,(command,"enter room"))

        # go to target room
        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig)
            return ([quest],None)

        # abort on rooms not fully painted
        if character.container.floorPlan:
            if not dryRun:
                self.fail("room not fully painted yet")
            return (None,None)
            
        # end if no more buildsites left
        if not character.container.buildSites:
            if not dryRun:
                self.postHandler()
            return (None,None)

        # place items on buildsites
        checkedMaterial = set()
        room = character.container
        for buildSite in room.buildSites:

            # test each itemType only once
            if buildSite[1] in checkedMaterial:
                continue
            if not buildSite[1] == "Machine":
                checkedMaterial.add(buildSite[1])

            # remap reqiuirements for special items
            neededItem = buildSite[1]
            if buildSite[1] == "Command":
                neededItem = "Sheet"

            # check if the character has that item in inventory
            hasItem = False
            source = None
            if character.inventory and character.inventory[-1].type == neededItem:
                hasItem = True

            # create quest to set up actual machines
            if buildSite[1] == "Machine":
                quest = src.quests.questMap["SetUpMachine"](itemType=buildSite[2]["toProduce"],targetPositionBig=room.getPosition(),targetPosition=buildSite[0])
                if not dryRun:
                    beUsefull.idleCounter = 0
                return ([quest],None)

            # try to obtain the item needed
            if not hasItem:
                # check the local list of supplies (not active right now?)
                for candidateSource in room.sources:
                    if candidateSource[1] != neededItem:
                        continue

                    sourceRoom = room.container.getRoomByPosition(candidateSource[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    if not sourceRoom.getNonEmptyOutputslots(itemType=neededItem):
                        continue

                    source = candidateSource
                    break

                # check all rooms 
                if not source:
                    for checkRoom in random.sample(character.getTerrain().rooms,len(character.getTerrain().rooms)):
                        if not checkRoom.getNonEmptyOutputslots(itemType=neededItem):
                            continue

                        source = (checkRoom.getPosition(),neededItem)
                        break

                # abort if no source was found
                if not source:
                    continue

            # place sheet for setting up command (ugly!)
            if buildSite[1] != "Command":
                quest = src.quests.questMap["PlaceItem"](itemType=buildSite[1],targetPositionBig=room.getPosition(),targetPosition=buildSite[0],boltDown=True)
                return ([quest],None)

            # place the actual command
            # TODO: remove runCommand
            if hasItem:
                quests = []
                if buildSite[1] == "Command":
                    if "command" in buildSite[2]:
                        quests.append(src.quests.questMap["RunCommand"](command="jjssj%s\n"%(buildSite[2]["command"])))
                    else:
                        quests.append(src.quests.questMap["RunCommand"](command="jjssj.\n"))
                quests.append(src.quests.questMap["RunCommand"](command="lcb"))
                quests.append(src.quests.questMap["GoToPosition"](targetPosition=buildSite[0]))
                buildSite[2]["reservedTill"] = room.timeIndex+100
                quests.append(src.quests.questMap["GoToTile"](targetPosition=room.getPosition()))
                #self.addQuest(produceQuest)
                return (quests,None)

            # obtain item
            if source:
                if not character.getFreeInventorySpace() > 0:
                    quest = src.quests.questMap["ClearInventory"]()
                    if not dryRun:
                        beUsefull.idleCounter = 0
                    return ([quest],None)

                roomPos = (room.xPosition,room.yPosition)
                quests = []
                if source[0] != roomPos:
                    quests.append(src.quests.questMap["GoToTile"](targetPosition=(roomPos[0],roomPos[1],0)))
                quests.append(src.quests.questMap["FetchItems"](toCollect=neededItem,amount=1))
                return (quests,None)

        # produce items needed
        checkedMaterial = list(checkedMaterial)
        random.shuffle(checkedMaterial)
        for material in checkedMaterial:
            if material == "Command":
                material = "Sheet"

            quest = src.quests.questMap["MetalWorking"](toProduce=material, amount=1, produceToInventory=True)
            return ([quest],None)

        # fail on weird state
        if not dryRun:
            self.fail("no known path to solution. missing machine?")
        return (None,None)
            
    def handleQuestFailure(self,extraParam):
        '''
        cascade failure
        '''
        super().handleQuestFailure(extraParam)
        self.fail(reason=extraParam["reason"])

# register the quest
src.quests.addType(FurnishRoom)

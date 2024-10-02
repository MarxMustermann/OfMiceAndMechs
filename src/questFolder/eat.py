import random

import src


class Eat(src.quests.MetaQuestSequenceV2):
    type = "Eat"

    def __init__(self, description="eat", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def handleMoved(self,extraInfo=None):
        self.subQuestCompleted()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMoved, "moved")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if character.satiation > 800:
            self.postHandler()
            return
        return

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest()
        if not self.subQuests:
            self.generateSubquests(self.character)


    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        toSearchFor = ["PressCake","BioMass"]

        pos = character.getBigPosition()
        pos = (pos[0],pos[1])
        if pos in character.getTerrain().forests:
            if character.getSpacePosition() == (8,7,0):
                return (None,("Jaj","Eat"))
            quest = src.quests.questMap["GoToPosition"](targetPosition=(8,7,0))
            return ([quest],None)

        if not isinstance(character.container,src.rooms.Room):
            """
            if character.yPosition%15 == 14 or character.yPosition%15 == 0 or character.xPosition%15 == 14 or character.xPosition%15 == 0:
                quest = src.quests.questMap["EnterRoom"]()
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                self.startWatching(quest,self.subQuestCompleted,"completed")
                return
            """

            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        room = character.container

        for itemType in toSearchFor:
            sourceSlots = room.getNonEmptyOutputslots(itemType=itemType)
            if sourceSlots:
                break

        if not sourceSlots:
            source = None
            for itemType in toSearchFor:
                for candidate in room.sources:
                    if candidate[1] != itemType:
                        continue

                    sourceRoom = room.container.getRoomByPosition(candidate[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    sourceSlots = sourceRoom.getNonEmptyOutputslots(itemType=itemType)
                    if not sourceSlots:
                        continue

                    source = candidate
                    break

                for otherRoom in character.getTerrain().rooms:
                    sourceSlots = otherRoom.getNonEmptyOutputslots(itemType=itemType)
                    if not sourceSlots:
                        continue
                    source = (otherRoom.getPosition(),itemType)
                    break

                if source:
                    break

            if not source:
                pos = character.getBigPosition()
                pos = (pos[0],pos[1])
                if character.getTerrain().forests:
                    forest = random.choice(character.getTerrain().forests)
                    #forest = (forest[0],forest[1],0)
                    description = "go to forest"
                    quest = src.quests.questMap["GoToTile"](targetPosition=forest,description=description)
                    return ([quest],None)                
                self.fail(reason="no source for food")
                return (None,None)

            description="go to food source "

            quest = src.quests.questMap["GoToTile"](targetPosition=source[0],description=description)
            return ([quest],None)

        characterPos = character.getPosition()
        command = None
        if sourceSlots[0][0] == (characterPos[0],characterPos[1],characterPos[2]):
            command = "j"
        elif sourceSlots[0][0] == (characterPos[0]-1,characterPos[1],characterPos[2]):
            command = "Ja"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Jw"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]+1,characterPos[2]):
            command = "Js"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Js"

        if command:
            return (None, (command,"eat"))
        
        quest = src.quests.questMap["GoToPosition"](targetPosition=sourceSlots[0][0],description="go to "+itemType,ignoreEndBlocked=True)
        return ([quest],None)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        if character.satiation < 200:
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([src.quests.questMap["Eat"]()],None)
        return (None,None)
src.quests.addType(Eat)

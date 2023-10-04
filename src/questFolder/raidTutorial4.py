import src


class RaidTutorial4(src.quests.MetaQuestSequence):
    type = "RaidTutorial4"

    def __init__(self, description="do throne run", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        terrain = character.getTerrain()

        if (terrain.yPosition == 7 and terrain.xPosition == 6) and not self.shownPickedUpSpecialItemSlot:
            for item in character.inventory:
                if item.type == "Machine":
                    self.postHandler()
                    return (None,None)
            if character.inventory:
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                return ([quest],None)
            if character.getBigPosition() not in ((14,7,0),(13,7,0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=(13,7,0))
                return ([quest],None)
            if character.getBigPosition() not in ((14,7,0),) and character.getSpacePosition() != (13, 7, 0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(13,7,0))
                return ([quest],None)
            return (None,("d","to cheat yourself onto the neighbor terrain"))

        if (terrain.yPosition == 7 and terrain.xPosition == 7):
            throne = None
            for room in terrain.rooms:
                for item in room.getItemsByType("Throne"):
                    throne = item
                    break

            if character.container != throne.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=throne.container.getPosition())
                return ([quest],None)

            if character.getDistance(throne.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=throne.getPosition(),ignoreEndBlocked=True)
                return ([quest],None)

            offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w")]
            for offset in offsets:
                if character.getPosition(offset=offset[0]) == throne.getPosition():
                    return (None,("J"+offset[1],"sit on the throne"))
            return None
        return None

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

src.quests.addType(RaidTutorial4)

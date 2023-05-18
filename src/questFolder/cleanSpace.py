import src
import random

class CleanSpace(src.quests.MetaQuestSequence):
    type = "CleanSpace"

    def __init__(self, description="clean space", creator=None, targetPositionBig=None, targetPosition=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        self.targetPosition = targetPosition 
        self.targetPositionBig = targetPositionBig

    def generateTextDescription(self):
        text = """
Remove all items from the space %s on tile %s.
"""%(self.targetPosition,self.targetPositionBig)
        return text

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def triggerCompletionCheck(self,character=None):
        return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            room = rooms[0]
            items = room.getItemByPosition(self.targetPosition)
            if not items:
                self.postHandler()
                return (None,None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition())
                return ([quest], None)

            if character.getDistance(self.targetPosition) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True)
                return ([quest], None)

            offsets = {(0,0,0):"k",(1,0,0):"Kd",(-1,0,0):"Ka",(0,1,0):"Ks",(0,-1,0):"Kw"}
            for (offset,command) in offsets.items():
                if character.getPosition(offset=offset) == self.targetPosition:
                    return (None, command)
        return (None,None)
    

src.quests.addType(CleanSpace)

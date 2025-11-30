import random
import src


class UnblockDoor(src.quests.MetaQuestSequence):
    type = "UnblockDoor"

    def __init__(self, description="unblock door", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def handleUnblockedDoor(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        if extraInfo["item"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleUnblockedDoor, "unblockedDoor")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
unblock door in room {self.targetPositionBig} on position {self.targetPosition}{reason}.
"""

    def triggerCompletionCheck(self,character=None,dryRun=True):
        return False
        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return False

        if not character.container.isRoom:
            if not dryRun:
                self.fail()
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        for item in items:
            if item.walkable:
                if not dryRun:
                    self.postHandler()
                return True
        if not items or items[0].type not in ("Door",):
            if not dryRun:
                self.fail()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the machine is on")
            return ([quest],None)

        pos = character.getPosition()
        if self.targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the machine")
            return ([quest],None)

        message = "unblock door"
        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("cx",message))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Cax",message))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Cdx",message))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,("Cwx",message))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,("Csx",message))
        return (None,(".","stand around confused"))

src.quests.addType(UnblockDoor)

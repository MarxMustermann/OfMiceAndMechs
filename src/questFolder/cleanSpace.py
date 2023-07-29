import src
import random

class CleanSpace(src.quests.MetaQuestSequence):
    type = "CleanSpace"

    def __init__(self, description="clean space", creator=None, targetPositionBig=None, targetPosition=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description

        self.targetPosition = targetPosition 
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        text = """
Remove all items from the space %s on tile %s%s.
"""%(self.targetPosition,self.targetPositionBig,reason,)
        return text

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def triggerCompletionCheck(self,character=None):
        return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            terrain = character.getTerrain()
            rooms = terrain.getRoomByPosition(self.targetPositionBig)
            if not character.getFreeInventorySpace():
                quest = src.quests.questMap["ClearInventory"]()
                return ([quest],None)
            if rooms:
                room = rooms[0]
                items = room.getItemByPosition(self.targetPosition)
                if not items or items[0].bolted:
                    self.postHandler()
                    return (None,None)
            else:
                items = terrain.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))
                if not items or items[0].bolted:
                    self.postHandler()
                    return (None,None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get near the target tile")
                return ([quest], None)

            if character.container.isRoom:
                if character.getDistance(self.targetPosition) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get to the target space")
                    return ([quest], None)
            else:
                if character.getDistance((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0)) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get to the target space")
                    return ([quest], None)

            offsets = {(0,0,0):"k",(1,0,0):"Kd",(-1,0,0):"Ka",(0,1,0):"Ks",(0,-1,0):"Kw"}
            for (offset,command) in offsets.items():
                if character.container.isRoom:
                    if character.getPosition(offset=offset) == self.targetPosition:
                        return (None, (command,"to pick up item"))
                else:
                    if character.getPosition(offset=offset) == (self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0):
                        return (None, (command,"to pick up item"))
        return (None,None)
    
    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

src.quests.addType(CleanSpace)

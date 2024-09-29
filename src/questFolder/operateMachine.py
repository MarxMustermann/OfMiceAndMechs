import random
import src


class OperateMachine(src.quests.MetaQuestSequenceV2):
    type = "OperateMachine"

    def __init__(self, description="operate machine", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def handleOperatedMachine(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        if extraInfo["machine"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleOperatedMachine, "operated machine")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
operate the machine on {self.targetPosition}{reason}.
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return False

        if not character.container.isRoom:
            self.fail()
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        if not items or items[0].type not in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer","Electrifier",):
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

        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("j","activate machine"))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Ja","activate machine"))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Jd","activate machine"))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,("Jw","activate machine"))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,("Js","activate machine"))
        return None

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPositionBig:
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
            if self.targetPosition and self.targetPositionBig:
                result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):
        terrain = character.getTerrain()
        for checkRoom in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            items = checkRoom.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                #if not item.bolted:
                #    continue
                if item.type not in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer","Electrifier",):
                    continue
                if not item.readyToUse():
                    continue
                if checkRoom == character.container:
                    quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition())
                    beUsefull.addQuest(quest)
                    quest.activate()
                    beUsefull.idleCounter = 0
                    return True
                else:
                    quest = src.quests.questMap["GoToTile"](targetPosition=checkRoom.getPosition(),reason="go to a machine room")
                    beUsefull.addQuest(quest)
                    quest.activate()
                    beUsefull.idleCounter = 0
                    return True
        return None


src.quests.addType(OperateMachine)

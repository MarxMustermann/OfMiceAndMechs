import random
import src


class StoryWakeWorker(src.quests.MetaQuestSequence):
    type = "StoryWakeWorker"

    def __init__(self, description="wake worker", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def handleWokeClone(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleWokeClone, "woke clone")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        position_string = ""
        if self.targetPosition:
            position_string = f" on position {self.targetPosition}"
        if self.targetPositionBig:
            position_big_string = f" in room {self.targetPositionBig}"
        return f"""
Remove the worker from the StasisTank{position_string}{position_big_string}{reason}.

Activate the StasisTank to release the worker.
"""

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            if not dryRun:
                self.fail("room gone")
            return True
        targetRoom = rooms[0]
        if self.targetPosition:
            items = targetRoom.getItemByPosition(self.targetPosition)
        else:
            items = targetRoom.getItemsByType("StasisTank")
        if not items or items[0].type not in ("StasisTank",):
            if not dryRun:
                self.fail()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        targetPosition = self.targetPosition
        if not targetPosition:
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                return self._solver_trigger_fail(dryRun,"target room gone")
            room = rooms[0]

            stasisTanks = room.getItemsByType("StasisTank")
            if not stasisTanks:
                return self._solver_trigger_fail(dryRun,"stasis tank missing")

            nearBy_stasisTanks = []
            for stasisTank in stasisTanks:
                if character.getDistance(stasisTank.getPosition()) > 1:
                    continue
                nearBy_stasisTanks.append(stasisTank)

            if not nearBy_stasisTanks:
                stasisTank = random.choice(stasisTanks)

            targetPosition = stasisTank.getPosition()

        quest = src.quests.questMap["ActivateItem"](targetPosition=targetPosition,targetPositionBig=self.targetPositionBig,reason="smash StasisTank")
        return ([quest],None)

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
            if character.getBigPosition() == self.targetPositionBig and character.container.isRoom:
                for stasisTank in character.container.getItemsByType("StasisTank"):
                    result.append(((stasisTank.getPosition()[0],stasisTank.getPosition()[1]),"target"))
        return result

    def handleQuestFailure(self,extraParam):
        reason = extraParam.get("reason")
        quest = extraParam.get("quest")

        if quest.type == "GoToPosition" and reason == "no path found":
            pos = extraParam["quest"].targetPosition
            quest = src.quests.questMap["ClearPathToPosition"](targetPosition=(pos[0],pos[1]+1,pos[2]))
            self.addQuest(quest)
            self.startWatching(quest,self.handleQuestFailure,"failed")
            return
        super().handleQuestFailure(extraParam)

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        for checkRoom in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            items = checkRoom.itemsOnFloor[:]
            random.shuffle(items)
            for item in items:
                if not item.bolted:
                    continue
                if item.type not in ("Machine","ScrapCompactor","MaggotFermenter","BioPress","GooProducer","Electrifier","BloomShredder","CorpseShredder","Merger"):
                    continue
                if not item.readyToUse():
                    continue

                quest = src.quests.questMap["OperateMachine"](targetPosition=item.getPosition(),targetPositionBig=checkRoom.getPosition())
                if not dryRun:
                    beUsefull.idleCounter = 0
                return ([quest],None)
        return (None,None)


src.quests.addType(StoryWakeWorker)

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

        # handle menus
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("StasisTank",))
        if action:
            return action

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the machine is on")
            return ([quest],None)

         # enter rooms fully
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))
            return self._solver_trigger_fail(dryRun,"room missing")
        room = character.container

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
            quest = src.quests.questMap["GoToPosition"](targetPosition=stasisTank.getPosition(),ignoreEndBlocked=True,reason="be able to use the StasisTank")
            return ([quest],None)

        pos = character.getPosition()
        targetPosition = random.choice(nearBy_stasisTanks).getPosition()
        interactionCommand = "J"
        if submenue:
            if submenue.tag == "advancedInteractionSelection":
                interactionCommand = ""
            else:
                return (None,(["esc"],"close menu"))
        if (pos[0],pos[1],pos[2]) == targetPosition:
            return (None,("j","activate machine"))
        if (pos[0]-1,pos[1],pos[2]) == targetPosition:
            return (None,(interactionCommand+"a","activate machine"))
        if (pos[0]+1,pos[1],pos[2]) == targetPosition:
            return (None,(interactionCommand+"d","activate machine"))
        if (pos[0],pos[1]-1,pos[2]) == targetPosition:
            return (None,(interactionCommand+"w","activate machine"))
        if (pos[0],pos[1]+1,pos[2]) == targetPosition:
            return (None,(interactionCommand+"s","activate machine"))
        return (None,(".","stand around confused"))

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

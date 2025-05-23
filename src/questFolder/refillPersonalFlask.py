import src

import logging

logger = logging.getLogger(__name__)

class RefillPersonalFlask(src.quests.MetaQuestSequence):
    type = "RefillPersonalFlask"

    def __init__(self, description="refill flask", creator=None, command=None, lifetime=None):
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
            return False

        if character.flask and character.flask.uses > 80:
            self.postHandler()
            return True
        return False

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest()
        if not self.subQuests:
            self.generateSubquests(self.character)


    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        pos = character.getBigPosition()
        pos = (pos[0],pos[1])

        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue

                for item in items:
                    shouldUse = False
                    if item.type in ["GooDispenser"] and item.charges:
                        shouldUse = True

                    if item.type in ["GooFlask"] and item.uses:
                        shouldUse = True

                    if not shouldUse:
                        continue

                    if not item == character.container.getItemByPosition(item.getPosition())[0]:
                        pickupCommand = None
                        if offset == (0,0,0):
                            pickupCommand = "k"
                        if offset == (1,0,0):
                            pickupCommand = "Kd"
                        if offset == (-1,0,0):
                            pickupCommand = "Ka"
                        if offset == (0,1,0):
                            pickupCommand = "Kw"
                        if offset == (0,-1,0):
                            pickupCommand = "Ks"

                        return (None,(pickupCommand,"remove item from flask"))
                
                    if offset == (0,0,0):
                        return (None,("jj","refill"))
                    if offset == (1,0,0):
                        return (None,("Jdj","refill"))
                    if offset == (-1,0,0):
                        return (None,("Jaj","refill"))
                    if offset == (0,1,0):
                        return (None,("Jsj","refill"))
                    if offset == (0,-1,0):
                        return (None,("Jwj","refill"))


            for item in character.container.itemsOnFloor:
                if not character.container.getItemByPosition(item.getPosition()):
                    continue
                if item.type == "GooDispenser" and item.charges:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to goo dispenser",ignoreEndBlocked=True)
                    return ([quest],None)
                if item.type == "GooFlask" and item.uses:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to goo flask",ignoreEndBlocked=True)
                    return ([quest],None)


        room = None
        for roomCandidate in character.getTerrain().rooms:
            for item in roomCandidate.itemsOnFloor:
                if item.type == "GooDispenser" and item.charges:
                    room = roomCandidate
                if item.type == "GooFlask" and item.uses:
                    room = roomCandidate

        if room:
            quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to goo source")
            return ([quest],None)

        character.addMessage("found no source for goo")
        if not dryRun:
            self.fail()
        return (None,None)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        if character.flask and character.flask.uses < 3:
            if not dryRun:
                beUsefull.idleCounter = 0
            return ([src.quests.questMap["RefillPersonalFlask"]()],None)
        return (None,None)
src.quests.addType(RefillPersonalFlask)

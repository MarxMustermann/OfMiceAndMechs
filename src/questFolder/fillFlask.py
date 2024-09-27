import src


class FillFlask(src.quests.MetaQuestSequence):
    type = "FillFlask"

    def __init__(self, description="fill flask", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        if not character.searchInventory("Flask"):
            self.postHandler()
            return
        return

    def handleFlaskFilled(self,extraInfo=None):
        self.triggerCompletionCheck()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleFlaskFilled, "filledGooFlask")
        super().assignToCharacter(character)

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest()
        if not self.subQuests:
            self.generateSubquests(self.character)

    def getSolvingCommandString(self,character,dryRun=True):

        if self.triggerCompletionCheck(character):
            return None

        offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for offset in offsets:
            pos = character.getPosition(offset=offset)
            items = character.container.getItemByPosition(pos)
            if not items:
                continue

            shouldUse = False
            if items[0].type in ["GooDispenser"]:
                shouldUse = True

            if not shouldUse:
                continue

            if offset == (0,0,0):
                return "jsj"
            if offset == (1,0,0):
                return "Jdsj"
            if offset == (-1,0,0):
                return "Jasj"
            if offset == (0,1,0):
                return "Jssj"
            if offset == (0,-1,0):
                return "Jwsj"

        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character):
        pos = character.getBigPosition()
        pos = (pos[0],pos[1])

        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue

                shouldUse = False
                if items[0].type in ["GooDispenser"] and items[0].charges:
                    shouldUse = True

                if not shouldUse:
                    continue

                return

            for item in character.container.itemsOnFloor:
                if not item == character.container.getItemByPosition(item.getPosition())[0]:
                    continue
                if item.type == "GooDispenser" and item.charges:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to goo dispenser",ignoreEndBlocked=True)
                    quest.assignToCharacter(character)
                    quest.activate()
                    self.addQuest(quest)
                    self.startWatching(quest,self.subQuestCompleted,"completed")
                    return

        room = None
        for roomCandidate in character.getTerrain().rooms:
            for item in roomCandidate.itemsOnFloor:
                if item.type == "GooDispenser" and item.charges:
                    room = roomCandidate

        if room:
            quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to goo source")
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            self.startWatching(quest,self.subQuestCompleted,"completed")
            return

        character.addMessage("found no source for goo")
        self.fail()


    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return None

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return None

        if not self.subQuests:
            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return None

        return super().solver(character)
    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom):
        foundGooDispenser = None
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for gooDispenser in room.getItemsByType("GooDispenser"):
                if not gooDispenser.charges:
                    continue
                foundGooDispenser = gooDispenser
                break
            if foundGooDispenser:
                break

        if foundGooDispenser:
            beUsefull.addQuest(src.quests.questMap["ClearInventory"]())
            quest = src.quests.questMap["FillFlask"]()
            beUsefull.addQuest(quest)
            if not character.searchInventory("Flask"):
                quest = src.quests.questMap["FetchItems"](toCollect="Flask",amount=1)
                beUsefull.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            beUsefull.idleCounter = 0
            return True
        return None

src.quests.addType(FillFlask)

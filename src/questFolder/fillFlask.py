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

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):
        if self.triggerCompletionCheck(character):
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]

            if not submenue.extraInfo.get("item"):
                return (None,(["esc"],"exit submenu"))

            menuEntry = "fill_empty_flask"
            counter = 1
            for option in submenue.options.values():
                if option == menuEntry:
                    index = counter
                    break
                counter += 1
            command = ""
            if submenue.selectionIndex > counter:
                command += "w"*(submenue.selectionIndex-counter)
            if submenue.selectionIndex < counter:
                command += "s"*(counter-submenue.selectionIndex)

            command += "j"
            return (None,(command,"fill flasks"))

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

                if offset == (0,0,0):
                    return (None,("jsj","fill flask"))

                interactionCommand = "J"
                if "advancedInteraction" in character.interactionState:
                    interactionCommand = ""

                if offset == (1,0,0):
                    return (None,(interactionCommand+"dsj","fill flask"))
                if offset == (-1,0,0):
                    return (None,(interactionCommand+"asj","fill flask"))
                if offset == (0,1,0):
                    return (None,(interactionCommand+"ssj","fill flask"))
                if offset == (0,-1,0):
                    return (None,(interactionCommand+"wsj","fill flask"))

            for item in character.container.itemsOnFloor:
                if not item == character.container.getItemByPosition(item.getPosition())[0]:
                    continue
                if item.type == "GooDispenser" and item.charges:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to goo dispenser",ignoreEndBlocked=True)
                    return ([quest],None)

        room = None
        for roomCandidate in character.getTerrain().rooms:
            for item in roomCandidate.itemsOnFloor:
                if item.type == "GooDispenser" and item.charges:
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
            quests = [src.quests.questMap["ClearInventory"](),src.quests.questMap["FillFlask"]()]
            if not character.searchInventory("Flask"):
                quest = src.quests.questMap["FetchItems"](toCollect="Flask",amount=1)
                quests.append(quest)
            if not dryRun:
                beUsefull.idleCounter = 0
            return (quests,None)
        return (None,None)

src.quests.addType(FillFlask)

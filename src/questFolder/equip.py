import src

class Equip(src.quests.MetaQuestSequence):
    type = "Equip"

    def __init__(self, description="equip", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"

    def generateTextDescription(self):
        sword = src.items.itemMap["Sword"]()
        armor = src.items.itemMap["Armor"]()
        return ["""
The world is a dangerous place.
You need to be able to defend yourself.
Equip yourself with weapons preferably a sword (""",sword.render(),""") and armor (""",armor.render(),""").

You can try to find euqipment in storage.
Alternatively fetch your equipment directly from the production line.
If you find some other source for equipment, that is fine, too.

Take care to select a good weapon and armor.
The differences are significant.

Armor can absorb 1 to 5 damage depending on quality.
Swords can range from 10 to 25 damage per hit.
"""]

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def handleMoved(self,extraInfo=None):
        self.subQuestCompleted()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "equipedItem")
        self.startWatching(character,self.handleMoved, "moved")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return 

        if character.armor and character.weapon:
            self.postHandler()
            return

        return

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest() 
        if not self.subQuests:
            self.generateSubquests(self.character)

    def getSolvingCommandString(self,character,dryRun=True):
        offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for offset in offsets:
            pos = character.getPosition(offset=offset)
            items = character.container.getItemByPosition(pos)
            if not items:
                continue

            shouldGrab = False
            if not character.armor and items[0].type == "Armor":
                shouldGrab = True
            if not character.weapon and (items[0].type == "Sword" or items[0].type == "Rod"):
                shouldGrab = True

            if not shouldGrab:
                continue

            if offset == (0,0,0):
                return "j"
            if offset == (1,0,0):
                return "Jd"
            if offset == (-1,0,0):
                return "Ja"
            if offset == (0,1,0):
                return "Js"
            if offset == (0,-1,0):
                return "Jw"

        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character):
        toSearchFor = []
        if not character.armor:
            toSearchFor.append("Armor")
        if not character.weapon:
            toSearchFor.append("Sword")
            toSearchFor.append("Rod")
        if not toSearchFor:
            return

        if not isinstance(character.container,src.rooms.Room):
            if character.yPosition%15 == 14 or character.yPosition%15 == 0 or character.xPosition%15 == 14 or character.xPosition%15 == 0:
                quest = src.quests.questMap["EnterRoom"]()
                self.addQuest(quest)
                quest.assignToCharacter(character)
                quest.activate()
                self.startWatching(quest,self.subQuestCompleted,"completed")
                return
                
            self.addQuest(src.quests.questMap["GoHome"]())
            return
        room = character.container

        for itemType in toSearchFor:
            sourceSlots = room.getNonEmptyOutputslots(itemType=itemType)
            if sourceSlots:
                break

        if not sourceSlots:
            source = None
            for itemType in toSearchFor:
                for candidate in room.sources:
                    if not candidate[1] == itemType:
                        continue

                    sourceRoom = room.container.getRoomByPosition(candidate[0])
                    if not sourceRoom:
                        continue

                    sourceRoom = sourceRoom[0]
                    sourceSlots = sourceRoom.getNonEmptyOutputslots(itemType=itemType)
                    if not sourceSlots:
                        continue

                    source = candidate
                    break
                if source:
                    break
            if not source:
                #character.runCommandString(".14.")
                self.fail(reason="no source for equipment")
                return

            description="go to weapon production "
            if source[0] == (8,9,0):
                description="go storage room "

            quest = src.quests.questMap["GoToTile"](targetPosition=source[0],description=description)
            quest.assignToCharacter(character)
            self.startWatching(quest,self.subQuestCompleted,"completed")
            quest.activate()
            self.addQuest(quest)
            return

        characterPos = character.getPosition()
        command = None
        if sourceSlots[0][0] == (characterPos[0],characterPos[1],characterPos[2]):
            command = "j"
        elif sourceSlots[0][0] == (characterPos[0]-1,characterPos[1],characterPos[2]):
            command = "Ja"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Jw"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]+1,characterPos[2]):
            command = "Js"
        elif sourceSlots[0][0] == (characterPos[0],characterPos[1]-1,characterPos[2]):
            command = "Js"

        if command:
            return
        else:
            quest = src.quests.questMap["GoToPosition"](targetPosition=sourceSlots[0][0],description="go to "+itemType,ignoreEndBlocked=True)
            quest.assignToCharacter(character)
            quest.activate()
            self.addQuest(quest)
            self.startWatching(quest,self.subQuestCompleted,"completed")
            return

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        if not self.subQuests:
            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return
            
        return super().solver(character)

src.quests.addType(Equip)

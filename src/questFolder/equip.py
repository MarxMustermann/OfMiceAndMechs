import src

class Equip(src.quests.MetaQuestSequence):
    type = "Equip"

    def __init__(self, description="equip", creator=None, command=None, lifetime=None, weaponOnly=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

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

        if (character.armor or self.weaponOnly) and character.weapon:
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

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return nextStep[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))
            toSearchFor = []
            if not character.armor and not self.weaponOnly:
                toSearchFor.append("Armor")
            if not character.weapon:
                toSearchFor.append("Sword")
                toSearchFor.append("Rod")
            if not toSearchFor:
                return (None,None)

            if not isinstance(character.container,src.rooms.Room):
                if character.yPosition%15 == 14 or character.yPosition%15 == 0 or character.xPosition%15 == 14 or character.xPosition%15 == 0:
                    quest = src.quests.questMap["EnterRoom"]()
                    return ([quest],None)
                    
                quest = src.quests.questMap["GoHome"]()
                return ([quest],None)
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
                    for itemType in toSearchFor:
                        for room in character.getTerrain().rooms:
                            sourceSlots = room.getNonEmptyOutputslots(itemType=itemType)
                            if not sourceSlots:
                                continue
                            source = (room.getPosition(),itemType)
                            break
                        if source:
                            break

                if not source:
                    #character.runCommandString(".14.")
                    self.fail(reason="no source for equipment")
                    return (None,None)

                description="go to weapon production "
                if source[0] == (8,9,0):
                    description="go storage room "

                quest = src.quests.questMap["GoToTile"](targetPosition=source[0],description=description)
                return ([quest],None)

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
            elif sourceSlots[0][0] == (characterPos[0]+1,characterPos[1],characterPos[2]):
                command = "Jd"

            if command:
                return (None,(command,"equip the weapon"))

            else:
                quest = src.quests.questMap["GoToPosition"](targetPosition=sourceSlots[0][0],description="go to "+itemType,ignoreEndBlocked=True)
                return ([quest],None)
        return (None,None)

src.quests.addType(Equip)

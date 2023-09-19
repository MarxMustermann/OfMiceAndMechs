import src

# equip
# rest

class DelveDungeon(src.quests.MetaQuestSequence):
    type = "DelveDungeon"

    def __init__(self, description="delve dungeon",targetTerrain=None,itemID=None):
        questList = []
        super().__init__(questList, creator=None)
        self.metaDescription = description
        self.targetTerrain = targetTerrain
        self.itemID = itemID

    def generateTextDescription(self):
        text = """
%s
"""%(self.itemID,)
        return text

    def handleDelivery(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleDelivery, "deliveredSpecialItem")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        hasSpecialItem = None
        for item in character.inventory:
            if not item.type == "SpecialItem":
                continue
            hasSpecialItem = item
        
        terrain = character.getTerrain()

        if not hasSpecialItem:
            if not terrain.xPosition == self.targetTerrain[0] or not terrain.yPosition == self.targetTerrain[1]:
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=(self.targetTerrain[0],self.targetTerrain[1],0))
                return ([quest],None)
            if character.health < character.maxHealth//5:
                if character.getNearbyEnemies():
                    quest = src.quests.questMap["Flee"]()
                    return ([quest],None)
            if character.health < character.maxHealth*0.75:
                if character.getNearbyEnemies():
                    quest = src.quests.questMap["Fight"]()
                    return ([quest],None)
                #if character.health > character.maxHealth*0.5 and character.health < character.maxHealth:
                #    return (None,("..............","wait to heal"))
                if not dryRun:
                    self.fail()
                return (None,None)
            if not character.getBigPosition() == (7,7,0):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),abortHealthPercentage=0.75)
                return ([quest],None)
            specialItem = character.container.getItemByType("SpecialItem")
            if not specialItem:
                specialItemSlots = character.container.getItemsByType("SpecialItemSlot")
                for specialItemSlot in specialItemSlots:
                    if not specialItemSlot.hasItem:
                        continue
                    if self.itemID and not specialItemSlot.itemID == self.itemID:
                        continue
                    if not character.getPosition() == specialItemSlot.getPosition():
                        quest = src.quests.questMap["GoToPosition"](targetPosition=specialItemSlot.getPosition())
                        return ([quest],None)
                    return (None,("j","get special item"))
                if not dryRun:
                    self.fail()
                return (None,None)

            if not character.getPosition() == specialItem.getPosition():
                quest = src.quests.questMap["GoToPosition"](targetPosition=specialItem.getPosition())
                return ([quest],None)
            return (None,("k","pick up special item"))

        if not terrain.xPosition == character.registers["HOMETx"] or not terrain.yPosition == character.registers["HOMETy"]:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        if not character.container.isRoom:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)
        specialItemSlots = character.container.getItemsByType("SpecialItemSlot")
        if not specialItemSlots:
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        for specialItemSlot in specialItemSlots:
            if specialItemSlot.itemID == hasSpecialItem.itemID:
                if not character.getPosition() == specialItemSlot.getPosition():
                    quest = src.quests.questMap["GoToPosition"](targetPosition=specialItemSlot.getPosition())
                    return ([quest],None)
                return (None,("j","insert special item"))

        if not dryRun:
            self.fail()
        return (None,None)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        if character == src.gamestate.gamestate.mainChar:
            print("solver delve")

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

src.quests.addType(DelveDungeon)

import src


class Equip(src.quests.MetaQuestSequence):
    type = "Equip"

    def __init__(self, description="equip", creator=None, command=None, lifetime=None, weaponOnly=False, reason=None, story=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

        self.shortCode = "e"
        self.reason = reason
        self.story = story

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        storyString = ""
        if self.story:
            storyString = f"{self.story}"
        sword = src.items.itemMap["Sword"]()
        armor = src.items.itemMap["Armor"]()
        return [f"""{storyString}
Equip yourself{reasonString}.
A Aword (""",sword.render(),""") and Armor (""",armor.render(),""") are good equipment.

You can try to find equipment in storage.
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

    def findBestEquipment(self,character):
        bestArmor = None
        bestSword = None
        for room in self.character.getTerrain().rooms:
            for item in room.getItemsByType("Armor"):
                if item != room.getItemByPosition(item.getPosition())[0]:
                    continue
                if not bestArmor:
                    bestArmor = item
                    continue
                if bestArmor.armorValue > item.armorValue:
                    continue
                bestArmor = item
            for item in room.getItemsByType("Sword"):
                if item != room.getItemByPosition(item.getPosition())[0]:
                    continue
                if not bestSword:
                    bestSword = item
                    continue
                if bestSword.baseDamage > item.baseDamage:
                    continue
                bestSword = item

        if bestArmor and character.armor and bestArmor.armorValue <= character.armor.armorValue:
            bestArmor = None
        if bestSword and character.weapon and bestSword.baseDamage <= character.weapon.baseDamage:
            bestSword = None
        return (bestSword,bestArmor)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        (bestSword,bestArmor) = self.findBestEquipment(character)

        if bestSword and not character.weapon:
            return

        if bestArmor and not character.armor:
            return

        if bestSword and character.weapon and bestSword.baseDamage > character.weapon.baseDamage:
            return

        if bestArmor and character.armor and bestArmor.armorValue > character.armor.armorValue:
            return

        if "metal working" in character.duties and (not character.weapon or not character.armor):
            return

        self.postHandler()
        return

    def clearCompletedSubquest(self):
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        self.clearCompletedSubquest()
        if not self.subQuests:
            self.generateSubquests(self.character)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState.get("submenue"):
            return (None,(["esc"],"close the menu"))

        (bestSword,bestArmor) = self.findBestEquipment(character)
        if bestSword and (not character.weapon or bestSword.baseDamage > character.weapon.baseDamage):
            if character.container != bestSword.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=bestSword.container.getPosition())
                return ([quest],None)

            if character.getDistance(bestSword.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=bestSword.getPosition(),ignoreEndBlocked=True)
                return ([quest],None)

            offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w"),((0,0,0),".")]
            for offset in offsets:
                if character.getPosition(offset=offset[0]) == bestSword.getPosition():
                    return (None,("J"+offset[1],"equip the item"))
            1/0

        if bestArmor and (not character.armor or bestArmor.armorValue > character.armor.armorValue):
            if character.container != bestArmor.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=bestArmor.container.getPosition())
                return ([quest],None)

            if character.getDistance(bestArmor.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=bestArmor.getPosition(),ignoreEndBlocked=True)
                return ([quest],None)

            offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w"),((0,0,0),".")]
            for offset in offsets:
                if character.getPosition(offset=offset[0]) == bestArmor.getPosition():
                    return (None,("J"+offset[1],"equip the item"))
            2/0

        if "metal working" in character.duties:
            if not character.weapon:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Sword",produceToInventory=False)
                quests.append(quest)
                return (quests,None)

            if not character.armor:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Armor",produceToInventory=False)
                quests.append(quest)
                return (quests,None)

        return (None,None)

src.quests.addType(Equip)

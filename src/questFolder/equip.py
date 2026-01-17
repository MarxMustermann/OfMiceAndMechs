import src

import random

class Equip(src.quests.MetaQuestSequence):
    '''
    quest for a NPC to equip with weapons etc
    '''
    type = "Equip"
    lowLevel = True

    def __init__(self, description="equip", creator=None, command=None, lifetime=None, weaponOnly=False, reason=None, story=None, tryHard=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.weaponOnly = weaponOnly

        self.shortCode = "e"
        self.reason = reason
        self.story = story
        self.tryHard = tryHard

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
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
        '''
        calls the actual function with modified parameters
        '''
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def handleMoved(self,extraInfo=None):
        '''
        try to fix the quests states with every move
        '''
        self.subQuestCompleted()

    def assignToCharacter(self, character):
        '''
        listen for the character to move or equip stuff
        '''
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "equipedItem")
        self.startWatching(character,self.handleMoved, "moved")
        super().assignToCharacter(character)

    def findBestEquipment(self,character):
        '''
        get the best equipment available for the character
        '''
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

        for item in character.searchInventory("Armor"):
            if not bestArmor:
                bestArmor = item
                continue
            if bestArmor.armorValue > item.armorValue:
                continue
            bestArmor = item
        for item in character.searchInventory("Sword"):
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

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest when done
        '''
        if not character:
            return False

        (bestSword,bestArmor) = self.findBestEquipment(character)

        if bestSword and not character.weapon:
            return False

        if bestArmor and not character.armor:
            return False

        if bestSword and character.weapon and bestSword.baseDamage > character.weapon.baseDamage:
            return False

        if bestArmor and character.armor and bestArmor.armorValue > character.armor.armorValue:
            return False

        if ("metal working" in character.duties or self.tryHard) and (not character.weapon or not character.armor):
            return False

        if dryRun:
            self.postHandler()
        return True

    def clearCompletedSubquest(self):
        '''
        remove completed subquests (hack)
        '''
        while self.subQuests and self.subQuests[0].completed:
            self.subQuests.remove(self.subQuests[0])

    def subQuestCompleted(self,extraInfo=None):
        '''
        hande a subquest beeing completed
        '''
        self.clearCompletedSubquest()
        if not self.subQuests:
            self.generateSubquests(self.character)

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step towards solving the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # find what to equip
        (bestSword,bestArmor) = self.findBestEquipment(character)

        # handle menus
        submenue = character.macroState.get("submenue")
        if submenue:
            if bestSword in character.inventory:
                return (None,(submenue.get_command_to_select_item(item_to_select=bestSword),"equip from inventory"))
            if bestArmor in character.inventory:
                return (None,(submenue.get_command_to_select_item(item_to_select=bestArmor),"equip from inventory"))
            if submenue.tag not in ("advancedInteractionSelection","advancedPickupSelection",):
                return (None,(["esc"],"close menu"))

        # enter tile properly
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))

        if bestSword in character.inventory:
            command = "i"
            for item in character.inventory:
                if item == bestSword:
                    break
                command += "s"
            command += "j"
            return (None,(command,"equip from inventory"))
        if bestArmor in character.inventory:
            command = "i"
            for item in character.inventory:
                if item == bestArmor:
                    break
                command += "s"
            command += "j"
            return (None,(command,"equip from inventory"))

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
                    items = bestSword.container.getItemByPosition(bestSword.getPosition())
                    if items[-1] == bestSword:
                        interactionCommand = "J"
                        if submenue:
                            if submenue.tag == "advancedInteractionSelection":
                                interactionCommand = ""
                            else:
                                return (None,(["esc"],"close menu"))
                    else:
                        if not character.getFreeInventorySpace():
                            return (None,(random.choice(["l","Ld","Lw","Ls","La"]),"free up inventory"))
                        interactionCommand = "K"
                        if submenue:
                            if submenue.tag == "advancedPickupSelection":
                                interactionCommand = ""
                            else:
                                return (None,(["esc"],"close menu"))
                    command = interactionCommand+offset[1]
                    if command == "J.":
                        command = "j"
                    if command == "K.":
                        command = "k"
                    return (None,(command,"equip the item"))
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
                    items = bestArmor.container.getItemByPosition(bestArmor.getPosition())
                    if items[-1] == bestArmor:
                        interactionCommand = "J"
                        if submenue:
                            if submenue.tag == "advancedInteractionSelection":
                                interactionCommand = ""
                            else:
                                return (None,(["esc"],"close menu"))
                    else:
                        if not character.getFreeInventorySpace():
                            return (None,(random.choice(["l","Ld","Lw","Ls","La"]),"free up inventory"))
                        interactionCommand = "K"
                        if submenue:
                            if submenue.tag == "advancedPickupSelection":
                                interactionCommand = ""
                            else:
                                return (None,(["esc"],"close menu"))
                    command = interactionCommand+offset[1]
                    if command == "J.":
                        command = "j"
                    if command == "K.":
                        command = "k"
                    return (None,(command,"equip the item"))
            2/0

        if "metal working" in character.duties or self.tryHard:
            if not character.weapon:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Sword",produceToInventory=False,tryHard=True)
                quests.append(quest)
                return (quests,None)

            if not character.armor:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False)
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Armor",produceToInventory=False,tryHard=True)
                quests.append(quest)
                return (quests,None)

        return (None,(".","stand around confused"))

    def handleQuestFailure(self,extraParam):
        '''
        handle a subquest failing
        '''

        # set up helper variables
        quest = extraParam.get("quest")
        reason = extraParam.get("reason")

        if reason:
            if reason == "no tile path":
                self.fail(reason=reason)
                return

        super().handleQuestFailure(extraParam)

# register the quest type
src.quests.addType(Equip)

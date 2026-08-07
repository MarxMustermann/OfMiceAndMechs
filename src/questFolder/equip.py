import src

import random

class Equip(src.quests.MetaQuestSequence):
    '''
    quest for a NPC to equip with weapons etc
    '''
    type = "Equip"
    lowLevel = True

    def __init__(self, description="equip", creator=None, command=None, lifetime=None, noRods=False, reason=None, story=None, tryHard=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description
        self.noRods = noRods

        self.shortCode = "e"
        self.reason = reason
        self.story = story
        self.tryHard = tryHard

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        reasonString = (src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),".")
        if self.reason:
            reasonString = [(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),",")," to "+self.reason+"."]
        storyString = ""
        if self.story:
            storyString = f"{self.story}"
        sword = src.items.itemMap["Sword"]()
        armor = src.items.itemMap["Armor"]()
        rod = src.items.itemMap["Rod"]()
        return [f"""{storyString}
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Equip yourself"),reasonString,"""
A Sword (""",sword.metaRender(),""") and Armor (""",armor.metaRender(),""") are good equipment.
A Rod (""",rod.metaRender(),""")will work as an improvised weapon as well.

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

    def assignToCharacter(self, character):
        '''
        listen for the character to move or equip stuff
        '''
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "equipedItem")
        super().assignToCharacter(character)

    def findEquipment(self,character):
        '''
        get the equipment available for the character
        '''

        # set up helper variables
        armor = None
        weapon = None

        # check for equipment within rooms
        for room in self.character.getTerrain().rooms:
            for item in room.getItemsByType("Armor"):
                if not armor:
                    armor = item
                    break
            items = room.getItemsByType("Sword")
            if not self.noRods:
                items.extend(room.getItemsByType("Rod"))
            for item in items:
                if not weapon:
                    weapon = item
                    break

        # check in inventory
        for item in character.searchInventory("Armor"):
            if not sword:
                sword = item
                break
        items = character.searchInventory("Sword")
        if not self.noRods:
            items.extend(character.searchInventory("Rod"))
        for item in items:
            weapon = item

        if character.armor:
            armor = None
        if character.weapon:
            weapon = None
        return (weapon,armor)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest when done
        '''
        if not character:
            return False

        (weapon,armor) = self.findEquipment(character)

        if weapon or armor:
            return False

        if ("metal working" in character.duties or self.tryHard) and (not character.weapon or not character.armor):
            return False

        if dryRun:
            self.postHandler()
        return True

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step towards solving the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)
        if character.getNearbyEnemies():
            return self._solver_trigger_fail(dryRun,"enemies nearby")

        # find what to equip
        (weapon,armor) = self.findEquipment(character)

        # handle menus
        submenue = character.macroState.get("submenue")
        if submenue:
            if isinstance(submenue,src.menues.menuMap["InventoryMenu"]):
                if weapon in character.inventory:
                    return (None,(submenue.get_command_to_select_item(item_to_select=weapon),"equip from inventory"))
                if armor in character.inventory:
                    return (None,(submenue.get_command_to_select_item(item_to_select=armor),"equip from inventory"))
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

        # equip items from inventory
        if weapon in character.inventory:
            command = "i"
            for item in character.inventory:
                if item == weapon:
                    break
                command += "s"
            command += "j"
            return (None,(command,"equip from inventory"))
        if armor in character.inventory:
            command = "i"
            for item in character.inventory:
                if item == armor:
                    break
                command += "s"
            command += "j"
            return (None,(command,"equip from inventory"))

        # ensure there is inventory space to pick up a new weapon
        if not character.getFreeInventorySpace() and character.isOnHomeTerrain():
            quest = src.quests.questMap["ClearInventory"](reason="ensure you can pich up new equipment")
            return ([quest],None)

        # pick up weapon
        if weapon:

            # go to weapon
            if character.container != weapon.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=bestSword.container.getPosition(),reason="get near a weapon")
                return ([quest],None)
            if character.getDistance(weapon.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=weapon.getPosition(),ignoreEndBlocked=True,reason="be able pick up the weapon")
                return ([quest],None)

            # pick up weapon
            offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w"),((0,0,0),".")]
            for offset in offsets:
                if character.getPosition(offset=offset[0]) == weapon.getPosition():
                    items = weapon.container.getItemByPosition(weapon.getPosition())
                    if items[-1] == weapon:
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

        # pick up armor
        if armor:

            # go to armor
            if character.container != armor.container:
                quest = src.quests.questMap["GoToTile"](targetPosition=armor.container.getPosition(),reason="get near armor")
                return ([quest],None)
            if character.getDistance(armor.getPosition()) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=armor.getPosition(),ignoreEndBlocked=True,reason="be able to pick up armor")
                return ([quest],None)

            # pick up armor
            offsets = [((1,0,0),"d"),((-1,0,0),"a"),((0,1,0),"s"),((0,-1,0),"w"),((0,0,0),".")]
            for offset in offsets:
                if character.getPosition(offset=offset[0]) == armor.getPosition():
                    items = armor.container.getItemByPosition(armor.getPosition())
                    if items[-1] == armor:
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

        # produce new equipment
        if "metal working" in character.duties or self.tryHard:
            if not character.weapon:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="have space to store a weapon")
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Sword",produceToInventory=False,tryHard=True,reason="have a Sword to equip")
                quests.append(quest)
                return (quests,None)

            if not character.armor:
                quests = []
                quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="have space to store an armor")
                quests.append(quest)
                quest = src.quests.questMap["MetalWorking"](amount=1,toProduce="Armor",produceToInventory=False,tryHard=True,reason="have an armor to equip")
                quests.append(quest)
                return (quests,None)

        # do nothing
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

import src

class BecomeStronger(src.quests.MetaQuestSequence):
    type = "BecomeStronger"

    def __init__(self, description="become stronger", creator=None, lifetime=None, reason=None, targetStrength=1):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetStrength = targetStrength

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        if not character.weapon:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Sword"):
                    quest = src.quests.questMap["Equip"]()
                    return ([quest],None)
            quest = src.quests.questMap["MetalWorking"](toProduce="Sword",produceToInventory=False,amount=1)
            return ([quest],None)
        else:
            shouldSharpen = False
            if character.weapon.baseDamage < 15:
                shouldSharpen = True
            elif character.weapon.baseDamage < 30:
                if character.searchInventory("Grindstone"):
                    shouldSharpen = True

            if shouldSharpen:
                for room in terrain.rooms:
                    for item in room.getItemsByType("SwordSharpener",needsBolted=True):
                        quest = src.quests.questMap["SharpenPersonalSword"]()
                        return ([quest],None)

            if character.weapon.baseDamage < 30:
                for room in terrain.rooms:
                    if room.getNonEmptyOutputslots("Grindstone"):
                        quest = src.quests.questMap["FetchItems"](toCollect="Grindstone")
                        return ([quest],None)

        if not character.armor:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Armor"):
                    quest = src.quests.questMap["Equip"]()
                    return ([quest],None)
            quest = src.quests.questMap["MetalWorking"](toProduce="Armor",produceToInventory=False,amount=1)
            return ([quest],None)
        else:
            if character.armor.armorValue < 3:
                for room in terrain.rooms:
                    for item in room.getItemsByType("ArmorReinforcer",needsBolted=True):
                        quest = src.quests.questMap["ReinforcePersonalArmor"]()
                        return ([quest],None)

        if character.inventory:
            quest = src.quests.questMap["ClearInventory"](returnToTile=False)
            return ([quest],None)

        quest = src.quests.questMap["Adventure"]()
        return ([quest],None)

    def generateTextDescription(self):
        return ["""
The dungeons are too hard for you. 
You need to be stronger, to take them on.

Get some upgrades to be stronger.
"""]

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.getStrengthSelfEstimate() < self.targetStrength:
            return False

        self.postHandler()
        return True

src.quests.addType(BecomeStronger)

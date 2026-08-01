import src


class StoryImproveEquipment(src.quests.MetaQuestSequence):
    type = "StoryImproveEquipment"

    def __init__(self, description="improve equipment", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getTargetRoom(self):
        terrain = self.character.getTerrain()
        for room in terrain.rooms:
            if room.getItemByType("SiegeManager"):
                return room
        return None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # set up helper variables
        terrain = character.getTerrain()

        # upgrade the swords
        if isinstance(character.weapon,src.items.itemMap["Sword"]):

            # try to use a SwordSharpener
            found_swordSharpener = None
            for room in character.getTerrain().rooms:
                if room.getEnemies(character):
                    continue
                swordSharpeners = room.getItemsByType("SwordSharpener",needsBolted=True)
                if not swordSharpeners:
                    continue
                for swordSharpener in swordSharpeners:
                    found_swordSharpener = swordSharpener
                    if swordSharpener.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["SharpenPersonalSword"]()
                        return ([quest],None)

            # collect Grindstones
            if found_swordSharpener:
                upgrade_cost = found_swordSharpener.amountNeededForOneUpgrade(character.weapon.baseDamage)
                upgrade_cost -= len(found_swordSharpener.getAvailableGrindStones(character))

                num_grindstones_available = 0
                for room in character.getTerrain().rooms:
                    if room.getEnemies(character):
                        continue
                    if room.tag == "ruin":
                        continue
                    outputSlots = room.getNonEmptyOutputslots("Grindstone",allowStorage=True)
                    for outputSlot in outputSlots:
                        items = room.getItemByPosition(outputSlot[0])
                        for item in items:
                            if item.type == "Grindstone":
                                num_grindstones_available += 1
                
                if num_grindstones_available >= upgrade_cost:
                    quest = src.quests.questMap["FetchItems"](toCollect="Grindstone",amount=upgrade_cost)
                    return ([quest],None)

        # upgrade the armor
        if character.armor:

            # try to use a ArmorReinforcer
            found_armorReinforcer = None
            for room in character.getTerrain().rooms:
                if room.getEnemies(character):
                    continue
                armorReinforcers = room.getItemsByType("ArmorReinforcer",needsBolted=True)
                if not armorReinforcers:
                    continue
                for armorReinforcer in armorReinforcers:
                    found_armorReinforcer = armorReinforcer
                    if armorReinforcer.readyToBeUsedByCharacter(character):
                        quest = src.quests.questMap["ReinforcePersonalArmor"]()
                        return ([quest],None)

            # collect ChitinPlates
            if found_armorReinforcer:
                upgrade_cost = found_armorReinforcer.amountNeededForOneUpgrade(character.armor.armorValue)
                upgrade_cost -= len(found_armorReinforcer.getAvailableChitinPlates(character))

                num_chitinPlates_available = 0
                for room in character.getTerrain().rooms:
                    if room.getEnemies(character):
                        continue
                    if room.tag == "ruin":
                        continue
                    outputSlots = room.getNonEmptyOutputslots("ChitinPlates",allowStorage=True)
                    for outputSlot in outputSlots:
                        items = room.getItemByPosition(outputSlot[0])
                        for item in items:
                            if item.type == "ChitinPlates":
                                num_chitinPlates_available += 1
                
                if num_chitinPlates_available >= upgrade_cost:
                    quest = src.quests.questMap["FetchItems"](toCollect="ChitinPlates",amount=upgrade_cost)
                    return ([quest],None)

        # abort
        return self._solver_trigger_fail(dryRun,"no way to improve equipment")

    def generateTextDescription(self):
        text = ["""
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Improve your equipment."),f"""

Swords can be upgraded a SwordSharpener.
This may need GrindStones.

Armor can be upgraded a ArmorReinforcer.
This may need ChitinPlates.
"""]
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

src.quests.addType(StoryImproveEquipment)

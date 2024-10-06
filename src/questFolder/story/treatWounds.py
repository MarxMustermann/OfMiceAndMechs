import src
import random


class TreatWounds(src.quests.MetaQuestSequence):
    type = "TreatWounds"

    def __init__(self, description="treat wounds", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    @staticmethod
    def getTileVials(character):
        terrain = character.getTerrain()
        tileVials = []
        rooms = terrain.getRoomByPosition(character.getBigPosition())
        if rooms:
            items = rooms[0].itemsOnFloor
        else:
            items = terrain.itemsByBigCoordinate.get(character.getBigPosition(),[])

        for item in items:
            if not item.type == "Vial":
                continue
            if not item.uses > 0:
                continue
            tileVials.append(item)
        return tileVials

    def characterHasVial(self,character):
        for item in character.inventory:
            if not item.type == "Vial":
                continue
            if not item.uses > 0:
                continue
            return True
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None,(["esc",],"to close the menu"))

        if character.health < (character.maxHealth-10):
            # make completion smooth
            if character.interactionState.get("advancedInteraction") == {}:
                return (None,("H","drink the whole Vial"))

            # drink Vials from inventory
            hasInventoryVial = self.characterHasVial(character)
            if hasInventoryVial:
                return (None,("JH","drink the whole Vial"))

        #if character.inventory and character.inventory[-1].type == "Vial" and character.inventory[-1].uses == 0:
        #    return (None,("l","drop empty vial"))

        tileVials = self.getTileVials(character)
        if not tileVials:
            return (None,None)
        random.shuffle(tileVials)

        characterPos = character.getPosition()
        for tileVial in tileVials:
            if tileVial.getPosition() == characterPos:
                return (None,("k","pick up the Vial"))

        quest = src.quests.questMap["GoToPosition"](targetPosition=tileVials[0].getSmallPosition(),reason="be able to pick up the vial",description="go to the next Vial")
        return ([quest],None)

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = True
        door.blocked = False

        hasVial = False
        for item in self.character.inventory:
            if not item.type == "Vial":
                continue
            if item.uses == 0:
                continue
            hasVial = True

        result = []
        result.append("""
You reach out to your implant and it answers:

You are hurt and need to heal.
Passing time will heal your wounds, but you don't have the time for that.

A quick way to heal is to use Vials.""")
        if hasVial:
            result.append("""
You have a Vial in your inventory. Use it to heal yourself.
""")
        result.append("""

Try to collect more vials and other useful things.
Your inventory is now shown on the top right side of the screen.
You can access the inventory menu by pressing i.


Right now you are looking at the quest menu.
Detailed instructions are shown here.
For now ignore the options below and press esc to continue.

""")
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "healed")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "itemPickedUp")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return
    
        self.triggerCompletionCheck(self.character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.health < (character.maxHealth-10):
            hasInventoryVial = self.characterHasVial(character)
            if hasInventoryVial:
                return False

        hasTileVial = self.getTileVials(character)
        if hasTileVial:
            return False

        self.postHandler()

src.quests.addType(TreatWounds)

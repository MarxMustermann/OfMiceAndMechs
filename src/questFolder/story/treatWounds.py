import src
import random


class TreatWounds(src.quests.MetaQuestSequence):
    type = "TreatWounds"

    def __init__(self, description="treat wounds", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getTileVials(self,character):
        terrain = character.getTerrain()
        tileVials = []
        for item in terrain.itemsByBigCoordinate.get(character.getBigPosition(),[]):
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

    def getNextStep(self,character=None,ignoreCommands=False):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None,(["esc",],"to close the menu"))

        if character.health < 80:
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

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = True
        door.blocked = False

        return ["""
You reach out to your implant and it answers.

You are hurt and need to heal.
Passing time will heal your wounds, but you don't have the time for that.

A quick way to heal is to use Vials.
You started with a Vial in your inventory. Use it to heal yourself.


Try to collect more vials and other useful things. You can access the inventory menu by pressing i.
For convenience your inventory is now shown on the top right side of the screen.


Right now you are looking at the quest menu.
Detailed instructions are shown here.
For now ignore the options below and press esc to continue.

"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.health < 80:
            hasInventoryVial = self.characterHasVial(character)
            if hasInventoryVial:
                return False

        hasTileVial = self.getTileVials(character)
        if hasTileVial:
            return False

        self.postHandler()

src.quests.addType(TreatWounds)

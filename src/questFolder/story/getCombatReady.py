import src
import random


class GetCombatReady(src.quests.MetaQuestSequence):
    type = "GetCombatReady"

    def __init__(self, description="get combat ready", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def getNextStep(self,character=None,ignoreCommands=False):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None,(("esc"),"close the menu"))

        if not character.weapon:
            items = character.container.getItemsByType("Sword")

            if items:
                for sword in items:
                    if character.getPosition() != sword.getPosition():
                        continue

                    return (None,("j","equip sword"))

                quest = src.quests.questMap["GoToPosition"](targetPosition=sword.getPosition(),reason="be able to equip the sword",description="go to a sword")
                return ([quest],None)

        if not character.armor:
            items = character.container.getItemsByType("Armor")

            if items:
                for armor in items:
                    if character.getPosition() != armor.getPosition():
                        continue

                    return (None,("j","equip armor"))

                quest = src.quests.questMap["GoToPosition"](targetPosition=armor.getPosition(),reason="be able to equip the armor",description="go to a armor")
                return ([quest],None)

        return (None,None)

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
        return ["""
The center room of the base is blocked by an enemy.
It will attack you once you enter that room.
You should prepare to fight.

The arena is a good place to do that.
Enemies that manage to pass the trap room are fought here.
So there should be some fighting equipment here.

Get yourself a Sword and a piece of Armor.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "equipedItem")
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

        if not character.weapon and character.container.getItemsByType("Sword"):
            return False

        if not character.armor and character.container.getItemsByType("Armor"):
            return False

        self.postHandler()

src.quests.addType(GetCombatReady)

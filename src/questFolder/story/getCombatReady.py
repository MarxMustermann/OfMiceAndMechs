import src
import random


class GetCombatReady(src.quests.MetaQuestSequence):
    type = "GetCombatReady"

    def __init__(self, description="get combat ready", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)
        
        if not isinstance(character.container,src.rooms.Room):
            return (None,None)

        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close the menu"))

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

        if character.health < character.maxHealth - 10:
            if character.container.isRoom:
                items = character.container.getItemsByType("CoalBurner")
                validCoalBurners = []
                for item in items:
                    if not item.getMoldFeed(character):
                        continue
                    validCoalBurners.append(item)

                if len(validCoalBurners) == 0:
                    return (None,(".","stand around confused"))

                for item in validCoalBurners:
                    if character.getDistance(item.getPosition()) > 1:
                        continue
                    direction = "."
                    if character.getPosition(offset=(1,0,0)) == item.getPosition():
                        direction = "d"
                    if character.getPosition(offset=(-1,0,0)) == item.getPosition():
                        direction = "a"
                    if character.getPosition(offset=(0,1,0)) == item.getPosition():
                        direction = "s"
                    if character.getPosition(offset=(0,-1,0)) == item.getPosition():
                        direction = "w"

                    interaction_command = "J"
                    if submenue:
                        if submenue.tag == "advancedInteractionSelection":
                            interaction_command = ""
                        else:
                            return (None,(["esc"],"close menu"))
                    return (None,(interaction_command+direction,"heal"))

                quest = src.quests.questMap["GoToPosition"](targetPosition=validCoalBurners[0].getPosition(),reason="be able to heal",description="go to a coal burner",ignoreEndBlocked=True)
                return ([quest],None)

        return (None,(".","stand around confused"))

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

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        
        if not isinstance(character.container,src.rooms.Room):
            return False

        if not character.weapon and character.container.getItemsByType("Sword"):
            return False

        if not character.armor and character.container.getItemsByType("Armor"):
            return False

        if character.health < character.maxHealth-10:
            if character.container.isRoom:
                items = character.container.getItemsByType("CoalBurner")
                for item in items:
                    if not item.getMoldFeed(character):
                        continue
                    return False

        if not dryRun:
            self.postHandler()
        return True

src.quests.addType(GetCombatReady)

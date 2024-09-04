import src


class CollectGlassHearts(src.quests.MetaQuestSequence):
    type = "CollectGlassHearts"

    def __init__(self, description="collect glass hearts", creator=None, lifetime=None):
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

        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue

            quest = src.quests.questMap["DelveDungeon"](targetTerrain=god["lastHeartPos"],itemID=godId,suicidal=True)
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
        text = ["""
You reach out to your implant and it answers:

You have control over the base now, but your ressources are limited.
You need to use magic to keep the base runnning in the long term.

The GlassStatues in the temple allow you to cast magic.
This will use up the mana of the area.

The mana will slowly regenerate, but there is a faster way.
The GlassStatues are missing their hearts.
Obtain their GlassHeart and make them whole.

This will give you 3 advantages:
1. you will get a immediate mana boost
2. the GlassStatues will generate extra mana each epoch
1. the cost for using magic will be halfed

"""]
        if not self.subQuests:
            text.append("press + to generate a sub quest") 
        else:
            text.append("press d to view sub quest")
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

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

        return False

        self.postHandler()

src.quests.addType(CollectGlassHearts)

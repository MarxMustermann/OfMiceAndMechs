import src

class GetEpochReward(src.quests.MetaQuestSequence):
    type = "GetEpochReward"

    def __init__(self, description="spend epoch reward", creator=None, doEpochEvaluation=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

        self.doEpochEvaluation = doEpochEvaluation
        self.gotEpochEvaluation = False

    def getSolvingCommandString(self,character,dryRun=True):
        if character.getBigPosition() == (7,7,0):
            if character.getPosition() == (6,7,0):
                if self.doEpochEvaluation and not self.gotEpochEvaluation:
                    return list("Jw."+"ssj")+3*["enter"]+["esc"]
                else:
                    return list("Jw."+"sj"+"sj")+["enter"]+["esc"]
        return super().getSolvingCommandString(character)

    def generateTextDescription(self):
        text = ""
        if self.doEpochEvaluation and not self.gotEpochEvaluation:
            text += """
You completed a task for the epoch artwork.
Get a epoch review to get credited with the glass tears you earned.
Use the epoch artwork to get the epoch review.

"""
        text += """
You accumulated some glass tears.
You can use them at the epoch artwork to buy upgrades for yourself and the base.


In auto mode this quest will use the auto spend option.
That option will spend your glass tears on something.
So you might want to check out the other option and buy useful stuff.


Use the epoch artwork to spend your glass tears.
"""
        return text

    def triggerCompletionCheck(self, character=None):
        if not character:
            return

        if self.doEpochEvaluation and not self.gotEpochEvaluation:
            return

        if self.getEpochQuestCharges(character) < 10:
            self.postHandler()
            return

        if (character.health >= character.maxHealth and
            character.weapon and character.weapon.baseDamage >= 25 and
            character.armor and character.armor.armorValue >= 5):
            self.postHandler()
            return

        return

    def handleGotEpochEvaluation(self):
        self.gotEpochEvaluation = True
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotEpochEvaluation, "got epoch evaluation")

        super().assignToCharacter(character)

    def getEpochQuestCharges(self,character):
        room = character.getHomeRoom()
        epochArtwork = room.getItemByPosition((6,6,0))[0]
        return epochArtwork.charges

    def generateSubquests(self,character): 
        
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if not character.getPosition() == (6,7,0):
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,7,0), description="go to epoch artwork")
                quest.activate()
                self.addQuest(quest)
                return

            return

        directions = {
                (7,5,0):"south",
                (7,6,0):"west",
                (8,6,0):"south",
                (6,6,0):"south",
                (8,7,0):"south",
                (6,7,0):"south",
                (8,8,0):"south",
                (6,8,0):"south",
                (8,9,0):"west",
                (6,9,0):"east",
                (7,9,0):"north",
                (7,8,0):"north",
                }

        quest = src.quests.questMap["GoHome"](description="go to command centre")
        self.addQuest(quest)

        return

    def solver(self,character):
        self.triggerCompletionCheck(character)
        self.generateSubquests(character)

        super().solver(character)

src.quests.addType(GetEpochReward)

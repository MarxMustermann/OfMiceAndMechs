import src


class GetRank5PromotionStory(src.quests.MetaQuestSequence):
    '''
    quest to get a promotion to rank 5
    '''
    type = "GetRank5PromotionStory"
    def __init__(self, description="get promotion to rank 5", reason=None):
        super().__init__()
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a description text to be shown on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason

        text = f"""
You reach out to your implant and it answers:

The Communicator does not work with your current rank.
The reset of your faction marker seems to also has reset your rank marker to rank 6.
Since the base is empty this error can not be resolved.

Gain rank 5 by getting promoted using the normal way{reasonString}.
The base has a Promoter, use that to get promoted.
"""

        return text

    def handleGotPromotion(self, extraInfo):
        '''
        end quest after getting a promotion
        '''
        self.postHandler()

    def handlePromotionBlocked(self, extraInfo):
        '''
        ensure condition for promotion if that is an issue
        '''
        for quest in self.subQuests[:]:
            quest.postHandler()

        quest = src.quests.questMap["SpawnClone"]()
        self.addQuest(quest)

    def assignToCharacter(self, character):
        '''
        watch for events getting triggered by trying to get the promotion
        '''
        if self.character:
            return

        self.startWatching(character,self.handleGotPromotion, "got promotion")
        self.startWatching(character,self.handlePromotionBlocked, "promotion blocked")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end the quest if done
        '''
        if not character:
            return None

        if character.rank and character.rank <= 5:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        '''
        calculate next step towards solving the quest
        '''
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        quest = src.quests.questMap["GetPromotion"](targetRank=5)
        return ([quest],None)

# register quest type
src.quests.addType(GetRank5PromotionStory)

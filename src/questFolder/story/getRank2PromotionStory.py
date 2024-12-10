import src


class GetRank2PromotionStory(src.quests.MetaQuestSequence):
    type = "GetRank2PromotionStory"

    def __init__(self, description="get promotion to rank 2", reason=None):
        super().__init__()
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason

        text = f"""
You reach out to your implant and it answers:

The Communicator does let you contact tha main base with your current rank.
Gain rank 2 by getting promoted using the normal way{reasonString}.
The base has a Promoter, use that to get promoted.

"""
    
        if self.subQuests:
            text += """
this quest has sub quests. Press d to show subquest.
"""

        return text

    def handleGotPromotion(self, extraInfo):
        self.postHandler()

    def handlePromotionBlocked(self, extraInfo):
        for quest in self.subQuests[:]:
            quest.postHandler()

        quest = src.quests.questMap["StoryClearTerrain"]()
        self.addQuest(quest)

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotPromotion, "got promotion")
        self.startWatching(character,self.handlePromotionBlocked, "promotion blocked")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if character.rank <= 2:
            self.postHandler()
            return True
        return False

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        quest = src.quests.questMap["GetPromotion"](targetRank=2)
        return ([quest],None)


        # kill snatchers
        snatcherCount = 4
        if snatcherCount:
            quest = src.quests.questMap["SecureTile"](toSecure=(5,6,0),endWhenCleared=False,reason="confront the Snatchers",story="You reach out to your implant and it answers:\n\nThe base itself is safe now, but there are Snatchers out there.\nThey will try to swarm and kill everyone that goes outside.",lifetime=100)
            return ([quest],None)

        return (None,None)

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            return  ([quest],None)
        
        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "Promoter":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return (None,("Ja","get promotion"))
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return (None,("Jd","get promotion"))
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return (None,("Jw","get promotion"))
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return (None,("Js","get promotion"))
            
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to promoter ")
            return  ([quest],None)
        
        quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre")
        return  ([quest],None)


src.quests.addType(GetRank2PromotionStory)

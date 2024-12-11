import src


class GetPromotion(src.quests.MetaQuestSequence):
    type = "GetPromotion"

    def __init__(self, targetRank, description="get promotion", reason=None):
        super().__init__()
        self.metaDescription = description
        self.targetRank = targetRank
        self.reason = reason

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason

        text = f"""
Rise in the hierarchy and get a Promotion{reasonString}.
Use the Promotor to do this.
"""

        return text

    def handleGotPromotion(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotPromotion, "got promotion")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if character.rank <= self.targetRank:
            self.postHandler()
            return True
        return False

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            return (None,(["esc"],"close the menu"))

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


src.quests.addType(GetPromotion)

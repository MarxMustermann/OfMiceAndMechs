import src

class GetBodyGuards(src.quests.MetaQuestSequence):
    type = "GetBodyGuards"

    def __init__(self, description="get body guards"):
        questList = []
        super().__init__(questList)
        self.metaDescription = description

    def generateTextDescription(self):
        numMaxPosSubordinates = self.character.getNumMaxPosSubordinates()
        numSubordinates = self.character.getNumSubordinates()
        extraS = "s"
        if numSubordinates == 1:
            extraS = ""
        text = ("""
Since you are rank %s you can have %s subordinate"""+extraS+""".
You currently only have %s subordinates.
""")%(self.character.rank, numMaxPosSubordinates, numSubordinates, )

        if (numMaxPosSubordinates-numSubordinates) == 1:
            extra = "a "
            if numSubordinates > 0:
                extra = "one more "
            text += """
Get """+extra+"""body guard to replenish your subordinates."""
        else:
            extra = ""
            if numSubordinates > 0:
                extra = "more "
            text += """
Get """+extra+""" body guards to replenish your subordinates."""
        text += """
Body guards will follow you around and will try to protect you."""

        text += """


Go to the personnel artwork in the command centre.
Use it to gain a new body guard."""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not self.active:
            return False
        if self.completed:
            1/0

        numMaxPosSubordinates = self.character.getNumMaxPosSubordinates()
        numSubordinates = self.character.getNumSubordinates()
        if not numMaxPosSubordinates > numSubordinates:
            self.postHandler()
            return True

        personnelArtwork = self.getPersonnelArtwork(character)
        if personnelArtwork and personnelArtwork.charges < 1:
            self.fail()
            return True

        return False

    def getPersonnelArtwork(self,character):
        homeRoom = character.getHomeRoom()
        if not homeRoom:
            return None
        return homeRoom.getItemByType("PersonnelArtwork")

    def generateSubquests(self,character):
        if not self.active:
            return

        if self.completed:
            1/0

        if self.subQuests:
            return

        if not character.getIsHome():
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

        personnelArtwork = self.getPersonnelArtwork(character)
        if personnelArtwork and character.getDistance(personnelArtwork.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](description="go to personnel artwork",targetPosition=personnelArtwork.getPosition(),ignoreEndBlocked=True)
            self.addQuest(quest)
            quest.activate()
            quest.assignToCharacter(character)
            return

    def getSolvingCommandString(self,character,dryRun=True):
        personnelArtwork = self.getPersonnelArtwork(character)
        if not personnelArtwork:
            1/0
            return
        offset = character.getOffset(personnelArtwork.getPosition())
        baseCommand = None
        if offset == (0,0,0):
            baseCommand = "j"
        if offset == (-1,0,0):
            baseCommand = "Jd."
        if offset == (0,-1,0):
            baseCommand = "Js."
        if offset == (1,0,0):
            baseCommand = "Ja."
        if offset == (0,1,0):
            baseCommand = "Jw."

        if baseCommand:
            return baseCommand+"sj"

    def handleGotBodyguard(self,extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0
        self.triggerCompletionCheck(self.character)

    def handleTileChange(self,extraInfo=None):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.triggerCompletionCheck(self.character):
            return

        self.generateSubquests(self.character)

    def assignToCharacter(self,character):
        if self.character:
            return

        self.startWatching(character,self.handleTileChange, "changedTile")
        self.startWatching(character,self.handleTileChange, "got subordinate")

        return super().assignToCharacter(character)

    def solver(self,character):
        if self.triggerCompletionCheck(character):
            return

        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return

        super().solver(character)

src.quests.addType(GetBodyGuards)

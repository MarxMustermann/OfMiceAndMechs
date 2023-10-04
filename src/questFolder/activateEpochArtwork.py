import src


class ActivateEpochArtwork(src.quests.MetaQuestSequence):
    type = "ActivateEpochArtwork"

    def __init__(self, description="activate epoch artwork",epochArtwork=None,storyText=None):
        questList = []
        super().__init__(questList)
        self.metaDescription = description
        self.epochArtwork = epochArtwork
        self.storyText = storyText

        self.startWatching(epochArtwork,self.handleEpochrArtworkUsed, "epoch artwork used")

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((7,7,0),"target"))
        return result

    def generateTextDescription(self):
        out = ""
        if not self.storyText:
            out += """
You reached the base and you are safe for now.
The farms have been neglected and hives have developed.
But it has defenses.

Find out who is commanding this base.
Maybe you will be safe for longer here."""
        else:
            out += self.storyText
        out += """


Go to the command centre and activate the epoch artwork.
That should reveal who is commanding this base.



You can move using full tiles by pressing WASD. Your character will automove.
This is a lot less keys to press, but should only be done in safe areas.
Remember to press ctrl-d if you lose control over your character.
"""
        return out


    def handleEpochrArtworkUsed(self,extraInfo):
        if extraInfo[0] == self.character:
            self.postHandler()

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        return False

    def solver(self,character):
        self.triggerCompletionCheck(character)
        self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

    def getSolvingCommandString(self,character,dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
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

        direction = directions.get(character.getBigPosition())
        if direction:
            if direction == "north":
                return "W"
            if direction == "south":
                return "S"
            if direction == "west":
                return "A"
            if direction == "east":
                return "D"

        if not self.subQuests and character.getPosition() == (6,7,0):
            return "Jw"
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character,silent=False):

        if not self.active:
            return
        if self.completed:
            return

        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return

        pos = character.getBigPosition()

        if pos == (7,7,0):
            if character.getPosition() != (6, 7, 0):
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

        direction = directions.get(pos)
        if direction == None:
            return

        if direction == "north":
            targetPos = (pos[0],pos[1]-1,pos[2])
        if direction == "south":
            targetPos = (pos[0],pos[1]+1,pos[2])
        if direction == "west":
            targetPos = (pos[0]-1,pos[1],pos[2])
        if direction == "east":
            targetPos = (pos[0]+1,pos[1],pos[2])

        if not silent:
            character.addMessage("move one tile to the "+direction)
        quest = src.quests.questMap["GoToTile"](description="go one tile "+direction,targetPosition=targetPos,showCoordinates=False)
        self.addQuest(quest)
        quest.activate()

    def handleMovement(self, extraInfo):
        if self.completed:
            1/0

        if not self.active:
            return

        self.generateSubquests(extraInfo[0],silent=True)

    def handleTileChange(self):
        if self.completed:
            1/0

        for quest in self.subQuests:
            quest.postHandler()

        self.subQuests = []

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleMovement, "moved")
        self.startWatching(character,self.handleTileChange, "changedTile")

        super().assignToCharacter(character)

src.quests.addType(ActivateEpochArtwork)

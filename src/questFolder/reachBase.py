import src

class ReachBase(src.quests.MetaQuestSequence):
    type = "ReachBase"

    def __init__(self, description="reach base",storyText=None):
        super().__init__()
        self.metaDescription = description
        self.lastDirection = None
        self.storyText = storyText

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((7,6,0),"target"))
        return result

    def solver(self,character):
        self.generateSubquests(character)

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

    def generateTextDescription(self):

        text = """
You reach out to your implant and in answers:"""
        if self.storyText:
            text += f"""
{self.storyText}"""
        else:
            text += """

There is a base in the north. The base belongs to your faction.
Enter the base to get into the safety of the bases defenses.


The entry is on the northern side of the base.
You need to go around the base to actually enter it.
You are likely getting chased and the area is overrun with insects.
So you have to be careful."""

        text += f"""

You have to cross several tiles to find your path to the entry of the base.
Currently the suggested next step is to go one tile to the {self.lastDirection}.
Following the suggestions will guide you into the base.
It might also steer you into groups of enemies on the way.
So watch the environment and don't follow all suggestions blindly.



You can see description for sub quests.
Press d now to move the quest cursor to select the sub quest.
"""
        return text

    def generateSubquests(self,character):
        if self.subQuests:
            return

        if not self.active:
            return
        if self.completed:
            return

        if character.getPosition() == (7,0,0):
            quest = src.quests.questMap["RunCommand"](command="s")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return
        pos = character.getBigPosition()
        if pos == (7,6,0):
            self.postHandler()
            return

        if pos == (9,5,0):
            direction = "north"
        elif pos[1] > 10:
            if pos[0] == 7:
                direction = "west"
            elif pos[0] < 7:
                if pos[0] == 6:
                    direction = "north"
                else:
                    direction = "east"
            else:
                direction = "west"
        elif pos[1] > 6:
            if pos[0] <= 7:
                if pos[0] <= 4:
                    direction = "north"
                else:
                    direction = "west"
            elif pos[0] >= 10:
                direction = "north"
            else:
                direction = "east"
        elif pos[1] == 6:
            if pos[0] <= 7:
                if pos[0] == 4:
                    direction = "north"
                elif pos[0] == 5:
                    direction = "north"
                else:
                    direction = "east"
            else:
                direction = "north"
        elif pos[1] == 4:
            if pos[0] < 7:
                direction = "east"
            elif pos[0] < 7:
                direction = "west"
            else:
                direction = "south"
        else:
            if pos[0] < 4:
                direction = "south"
            elif pos[0] < 7:
                direction = "east"
            elif pos[0] == 7:
                direction = "south"
            else:
                direction = "west"

        if direction == "north":
            targetPos = (pos[0],pos[1]-1,pos[2])
        if direction == "south":
            targetPos = (pos[0],pos[1]+1,pos[2])
        if direction == "west":
            targetPos = (pos[0]-1,pos[1],pos[2])
        if direction == "east":
            targetPos = (pos[0]+1,pos[1],pos[2])

        extra = ""
        if self.lastDirection == direction:
            extra = "another "
        character.addMessage("move "+extra+"one tile to the "+direction)
        self.lastDirection = direction
        quest = src.quests.questMap["GoToTileStory"](description="go one tile to the "+direction,targetPosition=targetPos,showCoordinates=False,direction=direction)
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        quest.generatePath(character)
        quest.generateSubquests(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if character.getBigPosition() == (7,6,0):
            for quest in self.subQuests:
                quest.postHandler()
            self.postHandler()
            return None
        return False

    def handleMovement(self, extraInfo):
        if not self.active:
            return
        if self.completed:
            1/0

        if self.triggerCompletionCheck(self.character):
            return
        self.generateSubquests(extraInfo[0])

    def handleTileChange(self):
        if not self.active:
            return
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

src.quests.addType(ReachBase)

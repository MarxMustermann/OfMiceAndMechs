import src


class EscapeLab(src.quests.MetaQuestSequence):
    type = "EscapeLab"

    def __init__(self, description="escape lab", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description


    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.yPosition == 0:
            return (None,("w","leave room"))
        if character.yPosition%15 == 14:
            return (None,("w","leave room"))
        if not character.container.isRoom:
            return (None,("w","leave room"))
        if character.yPosition%15 == 14:
            return (None,("w","leave room"))

        quest = src.quests.questMap["GoToPosition"](targetPosition=(6,0,0),reason="reach the door",description="reach the door")
        return ([quest],None)


    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = True
        door.blocked = False

        return ["""
You reach out to your implant and it answers:
It whispers, but you understand clearly:

Something has gone wrong.
This room is not a safe place to stay.

So get moving and leave this room.
Use the wasd movement keys to move.
Pass through the door (""",door.render(),""") in the north.



Right now you are looking at the quest menu.
Detailed instructions are shown here.
For now ignore the options below and press esc to continue.

"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
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

        for room in character.getTerrain().rooms:
            if not room.tag == "sternslab":
                continue
            return False

        if character.yPosition%15 in (0,14):
            return False

        self.postHandler()

src.quests.addType(EscapeLab)

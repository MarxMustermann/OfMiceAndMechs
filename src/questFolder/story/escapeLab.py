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

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if submenue.tag == "configurationSelection":
                return (None,("x","unblock door"))
            return (None,(["esc",],"to close the menu"))

        if character.yPosition == 0:
            return (None,("w","leave room"))
        if character.yPosition%15 == 14:
            return (None,("w","leave room"))
        if not character.container.isRoom:
            return (None,("w","gain distance to room"))

        if not character.getPosition() == (6,1,0):
            quest = src.quests.questMap["GoToPosition"](targetPosition=(6,1,0),reason="reach the door",description="reach the door")
            return ([quest],None)
        
        if not character.container.getPositionWalkable((6,0,0)):
            configuration_command = "C"
            if "advancedConfigure" in character.interactionState:
                configuration_command = ""
            command = configuration_command + "wx"
            return (None,(command,"open door"))

        return (None,("w","step through door"))

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = False
        door.blocked = False

        text = []
        text.extend(["""
You reach out to your implant and it answers:
It whispers, but you understand clearly:

Something has gone wrong.
This room is not a safe place to stay.

So get moving and leave this room.
Pass through the door (""",door.render(),""") in the north.
"""])

        text.append("""
The Door needs to be opened before you can pass through it.
How to move and open the Door will be shown as suggested action.

Typing the shown characters there should complete the quest.
Use this as tutorial and hint function.
Uppercase letters are shown in a light grey.
""")

        text.append("""
Right now you are looking at the quest menu.
Detailed instructions are shown here.
For now ignore the options below and press esc to continue.

""")

        return text

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

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        for room in character.getTerrain().rooms:
            if not room.tag == "sternslab":
                continue
            return False

        if character.yPosition%15 in (0,14):
            return False

        if not dryRun:
            self.postHandler()
        return True

src.quests.addType(EscapeLab)

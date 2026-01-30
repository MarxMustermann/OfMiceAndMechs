import src


class EscapeLab(src.quests.MetaQuestSequence):
    type = "EscapeLab"

    def __init__(self, description="escape lab", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.lookedAtDoor = False
        self.shownGoToDoor = False

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not self.shownGoToDoor:
            submenue = character.macroState["submenue"]
            if submenue and not ignoreCommands:
                if isinstance(submenue,src.menuFolder.observeMenu.ObserveMenu):
                    if submenue.index[0] < 6:
                        return (None,("d","move cursor east"))
                    if submenue.index[0] > 6:
                        return (None,("a","move cursor west"))
                    if submenue.index[1] > 0:
                        return (None,("w","move cursor north"))
                return (None,(["esc",],"close the menu"))
            if not self.lookedAtDoor:
                return (None,("o","open observe menu"))

        if not self.shownGoToDoor and not character.macroState.get("submenue"):
            if not dryRun:
                self.character.showTextMenu("""
Now that you found the Door, exit the room before it explodes.

The instructions on how to do this will be shown on the left side on the screen.
Keep in mind that capital letters have to be pressed as shift+letter.
Cappital letters will be shown in blueish tint.

For example:

if the suggested action is "C w x":

    press shift+c then
    press w then
    press x
""")
                self.shownGoToDoor = True
                return (None,("~","reach out to implant"))

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if submenue.tag == "configurationSelection":
                return (None,("x","unblock door"))
            return (None,(["esc",],"close the menu"))

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


This room is exploding! We need to leave fast.

Look for the door first then move.

Instructions to do that will be shown on the left of the screen as "suggested action"

"""])
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.lookedAt, "lookedAt")
        super().assignToCharacter(character)

    def lookedAt(self, extraInfo):
        if extraInfo["index"] == (6,0,0) and extraInfo["index_big"] == (6,10,0):
            if not self.lookedAtDoor:
                self.lookedAtDoor = True
                self.character.addMessage("You found the Door. Close the menu now")

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

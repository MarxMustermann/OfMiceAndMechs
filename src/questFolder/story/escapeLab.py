import src


class EscapeLab(src.quests.MetaQuestSequence):
    type = "EscapeLab"

    def __init__(self, description="escape lab", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
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
                    command = ""
                    command += "D"*(6-submenue.index_big[0])
                    command += "A"*(submenue.index_big[0]-6)
                    command += "W"*(submenue.index_big[1]-10)
                    command += "S"*(10-submenue.index_big[1])
                    command += "d"*(6-submenue.index[0])
                    command += "a"*(submenue.index[0]-6)
                    command += "w"*(submenue.index[1]-0)
                    command += "s"*(0-submenue.index[1])
                    if command != "":
                        return (None,(command,"move cursor to door"))
                return (None,(["esc",],"close the menu"))

        if character.yPosition == 0:
            return (None,("w","leave room"))
        if character.yPosition%15 == 14:
            return (None,("w","leave room"))
        if not character.container.isRoom:
            return (None,("w","gain distance to room"))

        if not character.getPosition() == (6,1,0):
            quest = src.quests.questMap["GoToPosition"](targetPosition=(6,1,0),reason="reach the door",description="reach the door",targetName="Door")
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
        text.append("""
You reach out to your implant and it answers:


This room is exploding! We need to leave fast.
""")

        text.append((src.interaction.urwid.AttrSpec("#ff2","#000"),"""

Instructions to do that will be shown on the left of the screen as "suggested action"

"""))
        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        src.interaction.send_tracking_ping("assigned_quest_EscapeLab")
        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        self.startWatching(character,self.lookedAt, "lookedAt")
        super().assignToCharacter(character)

    def lookedAt(self, extraInfo):
        """
        if extraInfo["index"] == (6,0,0) and extraInfo["index_big"] == (6,10,0):
            if not self.lookedAtDoor:
                self.lookedAtDoor = True
                self.character.addMessage("You found the Door. Close the menu now")
        """

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0],dryRun=False)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.container.isRoom and character.container.tag == "the architects tomb":
            return False

        if character.yPosition%15 in (0,14):
            return False

        if not dryRun:
            self.postHandler()
        return True

src.quests.addType(EscapeLab)

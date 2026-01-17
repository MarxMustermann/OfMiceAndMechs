import src


class ActivateGlassStatue(src.quests.MetaQuestSequence):
    type = "ActivateGlassStatue"

    def __init__(self, description="activate glass statue", creator=None, targetPosition=None, targetPositionBig=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig

    def handleActivatedGlassStatue(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def handleStatueUsed(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleStatueUsed, "glass statue used")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.rank != 1:
            return False

        if not dryRun:
            self.postHandler()
        return True

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        # handle menues
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:

            # do the teleport
            if submenue.tag == "applyOptionSelection":
                command = submenue.get_command_to_select_option("teleport")
                if command:
                    return (None,(command,"teleport to dungeon"))

            # close unknown menues
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # activate production item when marked
        if character.macroState.get("itemMarkedLast"):
            item = character.macroState["itemMarkedLast"]
            if item.type == "GlassStatue":
                return (None,("j","activate GlassStatue"))
            else:
                return (None,(".","undo selection"))

        # go to glass statue
        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to the temple",reason="reach the GlassStatue")
            return ([quest],None)
        if character.getDistance(self.targetPosition) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,description="go to the GlassStatue",reason="be able to activae the GlassStatue")
            return ([quest],None)

        # activate the glass statue
        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            direction = "s"
        interactionCommand = "J"
        if submenue:
            if submenue.tag == "advancedInteractionSelection":
                interactionCommand = ""
            else:
                return (None,(["esc"],"close menu"))
        return (None,(interactionCommand+direction,"activate the GlassStatue"))

    def generateTextDescription(self):
        reason_string = ""
        if self.reason:
            reason_string = f", to {self.reason}"
        text = [f"""
Activate a GlassStatue{reason_string}.

The GlassStatues are connected to the heart of their god.
Use the GlassStatue to be teleported to the dungeon the heart is in.

Expect combat after the teleport.
"""]
        return text


src.quests.addType(ActivateGlassStatue)

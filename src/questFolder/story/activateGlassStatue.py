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

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.rank != 1:
            return False

        self.postHandler()

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]

            targetIndex = 0
            for option in submenue.options.values():
                if option == "teleport":
                    break
                targetIndex += 1
            else:
                return (None,(["esc"],"close menu"))

            targetIndex = 4
            offset = targetIndex-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += "j"
            return (None,(command,"teleport to dungeon"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))

        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break

        if character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to the temple",reason="to reach the GlassStatue")
            return ([quest],None)

        if character.getDistance(self.targetPosition) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,description="go to the GlassStatue",reason="be able to activae the GlassStatue")
            return ([quest],None)

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
        if "advancedInteraction" in character.interactionState:
            interactionCommand = ""
        return (None,(interactionCommand+direction+"sssj","activate the GlassStatue"))

    def generateTextDescription(self):
        text = ["""
The GlassStatues are connected to the heart of their god. 
Use the GlassStatue to be teleported to the dungeon the heart is in.

Expect combat after the teleport.
"""]
        return text


src.quests.addType(ActivateGlassStatue)

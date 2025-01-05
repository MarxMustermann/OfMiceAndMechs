import src


class ActivateRegenerator(src.quests.MetaQuestSequence):
    type = "ActivateRegenerator"

    def __init__(self, description="activate the regenerator", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.regenerator = None
    def handleRegeneratorActivated(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleRegeneratorActivated, "regenerator activated")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.regenerator and self.regenerator.activated:
            self.postHandler()
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)
        
        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to close menu"))
        
        if not self.regenerator:
            terrain = character.getTerrain()
            for room in terrain.rooms:
                self.regenerator = room.getItemByType("Regenerator",needsBolted=True)
                if self.regenerator:
                    break

        if character.getBigPosition() != self.regenerator.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=self.regenerator.container.getPosition(),description="go to the temple",reason="to reach the regenerator")
            return ([quest],None)

        if character.getDistance(self.regenerator.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.regenerator.getPosition(),ignoreEndBlocked=True,description="go to the Regenerator",reason="to activate the regenerator")
            return ([quest],None)
        
        t_pos = self.regenerator.getPosition()
        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == t_pos:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == t_pos:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == t_pos:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == t_pos:
            direction = "s"

        interactionCommand = "J"
        if "advancedInteraction" in character.interactionState:
            interactionCommand = ""
        return (None,(interactionCommand+direction,"activate the Regenerator"))

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

The base has some clones now and there are many enemies to be slain.
There will be fights and somebody will get hurt
Time will heal wounds, but that can be sped up.

The base has a Regenerator. It is located in the temple.
It will heal all nearby creatures faster.
Activate it so you and the other clones heal while waiting in the temple.
"""]
        return text


src.quests.addType(ActivateRegenerator)

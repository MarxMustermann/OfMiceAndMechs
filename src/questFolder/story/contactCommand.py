import src

class ContactCommand(src.quests.MetaQuestSequence):
    type = "ContactCommand"

    def __init__(self, description="contact command", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.getBigPosition() == (7,7,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="reach the communicator",description="go to command centre")
            return ([quest],None)

        if not character.container.isRoom:
            return (None,None)

        communicator = character.container.getItemByType("Communicator")
        if not communicator:
            self.fail(reason="no communicator found")
            return (None,None)

        itemPos = communicator.getPosition()
        if character.getDistance(itemPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=communicator.getPosition(),reason="to be able to use the communicator",description="go to communicator",ignoreEndBlocked=True)
            return ([quest],None)

        direction = ""
        if character.getPosition(offset=(1,0,0)) == itemPos:
            direction = "d"
        if character.getPosition(offset=(-1,0,0)) == itemPos:
            direction = "a"
        if character.getPosition(offset=(0,1,0)) == itemPos:
            direction = "s"
        if character.getPosition(offset=(0,-1,0)) == itemPos:
            direction = "w"

        return (None,(direction+"jj","activate communicator"))

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

The base is secure from immediate dangers.
Comtact the bases leader to get further instrucions.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handePermissionDenied, "permission denied")
        super().assignToCharacter(character)

    def handePermissionDenied(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        return False

src.quests.addType(ContactCommand)

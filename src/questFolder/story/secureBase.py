import src


class SecureBase(src.quests.MetaQuestSequenceV2):
    type = "SecureBase"

    def __init__(self, description="secure base", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.getBigPosition() == (5,7,0):
            quest = src.quests.questMap["CrossTrapRoom"](targetPosition=(6,7,0),reason="cross trap room",description="cross trap room")
            return ([quest],None)
        if character.getBigPosition() == (6,7,0):
            if not character.armor or not character.weapon:
                quest = src.quests.questMap["GetCombatReady"](reason="get combat ready",description="get combat ready")
                return ([quest],None)
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="reach the main room",description="reach the main room",paranoid=True)
            return ([quest],None)
        if character.getBigPosition() == (7,7,0):
            if not character.container.isRoom:
                return (None,("d","to enter the room"))
            if character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"](description="kill the last enemy")
                return ([quest],None)
            return (None,None)
        quest = src.quests.questMap["GoToTileStory"](targetPosition=(5,7,0),reason="reach the base entrance",description="reach the base entrance")
        return ([quest],None)

    def generateTextDescription(self):
        door = src.items.itemMap["Door"]()
        door.open = True
        door.walkable = True
        door.blocked = False

        text = ["""
You reach out to your implant and it answers.

The meltdown of the lab woke the insects.
It will take some time for them to start hunting you, but you should get to safety.

There is an old base nearby that should have some defences.
Enter the base and secure it.


This will be a bit more complicated than the last quests.
To make things easier this quest splits into subquests.

"""]
        if not self.subQuests:
            text.append("press + to generate a sub quest") 
        else:
            text.append("press d to view sub quest")
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

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if not character.getBigPosition() == (7,7,0):
            return False

        if not character.container.isRoom:
            return False

        if character.getNearbyEnemies():
            return False

        self.postHandler()

src.quests.addType(SecureBase)

import src
import random

class StoryReachTeleporterRoom(src.quests.MetaQuestSequence):
    type = "StoryReachTeleporterRoom"

    def __init__(self, description="reach the teleporter room", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        if character.macroState.get("submenue"):
            submenue = character.macroState.get("submenue")
            if isinstance(submenue,src.menuFolder.selectionMenu.SelectionMenu):
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == "contact main base":
                            foundOption = True
                            break
                        counter += 1
                    rewardIndex = counter

                if not foundOption:
                    return (None,(["esc"],"to close menu"))

                offset = rewardIndex-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += "j"
                return (None,(command,"contact command"))
            
            return (None,(["esc"],"close the menu"))

        if character.macroState.get("itemMarkedLast"):
            if character.macroState["itemMarkedLast"].type == "Communicator":
                return (None,("j","activate communicator"))
            else:
                return (None,(".","undo selection"))

        target_pos = None
        if character.getBigPosition() == (7,5,0):
            target_pos = (7,6,0)
        if character.getBigPosition() == (7,6,0):
            target_pos = random.choice([(6,6,0),(8,6,0)])
        if character.getBigPosition() == (6,6,0):
            target_pos = (6,7,0)
        if character.getBigPosition() == (6,7,0):
            target_pos = (6,8,0)
        if character.getBigPosition() == (8,6,0):
            target_pos = (8,7,0)
        if character.getBigPosition() == (8,7,0):
            target_pos = (8,8,0)
        if target_pos:
            if terrain.getEnemiesOnTile(character,target_pos):
                quest = src.quests.questMap["SecureTile"](toSecure=target_pos,reason="be able to leave",description="search for teleporter",endWhenCleared=True)
            else:
                quest = src.quests.questMap["GoToTile"](targetPosition=target_pos)
            return ([quest],None)

        if not character.getBigPosition() == (7,8,0):
            quest = src.quests.questMap["GoToTile"](targetPosition=(7,8,0),reason="go to the teleporter room",description="go to teleporter room")
            return ([quest],None)

        if not dryRun:
            self.postHandler()
        return (None,("+","complete quest"))

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

There is no base leader. This means this base got abandoned by main command.
Comtact main command to get reregistered as colony.
"""]

    def handleEnteredRoom(self, extraInfo):
        if extraInfo[1].getPosition() == (7,8,0):
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleEnteredRoom, "entered room")
        super().assignToCharacter(character)

    def handePermissionDenied(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def handleNoMainBase(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.getBigPosition() == (7,8,0):
            if not dryRun:
                self.postHandler()
            return True
        return False

src.quests.addType(StoryReachTeleporterRoom)

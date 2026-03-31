import src
import random

class StoryTeleport(src.quests.MetaQuestSequence):
    type = "StoryTeleport"

    def __init__(self, description="leave the mausoleum", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
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
            return (None,(["esc"],"close the menu"))

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("PersonnelTeleporter",))
        if action:
            return action

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

        if not character.container.isRoom:
            return (None,(".","stand around confused"))

        personnelTeleporter = character.container.getItemByType("PersonnelTeleporter")
        if not personnelTeleporter:
            return self._solver_trigger_fail(dryRun,"no teleporter found")

        itemPos = personnelTeleporter.getPosition()
        if character.getDistance(itemPos) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=personnelTeleporter.getPosition(),reason="to be able to use the teleporter",description="go to teleporter",ignoreEndBlocked=True)
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

        return (None,(direction+"j","activate teleporter"))

    def generateTextDescription(self):
        return ["""
You can use the Teleporter to get out of here.
The teleporter is in room (7,8,0).
Use it to leave the mausoleum.
"""]

    def handleTeleported(self, character):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handePermissionDenied, "permission denied")
        self.startWatching(character,self.handleNoMainBase, "no main base")
        self.startWatching(character,self.handleTeleported, "teleported")
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
        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "Communicator":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(StoryTeleport)

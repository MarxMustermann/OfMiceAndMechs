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
        rooms = terrain.getRoomByPosition((7,8,0))
        if not rooms:
            return self._solver_trigger_fail(dryRun,"target room gone")
        personnelTeleporter = character.container.getItemByType("PersonnelTeleporter")
        if not personnelTeleporter:
            return self._solver_trigger_fail(dryRun,"no teleporter found")

        quest = src.quests.questMap["ActivateItem"](targetPosition=personnelTeleporter.getPosition(),targetPositionBig=personnelTeleporter.getBigPosition(),reason="teleport",targetItemType="PersonnelTeleporter")
        return ([quest],None)

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

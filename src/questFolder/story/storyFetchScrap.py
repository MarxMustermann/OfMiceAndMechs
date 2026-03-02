import src
import random

class StoryFetchScrap(src.quests.MetaQuestSequence):
    type = "StoryFetchScrap"

    def __init__(self, description="fetch scrap", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
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
        rooms = terrain.getRoomByPosition((7,6,0))

        if rooms:
            hub_room = rooms[0]
            items = hub_room.getItemsByType("Scrap")
            random.shuffle(items)

            if items:
                item = items[0]
                quest = src.quests.questMap["CleanSpace"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="gather some scrap")
                return ([quest],None)
        quest = src.quests.questMap["GatherScrap"]()
        return ([quest],None)

    def generateTextDescription(self):
        return ["""
Find Scrap. 

If you don't find Scrap in the room, collect some from the exploded room.
"""]

    def pickedUpItem(self, extra_parameter):
        item = extra_parameter[1]

        if item.type == "Scrap":
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        if self.character.searchInventory("Scrap"):
            return True
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

src.quests.addType(StoryFetchScrap)

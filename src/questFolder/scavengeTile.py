import src
import random

class ScavengeTile(src.quests.MetaQuestSequence):
    type = "ScavengeTile"

    def __init__(self, description="scavenge tile", creator=None, targetPosition=None,toCollect=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description+" "+str(targetPosition)
        self.baseDescription = description
        self.toCollect = toCollect

        self.targetPosition = targetPosition

    def triggerCompletionCheck(self,character=None):

        if not character:
            return

        if not self.getLeftoverItems(character):
            self.postHandler()
            return

        return

    def solver(self, character):
        self.triggerCompletionCheck(character=character)

        if not self.subQuests:
            if not character.getFreeInventorySpace() > 0:
                quest = src.quests.questMap["ClearInventory"]()
                self.addQuest(quest)
                return

            if not (character.getBigPosition() == (self.targetPosition[0],self.targetPosition[1],0)):
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPosition)
                self.addQuest(quest)
                return

            items = self.getLeftoverItems(character)
            if items:

                item = random.choice(items)

                quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=self.targetPosition)
                self.addQuest(quest)
                return

        super().solver(character)

    def getLeftoverItems(self,character):
        terrain = character.getTerrain()
        leftOverItems = []
        items = terrain.itemsByBigCoordinate.get(self.targetPosition,[])
        for item in items:
            #if item.type == "Scrap":
            #    continue
            if self.toCollect and not item.type == self.toCollect:
                continue
            if item.bolted:
                continue

            leftOverItems.append(item)
        return leftOverItems

    def pickedUpItem(self,extraInfo):
        self.triggerCompletionCheck(extraInfo[0])

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.pickedUpItem, "itemPickedUp")
        return super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)

        if renderForTile:
            if character.getBigPosition() == self.targetPosition:
                for item in character.getTerrain().itemsByBigCoordinate.get(self.targetPosition,[]):
                    if self.toCollect and not item.type == self.toCollect:
                        continue
                    result.append((item.getPosition(),"target"))

        return result

src.quests.addType(ScavengeTile)

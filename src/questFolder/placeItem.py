import src
import random

class PlaceItem(src.quests.MetaQuestSequence):
    type = "PlaceItem"

    def __init__(self, description="place item", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, itemType=None, tryHard=False, boltDown=False):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = "%s %s on position %s on tile %s"%(description,itemType,targetPosition,targetPositionBig,)
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.boltDown = boltDown

    def generateTextDescription(self):
        text = """
place item %s on position %s on tile %s."""%(self.itemType,self.targetPosition,self.targetPositionBig,)
        if self.boltDown:
            text += """
Bolt down the item afterwards."""
        
        if self.tryHard:
            text += """

Try as hard as you can to achieve this.
If you don't find the items to place, produce them.
"""

        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.droppedItem, "dropped")
        self.startWatching(character, self.producedItem, "producedItem")
        super().assignToCharacter(character)

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        return result


    def producedItem(self,extraInfo):
        print(extraInfo)
        item = extraInfo["item"]
        self.checkPlacedItem(item)

    def droppedItem(self,extraInfo):
        item = extraInfo[1]
        self.checkPlacedItem(item)

    def checkPlacedItem(self,item):
        if item.type == self.itemType:
            if item.container.isRoom:
                if item.container.getPosition() == self.targetPositionBig and item.getPosition() == self.targetPosition:
                    self.postHandler()
            else:
                if item.getPosition() == (self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0):
                    self.postHandler()

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            itemFound = None
            for item in character.inventory:
                if item.type == self.itemType:
                    itemFound = item
                    break

            if not itemFound:
                quest = src.quests.questMap["FetchItems"](toCollect=self.itemType,amount=1,takeAnyUnbolted=True,tryHard=self.tryHard)
                return ([quest],None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite")
                return ([quest],None)

            if not character.getSpacePosition() == self.targetPosition:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,description="go to placement spot")
                return ([quest],None)

            if self.boltDown:
                return (None,"lcb")
            else:
                return (None,"l")
        return (None,None)
    
    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            items = character.getTerrain().getItemByPosition((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0))
        else:
            items = rooms[0].getItemByPosition(self.targetPosition)

        if not items:
            return False

        if items[-1].type == self.itemType:
            self.postHandler()
            return True
        return False


src.quests.addType(PlaceItem)

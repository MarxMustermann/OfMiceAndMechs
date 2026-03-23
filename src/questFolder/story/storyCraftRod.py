import src
import random

class StoryCraftRod(src.quests.MetaQuestSequence):
    type = "StoryCraftRod"

    def __init__(self, description="craft a rod", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
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

        rooms = terrain.getRoomByPosition((8,4,0))
        if not rooms:
            return self._solver_trigger_fail(dryRun,"crafting room gone")
        crafting_room = rooms[0]
        
        if character.searchInventory("Rod"):
            quest = src.quests.questMap["ConsumeItem"](itemType="Rod",description="equip Rod",consumeVerb="equip")
            return ([quest],None)

        if terrain.getEnemiesOnTile(character,(8,4,0)):
            quest = src.quests.questMap["SecureTile"](toSecure=(8,4,0),description="secure crafting room",reason="be able to carft",endWhenCleared=True)
            return ([quest],None)

        rods = crafting_room.getItemsByType("Rod")
        if rods:
            rod = rods[0]
            quest = src.quests.questMap["CleanSpace"](targetPosition=rod.getPosition(), targetPositionBig=rod.getBigPosition())
            return ([quest],None)

        for manufacturingTable in crafting_room.getItemsByType("ManufacturingTable"):
            if manufacturingTable.toProduce != "Rod":
                continue
            if not manufacturingTable.readyToUse():
                if character.searchInventory("MetalBars"):
                    quest = src.quests.questMap["PlaceItem"](targetPosition=manufacturingTable.getPosition(offset=(-1,0,0)), targetPositionBig=manufacturingTable.getBigPosition(), itemType="MetalBars")
                    return ([quest],None)
                continue
            if not character.getBigPosition() == manufacturingTable.getBigPosition():
                quest = src.quests.questMap["GoToTile"](targetPosition=manufacturingTable.getBigPosition())
                return ([quest],None)
            if not character.getPosition() == manufacturingTable.getPosition(offset=(0,1,0)):
                quest = src.quests.questMap["GoToPosition"](targetPosition=manufacturingTable.getPosition(offset=(0,1,0)))
                return ([quest],None)
            quest = src.quests.questMap["Manufacture"](targetPosition=manufacturingTable.getPosition(), targetPositionBig=manufacturingTable.getBigPosition())
            return ([quest],None)


        metalBars = crafting_room.getItemsByType("MetalBars")
        if metalBars:
            metalBar = metalBars[0]
            quest = src.quests.questMap["CleanSpace"](targetPosition=metalBar.getPosition(), targetPositionBig=metalBar.getBigPosition())
            return ([quest],None)

        for scrapCompactor in crafting_room.getItemsByType("ScrapCompactor"):
            if not scrapCompactor.readyToUse():
                continue
            if not character.getBigPosition() == scrapCompactor.getBigPosition():
                quest = src.quests.questMap["GoToTile"](targetPosition=scrapCompactor.getBigPosition())
                return ([quest],None)
            if not character.getPosition() == scrapCompactor.getPosition(offset=(0,-1,0)):
                quest = src.quests.questMap["GoToPosition"](targetPosition=scrapCompactor.getPosition(offset=(0,-1,0)))
                return ([quest],None)
            quest = src.quests.questMap["OperateMachine"](targetPosition=scrapCompactor.getPosition(), targetPositionBig=scrapCompactor.getBigPosition())
            return ([quest],None)

        items_out = crafting_room.getItemByPosition((5,11,0))
        if items_out:
            quest = src.quests.questMap["CleanSpace"](targetPosition=(5,11,0), targetPositionBig=(8,4,0))
            return ([quest],None)
        items_in = crafting_room.getItemByPosition((2,11,0))
        if not items_in: 
            if character.searchInventory("Scrap"):
                quest = src.quests.questMap["PlaceItem"](targetPosition=(3,11,0), targetPositionBig=(8,4,0), itemType="Scrap")
                return ([quest],None)

            quest = src.quests.questMap["StoryFetchScrap"]()
            return ([quest],None)
        quest = src.quests.questMap["CleanSpace"](targetPosition=(2,11,0), targetPositionBig=(8,4,0))
        return ([quest],None)


    def generateTextDescription(self):
        return ["""
Craft a Rod by:

* collecting Scrap
* putting the Scrap next to a scrap compactor
* producing a Metal by with the scrap compactor
* place the MetalBars at the ManufacturingTable for Rod
* produce the Rod
* equip the Rod
"""]

    def handleEquiped(self, extraParameter):
        if extraParameter[1].type in ("Rod","Sword",) and extraParameter[0] == self.character:
            self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleEquiped, "equipedItem")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        if character.weapon:
            if not dryRun:
                self.postHandler()
            return True
        return False

src.quests.addType(StoryCraftRod)

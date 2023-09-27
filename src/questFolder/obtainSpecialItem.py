import src

class ObtainSpecialItem(src.quests.MetaQuestSequence):
    type = "ObtainSpecialItem"

    def __init__(self, description="obtain special item", creator=None, targetTerrain=None, itemId=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetTerrain = targetTerrain
        self.itemId = itemId

    def generateTextDescription(self):
        return f"""
obtain the special item #{self.itemId} from the base on {self.targetTerrain}
"""

    def triggerCompletionCheck(self,character=None):
        return False

    def getSolvingCommandString(self,character=None,dryRun=True):
        if character == None:
            return

        if len(self.targetTerrain) < 3:
            self.targetTerrain = (self.targetTerrain[0],self.targetTerrain[1],0)
        if character.getTerrainPosition() != self.targetTerrain:
            return

        temple = None
        for room in character.getTerrain().rooms:
            if not isinstance(room,src.rooms.TempleRoom):
                continue
            temple = room
            break

        if temple.getPosition() != character.getBigPosition():
            return

        if temple != character.container:
            if character.xPosition%15 == 0:
                return "d"
            if character.xPosition%15 == 14:
                return "a"
            if character.yPosition%15 == 0:
                return "s"
            if character.yPosition%15 == 14:
                return "w"
            return

        for item in character.container.itemsOnFloor:
            if isinstance(item,src.items.itemMap["SpecialItem"]):
                if item.getPosition() != character.getPosition():
                    return
                return "k"
            if isinstance(item,src.items.itemMap["SpecialItemSlot"]):
                if item.itemID == self.itemId and item.hasItem:
                    if item.getPosition() != character.getPosition():
                        return
                    return "j"
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character=None):
        if character == None:
            return

        foundSpecialItem = False
        for item in character.inventory:
            if not isinstance(item, src.items.itemMap["SpecialItem"]):
                continue
            if item.itemID != self.itemId:
                continue
            foundSpecialItem = True

        if not foundSpecialItem:
            if len(self.targetTerrain) < 3:
                self.targetTerrain = (self.targetTerrain[0],self.targetTerrain[1],0)
            if character.getTerrainPosition() != self.targetTerrain:
                self.addQuest(src.quests.questMap["GoToTerrain"](targetTerrain=self.targetTerrain))
                return

            temple = None
            for room in character.getTerrain().rooms:
                if not isinstance(room,src.rooms.TempleRoom):
                    continue
                temple = room
                break

            if temple.getPosition() != character.getBigPosition():
                self.addQuest(src.quests.questMap["GoToTile"](targetPosition=temple.getPosition()))
                return

            if temple != character.container:
                return

            for item in character.container.itemsOnFloor:
                if isinstance(item,src.items.itemMap["SpecialItem"]):
                    if item.getPosition() != character.getPosition():
                        self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition()))
                        return
                    return
                if isinstance(item,src.items.itemMap["SpecialItemSlot"]):
                    if item.itemID == self.itemId and item.hasItem:
                        if item.getPosition() != character.getPosition():
                            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=item.getPosition()))
                            return
                        return
            return
        if foundSpecialItem:
            self.addQuest(src.quests.questMap["GoHome"]())
            return

    def solver(self, character):
        if not self.subQuests:
            self.generateSubquests(character)
            if self.subQuests:
                return
        command = self.getSolvingCommandString(character,dryRun=False)
        if command:
            character.runCommandString(command)
            return
        super().solver(character)

src.quests.addType(ObtainSpecialItem)

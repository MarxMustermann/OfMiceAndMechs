import src


class ExtendBase(src.quests.MetaQuestSequence): 
    type = "ExtendBase"

    def __init__(self, description="set up base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        out = ""
        if len(self.character.getTerrain().rooms) == 1:
            out += """
Your base is currently only the city core.
This is the room you started in.

To set up the base you need to build more rooms.
There should be some walls (XX), Doors ([]) and a few RoomBuilders (RB).
Start setting up the base using these materials.

Add the first room, to have space for some industry.
This has the nice side effect of freeing up space in the city core.
"""
        elif len(self.character.getTerrain().rooms) == 2:
            out += """
Your base has one additional room now.
This should give you some room to work with.
Set up a production line for walls and some basic infrastructure.

Use this to build another room.
"""
        elif len(self.character.getTerrain().rooms) == 3:
            out += """
Your base has 2 additional rooms now.
That is actually quite a lot of space.
Try to fill that space.

"""
        elif len(self.character.getTerrain().rooms) == 4:
            out += """
Your base has 3 additional rooms now. great.
Did you set food production already?

"""
        elif len(self.character.getTerrain().rooms) == 5:
            out += """
Almost done! Keep going

"""
        else:
            out += """
Extend the base further.

"""

        out +=  """
Build 6 rooms to complete this quest.
Build %s more rooms to achive that.
"""%(6-len(self.character.getTerrain().rooms),)

        if not self.subQuests:
            out += """
This quest has no subquests. Press r to generate subquests for this quest.
The subquests will guide you, but you don't have to follow them as long as the is getting extended."""
        else:
            out += """
Follow this quests sub quests. They will guide you and try to explain how to build a base.
Press d to move the cursor and show the subquests description.
Press a to move back to the main quest.
"""
        return out

    def roomBuildingFailed(self,extraParam):
        print(extraParam)
        3/0

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not character.getTerrain().getRoomByPosition((6,7,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(6,7,0),tryHard=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)

            rooms = character.getTerrain().getRoomByPosition((7,7,0))
            if not rooms:
                self.fail("command centre missing")
                return (None,None)
            room = rooms[0]

            foundInput1 = False
            foundInput2 = False
            for inputSlot in room.inputSlots:
                if inputSlot[0] == (7,4,0):
                    foundInput1 = True
                if inputSlot[0] == (4,7,0):
                    foundInput2 = True

            if not foundInput1:
                quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=(7,7,0),targetPosition=(7,4,0))
                return ([quest],None)

            items = room.getItemByPosition((8,4,0))
            if not items or not items[-1].type == "ScrapCompactor":
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(8,4,0),itemType="ScrapCompactor",tryHard=True,boltDown=True)
                return ([quest],None)

            if not foundInput2:
                quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=(7,7,0),targetPosition=(4,7,0))
                return ([quest],None)

            items = room.getItemByPosition((5,7,0))
            if not items or not items[-1].type == "ScrapCompactor":
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(5,7,0),itemType="ScrapCompactor",tryHard=True,boltDown=True)
                return ([quest],None)

            items = room.getItemByPosition((7,4,0))
            if not items or not items[-1].type == "Scrap":
                quest1 = src.quests.questMap["GatherScrap"]()
                quest2 = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap")
                return ([quest3,quest2,quest1],None)
            
            items = room.getItemByPosition((4,7,0))
            if not items or not items[-1].type == "Scrap":
                quest1 = src.quests.questMap["GatherScrap"]()
                quest2 = src.quests.questMap["GoToTile"](targetPosition=(7,7,0))
                quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap")
                return ([quest3,quest2,quest1],None)

            quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Wall",targetPositionBig=(6,7,0))
            self.startWatching(quest,self.roomBuildingFailed,"failed")
            return ([quest],None)

            if not character.getTerrain().getRoomByPosition((7,8,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(7,8,0),tryHard=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((8,7,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(8,7,0),tryHard=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((7,6,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(7,6,0),tryHard=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            if not character.getTerrain().getRoomByPosition((8,8,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(8,8,0),tryHard=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)
            90023/0
            90023/0
        
        return (None,None)

    def gotThirsty(self,extraParam=None):
        quest = src.quests.questMap["Eat"]()
        self.addQuest(quest)
        return
    
    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.gotThirsty, "thirst")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        return False
    
    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand)
            return
        super().solver(character)


src.quests.addType(ExtendBase)

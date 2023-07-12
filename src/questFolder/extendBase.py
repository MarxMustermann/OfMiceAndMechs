import src


class ExtendBase(src.quests.MetaQuestSequence): 
    type = "ExtendBase"

    def __init__(self, description="set up base", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

    def generateTextDescription(self):
        out = []
        if len(self.character.getTerrain().rooms) == 1:
            roomBuilder = src.items.itemMap["RoomBuilder"]()
            wall = src.items.itemMap["Wall"]()
            door = src.items.itemMap["Door"]()
            out.extend(["""
You remember that your task was to set up a base.
You know you are equiped for it, but you remember nothing more.
Follow that order and set up a base.

Your base is currently only the city core.
This is the room you started in.
To set up the base you need to build more rooms.

Use a RoomBuilder (""",roomBuilder.render(),""") to build a room.
The needed walls (""",wall.render(),""") and Doors (""",door.render(),""") should be in the city core.
Start setting up the base using these materials.

Add the first room, to have space for some industry.
This has the nice side effect of freeing up space in the city core.
"""])
        elif len(self.character.getTerrain().rooms) == 2:
            out.append("""
Your base has one additional room now.
This should give you some room to work with.
Set up a production line for walls and some basic infrastructure.

Use this to build another room.
""")
        elif len(self.character.getTerrain().rooms) == 3:
            out.append("""
Your base has 2 additional rooms now.
That is actually quite a lot of space.
Try to fill that space.

""")
        elif len(self.character.getTerrain().rooms) == 4:
            out.append("""
Your base has 3 additional rooms now. great.
Did you set food production already?

""")
        elif len(self.character.getTerrain().rooms) == 5:
            out.append("""
Almost done! Keep going

""")
        else:
            out.append("""
Extend the base further.

""")

        out.append("""
Build 6 rooms to complete this quest.
Build %s more rooms to achive that.
"""%(6-len(self.character.getTerrain().rooms),))

        if not self.subQuests:
            out.append((src.interaction.urwid.AttrSpec("#f00", "black"),"""
This quest has no subquests. Press r to generate subquests for this quest."""))
        else:
            out.append("""
This quests has subquests.
Follow this quests sub quests. They will guide you and try to explain how to build a base.
You do not have to follow the subquests as long as the base is getting set up.
Press d to move the cursor and show the subquests description.
""")
        return out

    def roomBuildingFailed(self,extraParam):
        3/0

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return nextStep[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))

            if not character.weapon:
                quest = src.quests.questMap["Equip"](weaponOnly=True)
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)

            if not character.getTerrain().getRoomByPosition((6,7,0)):
                quest = src.quests.questMap["BuildRoom"](targetPosition=(6,7,0),tryHard=True,reason="extend the base")
                self.startWatching(quest,self.roomBuildingFailed,"failed")
                return ([quest],None)

            rooms = character.getTerrain().getRoomByPosition((7,7,0))
            if not rooms:
                self.fail("command centre missing")
                return (None,None)
            room = rooms[0]

            npcs = []
            npcs.extend(character.getTerrain().characters)
            for checkRoom in character.getTerrain().rooms:
                npcs.extend(checkRoom.characters)
            for npc in npcs:
                if npc == character:
                    continue
                if not npc.faction == character.faction:
                    continue
                quest = src.quests.questMap["ReduceFoodConsumption"](reason="prevent starvation")
                return ([quest],None)

            for checkRoom in character.getTerrain().rooms:
                for item in checkRoom.itemsOnFloor:
                    if not item.type in ("Corpse","GooFlask"):
                        continue

                    inStorage = False
                    for storageSlot in checkRoom.storageSlots:
                        if not storageSlot[0] == item.getPosition():
                            continue
                        inStorage = True

                    if inStorage:
                        continue
                            
                    quest1 = src.quests.questMap["CleanSpace"](targetPosition=item.getPosition(),targetPositionBig=checkRoom.getPosition(),reason="pick up valuables")
                    quest2 = src.quests.questMap["ClearInventory"](reason="store the valuables")
                    return ([quest2,quest1], None)

            if character.flask and character.flask.uses < 8:
                quest = src.quests.questMap["FillFlask"]()
                return ([quest],None)

            foundInput1 = False
            for inputSlot in room.inputSlots:
                if inputSlot[0] == (7,4,0):
                    foundInput1 = True

            if not foundInput1:
                if room.getItemByPosition((7,4,0)):
                    quest = src.quests.questMap["CleanSpace"](targetPosition=(7,4,0),targetPositionBig=(7,7,0),reason="remove blocking item")
                    return ([quest],None)
                quest = src.quests.questMap["DrawStockpile"](tryHard=True,itemType="Scrap",stockpileType="i",targetPositionBig=(7,7,0),targetPosition=(7,4,0),reason="set up scrap supply infrastructure for the machine production")
                return ([quest],None)

            items = room.getItemByPosition((8,4,0))
            if not items or not items[-1].type == "ScrapCompactor":
                quest = src.quests.questMap["PlaceItem"](targetPositionBig=(7,7,0),targetPosition=(8,4,0),itemType="ScrapCompactor",tryHard=True,boltDown=True,reason="set up metal bar production for the machine production")
                return ([quest],None)

            for room in character.getTerrain().rooms:
                for inputSlot in room.inputSlots:
                    if inputSlot[1] == "Scrap":
                        items = room.getItemByPosition(inputSlot[0])
                        if not items or not items[-1].type == "Scrap":
                            quest1 = src.quests.questMap["GatherScrap"](reason="have Scrap to supply the city with")
                            quest2 = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),reason="get back to tile in need of Scrap")
                            quest3 = src.quests.questMap["RestockRoom"](toRestock="Scrap",reason="ensure scrap supply")
                            return ([quest3,quest2,quest1],None)
            
            foundCaseOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Case":
                        foundCaseOutput = True

            if not foundCaseOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Case",targetPositionBig=(6,7,0))
                return ([quest],None)

            foundWallOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Wall":
                        foundWallOutput = True

            if not foundWallOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Wall",targetPositionBig=(6,7,0))
                return ([quest],None)

            foundDoorOutput = False
            for room in character.getTerrain().rooms:
                for outputSlot in room.outputSlots:
                    if outputSlot[1] == "Door":
                        foundDoorOutput = True

            if not foundDoorOutput:
                quest = src.quests.questMap["SetUpProductionLine"](tryHard=True,itemType="Door",targetPositionBig=(6,7,0))
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
    
src.quests.addType(ExtendBase)

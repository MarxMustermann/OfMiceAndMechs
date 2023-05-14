import src

class DrawStockpile(src.quests.MetaQuestSequence):
    type = "DrawStockpile"

    def __init__(self, description="draw stockpile", creator=None, targetPosition=None, targetPositionBig=None,itemType=None,stockpileType=None,tryHard=False):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.stockpileType = stockpileType
        self.tryHard = tryHard
        self.painterPos = None

    def triggerCompletionCheck(self,character=None):
        if not character:
            return

    def generateTextDescription(self):
        text = """
draw a %s stockpile for %s on position %s on tile %s.

"""%(self.stockpileType,self.itemType,self.targetPosition,self.targetPositionBig,)

        text += """
Stockpiles are drawn using a Painter (xi).
Examine the Painter for more details.
"""

        if self.tryHard:
            text += """
Try as hard as you can to achieve this.
"""

        return text

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

    def getSolvingCommandString(self, character, dryRun=True):
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def getNextStep(self,character=None,ignoreCommands=False):
        try:
            self.painterPos
        except:
            self.painterPos = None
        if not self.subQuests:
            rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
            if not rooms:
                self.fail("target room missing")
                return (None,None)
            room = rooms[0]

            for inputSlot in room.inputSlots:
                print("inputSlot")
                print(inputSlot)
                if inputSlot[0] == self.targetPosition:
                    self.postHandler()
                    return (None,None)

            offsets = ((0,0,0),(0,1,0),(1,0,0),(0,-1,0),(-1,0,0))
            foundOffset = None
            for offset in offsets:
                items = room.getItemByPosition((self.targetPosition[0]+offset[0],self.targetPosition[1]+offset[1],self.targetPosition[2]+offset[2]))
                if not items or not items[-1].type == "Painter":
                    continue

                foundOffset = (offset,items[-1])
            if foundOffset:
                if character.getDistance(self.targetPosition) > 0:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition)
                    return ([quest],None)
                return (None,"jk")

            if not self.painterPos:
                if not character.inventory or not character.inventory[-1].type == "Painter":
                    quest = src.quests.questMap["FetchItems"](toCollect="Painter",amount=1)
                    return ([quest],None)
                painter = character.inventory[-1]

            if character.getDistance(self.targetPosition) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True)
                return ([quest],None)

                pass

            return (None,"l")

        return (None,None)

        self.activate()
        self.assignToCharacter(character)
        if self.subQuests:
            return super().solver(character)

        if not character.inventory or not character.inventory[-1].type == "Painter":
            character.addMessage("no painter")
            self.addQuest(src.quests.questMap["FetchItems"](toCollect="Painter",amount=1))
            return
        painter = character.inventory[-1]

        if not isinstance(character.container,src.rooms.Room):
            if character.xPosition%15 == 0:
                character.runCommandString("d")
            if character.xPosition%15 == 14:
                character.runCommandString("a")
            if character.yPosition%15 == 0:
                character.runCommandString("s")
            if character.yPosition%15 == 14:
                character.runCommandString("w")
            return


        if not character.container.floorPlan:
            self.fail()
            return

        if character.container.floorPlan.get("walkingSpace"):
            if not painter.paintMode == "walkingSpace":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmwalkingSpace\nk"))
                return

            walkingSpace = character.container.floorPlan["walkingSpace"].pop()

            if walkingSpace[0] == 0 or walkingSpace[0] == 12 or walkingSpace[1] == 0 or walkingSpace[1] == 12:
                return
            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=walkingSpace))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("inputSlots"):
            if not painter.paintMode == "inputSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcminputSlot\nk"))
                return

            inputSlot = character.container.floorPlan["inputSlots"][-1]

            if not painter.paintType == inputSlot[1]:
                self.addQuest(src.quest.questMap["RunCommand"](command="lct%s\nk"%(inputSlot[1],)))
                return

            character.container.floorPlan["inputSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=inputSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("outputSlots"):
            if not painter.paintMode == "outputSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmoutputSlot\nk"))
                return

            outputSlot = character.container.floorPlan["outputSlots"][-1]

            if not painter.paintType == outputSlot[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(outputSlot[1],)))
                return

            character.container.floorPlan["outputSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=outputSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("storageSlots"):
            if not painter.paintMode == "storageSlot":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmstorageSlot\nk"))
                return

            storageSlot = character.container.floorPlan["storageSlots"][-1]

            if not painter.paintType == storageSlot[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(storageSlot[1],)))
                return
            
            character.container.floorPlan["storageSlots"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=storageSlot[0]))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        if character.container.floorPlan.get("buildSites"):

            buildingSite = character.container.floorPlan["buildSites"][-1]

            character.container.floorPlan["buildSites"].pop()

            self.addQuest(src.quests.questMap["RunCommand"](command="ljk"))
            self.addQuest(src.quests.questMap["GoToPosition"](targetPosition=buildingSite[0]))

            for (key,value) in buildingSite[2].items():
                valueType = ""
                if key == "command":
                    value = "".join(value)

                if key == "commands":
                    value = json.dumps(value)
                    valueType = "json"

                if key == "settings":
                    value = json.dumps(value)
                    valueType = "json"


                if isinstance(value,int):
                    valueType = "int"

                self.addQuest(src.quests.questMap["RunCommand"](command="lce%s\n%s\n%s\nk"%(key,valueType,value)))

            if not painter.paintMode == "buildSite":
                self.addQuest(src.quests.questMap["RunCommand"](command="lcmbuildSite\nk"))

            if not painter.paintType == buildingSite[1]:
                self.addQuest(src.quests.questMap["RunCommand"](command="lct%s\nk"%(buildingSite[1],)))

            if painter.paintExtraInfo:
                self.addQuest(src.quests.questMap["RunCommand"](command="lcck"))

            return

        character.container.floorPlan = None
        self.postHandler()
        return

src.quests.addType(DrawStockpile)

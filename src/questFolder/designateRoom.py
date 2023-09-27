import src

class DesignateRoom(src.quests.MetaQuestSequence):
    type = "DesignateRoom"

    def __init__(self, description="designate room", creator=None, roomPosition=None, roomType="generalPurposeRoom", roomTag="",reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.roomType = roomType
        self.roomTag = roomTag
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"

        if self.roomType == "undesignate":
            out.append(f"""
Undesignate the room on coordinate {self.roomPosition}{reason}.
""")
        else:
            out.append(f"""
Designate the room on coordinate {self.roomPosition} as {self.roomType}{reason}.
""")

            if self.roomType == "generalPurposeRoom":
                out.append("""
This designation signals that this room can be used for temporary constructions.
This means every clone can use this room for anything.

It also means that any clone can take from that room,
so do not use it for permanent constructions.

""")
            if self.roomType == "specialPurposeRoom":
                out.append(f"""
This signals that this room is reserved for some kind of purpose.
This means no clone not involved should not change the room.

The rooms tag indicates the rooms purpose.
Set the rooms tag to: {self.roomTag}
""")

        out.append("""
Use the CityPlaner to designate the room.
""")

        out.append("""

(doing wrong designations may break the tutorial, but is FUN)
""")
        return out

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.MapMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            command = ""
            if submenue.cursor[0] > self.roomPosition[0]:
                command += "a"*(submenue.cursor[0]-self.roomPosition[0])
            if submenue.cursor[0] < self.roomPosition[0]:
                command += "d"*(self.roomPosition[0]-submenue.cursor[0])
            if submenue.cursor[1] > self.roomPosition[1]:
                command += "w"*(submenue.cursor[1]-self.roomPosition[1])
            if submenue.cursor[1] < self.roomPosition[1]:
                command += "s"*(self.roomPosition[1]-submenue.cursor[1])

            cityPlaner = character.container.getItemsByType("CityPlaner")[0]
            if self.roomPosition in cityPlaner.plannedRooms:
                command += "x"
                return (None,(command,"to remove old construction site marker"))

            if not self.roomPosition in cityPlaner.getAvailableRoomPositions():
                if not dryRun:
                    self.fail(reason="room position already taken")
                return (None,None)

            if self.roomType == "generalPurposeRoom":
                command += "g"
                return (None,(command,"to designate room as general pupose room"))
            if self.roomType == "specialPurposeRoom":
                command += "p"
                return (None,(command,"to designate room as special pupose room"))
            if self.roomType == "undesignate":
                command += "x"
                return (None,(command,"to undesignate room"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.InputMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.text == "":
                return (None,(list(self.roomTag),"to enter the rooms tag"))
            if submenue.text == self.roomTag:
                return (None,(["enter"],"to set the rooms tag"))

            correctIndex = 0
            while correctIndex < len(submenue.text) and correctIndex < len(self.roomTag):
                if submenue.text[correctIndex] != self.roomTag[correctIndex]:
                    break
                correctIndex += 1

            if correctIndex < len(submenue.text):
                return (None,(["backspace"]*(len(submenue.text)-correctIndex),"to delete spelling mistake"))

            if correctIndex < len(self.roomTag):
                return (None,((list(self.roomTag[correctIndex:])),"to enter the room tag"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            return (None,("j","to show the map"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to exit submenu"))

        pos = character.getBigPosition()

        if pos != (7, 7, 0):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            return ([quest],None)

        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        cityPlaner = character.container.getItemsByType("CityPlaner")[0]
        command = None
        if character.getPosition(offset=(1,0,0)) == cityPlaner.getPosition():
            command = "d"
        if character.getPosition(offset=(-1,0,0)) == cityPlaner.getPosition():
            command = "a"
        if character.getPosition(offset=(0,1,0)) == cityPlaner.getPosition():
            command = "s"
        if character.getPosition(offset=(0,-1,0)) == cityPlaner.getPosition():
            command = "w"
        if character.getPosition(offset=(0,0,0)) == cityPlaner.getPosition():
            command = "."

        if command:
            return (None,("J"+command,"to activate the CityPlaner"))

        quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(), description="go to CityPlaner",ignoreEndBlocked=True)
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        if not character:
            return

        terrain = character.getTerrain()
        room = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = room.getItemsByType("CityPlaner")[0]

        if self.roomType == "specialPurposeRoom":
            if self.roomPosition in cityPlaner.specialPurposeRooms:
                self.postHandler()
                return True

        if self.roomType == "generalPurposeRoom":
            if self.roomPosition in cityPlaner.generalPurposeRooms:
                self.postHandler()
                return True

        if self.roomType == "undesignate":
            if self.roomPosition in cityPlaner.generalPurposeRooms:
                return
            if self.roomPosition in cityPlaner.specialPurposeRooms:
                return
            self.postHandler()
            return True

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return

        (nextQuests,nextCommand) = self.getNextStep(character,dryRun=False)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def handleDesignatedRoom(self,extraParams):
        self.triggerCompletionCheck(extraParams["character"])

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.roomPosition[0],self.roomPosition[1]),"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleDesignatedRoom, "designated room")

        return super().assignToCharacter(character)

src.quests.addType(DesignateRoom)

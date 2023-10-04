import src


class ScheduleRoomBuilding(src.quests.MetaQuestSequence):
    type = "ScheduleRoomBuilding"

    def __init__(self, description="schedule room building", creator=None, roomPosition=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.reason = reason

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Schedule a room to be built on tile{reason}.

Use a CityPlaner to do this.

"""

        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False):

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
            command += "r"
            return (None,(command,"schedule building a room"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:

            submenue = character.macroState["submenue"]
            rewardIndex = 0
            if rewardIndex == 0:
                counter = 1
                for option in submenue.options.items():
                    if option[1] == "showMap":
                        break
                    counter += 1
                rewardIndex = counter

            offset = rewardIndex-submenue.selectionIndex
            command = ""
            if offset > 0:
                command += "s"*offset
            else:
                command += "w"*(-offset)
            command += "j"
            return (None,(command,"show the map"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        pos = character.getBigPosition()
        if pos != (7, 7, 0):
            quest = src.quests.questMap["GoHome"](description="go to command centre",reason="go to command centre")
            return ([quest],None)

        if not character.container.isRoom:
            quest = src.quests.questMap["EnterRoom"]()
            return ([quest],None)

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
            return (None,("J"+command,"activate the CityPlaner"))

        quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(), description="go to CityPlaner",ignoreEndBlocked=True, reason="go to the CityPlaner")
        return ([quest],None)

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        terrain = character.getTerrain()
        room = terrain.getRoomByPosition((7,7,0))[0]
        cityPlaner = room.getItemsByType("CityPlaner")[0]

        if self.roomPosition in cityPlaner.plannedRooms:
            self.postHandler()
            return True
        return None

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

        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def handleScheduledRoom(self,extraParams):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleScheduledRoom, "scheduled room")

        return super().assignToCharacter(character)

src.quests.addType(ScheduleRoomBuilding)

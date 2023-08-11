import src

class AssignFloorPlan(src.quests.MetaQuestSequence):
    type = "AssignFloorPlan"

    def __init__(self, description="assign floor plan", creator=None, roomPosition=None, floorPlanType=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.roomPosition = roomPosition
        self.floorPlanType = floorPlanType
        self.reason = reason

    def generateTextDescription(self):
        out = []
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        text = """
Assign a floor plan to room %s%s.

Set the floor plan: %s

(setting the wrong floor plan may break the tutorial, but is FUN)
"""%(self.roomPosition,reason,self.floorPlanType,)
        out = [text]
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
                    self.fail("room already registered")
                return (None,None)

            command += "f"
            return (None,(command,"to set a floor plan"))

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.interaction.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "floorplanSelection":
                counter = 1
                for option in submenue.options.items():
                    if option[1] == self.floorPlanType:
                        break
                    counter += 1

                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"to select the floor plan"))
            else:
                return (None,("j","to show the map"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"to exit submenu"))

        pos = character.getBigPosition()

        if not pos == (7,7,0):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
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
        room = terrain.getRoomByPosition(self.roomPosition)[0]

        if room.floorPlan:
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

    def handleAssignFloorPlan(self,extraParams):
        self.triggerCompletionCheck(extraParams["character"])

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        result.append(((self.roomPosition[0],self.roomPosition[1]),"target"))
        return result

    def assignToCharacter(self, character):
        if self.character:
            return
        
        self.startWatching(character,self.handleAssignFloorPlan, "assigned floor plan")

        return super().assignToCharacter(character)

src.quests.addType(AssignFloorPlan)

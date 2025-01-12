import src


class SetBaseAutoExpansion(src.quests.MetaQuestSequence):
    type = "SetBaseAutoExpansion"

    def __init__(self, description="set base expansion parameter", creator=None, targetLevel=2):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetLevel = targetLevel

    def handleSiegeDisabled(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleSiegeDisabled, "did unrestricted outside")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        foundCityPlaner = None
        for room in character.getTerrain().rooms:
            items = room.getItemsByType("CityPlaner",needsBolted=True)
            if not items:
                continue
            foundCityPlaner = items[0]
            break

        if foundCityPlaner:
            if foundCityPlaner.autoExtensionThreashold:
                self.postHandler()
                return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)
        
        if character.macroState["submenue"] and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "configurationSelection":
                return (None,("a","to select configuring the auto extension threashold"))
            if submenue.tag == "autoExtensionThreasholdInput":
                if submenue.text == str(self.targetLevel):
                    return (None,(["enter"],"to set the auto extension threashold"))

                if len(submenue.text) > len(str(self.targetLevel)):
                    return (None,(["backspace"],"remove input"))

                counter = 0
                while counter < len(submenue.text):
                    if submenue.text[counter] != str(self.targetLevel)[counter]:
                        return (None,(["backspace"],"remove input"))
                    counter += 1

                return (None,(str(self.targetLevel),"to enter the auto extension threashold"))

            return (None,(["esc"],"to close menu"))
        
        terrain = character.getTerrain()
        cityPlaner = None
        for room in terrain.rooms:
            item = room.getItemByType("CityPlaner",needsBolted=True)
            if not item:
                continue
            
            cityPlaner = item
            break

        if not cityPlaner:
            if not dryRun:
                self.fail("no city planer")
            return (None,None)

        if character.getBigPosition() != cityPlaner.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=cityPlaner.container.getPosition(),description="go to the command centre",reason="to reach the CityPlaner")
            return ([quest],None)

        if character.getDistance(cityPlaner.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=cityPlaner.getPosition(),ignoreEndBlocked=True,description="go to the CityPlaner",reason="to be able to activate the CityPlaner")
            return ([quest],None)
        
        target_pos = cityPlaner.getPosition()
        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == target_pos:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == target_pos:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == target_pos:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == target_pos:
            direction = "s"

        interactionCommand = "C"
        if "advancedConfigure" in character.interactionState:
            interactionCommand = ""
        return (None,(list(interactionCommand+direction+"a"+"2")+["enter"],"disable the outside restrictions"))

    def generateTextDescription(self):
        text = ["""
"""]
        return text


src.quests.addType(SetBaseAutoExpansion)

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
            if isinstance(submenue,src.menuFolder.selectionMenu.SelectionMenu):
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == "unrestrict outside":
                            foundOption = True
                            break
                        counter += 1
                    rewardIndex = counter

                if not foundOption:
                    return (None,(["esc"],"to close menu"))

                offset = rewardIndex-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += "j"
                return (None,(command,"contact command"))
            
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
        if "advancedInteraction" in character.interactionState:
            interactionCommand = ""
        return (None,(list(interactionCommand+direction+".a"+"2")+["enter"],"disable the outside restrictions"))

    def generateTextDescription(self):
        text = ["""
"""]
        return text


src.quests.addType(SetBaseAutoExpansion)

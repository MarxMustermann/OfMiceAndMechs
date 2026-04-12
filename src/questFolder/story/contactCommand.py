import src

class ContactCommand(src.quests.MetaQuestSequence):
    '''
    story quest pretending to try to contact a higher command
    '''
    type = "ContactCommand"
    def __init__(self, description="contact command", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step toward solving the quest
        '''

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "communicatorActicitySelection":
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == "contact base leader":
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
            
            return (None,(["esc"],"close the menu"))

        terrain = character.getTerrain()
        for room in terrain.rooms:
            items = room.getItemsByType("Communicator")
            if not items:
                continue
            item = items[0]
            quest = src.quests.questMap["ActivateItem"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="start communicating")
            return ([quest],None)

        return self._solver_trigger_fail(dryRun,"no communicator found")

    def generateTextDescription(self):
        return ["""
You reach out to your implant and it answers:

The base is secure from immediate dangers.
Contact the bases leader to get further instrucions.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handePermissionDenied, "permission denied")
        self.startWatching(character,self.handleNoCommander, "no base commander")
        super().assignToCharacter(character)

    def handePermissionDenied(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def handleNoCommander(self,extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def triggerCompletionCheck(self,character=None, dryRun=True):
        if not character:
            return False
        return False

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "Communicator":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(ContactCommand)

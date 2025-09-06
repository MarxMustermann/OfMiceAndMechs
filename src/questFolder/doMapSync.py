import src


class DoMapSync(src.quests.MetaQuestSequence):
    '''
    quest to get a NPC to synx with a map table
    '''
    type = "DoMapSync"
    def __init__(self, description="do map sync", reason=None):
        super().__init__()
        self.metaDescription = description
        self.reason = reason

    def generateTextDescription(self):
        '''
        get a long text description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"""
Update you map knowledge{reasonString}.
Use the MapTable to do this.
"""
        return text

    def handleSyncedMap(self, extraInfo):
        '''
        complete the quest after syncing
        '''
        self.postHandler()

    def assignToCharacter(self, character):
        '''
        start watching the character for getting promotions
        '''
        if self.character:
            return
        self.startWatching(character,self.handleSyncedMap, "synced map")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        '''
        check and complete the quest when done
        '''
        if not character:
            return False
        return False

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        '''
        calculate the next step towards solving the quest
        '''

        # wait for subquests to complete
        if self.subQuests:
            return (None,None)

        # skip on weird states
        if not character:
            return (None,None)

        # handle menus
        submenue = character.macroState["submenue"]
        if submenue:
            if submenue.tag == "applyOptionSelection":
                menuEntry = "studyMap"
                counter = 1
                for option in submenue.options.values():
                    print(option)
                    if option == menuEntry:
                        index = counter
                        break
                    counter += 1
                command = ""
                if submenue.selectionIndex > counter:
                    command += "w"*(submenue.selectionIndex-counter)
                if submenue.selectionIndex < counter:
                    command += "s"*(counter-submenue.selectionIndex)
                command += "j"
                return (None,(command,"study map"))
            return (None,(["esc"],"close the menu"))

        # go home
        if not character.getTerrain() == character.getHomeTerrain():
            quest = src.quests.questMap["GoHome"]()
            return  ([quest],None)

        # go inside
        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))
        room = character.container
        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go inside")
            return  ([quest],None)
        
        # activate map table
        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "MapTable":
                continue

            interactionCommand = "J"
            if "advancedInteraction" in character.interactionState:
                interactionCommand = ""
            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return (None,(interactionCommand+"aj","map table"))
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return (None,(interactionCommand+"dj","map table"))
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return (None,(interactionCommand+"wj","map table"))
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return (None,(interactionCommand+"sj","map table"))
            
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to map table")
            return  ([quest],None)
        
        # go to room with map table
        terrain = character.getTerrain()
        for room in terrain.rooms:
            if room.getItemByType("MapTable"):
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to command centre")
                return ([quest],None)

        # fail 
        if not dryRun:
            self.fail("no Map Table")
        return (None,("+","abort the quest"))

# register the quest type
src.quests.addType(DoMapSync)

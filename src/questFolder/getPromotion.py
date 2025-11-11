import src


class GetPromotion(src.quests.MetaQuestSequence):
    '''
    quest to get a NPC to fetch a promotion
    '''
    type = "GetPromotion"
    def __init__(self, targetRank, description="get promotion", reason=None):
        super().__init__()
        self.metaDescription = description
        self.targetRank = targetRank
        self.reason = reason

    def generateTextDescription(self):
        '''
        get a long text description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"""
Rise in the hierarchy and get a Promotion{reasonString}.
Use the Promotor to do this.
"""
        return text

    def handleGotPromotion(self, extraInfo):
        '''
        complete the quest after getting a promotion
        '''
        self.postHandler()

    def assignToCharacter(self, character):
        '''
        start watching the character for getting promotions
        '''
        if self.character:
            return
        self.startWatching(character,self.handleGotPromotion, "got promotion")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and complete the quest when done
        '''
        if not character:
            return False
        if character.rank <= self.targetRank:
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self, character=None, ignoreCommands=False, dryRun = True):
        '''
        calculate the next step towards solving the quest
        '''
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if character.macroState["submenue"]:
            if isinstance(character.macroState["submenue"],src.menuFolder.selectionMenu.SelectionMenu):
                return (None,(["enter"],"select reward"))
            return (None,(["esc"],"close the menu"))

        if not character.getTerrain() == character.getHomeTerrain():
            quest = src.quests.questMap["GoHome"]()
            return  ([quest],None)

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
        
        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "Promoter":
                continue

            interactionCommand = "J"
            if "advancedInteraction" in character.interactionState:
                interactionCommand = ""
            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return (None,(interactionCommand+"a","get promotion"))
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return (None,(interactionCommand+"d","get promotion"))
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return (None,(interactionCommand+"w","get promotion"))
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return (None,(interactionCommand+"s","get promotion"))
            
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to promoter ")
            return  ([quest],None)
        
        terrain = character.getTerrain()
        for room in terrain.rooms:
            if room.getItemByType("Promoter"):
                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to command centre")
                return ([quest],None)

        if not dryRun:
            self.fail("no Promoter")
        return (None,None)

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
                    if not item.type == "Promoter":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

# register the quest type
src.quests.addType(GetPromotion)

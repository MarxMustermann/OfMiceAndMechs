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

    def failedPromotion(self,extraInfo):
        self.fail("got no promotion")

    def assignToCharacter(self, character):
        '''
        start watching the character for getting promotions
        '''
        if self.character:
            return
        self.startWatching(character,self.handleGotPromotion, "got promotion")
        self.startWatching(character,self.failedPromotion, "failed promotion")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and complete the quest when done
        '''
        if not character:
            return False
        if character.rank and character.rank <= self.targetRank:
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

        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "promotionRewardSelection":
                return (None,("j","select reward"))
            if submenue.tag == "promotionIntro":
                return (None,("j","continue"))
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close the menu"))

        if not character.getTerrain() == character.getHomeTerrain():
            quest = src.quests.questMap["GoHome"](reason="get back to base")
            return  ([quest],None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            items = room.getItemsByType("Promoter")
            if not items:
                continue
            item = items[0]
            quest = src.quests.questMap["ActivateItem"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="get promoted")
            return ([quest],None)

        return self._solver_trigger_fail(dryRun,"no Promoter found")
            
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

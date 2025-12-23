import src


class SharpenPersonalSword(src.quests.MetaQuestSequence):
    '''
    quest to sharpen your own sword
    '''
    type = "SharpenPersonalSword"
    def __init__(self, description="sharpen personal sword", creator=None, command=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"
        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason
        text = f"Sharpen your personal Sword{reasonString}."
        return [text]

    def handleSwordSharpened(self,extraInfo=None):
        '''
        end quest when sword was sharpened
        '''
        self.postHandler()

    def assignToCharacter(self, character):
        '''
        assign quest to a character
        '''
        if self.character:
            return

        self.startWatching(character,self.handleSwordSharpened, "sharpened sword")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check if the quest completed and end it
        '''

        if not character:
            return False

        if not character.weapon:
            return False

        if character.weapon.baseDamage >= 30:
            if not dryRun:
                self.postHandler()
            return True

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step to solve the quest
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # enter room properly
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        # handle submenues
        submenue = character.macroState.get("submenue")
        if submenue:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "SwordSharpener":
                command = submenue.get_command_to_select_option("sharpen equipped sword")
                if command:
                    return (None,(command,"use SwordSharpener"))
            if submenue.tag == "SwordSharpenerSlider":
                return (None,("j","sharpen the sword"))
            return (None,(["esc"],"close the menu"))

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](description="defend yourself")
            return ([quest],None)

        # activate production item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["SwordSharpener"])
        if action:
            return action

        # use the actual SwordSharpener
        if character.container.isRoom:

            # use the SwordSharpener nearby
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue
                if not items[0].type == "SwordSharpener":
                    continue
                if offset == (0,0,0):
                    return (None,("j","sharpen personal sword"))
                interactionCommand = "J"
                if "advancedInteraction" in character.interactionState:
                    interactionCommand = ""
                if offset == (1,0,0):
                    return (None,(interactionCommand+"d","sharpen personal sword"))
                if offset == (-1,0,0):
                    return (None,(interactionCommand+"a","sharpen personal sword"))
                if offset == (0,1,0):
                    return (None,(interactionCommand+"s","sharpen personal sword"))
                if offset == (0,-1,0):
                    return (None,(interactionCommand+"w","sharpen personal sword"))

            # go to the SwordSharpener
            for item in character.container.itemsOnFloor:
                if not item.type == "SwordSharpener":
                    continue
                if not item.bolted:
                    continue
                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to SwordSharpener",ignoreEndBlocked=True)
                    return ([quest],None)

        # go to a room with a SwordSharpener
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "SwordSharpener":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a SwordSharpener")
                return ([quest],None)

        # kind of fail
        return (None,(".","stand around confused"))

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
                    if not item.type == "SwordSharpener":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(SharpenPersonalSword)

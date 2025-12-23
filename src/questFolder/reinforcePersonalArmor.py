import src


class ReinforcePersonalArmor(src.quests.MetaQuestSequence):
    type = "ReinforcePersonalArmor"

    def __init__(self, description="reinforce personal armor", creator=None, command=None, lifetime=None, reason=None):
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
        text = f"Reinforce your personal Armor{reasonString}."
        return [text]

    def handleArmorImproved(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleArmorImproved, "improved armor")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # enter room fully
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        # use menues
        if character.macroState.get("submenue"):
            submenue = character.macroState.get("submenue")
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "ArmorReinforcer":
                command = submenue.get_command_to_select_option("reinforce equipped armor")
                if command:
                    return (None,(command,"reinforce armor"))
            if submenue.tag == "ArmorReinforcerSlider":
                return (None,("j","reinforce the armor"))
            return (None,(["esc"],"close the menu"))
        
        # activate item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["ArmorReinforcer"])
        if action:
            return action

        # defend yourself
        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](description="defend yourself",reason="survive")
            return ([quest],None)

        # use reachable armor reinforcer
        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue
                if not items[0].type == "ArmorReinforcer":
                    continue
                if offset == (0,0,0):
                    return (None,("j","improve personal armor"))
                interactionCommand = "J"
                if "advancedInteraction" in character.interactionState:
                    interactionCommand = ""
                if offset == (1,0,0):
                    return (None,(interactionCommand+"d","improve personal armor"))
                if offset == (-1,0,0):
                    return (None,(interactionCommand+"a","improve personal armor"))
                if offset == (0,1,0):
                    return (None,(interactionCommand+"s","improve personal armor"))
                if offset == (0,-1,0):
                    return (None,(interactionCommand+"w","improve personal armor"))

        # go to armor reinforcer in the same room
        if character.container.isRoom:
            for item in character.container.itemsOnFloor:
                if not item.type == "ArmorReinforcer":
                    continue
                if not item.bolted:
                    continue
                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to ArmorReinforcer",ignoreEndBlocked=True,reason="be able to reach the ArmorReinforcer")
                    return ([quest],None)

        # go to a room with a armor reinforcer
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "ArmorReinforcer":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a ArmorReinforcer",reason="be able to use the ArmorReinforcer")
                return ([quest],None)

        # should not be reached
        return (None,(".","stand around confused"))

src.quests.addType(ReinforcePersonalArmor)

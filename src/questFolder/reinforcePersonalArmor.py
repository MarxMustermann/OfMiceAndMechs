import src


class ReinforcePersonalArmor(src.quests.MetaQuestSequence):
    type = "ReinforcePersonalArmor"

    def __init__(self, description="reinforce personal armor", creator=None, command=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"

    def handleArmorImproved(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleArmorImproved, "improved armor")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        if character.macroState.get("submenue"):
            submenue = character.macroState.get("submenue")
            if isinstance(submenue,src.menuFolder.selectionMenu.SelectionMenu):
                foundOption = False
                rewardIndex = 0
                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == "Reinforce armor":
                            foundOption = True
                            break
                        if option[1] == "Reinforce Equipped Armor":
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

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](description="defend yourself")
            return ([quest],None)

        terrain = character.getTerrain()

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
                    return (None,("jjj","improve personal armor"))
                interactionCommand = "J"
                if "advancedInteraction" in character.interactionState:
                    interactionCommand = ""
                if offset == (1,0,0):
                    return (None,(interactionCommand+"djj","improve personal armor"))
                if offset == (-1,0,0):
                    return (None,(interactionCommand+"ajj","improve personal armor"))
                if offset == (0,1,0):
                    return (None,(interactionCommand+"sjj","improve personal armor"))
                if offset == (0,-1,0):
                    return (None,(interactionCommand+"wjj","improve personal armor"))


            for item in character.container.itemsOnFloor:
                if not item.type == "ArmorReinforcer":
                    continue
                if not item.bolted:
                    continue

                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to ArmorReinforcer",ignoreEndBlocked=True)
                    return ([quest],None)

        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "ArmorReinforcer":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a ArmorReinforcer")
                return ([quest],None)

        return (None,None)

src.quests.addType(ReinforcePersonalArmor)

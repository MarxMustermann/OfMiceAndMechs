import src


class LiftOutsideRestrictions(src.quests.MetaQuestSequence):
    type = "LiftOutsideRestrictions"

    def __init__(self, description="lift outside restrictions", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleSiegeDisabled(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleSiegeDisabled, "did unrestricted outside")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        terrain = character.getTerrain()
        if not terrain.alarm:
            if not dryRun:
                self.postHandler()
            return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        if self.subQuests:
            return (None,None)
        
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
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
            
        if not character.getTerrain() == character.getHomeTerrain():
            quest = src.quests.questMap["GoHome"](reason="get back to base")
            return  ([quest],None)

        terrain = character.getTerrain()
        for room in terrain.rooms:
            items = room.getItemsByType("SiegeManager",needsBolted=True)
            if not items:
                continue
            item = items[0]
            quest = src.quests.questMap["ActivateItem"](targetPosition=item.getPosition(),targetPositionBig=item.getBigPosition(),reason="get promoted")
            return ([quest],None)

        return self._solver_trigger_fail(dryRun,"no SiegeManager found")

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = f", {self.reason}"
        text= [f"""
There are many enemies left outside the base{reasonString}.
But all enemies left will only attack when somebody enters the tile they are on.
So they can be easily avoided by you and your clone.

This means that the restriction of the outside movement can be lifted now.
Use the SiegeManager to lift the restriction of the outside movement.
Once you do that, your clone will start to gather scrap and to produce items.
"""]
        return text

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
                    if not item.type == "SiegeManager":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(LiftOutsideRestrictions)

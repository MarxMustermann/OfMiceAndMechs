import src


class Ascend(src.quests.MetaQuestSequence):
    '''
    quest for a player to take the throne and actually win the game
    '''
    type = "Ascend"
    def __init__(self, description="ascend", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleAscended(self):
        '''
        complete when character ascended
        '''
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def assignToCharacter(self, character):
        '''
        start watching for events
        '''
        if self.character:
            return None

        self.startWatching(character,self.handleAscended, "ascended")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        '''
        generate text description to show on the UI
        '''
        text = ["""
You reach out to your implant and it answers:

You obtained all GlassHearts and fully control the GlassStatues now.
But you are under constant attack by your enemies.
They envy your status and try to steal it from you.

Show your enemies who rules this world by stepping to the throne and taking the crown.
This will permanently bond the GlassHearts and your enemies will see reason.
Rule the world and put an end to those attacks!
"""]
        return text

    def triggerCompletionCheck(self,character=None, dryRun=True):
        '''
        check and end the quest if done
        '''
        if not character:
            return False

        if character.rank != 1:
            return False

        if not dryRun:
            self.postHandler()
        return True

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):
        '''
        generate the next step towards solving the quest
        '''

        # handle edge cases
        if self.subQuests:
            return (None,None)

        # handle menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.type == "TextMenu":
                return (None,(["enter"],"continue"))
            if submenue.tag == "throneTeleport":
                command = submenue.get_command_to_select_option("no")
                return (None,(command,"teleport"))
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # abort on missing glass hearts
        for (godId,god) in src.gamestate.gamestate.gods.items():
            if (god["lastHeartPos"][0] == character.registers["HOMETx"] and god["lastHeartPos"][1] == character.registers["HOMETy"]):
                continue
            return self._solver_trigger_fail(dryRun,"missing glass heart")

        # enter rooms fully
        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        # set up helper variables
        currentTerrain = character.getTerrain()

        # go home
        if currentTerrain != character.getHomeTerrain() and currentTerrain.getPosition() != (7,7,0):
            quest = src.quests.questMap["GoHome"](reason="get back to base")
            return ([quest],None)

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("Throne","GlassThrone"))
        if action:
            return action

        # check if the Trone was properly activated yet
        hasSeeker = False
        for statusEffect in character.statusEffects:
            if not statusEffect.type == "ThroneSeeker":
                continue
            hasSeeker = True

        if hasSeeker:
            
            # prepare for the raid
            if currentTerrain == character.getHomeTerrain():

                # check in what state the base is
                num_NPCs = 0
                num_enemies = 0
                for check_character in currentTerrain.getAllCharacters():
                    if character.is_ally(check_character):
                        if not character.burnedIn and character.charType == "Clone":
                            num_NPCs += 1  
                    else:
                        num_enemies += 1

                # defend the base
                if num_enemies:
                    if src.gamestate.gamestate.tick > 1000:
                        quest = src.quests.questMap["ClearTerrain"]()
                        return ([quest],None)
                    quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                    return ([quest],None)

                # ensure there are backup NPCs
                if num_NPCs < 3:
                    quest = src.quests.questMap["SpawnClone"](tryHard=True,lifetime=5000,reason="ensure somebody will be left to man the base")
                    return ([quest],None)

                # ensure a good strength level
                if character.getStrengthSelfEstimate() < 5:
                    quest = src.quests.questMap["BecomeStronger"](targetStrength=5,lifetime=15*15*15*3)
                    return ([quest],None)

                # clear inventory
                if character.has_big_item_in_inventory():
                    quest = src.quests.questMap["ClearInventory"]()
                    return ([quest],None)

                # sharpen sword
                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("SwordSharpener"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["SharpenPersonalSword"]()
                            return ([quest],None)

                # improve armor
                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("ArmorReinforcer"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["ReinforcePersonalArmor"]()
                            return ([quest],None)

                # heal
                if character.health < character.adjustedMaxHealth:
                    readyCoalBurner = False
                    for room in currentTerrain.rooms:
                        for coalBurner in room.getItemsByType("CoalBurner"):
                            if not coalBurner.getMoldFeed(character):
                                continue
                            readyCoalBurner = True
                    if readyCoalBurner:
                        quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=True)
                        return ([quest],None)

                # make space to be able to fetch equipment
                for item in character.inventory:
                    if item.type in ("Scrap","Flask","ChitinPlates","MetalBars",):
                        quest = src.quests.questMap["ClearInventory"](returnToTile=False,reason="have space for equipment")
                        return ([quest],None)
                for itemType in ("Vial","Bolt",):
                    if character.getFreeInventorySpace():
                        for room in currentTerrain.rooms:
                            if not room.getNonEmptyOutputslots(itemType):
                                continue
                            quest = src.quests.questMap["FetchItems"](toCollect=itemType,reason="be properly equipped")
                            return ([quest],None)

            # go to glass palace
            terrain = character.getTerrain()
            if terrain.xPosition != 7 or terrain.yPosition != 7:
                quest = src.quests.questMap["TeleportToGlassPalace"]()
                return ([quest],None)
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=(7,7,0),reason="get to the glass palace", description="go to glass palace")
                return ([quest],None)

            # heal
            if character.health < character.adjustedMaxHealth:
                if character.searchInventory("Vial"):
                    quest = src.quests.questMap["Heal"](noWaitHeal=True,noVialHeal=False)
                    return ([quest],None)

            # fight
            if character.getNearbyEnemies():
                quest = src.quests.questMap["Fight"](suicidal=True)
                return ([quest],None)

            # go to glass throne
            if character.getBigPosition() != (7,7,0):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="get to the throne room", description="go to throne room",abortOnDanger=True)
                return ([quest],None)
            if character.getDistance((6,6,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,6,0),ignoreEndBlocked=True,reason="get near the glass throne", description="go to the glass throne")
                return ([quest],None)
            
            # actually activate the throne and win the game :-)
            pos = character.getPosition()
            targetPosition = (6,6,0)
            if (pos[0],pos[1],pos[2]) == targetPosition:
                return (None,("j","activate the Throne"))
            interactionCommand = "J"
            if submenue and submenue.tag in ("advancedInteractionSelection",):
                interactionCommand = ""
            if (pos[0]-1,pos[1],pos[2]) == targetPosition:
                return (None,(interactionCommand+"a","activate the Throne"))
            if (pos[0]+1,pos[1],pos[2]) == targetPosition:
                return (None,(interactionCommand+"d","activate the Throne"))
            if (pos[0],pos[1]-1,pos[2]) == targetPosition:
                return (None,(interactionCommand+"w","activate the Throne"))
            if (pos[0],pos[1]+1,pos[2]) == targetPosition:
                return (None,(interactionCommand+"s","activate the Throne"))
            return (None,(".","stand around confused"))

        # find throne
        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break
        if not throne:
            return self._solver_trigger_fail(dryRun,"no throne")

        # go to throne
        if character.container != throne.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=throne.container.getPosition(),reason="get to the temple", description="go to temple")
            return ([quest],None)
        pos = character.getPosition()
        targetPosition = throne.getPosition()
        if targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=targetPosition,ignoreEndBlocked=True,reason="get near the throne", description="go to throne")
            return ([quest],None)

        # activate throne
        if (pos[0],pos[1],pos[2]) == targetPosition:
            return (None,("j","activate the Throne"))
        interactionCommand = "J"
        if submenue and submenue.tag in ("advancedInteractionSelection",):
            interactionCommand = ""
        if (pos[0]-1,pos[1],pos[2]) == targetPosition:
            return (None,(interactionCommand+"a","activate the Throne"))
        if (pos[0]+1,pos[1],pos[2]) == targetPosition:
            return (None,(interactionCommand+"d","activate the Throne"))
        if (pos[0],pos[1]-1,pos[2]) == targetPosition:
            return (None,(interactionCommand+"w","activate the Throne"))
        if (pos[0],pos[1]+1,pos[2]) == targetPosition:
            return (None,(interactionCommand+"s","activate the Throne"))
        return (None,None)

    def handleQuestFailure(self,extraParam):
        
        # prepare helper variables
        reason = extraParam.get("reason")

        if reason == "no way to heal":
            for room in self.character.getTerrain().rooms:
                for item in room.getItemsByType("MoldFeed"):
                    newQuest = src.quests.questMap["CleanSpace"](targetPosition=item.getPosition(),targetPositionBig=room.getPosition(),tryHard=True)
                    self.addQuest(newQuest)
                    self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    if not self.character.getFreeInventorySpace():
                        newQuest = src.quests.questMap["ClearInventory"](tryHard=True)
                        self.addQuest(newQuest)
                        self.startWatching(newQuest,self.handleQuestFailure,"failed")
                    return


# register the quest type
src.quests.addType(Ascend)

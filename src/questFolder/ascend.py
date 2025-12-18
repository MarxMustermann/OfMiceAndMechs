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
        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"close menu"))

        if not character.container.isRoom:
            if character.xPosition%15 == 0:
                return (None,("d","enter room"))
            if character.xPosition%15 == 14:
                return (None,("a","enter room"))
            if character.yPosition%15 == 0:
                return (None,("s","enter room"))
            if character.yPosition%15 == 14:
                return (None,("w","enter room"))

        hasSeeker = False
        for statusEffect in character.statusEffects:
            if not statusEffect.type == "ThroneSeeker":
                continue
            hasSeeker = True

        if hasSeeker:
            currentTerrain = character.getTerrain()

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
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)

            # ensure there are backup NPCs
            if num_NPCs < 3:
                quest = src.quests.questMap["SpawnClone"](tryHard=True,lifetime=1000,reason="ensure somebody will be left to man the base")
                return ([quest],None)

            if currentTerrain == character.getHomeTerrain():
                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("SwordSharpener"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["SharpenPersonalSword"]()
                            return ([quest],None)

                for room in character.getTerrain().rooms:
                    for item in room.getItemsByType("ArmorReinforcer"):
                        if item.readyToBeUsedByCharacter(character):
                            quest = src.quests.questMap["ReinforcePersonalArmor"]()
                            return ([quest],None)

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

            terrain = character.getTerrain()
            if terrain.xPosition != 7 or terrain.yPosition != 7:
                quest = src.quests.questMap["GoToTerrain"](targetTerrain=(7,7,0),reason="get to the glass palace", description="go to glass palace")
                return ([quest],None)

            if character.getBigPosition() != (7,7,0):
                quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),reason="get to the throne room", description="go to throne room")
                return ([quest],None)

            if character.getDistance((6,6,0)) > 1:
                quest = src.quests.questMap["GoToPosition"](targetPosition=(6,6,0),ignoreEndBlocked=True,reason="get near the glass throne", description="go to the glass throne")
                return ([quest],None)
            
            pos = character.getPosition()
            targetPosition = (6,6,0)
            if (pos[0],pos[1],pos[2]) == targetPosition:
                return (None,("j","activate the Throne"))
            interactionCommand = "J"
            if "advancedInteraction" in character.interactionState:
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

        terrain = character.getTerrain()
        for room in terrain.rooms:
            throne = room.getItemByType("Throne",needsBolted=True)
            if throne:
                break

        if not throne:
            return self._solver_trigger_fail(dryRun,"no throne")

        if character.container != throne.container:
            quest = src.quests.questMap["GoToTile"](targetPosition=throne.container.getPosition(),reason="get to the temple", description="go to temple")
            return ([quest],None)

        pos = character.getPosition()
        targetPosition = throne.getPosition()
        if targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=targetPosition,ignoreEndBlocked=True,reason="get near the throne", description="go to throne")
            return ([quest],None)

        if (pos[0],pos[1],pos[2]) == targetPosition:
            return (None,("j","activate the Throne"))
        interactionCommand = "J"
        if "advancedInteraction" in character.interactionState:
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

# register the quest type
src.quests.addType(Ascend)

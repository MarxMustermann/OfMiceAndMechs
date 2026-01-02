import src


class TeleportToGlassPalace(src.quests.MetaQuestSequence):
    type = "TeleportToGlassPalace"

    def __init__(self, description="teleport to glass palace", creator=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.reason = reason

    def handleTeleported(self):
        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()

    def handleStatueUsed(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleStatueUsed, "glass statue used")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if character.getTerrain().getPosition() == (7,7,0):
            if not dryRun:
                self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # handle edge cases
        if self.subQuests:
            return (None,None)

        # go home
        if not character.isOnHomeTerrain():
            quest = src.quests.questMap["GoHome"]()
            return ([quest],None)

        # check in what state the base is
        num_NPCs = 0
        num_enemies = 0
        for check_character in character.getTerrain().getAllCharacters():
            if character.is_ally(check_character):
                if not check_character.burnedIn and check_character.charType == "Clone":
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
        print(num_NPCs)
        if num_NPCs < 3:
            quest = src.quests.questMap["SpawnClone"](tryHard=True,lifetime=1000,reason="ensure somebody will be left to man the base")
            return ([quest],None)

        # handle menues
        submenue = character.macroState.get("submenue")
        if submenue and not ignoreCommands:
            if submenue.tag == "throneTeleport":
                command = submenue.get_command_to_select_option("yes")
                return (None,(command,"teleport"))
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # activate correct item when marked
        if character.macroState.get("itemMarkedLast"):
            item = character.macroState["itemMarkedLast"]
            if item.type == "Throne":
                return (None,("j","activate Thron"))
            else:
                return (None,(".","undo selection"))

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

    def generateTextDescription(self):
        text = ["""
Teleport to the glass palace.
"""]
        return text


src.quests.addType(TeleportToGlassPalace)

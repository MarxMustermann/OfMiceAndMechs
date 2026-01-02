import src


class GetEpochReward(src.quests.MetaQuestSequence):
    type = "GetEpochReward"

    def __init__(self, description="get epoch reward", creator=None,rewardType=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description + " (" + rewardType + ")"
        self.rewardType = rewardType
        self.reason = reason

    def generateTextDescription(self):
        '''
        generate a textual description to show on the UI
        '''
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Claim a reward for the work you have done{reason}.

You accumulated some mana.
Spend them to claim the actual reward.
"""

        match self.rewardType:
            case "spawn room building NPC":
                text += """
Spawn a room builder. A room building clone will build rooms.
This will allow you to focus on getting more building materials.
"""
            case "spawn scavenging NPC":
                text += """
Spawn a scavenger. A scavenging clone will collect items from outside.
This will allow you to focus on producing walls.
"""
            case "spawn machine operating NPC":
                text += """
Spawn a machine operator. A machine operating clone will operate machines and produce items.
This will allow you to focus on supplying materials for producing walls.
"""

            case "spawn resource fetching NPC":
                text += """
Spawn a resource fetcher. A resource fetching clone will carry items from room to room.
This will allow you to focus on other tasks.
"""

            case "spawn resource gathering NPC":
                text += """
Spawn a resource gatherer. A resource gathering clone will collect scrap from scrap field.
This will allow you to focus on other tasks.
"""

            case "spawn painting NPC":
                text += """
Spawn a painter. A painting clone will draw stock piles and build sites.
This will allow you to focus on other tasks.
"""

            case "spawn machine placing NPC":
                text += """
Spawn a machine placer. A machine placing clone will produce and place machines.
This will allow you to focus on other tasks.
"""

            case "spawn hauling NPC":
                text += """
Spawn a hauler. A hauling clone will carry items withins rooms.
This will allow you to focus on other tasks.
"""
            case _:
                text += """
{self.rewardType}
"""


        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step to solve the quest
        Parameters:
            character:       the character doing the quest
            ignoreCommands:  whether to generate commands or not
            dryRun:          flag to be stateless or not
        Returns:
            the activity to run as next step
        '''

        # ensure subquests are completed
        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        # handle weird edge cases
        if self.subQuests:
            return (None,None)

        # handle sub menus
        submenue = character.macroState["submenue"]
        if character.macroState["submenue"] and not ignoreCommands:
            if submenue.tag == "applyOptionSelection" and submenue.extraInfo.get("item").type == "Shrine":
                command = submenue.get_command_to_select_option("wish")
                if command:
                    return (None,(command,"get your reward"))
            if submenue.tag == "rewardSelection":
                command = submenue.get_command_to_select_option(self.rewardType)
                if command:
                    return (None,(command,"get your reward"))
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        # activate production item when marked
        action = self.generate_confirm_interaction_command(allowedItems=["Shrine"])
        if action:
            return action

        # find a temple
        roomPos = None
        for room in character.getTerrain().rooms:
            if room.tag != "temple":
                continue
            roomPos = room.getPosition()
        if not roomPos:
            return self._solver_trigger_fail(dryRun,"no temple found")

        # activate shrine
        pos = character.getBigPosition()
        if pos == roomPos:

            # enter room properly
            if not character.container.isRoom:
                quest = src.quests.questMap["EnterRoom"](reason="be able to interact properly")
                return ([quest],None)

            # find shrine to pray at
            shrines = character.container.getItemsByType("Shrine")
            foundShrine = None
            for shrine in shrines:
                if (self.rewardType.startswith("spawn ") and self.rewardType.endswith("NPC")) and shrine.god == 1:
                    foundShrine = shrine
                if self.rewardType == "spawn scrap" and shrine.god == 2:
                    foundShrine = shrine
            if not foundShrine:
                return self._solver_trigger_fail(dryRun,"no shrine found")

            # activate nearby shrine
            command = None
            if character.getPosition(offset=(1,0,0)) == foundShrine.getPosition():
                command = "d"
            if character.getPosition(offset=(-1,0,0)) == foundShrine.getPosition():
                command = "a"
            if character.getPosition(offset=(0,1,0)) == foundShrine.getPosition():
                command = "s"
            if character.getPosition(offset=(0,-1,0)) == foundShrine.getPosition():
                command = "w"
            if command:
                interactionCommand = "J"
                if submenue:
                    if submenue.tag == "advancedInteractionSelection":
                        interactionCommand = ""
                    else:
                        return (None,(["esc"],"close menu"))
                return (None,(interactionCommand+command,"start praying at the shrine"))

            # go to shrine
            quest = src.quests.questMap["GoToPosition"](targetPosition=foundShrine.getPosition(), description="go to shrine",ignoreEndBlocked=True,reason="be able to activate the shrine")
            return ([quest],None)

        # go to temple
        quest = src.quests.questMap["GoToTile"](description="go to temple",targetPosition=roomPos,reason="be able to use the shrine")
        return ([quest],None)

    def handleGotEpochReward(self, extraInfo):
        '''
        end quest after having collected the reward
        Parameters:
            extraInfo:  context information
        '''

        if self.completed:
            1/0
        if not self.active:
            return

        self.postHandler()
        return

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleGotEpochReward, "got epoch reward")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        never complete
        Parameters:
            character:  the character doing the quest
            dryRun:     flag to be stateless or not
        Returns:
            whether the quest ended or not
        '''
        return False

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        '''
        generate quests to be used in the duty system
        Parameters:
            beUsefull:   the quest to generate the duty for
            character:   the character to generate the quest for
            currentRoom: the room the character is currently in
            dryRun:      flag for statelessness
        Returns:
            the generated quests ( (None,None) for no quest to do )
        '''

        # set up helper variables
        terrain = character.getTerrain()

        # get shrine
        foundShrine = None
        for room in beUsefull.getRandomPriotisedRooms(character,currentRoom):
            for checkShrine in room.getItemsByType("Shrine"):
                if checkShrine.god != 1:
                    continue
                foundShrine = checkShrine
        if not foundShrine:
            return (None,None)

        # gather npc duties
        npcDuties = {}
        for otherChar in terrain.characters:
            if not otherChar.burnedIn:
                continue
            for duty in otherChar.duties:
                if otherChar == character:
                    continue
                if duty not in npcDuties:
                    npcDuties[duty] = []
                npcDuties[duty].append(otherChar)
        for checkRoom in character.getTerrain().rooms:
            for otherChar in checkRoom.characters:
                if not otherChar.burnedIn:
                    continue
                if otherChar == character:
                    continue
                for duty in otherChar.duties:
                    if duty not in npcDuties:
                        npcDuties[duty] = []
                    npcDuties[duty].append(otherChar)

        # generate quests for all missing duty-clones
        chargesUsed = 0
        quests = []
        for duty in ["room building","cleaning","scavenging","manufacturing","resource gathering","scrap hammering","mold farming","hauling","metal working","resource fetching","painting","machine placing","machine operation","maggot gathering",]:
            if duty not in npcDuties:
                cost = foundShrine.getBurnedInCharacterSpawningCost(character)
                cost *= foundShrine.get_glass_heart_rebate()
                foundFlask = None
                for item in character.inventory:
                    if item.type != "GooFlask":
                        continue
                    if item.uses < 100:
                        continue
                    foundFlask = item
                if foundFlask:
                    cost /= 2
                cost += chargesUsed
                if character.getTerrain().mana >= cost:
                    quest = src.quests.questMap["GetEpochReward"](rewardType="spawn "+duty+" NPC",reason="spawn another clone to help you out")
                    chargesUsed += cost
                    quests.append(quest)

        # dispatch the generated quests
        if quests:
            quests.reverse()
            return (quests,None)
        return (None,None)

# register the quest type
src.quests.addType(GetEpochReward)

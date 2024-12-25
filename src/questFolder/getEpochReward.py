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
        out = []
        reason = ""
        if self.reason:
            reason = f",\nto {self.reason}"
        text = f"""
Claim a reward for completing the epoch challenge{reason}.

You accumulated some glass tears.
Spend them to claim the actual reward ({self.rewardType}).
"""

        if self.rewardType == "room building":
            text += """
Spawn a room builder. A room building clone will build rooms.
This will allow you to focus on getting more building materials.
"""
        if self.rewardType == "scavenging":
            text += """
Spawn a scavenger. A scavenging clone will collect items from outside.
This will allow you to focus on producing walls.
"""
        if self.rewardType == "machine operating":
            text += """
Spawn a machine operator. A machine operating clone will operate machines and produce items.
This will allow you to focus on supplying materials for producing walls.
"""

        if self.rewardType == "resource fetching":
            text += """
Spawn a resource fetcher. A resource fetching clone will carry items from room to room.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "resource gathering":
            text += """
Spawn a resource gatherer. A resource gathering clone will collect scrap from scrap field.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "painting":
            text += """
Spawn a painter. A painting clone will draw stock piles and build sites.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "machine placing":
            text += """
Spawn a machine placer. A machine placing clone will produce and place machines.
This will allow you to focus on other tasks.
"""

        if self.rewardType == "hauling":
            text += """
Spawn a hauler. A hauling clone will carry items withins rooms.
This will allow you to focus on other tasks.
"""

        text += """
(buying the wrong reward may break the tutorial, but is FUN)
"""

        out.append(text)
        return out

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        while self.subQuests:
            if not self.subQuests[-1].completed:
                break
            self.subQuests.pop()

        if self.subQuests:
            return (None,None)

        if character.macroState["submenue"] and isinstance(character.macroState["submenue"],src.menuFolder.SelectionMenu.SelectionMenu) and not ignoreCommands:
            submenue = character.macroState["submenue"]
            if submenue.tag == "rewardSelection":
                rewardIndex = 0
                if self.rewardType == "room building":
                    rewardIndex = 8
                if self.rewardType == "scavenging":
                    rewardIndex = 10
                if self.rewardType == "machine operating":
                    rewardIndex = 3
                if self.rewardType == "resource fetching":
                    rewardIndex = 4
                if self.rewardType == "resource gathering":
                    rewardIndex = 2
                if self.rewardType == "painting":
                    rewardIndex = 6

                if rewardIndex == 0:
                    counter = 1
                    for option in submenue.options.items():
                        if option[1] == self.rewardType:
                            break
                        counter += 1
                    rewardIndex = counter

                offset = rewardIndex-submenue.selectionIndex
                command = ""
                if offset > 0:
                    command += "s"*offset
                else:
                    command += "w"*(-offset)
                command += "j"
                return (None,(command,"get your reward"))

            submenue = character.macroState["submenue"]
            rewardIndex = 0
            if rewardIndex == 0:
                counter = 1
                for option in submenue.options.items():
                    if option[1] == "wish":
                        break
                    counter += 1
                rewardIndex = counter

            command = ""
            if submenue.selectionIndex > rewardIndex:
                command += "w"*(submenue.selectionIndex-rewardIndex)
            if submenue.selectionIndex < rewardIndex:
                command += "s"*(rewardIndex-submenue.selectionIndex)
            command += "j"
            return (None,(command,"get your reward"))

        if character.macroState["submenue"] and not ignoreCommands:
            return (None,(["esc"],"exit submenu"))

        pos = character.getBigPosition()

        roomPos = None
        for room in character.getTerrain().rooms:
            if room.tag != "temple":
                continue
            roomPos = room.getPosition()

        if not roomPos:
            self.fail("no temple found")
            return (None,None)

        if pos == roomPos:
            if not character.container.isRoom:
                quest = src.quests.questMap["EnterRoom"]()
                return ([quest],None)

            shrines = character.container.getItemsByType("Shrine")
            foundShrine = None
            for shrine in shrines:
                if (self.rewardType.startswith("spawn ") and self.rewardType.endswith("NPC")) and shrine.god == 1:
                    foundShrine = shrine
                if self.rewardType == "spawn scrap" and shrine.god == 2:
                    foundShrine = shrine

            if not foundShrine:
                self.fail("no shrine found")
                return (None,None)

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
                return (None,("J"+command,"start praying at the shrine"))

            quest = src.quests.questMap["GoToPosition"](targetPosition=foundShrine.getPosition(), description="go to shrine",ignoreEndBlocked=True)
            return ([quest],None)

        quest = src.quests.questMap["GoToTile"](description="go to temple",targetPosition=roomPos)
        return ([quest],None)

    def handleGotEpochReward(self, extraInfo):
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

    """
    never complete
    """
    def triggerCompletionCheck(self,character=None):
        return False

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        terrain = character.getTerrain()

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

        chargesUsed = 0
        quests = []
        for duty in ["room building","cleaning","scavenging","manufacturing","resource gathering","scrap hammering","mold farming","hauling","metal working","resource fetching","painting","machining","machine placing","machine operation","maggot gathering",]:

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
                    chargesUsed += 10
                    quests.append(quest)
                    break

        if quests:
            quests.reverse()
            return (quests,None)
        return (None,None)

src.quests.addType(GetEpochReward)

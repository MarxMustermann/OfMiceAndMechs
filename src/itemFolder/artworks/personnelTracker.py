import src


class PersonnelTracker(src.items.Item):
    """
    """


    type = "PersonnelTracker"

    def __init__(self, name="PersonnelTracker", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="PT", name=name)

        self.applyOptions.extend(
                        [
                                                                ("viewNPCs", "view npcs"),
                        ]
                        )
        self.applyMap = {
                    "viewNPCs": self.viewNPCs,
                        }

        self.faction = ""

    def viewNPCs(self,character):
        submenue = src.interaction.ViewNPCsMenu(self)
        character.macroState["submenue"] = submenue
        self.faction = character.faction

    def getPersonnelList(self):

        personnel = []

        terrain = self.getTerrain()
        for character in terrain.characters:
            if character.faction != self.faction:
                continue
            personnel.append(character)

        for room in terrain.rooms:
            for character in room.characters:
                if character.faction != self.faction:
                    continue
                personnel.append(character)

        return personnel

    def fetchCityleader(self):
        if self.cityLeader and self.cityLeader.dead:
            self.cityLeader = None
        return self.cityLeader

    def setCityleader(self,character):
        self.cityLeader = character

    def spawnSet(self,character):
        cityleader = self.spawnRank(3,character)
        for _i in range(3):
            self.spawnRank(4,character)
        for _i in range(9):
            self.spawnRank(5,character)
        for _i in range(9*3):
            self.spawnRank(6,character)
        return cityleader

    def spawnRank6(self,character):
        return self.spawnRank(6,character)
    def spawnRank5(self,character):
        return self.spawnRank(5,character)
    def spawnRank4(self,character):
        return self.spawnRank(4,character)
    def spawnRank3(self,character):
        return self.spawnRank(3,character)
    def spawnRankUnranked(self,character):
        return self.spawnRank(None,character)

    def spawnMilitary(self,character):
        return self.spawnRank(None,character,isMilitary=True)

    def spawnIndependentFighter(self,character,extraCost=1):
        if not self.charges > 0+extraCost:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None
        self.charges -= 1+extraCost

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        terrainPosition = self.getTerrainPosition()
        char.registers["HOMETx"] = terrainPosition[0]
        char.registers["HOMETy"] = terrainPosition[1]
        char.personality["abortMacrosOnAttack"] = False
        char.rank = None

        char.faction = self.faction

        quest = src.quests.questMap["Assimilate"]()
        quest.assignToCharacter(char)
        quest.activate()
        quest.autoSolve = True
        char.quests.append(quest)
        char.baseDamage = 10
        char.movementSpeed = 1.5

        char.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ]

        self.container.addCharacter(char,5,6)
        char.automated = True
        char.runCommandString("********")

        return char

    def spawnIndependentClone(self,character):
        if random.random() > 0.5:
            return self.spawnIndependentWorker(character,extraCost=0)
        else:
            return self.spawnIndependentFighter(character,extraCost=0)

    def spawnIndependentWorker(self,character,extraCost=1):
        if not self.charges > 0+extraCost:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None
        self.charges -= 1+extraCost

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        terrainPosition = self.getTerrainPosition()
        char.registers["HOMETx"] = terrainPosition[0]
        char.registers["HOMETy"] = terrainPosition[1]
        char.personality["abortMacrosOnAttack"] = False
        char.rank = None
        char.baseDamage = 5
        char.movementSpeed = 0.5

        char.faction = self.faction

        quest = src.quests.questMap["Assimilate"]()
        quest.assignToCharacter(char)
        quest.activate()
        quest.autoSolve = True
        char.quests.append(quest)

        char.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ]

        self.container.addCharacter(char,5,6)
        char.runCommandString("********")

        return char

    def spawnBodyguard(self,character):
        for subordinate in character.subordinates[:]:
            if subordinate.dead:
                character.subordinates.remove(subordinate)

        if character.rank == None or character.rank > 5:
            character.addMessage("you need to be rank 5 or higher to spawn a bodyguard")
            return None
        if character.rank == 5 and character.getNumSubordinates() > 0:
            character.addMessage("you can only have one bodyguard with rank 5")
            return
        if character.rank == 4 and character.getNumSubordinates() > 1:
            character.addMessage("you can only have two bodyguards with rank 4")
            return
        if character.rank == 3 and character.getNumSubordinates() > 2:
            character.addMessage("you can only have three bodyguards with rank 3")
            return

        if not self.charges:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None

        self.charges -= 1
        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        terrainPosition = self.getTerrainPosition()
        char.registers["HOMETx"] = terrainPosition[0]
        char.registers["HOMETy"] = terrainPosition[1]
        char.personality["abortMacrosOnAttack"] = False
        char.rank = 6
        char.movementSpeed = 0.5

        character.subordinates.append(char)
        char.superior = character
        char.faction = character.faction

        quest = src.quests.questMap["Equip"](lifetime=1000)
        quest.assignToCharacter(char)
        quest.activate()
        quest.autoSolve = True
        char.quests.append(quest)

        quest = src.quests.questMap["ProtectSuperior"]()
        quest.assignToCharacter(char)
        quest.activate()
        quest.autoSolve = True
        char.quests.append(quest)

        self.container.addCharacter(char,5,6)

        character.changed("got subordinate",(character,char,))
        char.runCommandString("********")

    def apply(self,character):
        #if not character.rank or character.rank > 5:
        #    character.addMessage("you need to have be at least rank 5 to use this machine")
        #    return
        super().apply(character)

    def configure(self,character):
        foundFlasks = []
        for item in character.inventory:
            if item.type != "GooFlask":
                continue
            if item.uses != 100:
                continue
            foundFlasks.append(item)

        if not foundFlasks:
            character.addMessage("you need to have at least one goo flask in inventory to recharge this item")
            return

        for flask in foundFlasks:
            character.inventory.remove(flask)

        amount = len(foundFlasks)
        self.changeCharges(amount)
        character.addMessage(f"you use your flasks to recharge the personell artwork for {amount} charges")

    def spawnRank(self,rank,actor,isMilitary=False):
        cityLeader = self.fetchCityleader()

        if rank == 3 and cityLeader and not cityLeader.dead:
            actor.addMessage("only one rank 3 possible")
            return None

        if rank == 4:
            if not cityLeader or self.cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return None

            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    cityLeader.subordinates.remove(subleader)

            if len(cityLeader.subordinates) > 2:
                actor.addMessage("no rank 3 to hook into")
                return None

        if rank == 5:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return None

            foundSubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue
                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        subleader.subordinates.remove(subsubleader)
                if len(subleader.subordinates) > 2:
                    continue
                foundSubleader = subleader

            if not foundSubleader:
                actor.addMessage("no rank 4 to hook into")
                return None

        if rank == 6:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return None

            foundSubsubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue

                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        continue
                    for subordinate in subsubleader.subordinates[:]:
                        if subordinate.dead:
                            subsubleader.subordinates.remove(subordinate)
                    if len(subsubleader.subordinates) > 2:
                        continue
                    foundSubsubleader = subsubleader

            if not foundSubsubleader:
                actor.addMessage("no rank 5 to hook into")
                return None

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        terrainPosition = self.getTerrainPosition()
        char.registers["HOMETx"] = terrainPosition[0]
        char.registers["HOMETy"] = terrainPosition[1]
        char.personality["abortMacrosOnAttack"] = False

        if rank == 3 and (not cityLeader or cityLeader.dead):
            self.cityLeader = char

        if rank == 4:
            cityLeader.subordinates.append(char)
            char.duties.extend(["scratch checking","clearing","painting"])

        if rank == 5:
            foundSubleader.subordinates.append(char)
            char.duties.extend(["resource fetching","trap setting","hauling","machine placing"])

        if rank == 6:
            foundSubsubleader.subordinates.append(char)
            char.duties.extend(["resource gathering"])

        quest = src.quests.questMap["BeUsefull"]()
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)
        char.faction = actor.faction
        char.isMilitary = False
        if rank:
            char.rank = rank
        self.container.addCharacter(char,5,6)
        char.runCommandString("********")
        char.godMode = True

        return char

src.items.addType(PersonnelTracker)

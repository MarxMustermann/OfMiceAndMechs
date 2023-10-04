import random

import src


class Shrine(src.items.Item):
    """
    """


    type = "Shrine"

    def __init__(self,name="shrine",god=None):
        """
        set up the initial state
        """

        super().__init__(display="\/", name=name)
        self.god = god

        self.applyOptions.extend(
                        [
                                                                ("showInfo", "show Info"),
                                                                ("wish", "wish"),
                                                                ("challenge", "pray"),
                        ]
                        )
        self.applyMap = {
                    "showInfo": self.showInfo,
                    "wish": self.getRewards,
                    "challenge": self.challenge,
                        }

    def isChallengeDone(self):
        if self.god == 1:
            terrain = self.getTerrain()
            god = src.gamestate.gamestate.gods[self.god]
            terrainPos = (terrain.xPosition,terrain.yPosition)
            roomRewardMapByTerrain = god.get("roomRewardMapByTerrain",{})
            lastNumRooms = roomRewardMapByTerrain.get(terrainPos,1)

            numRooms = len(terrain.rooms)

            if numRooms > lastNumRooms:
                return True

        return False

    def challenge(self,character):
        character.changed("prayed",{})

        if self.god == 1:
            terrain = self.getTerrain()
            god = src.gamestate.gamestate.gods[self.god]
            terrainPos = (terrain.xPosition,terrain.yPosition)
            roomRewardMapByTerrain = god.get("roomRewardMapByTerrain",{})
            lastNumRooms = roomRewardMapByTerrain.get(terrainPos,1)

            numRooms = len(terrain.rooms)

            if numRooms <= lastNumRooms:
                character.addMessage("build more rooms.")
                return

            terrain = self.getTerrain()
            increaseAmount = 15*(numRooms-lastNumRooms)

            src.gamestate.gamestate.gods[self.god]["mana"] -= increaseAmount

            terrain.mana += increaseAmount

            character.addMessage(f"your mana increased by {increaseAmount} for building {(numRooms-lastNumRooms)} rooms")
            roomRewardMapByTerrain[terrainPos] = numRooms
            god["roomRewardMapByTerrain"] = roomRewardMapByTerrain
        else:
            1/0

    def showInfo(self,character):
        character.addMessage(self.getTerrain().mana)

    def getCharacterSpawningCost(self,character):
        baseCost = 10
        terrain = self.getTerrain()

        numCharacters = 0
        for otherCharacter in terrain.characters:
            if not otherCharacter.faction == character.faction:
                continue
            numCharacters += 1
        for room in terrain.rooms:
            for otherCharacter in room.characters:
                if not otherCharacter.faction == character.faction:
                    continue
                numCharacters += 1

        baseCost += numCharacters*0.2
        return baseCost

    def getDutyMap(self,character):
        terrain = self.getTerrain()
        charactersOnMap = []
        charactersOnMap.extend(terrain.characters)
        for room in terrain.rooms:
            charactersOnMap.extend(room.characters)
        dutyMap = {}

        for otherCharacter in charactersOnMap:
            if otherCharacter.faction != character.faction:
                continue
            if len(otherCharacter.duties) != 1:
                continue
            dutyMap[otherCharacter.duties[0]] = dutyMap.get(otherCharacter.duties[0],0)+1

        return dutyMap

    def getRewards(self,character,selected=None):
        cost = self.getCharacterSpawningCost(character)

        dutyMap = self.getDutyMap(character)

        options = []
        options.append(("None","(0) None (exit)"))
        if self.god == 1:
            duties = ["resource gathering","resource fetching","hauling","room building","scrap hammering","metal working","machining","painting","scavenging","machine operation","machine placing","maggot gathering","cleaning"]

            for duty in duties:
                options.append((f"spawn {duty} NPC",f"({cost}) {dutyMap.get(duty,0)} spawn {duty} NPC"))
        elif self.god == 2:
            options.append(("spawn scrap","(20) respawn scrap field"))
        else:
            options.append(("spawn personnel tracker","(0) spawn personnel tracker"))
            options.append(("spawn PerformanceTester","(0) spawn PerformanceTester"))
            pass
        submenue = src.interaction.SelectionMenu(f"what do you wish for? You currently have {self.getTerrain().mana} mana",options,targetParamName="rewardType")

        counter = 0
        for option in options:
            counter += 1
            if option[0] == selected:
                submenue.selectionIndex = counter

        submenue.tag = "rewardSelection"
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"dispenseRewards","params":{"character":character}}

    def dispenseRewards(self,extraInfo):
        character = extraInfo.get("character")

        if not "rewardType" in extraInfo:
            return

        if extraInfo["rewardType"] == None:
            return
        if extraInfo["rewardType"] == "None":
            return

        text = "NIY"

        if extraInfo["rewardType"] == "spawn resource gathering NPC":
            text = "You spawned a clone with the duty resource gathering."
            self.spawnBurnedInNPC(character,"resource gathering")
        elif extraInfo["rewardType"] == "spawn machine operation NPC":
            text = "You spawned a clone with the duty machine operation."
            self.spawnBurnedInNPC(character,"machine operation")
        elif extraInfo["rewardType"] == "spawn resource fetching NPC":
            text = "You spawned a clone with the duty resource fetching."
            self.spawnBurnedInNPC(character,"resource fetching")
        elif extraInfo["rewardType"] == "spawn hauling NPC":
            text = "You spawned a clone with the duty hauling."
            self.spawnBurnedInNPC(character,"hauling")
        elif extraInfo["rewardType"] == "spawn painting NPC":
            text = "You spawned a clone with the duty painting."
            self.spawnBurnedInNPC(character,"painting")
        elif extraInfo["rewardType"] == "spawn machine placing NPC":
            text = "You spawned a clone with the duty machine placing."
            self.spawnBurnedInNPC(character,"machine placing")
        elif extraInfo["rewardType"] == "spawn room building NPC":
            text = "You spawned a clone with the duty room building."
            self.spawnBurnedInNPC(character,"room building")
        elif extraInfo["rewardType"] == "spawn maggot gathering NPC":
            text = "You spawned a clone with the duty maggot gathering."
            self.spawnBurnedInNPC(character,"maggot gathering")
        elif extraInfo["rewardType"] == "spawn scavenging NPC":
            text = "You spawned a clone with the duty scavenging."
            self.spawnBurnedInNPC(character,"scavenging")
        elif extraInfo["rewardType"] == "spawn scrap hammering NPC":
            text = "You spawned a clone with the scrap hammering"
            self.spawnBurnedInNPC(character,"scrap hammering")
        elif extraInfo["rewardType"] == "spawn metal working NPC":
            text = "You spawned a clone with the duty metal working"
            self.spawnBurnedInNPC(character,"metal working")
        elif extraInfo["rewardType"] == "spawn machining NPC":
            text = "You spawned a clone with the duty machining"
            self.spawnBurnedInNPC(character,"machining")
        elif extraInfo["rewardType"] == "spawn maggot gathering NPC":
            text = "You spawned a clone with the duty maggot gathering"
            self.spawnBurnedInNPC(character,"maggot gathering")
        elif extraInfo["rewardType"] == "spawn cleaning NPC":
            text = "You spawned a clone with the duty cleaning"
            self.spawnBurnedInNPC(character,"cleaning")

        elif extraInfo["rewardType"] == "spawn scrap":
            text = "spawning scrap"
            self.spawnScrap(character)

        character.changed("got epoch reward",{"rewardType":extraInfo["rewardType"]})
        character.addMessage(text)

        self.getRewards(character,selected=extraInfo["rewardType"])

    def spawnBurnedInNPC(self, character, duty):
        cost = self.getCharacterSpawningCost(character)
        mana = self.getTerrain().mana
        text = ""
        if not mana >= cost:
            text = "not enough mana"
        else:
            self.getTerrain().mana -= cost
            src.gamestate.gamestate.gods[self.god]["mana"] += cost/2

            npc = src.characters.Character()
            npc.questsDone = [
                "NaiveMoveQuest",
                "MoveQuestMeta",
                "NaiveActivateQuest",
                "ActivateQuestMeta",
                "NaivePickupQuest",
                "PickupQuestMeta",
                "DrinkQuest",
                "CollectQuestMeta",
                "FireFurnaceMeta",
                "ExamineQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
                "LeaveRoomQuest",
            ]

            npc.solvers = [
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
                "WaitQuest" "NaiveDropQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
            ]

            room = self.container
            terrain = self.container.container

            npc.faction = character.faction
            #npc.rank = 6
            room.addCharacter(npc,self.xPosition,self.yPosition)
            npc.flask = src.items.itemMap["GooFlask"]()
            npc.flask.uses = 100

            npc.duties = []
            #duty = random.choice(("hauling","resource fetching","maggot gathering","resource gathering","machine operation","hauling","resource fetching","cleaning","machine placing","maggot gathering"))
            #duty = random.choice(("maggot gathering",))
            if duty:
                npc.duties.append(duty)
            npc.registers["HOMEx"] = 7
            npc.registers["HOMEy"] = 7
            npc.registers["HOMETx"] = terrain.xPosition
            npc.registers["HOMETy"] = terrain.yPosition

            npc.personality["autoFlee"] = False
            npc.personality["abortMacrosOnAttack"] = False
            npc.personality["autoCounterAttack"] = False

            quest = src.quests.questMap["BeUsefull"](strict=True)
            quest.autoSolve = True
            quest.assignToCharacter(npc)
            quest.activate()
            npc.assignQuest(quest,active=True)
            npc.foodPerRound = 1

            '''
            numNewRooms = len(terrain.rooms)-state.get("lastNumRooms",1)
            while numNewRooms > 0:
                itemType = random.choice([("personelArtwork","DutyArtwork","OrderArtwork")])
                item = itemMap
                item = src.items.
                text = """
You have build a new room. you are rewarded with an extra item:

The item will appear in your inventory.

press enter to continue"""%(npc.name,duty,terrain)
                src.interaction.showInterruptText(text)
            '''
            text = f"spawning burned in NPC ({duty})"

        if character:
            character.addMessage(text)

    def spawnScrap(self, character):
        mana = self.getTerrain().mana
        text = ""
        if not mana >= 20:
            text = "not enough glass tears"
        else:
            self.getTerrain().mana -= 20

            text = "spawning scrap field"
            terrain = self.getTerrain()
            items = []
            for scrapField in terrain.scrapFields:
                for _i in range(30):
                    pos = (scrapField[0]*15+random.randint(1,13),scrapField[1]*15+random.randint(1,13),0)
                    scrap = src.items.itemMap["Scrap"](amount=random.randint(15,20))
                    terrain.addItem(scrap,pos)

            text = "spawing food into your inventory"

        if character:
            character.addMessage(text)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Shrine")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Shrine")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        return f"{self.god}"

src.items.addType(Shrine)

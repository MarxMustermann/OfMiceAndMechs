import random

import src
import math


class Shrine(src.items.Item):
    """
    """


    type = "Shrine"

    def __init__(self,name="shrine",god=None):
        """
        set up the initial state
        """

        super().__init__(display="\\/", name=name)
        self.god = god

        self.applyOptions.extend(
                        [
                                                                ("showInfo", "show Info"),
                                                                ("wish", "wish"),
                                                                ("challenge", "pray"),
                                                                ("teleport", "telport home"),
                        ]
                        )
        self.applyMap = {
                    "showInfo": self.showInfo,
                    "wish": self.getRewards,
                    "challenge": self.challenge,
                    "teleport": self.teleport,
                        }

    def teleport(self,character):
        x = character.registers["HOMETx"]
        y = character.registers["HOMETy"]
        newTerrain = src.gamestate.gamestate.terrainMap[y][x]

        bigPos = (7,7)
        character.container.removeCharacter(character)
        room = newTerrain.getRoomByPosition(bigPos)
        if room:
            room[0].addCharacter(character,7,7)
        else:
            newTerrain.addCharacter(character,15*bigPos[0]+7,15*bigPos[1]+7)
        character.changed("changedTerrain",{"character":character})

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

    def setGod1(self,character):
        options = []
        options.append((1,"1 - god of fertility"))
        options.append((2,"2 - god of desolution"))
        options.append((3,"3 - god of construction"))
        options.append((4,"4 - god of fighting"))
        options.append((5,"5 - god of battle gear"))
        options.append((6,"6 - god of life"))
        options.append((7,"7 - god of crushing"))
        options.append((None,"all gods"))

        submenu = src.interaction.SelectionMenu(
            "Select what god to pray to", options,
            targetParamName="god",
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
                "container": self,
                "method": "setGod2",
                "params": {"character":character},
        }

    def setGod2(self,extraInfo):
        # convert parameters to local variables
        godID = extraInfo["god"]
        character = extraInfo["character"]

        # determine what items are needed
        needItems = src.gamestate.gamestate.gods[godID]["sacrifice"]

        # handle the item requirements
        if needItems:
            itemType = needItems[0]
            amount = needItems[1]

            if itemType == "Scrap":
                ##
                # handle scrap special case

                # find scrap to take as saccrifice
                numScrapFound = 0
                scrap = self.container.getItemsByType("Scrap")
                for item in scrap:
                    numScrapFound += item.amount

                # ensure that there is enough scrap around
                if not numScrapFound >= 15:
                    character.addMessage("not enough scrap")
                    return

                # remove the scrap
                numScrapRemoved = 0
                for item in scrap:
                    if item.amount <= amount-numScrapRemoved:
                        self.container.removeItem(item)
                        numScrapRemoved += item.amount
                    else:
                        item.amount -= amount-numScrapRemoved
                        item.setWalkable()
                        numScrapRemoved += amount-numScrapRemoved

                    if numScrapRemoved >= amount:
                        break
                character.addMessage(f"you sacrifice {numScrapRemoved} Scrap")
            else:
                ##
                # handle normal items

                # get the items
                itemsFound = self.container.getItemsByType(itemType,needsUnbolted=True)

                # ensure item requirement can be fullfilled
                if not len(itemsFound) >= amount:
                    character.addMessage(f"you need {amount} {itemType}")
                    return

                # remove items from requirement
                character.addMessage(f"you sacrifice {amount} {itemType}")
                while amount > 0:
                    self.container.removeItem(itemsFound.pop())
                    amount -= 1

        character.addMessage(f"you set the shrine to god {godID}")
        self.god = godID

    def challenge(self,character):
        if self.god is None:
            self.setGod1(character)
            return
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
        elif self.god == 2:
            options = []
            options.append((100,"100"))
            options.append((1000,"1000"))
            options.append((10000,"10000"))
            submenue = src.interaction.SelectionMenu("How long do you want to pray?",options,targetParamName="duration")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"waitPraySelection","params":{"character":character}}
        else:
            character.addMessage("nothing happens - not implemented yet")

    def waitPraySelection(self,extraInfo):
        duration = extraInfo["duration"]
        character = extraInfo["character"]

        if not duration:
            return

        params = {}
        params["character"] = character
        params["productionTime"] = duration
        params["doneProductionTime"] = 0
        self.waitPrayWait(params)

    def waitPrayWait(self,params):
        character = params["character"]
        ticksLeft = params["productionTime"]-params["doneProductionTime"]

        progressbar = "X"*(params["doneProductionTime"]//100)+"."*(ticksLeft//100)

        progressbarWithNewlines = ""

        counter = 0
        for char in progressbar:
            counter += 1
            progressbarWithNewlines += char
            if counter%10 == 0:
                progressbarWithNewlines += "\n"
        if progressbarWithNewlines[-1] == "\n":
            progressbarWithNewlines = progressbarWithNewlines[:-1]

        if ticksLeft > 100:
            character.timeTaken += 100
            params["doneProductionTime"] += 100
            submenue = src.interaction.OneKeystrokeMenu(progressbarWithNewlines,targetParamName="abortKey")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"waitPrayWait","params":params}
        else:
            character.timeTaken += ticksLeft
            params["doneProductionTime"] += ticksLeft
            submenue = src.interaction.OneKeystrokeMenu(progressbarWithNewlines,targetParamName="abortKey")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"waitPrayEnd","params":params}
        character.runCommandString(".",nativeKey=True)

    def waitPrayEnd(self,extraInfo):
        character = extraInfo["character"]
        duration = extraInfo["productionTime"]

        terrain = self.getTerrain()
        increaseAmount = duration//100
        terrain.mana += increaseAmount

        character.addMessage(f"you prayed {duration} ticks and gain {increaseAmount} mana")

    def showInfo(self,character):

        character.addMessage(f"mana: {self.getTerrain().mana}")

        if self.god == 1:
            character.addMessage("this god can spawn NPCs")
        if self.god == 2:
            character.addMessage("this god can spawn ressources")
        if self.god == 3:
            character.addMessage("this god can spawn walls")
        if self.god == 4:
            character.addMessage("this god can improve your attack speed")
        if self.god == 5:
            character.addMessage("this god can improve your armor or weapon")
        if self.god == 6:
            character.addMessage("this god can improve your max health")
        if self.god == 7:
            character.addMessage("this god can improve your base damage")

    def getCharacterSpawningCost(self,character):
        baseCost = 30
        terrain = self.getTerrain()

        numCharacters = 0
        for otherCharacter in terrain.characters:
            if otherCharacter.faction != character.faction:
                continue
            if otherCharacter.burnedIn:
                continue
            numCharacters += 1
        for room in terrain.rooms:
            for otherCharacter in room.characters:
                if otherCharacter.faction != character.faction:
                    continue
                if otherCharacter.burnedIn:
                    continue
                numCharacters += 1

        baseCost *= 1.05**numCharacters
        baseCost = math.ceil(baseCost*10)/10
        return baseCost

    def getBurnedInCharacterSpawningCost(self,character):
        baseCost = 10
        terrain = self.getTerrain()

        numCharacters = 0
        for otherCharacter in terrain.characters:
            if otherCharacter.faction != character.faction:
                continue
            if not otherCharacter.burnedIn:
                continue
            numCharacters += 1
        for room in terrain.rooms:
            for otherCharacter in room.characters:
                if otherCharacter.faction != character.faction:
                    continue
                if not otherCharacter.burnedIn:
                    continue
                numCharacters += 1

        baseCost *= 1.05**numCharacters
        baseCost = math.ceil(baseCost*10)/10
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
            if not otherCharacter.burnedIn:
                continue
            dutyMap[otherCharacter.duties[0]] = dutyMap.get(otherCharacter.duties[0],0)+1

        return dutyMap

    def get_glass_heart_rebate(self):
        if self.god == None:
            return 1

        if src.gamestate.gamestate.gods[self.god]["lastHeartPos"] == (self.getTerrain().xPosition,self.getTerrain().yPosition):
            return 0.5
        else:
            return 1

    def getCost(self,wishType,character):
        baseCost = 1
        if wishType == "spawn scrap":
            baseCost = 20
        if wishType == "spawn walls":
            baseCost = 10

        glassHeartRebate = self.get_glass_heart_rebate()
        baseCost = baseCost*glassHeartRebate

        return baseCost

    def getRewards(self,character,selected=None):
        glassHeartRebate = self.get_glass_heart_rebate()

        options = []
        options.append(("None","(0) None (exit)"))
        if self.god == 1:
            cost = self.getCharacterSpawningCost(character)
            cost *= glassHeartRebate

            foundFlask = None
            for item in character.inventory:
                if item.type != "GooFlask":
                    continue
                if item.uses < 100:
                    continue
                foundFlask = item
            if foundFlask:
                cost /= 2

            options.append((f"spawn true NPC",f"({cost}) spawn NPC"))

            cost = self.getBurnedInCharacterSpawningCost(character)
            cost *= glassHeartRebate
            if foundFlask:
                cost /= 2

            duties = ["resource gathering","resource fetching","hauling","room building","scrap hammering","metal working","machining","painting","scavenging","machine operation","machine placing","maggot gathering","cleaning","manufacturing"]
            dutyMap = self.getDutyMap(character)

            for duty in duties:
                specificCost = cost*(dutyMap.get(duty,0)+1)
                specificCost = math.ceil(specificCost*10)/10
                options.append((f"spawn {duty} NPC",f"({specificCost}) {dutyMap.get(duty,0)} spawn {duty} NPC"))

        elif self.god == 2:
            cost = self.getCost("spawn scrap",character)
            options.append(("spawn scrap",f"({cost}) respawn scrap field"))

        elif self.god == 3:
            cost = self.getCost("spawn walls",character)
            options.append(("spawn walls",f"({cost}) spawn walls"))

        elif self.god == 4:
            cost = 10
            cost *= glassHeartRebate
            if character.attackSpeed <= 0.5:
                character.addMessage("you can't improve your attack speed further")
                return
            options.append(("upgrade attack speed",f"({cost}) upgrade attack speed"))
            options.append(("upgrade movement speed",f"({cost}) upgrade movement speed"))

        elif self.god == 5:
            foundArmor = None
            foundWeapon = None
            numMetalBars = 0
            for item in character.inventory:
                if item.type == "Sword":
                    foundWeapon = item
                    continue
                if item.type == "Armor":
                    foundArmor = item
                    continue
                if item.type == "MetalBars":
                    numMetalBars += 1
                    continue

            if character.armor and character.armor.armorValue < 8:
                cost = 10
                if foundArmor:
                    cost = cost/2
                cost *= glassHeartRebate
                options.append(("improve armor",f"({cost}) improve armor"))

            if character.weapon and character.weapon.baseDamage < 30:
                cost = 10
                if foundWeapon:
                    cost = cost/2
                cost *= glassHeartRebate
                options.append(("upgrade weapon",f"({cost}) upgrade weapon"))

            cost = 10
            cost = cost-0.5*numMetalBars
            cost *= glassHeartRebate
            options.append(("spawnBolts",f"({cost}) spawn bolts"))

        elif self.god == 6:

            cost = 10
            foundVial = None
            for item in character.inventory:
                if item.type != "Vial":
                    continue
                if item.uses < 10:
                    continue
                foundVial = item
            if foundVial:
                cost /= 2

            if character.maxHealth >= 500:
                character.addMessage("you can't improve your health further")
                return
            cost *= glassHeartRebate
            options.append(("improve your max health",f"({cost}) improve your max health"))

            cost = 5
            cost *= glassHeartRebate
            options.append(("heal",f"({cost}) heal"))
            #options.append(("healingThreashold","(10) improve your healing threashold"))
            #options.append(("healingModifier","(10) improve your healing amount"))

        elif self.god == 7:
            if character.baseDamage >= 10:
                character.addMessage("you can't improve your base damage further")
                return

            options.append(("improve base damage","(10) improve your base damage"))

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
        glassHeartRebate = self.get_glass_heart_rebate()

        character = extraInfo.get("character")

        if "rewardType" not in extraInfo:
            return

        if extraInfo["rewardType"] is None:
            return
        if extraInfo["rewardType"] == "None":
            return

        text = "NIY"

        if extraInfo["rewardType"] == "spawn true NPC":
            text = "You spawned a clone"
            self.spawnNPC(character)
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
        elif extraInfo["rewardType"] == "spawn manufacturing NPC":
            text = "You spawned a clone with the duty manufacturing"
            self.spawnBurnedInNPC(character,"manufacturing")

        elif extraInfo["rewardType"] == "spawn scrap":
             self.spawnScrap(character)
             text = None

        elif extraInfo['rewardType'] == "upgrade weapon":
            foundWeapon = None
            for item in character.inventory:
                if item.type == "Sword":
                    foundWeapon = item
                    continue

            cost = 10
            if foundWeapon:
                cost = cost/2
            cost *= glassHeartRebate

            text = "upgrading weapon"
            if self.getTerrain().mana >= cost:
                increaseValue = 4
                increaseValue = min(30-character.weapon.baseDamage,increaseValue)
                character.weapon.baseDamage += increaseValue
                character.addMessage(f"your weapons base damage is increased by {increaseValue} to {character.weapon.baseDamage}")
                self.getTerrain().mana -= cost
                if foundWeapon:
                    character.inventory.remove(foundWeapon)
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "upgrade attack speed":
            cost = 10
            cost *= glassHeartRebate

            text = "upgrading attack speed"
            if self.getTerrain().mana >= cost:
                increaseValue = 0.1*character.attackSpeed
                increaseValue = min(character.attackSpeed-0.5,increaseValue)
                character.attackSpeed -= increaseValue
                character.addMessage(f"your attack speed is improved by {increaseValue} to {character.attackSpeed}")
                self.getTerrain().mana -= cost
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "upgrade movement speed":
            cost = 10
            cost *= glassHeartRebate

            text = "upgrading movement speed"
            if self.getTerrain().mana >= cost:
                increaseValue = 0.1
                increaseValue = min(character.movementSpeed-0.5,increaseValue)
                character.movementSpeed -= increaseValue
                character.addMessage(f"your movement speed is improved by {increaseValue} to {character.movementSpeed}")
                self.getTerrain().mana -= cost
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "improve armor":
            foundArmor = None
            for item in character.inventory:
                if item.type == "Armor":
                    foundArmor = item
                    continue

            cost = 10
            if foundArmor:
                cost = cost/2
            cost *= glassHeartRebate

            if self.getTerrain().mana >= cost:
                text = "improving armor"
                increaseValue = 0.5
                increaseValue = min(8-character.armor.armorValue,increaseValue)
                character.armor.armorValue += increaseValue
                character.addMessage(f"your armors armor value is increased by {increaseValue} to {character.armor.armorValue}")
                self.getTerrain().mana -= cost
                if foundArmor:
                    character.inventory.remove(foundArmor)
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "improve your max health":
            cost = 10
            foundVial = None
            for item in character.inventory:
                if item.type != "Vial":
                    continue
                if item.uses < 10:
                    continue
                foundVial = item
            if foundVial:
                cost /= 2
            cost *= glassHeartRebate

            if self.getTerrain().mana >= cost:
                text = "improving your health"
                increaseValue = 20
                increaseValue = min(500-character.maxHealth,increaseValue)
                character.maxHealth += increaseValue
                character.addMessage(f"your max health is increased by {increaseValue} to {character.maxHealth}")
                self.getTerrain().mana -= cost
                if foundVial:
                    character.inventory.remove(foundVial)
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "heal":
            cost = 5
            cost *= glassHeartRebate

            if self.getTerrain().mana >= cost:
                text = "healing"
                character.heal(200,"wishing for health")
                character.addMessage(f"your are healed")
                self.getTerrain().mana -= cost
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "improve base damage":
            if self.getTerrain().mana >= 10:
                text = "increasing base damage"
                increaseValue = 2
                increaseValue = min(10-character.baseDamage,increaseValue)
                character.baseDamage += increaseValue
                character.addMessage(f"your base damage is increased by {increaseValue} to {character.baseDamage}")
                self.getTerrain().mana -= 10
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "spawn walls":
            cost = 10
            cost *= glassHeartRebate
            if self.getTerrain().mana >= cost:
                text = "spawning walls"
                for _i in range(0,10):
                    item = src.items.itemMap["Wall"]()
                    item.bolted = False
                    character.inventory.append(item)
                self.getTerrain().mana -= cost
            else:
                character.addMessage(f"the mana is used up")

        elif extraInfo['rewardType'] == "spawnBolts":
            cost = 10

            foundWeapons = []
            for item in character.inventory:
                if item.type == "MetalBars":
                    foundWeapons.append(item)

            for foundWeapon in foundWeapons:
                character.inventory.remove(foundWeapon)
                cost -= 0.5
            cost *= glassHeartRebate
            if self.getTerrain().mana >= cost:
                text = "spawning bolts"
                for _i in range(0,10):
                    item = src.items.itemMap["Bolt"]()
                    item.bolted = False
                    character.inventory.append(item)
                self.getTerrain().mana -= cost
            else:
                character.addMessage(f"the mana is used up")

        self.getRewards(character,selected=extraInfo["rewardType"])

        character.changed("got epoch reward",{"rewardType":extraInfo["rewardType"]})
        if text:
            character.addMessage(text)

    def spawnNPC(self, character):
        cost = self.getCharacterSpawningCost(character)
        glassHeartRebate = self.get_glass_heart_rebate()
        mana = self.getTerrain().mana

        foundFlask = None
        for item in character.inventory:
            if item.type != "GooFlask":
                continue
            if item.uses < 100:
                continue
            foundFlask = item
        if foundFlask:
            cost /= 2
        cost *= glassHeartRebate

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

            npc.duties.append("resource gathering")
            npc.duties.append("scrap hammering")
            npc.duties.append("resource fetching")
            npc.duties.append("hauling")
            npc.duties.append("metal working")
            npc.duties.append("machine placing")
            npc.duties.append("maggot gathering")
            npc.duties.append("painting")
            npc.duties.append("cleaning")
            npc.duties.append("machine operation")
            npc.duties.append("manufacturing")

            text = f"spawned NPC"

            if foundFlask:
                character.inventory.remove(foundFlask)

        if character:
            character.addMessage(text)


    def spawnBurnedInNPC(self, character, duty):
        cost = self.getBurnedInCharacterSpawningCost(character)
        glassHeartRebate = self.get_glass_heart_rebate()
        mana = self.getTerrain().mana

        foundFlask = None
        for item in character.inventory:
            if item.type != "GooFlask":
                continue
            if item.uses < 100:
                continue
            foundFlask = item
        if foundFlask:
            cost /= 2
        cost *= glassHeartRebate

        dutyMap = self.getDutyMap(character)
        cost = cost*dutyMap.get(duty,1)

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
            npc.burnedIn = True

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

            if foundFlask:
                character.inventory.remove(foundFlask)

        if character:
            character.addMessage(text)

    def spawnScrap(self, character):
        cost = self.getCost("spawn scrap",character)
        mana = self.getTerrain().mana
        text = ""
        if not mana >= cost:
            text = "not enough glass tears"
        else:
            self.getTerrain().mana -= cost

            text = "spawning scrap field"
            terrain = self.getTerrain()
            items = []
            for scrapField in terrain.scrapFields:
                for _i in range(30):
                    pos = (scrapField[0]*15+random.randint(1,13),scrapField[1]*15+random.randint(1,13),0)
                    scrap = src.items.itemMap["Scrap"](amount=random.randint(15,20))
                    terrain.addItem(scrap,pos)

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
        return f"""
A shrine allows to interact with a god.

You can wish for things or other favours.

This shrine is set to the god {self.god}.
"""

    def render(self):
        color = "#888"
        if self.god == 1:
            color = "#f00"
        elif self.god == 2:
            color = "#0f0"
        elif self.god == 3:
            color = "#00f"
        elif self.god == 4:
            color = "#0ff"
        elif self.god == 5:
            color = "#f0f"
        elif self.god == 6:
            color = "#ff0"
        elif self.god == 7:
            color = "#fff"
        display = [
                (src.interaction.urwid.AttrSpec(color, "black"), "\\/"),
            ]
        return display

src.items.addType(Shrine)

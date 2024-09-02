import src


class GlassStatue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "GlassStatue"
    description = "Used to pray to the gods."
    name = "glassStatue"

    def __init__(self,itemID=None):
        '''
        set up internal state
        '''
        super().__init__("GG")

        self.applyOptions.extend(
                        [
                                                                ("showInfo", "show Info"),
                                                                ("pray", "pray"),
                                                                ("getSetHeart", "remove/set glass heart"),
                                                                ("teleport", "teleport to dungeon"),
                        ]
                        )
        self.applyMap = {
                    "showInfo": self.showInfo,
                    "pray": self.pray,
                    "showChallenges": self.showChallenges,
                    "getExtraChallenge": self.getExtraChallenge,
                    "getReward": self.getReward,
                    "teleport": self.teleport,
                    "getSetHeart": self.getSetHeart,
                        }
        self.itemID = itemID
        self.challenges = []
        self.hasItem = False
        self.charges = 2
        self.stable = False
        self.numSubSacrifices = 0

    def handleItemRequirements(self,removeItems=False,character=None):
        # determine what items are needed
        if self.itemID == None:
            return
        needItems = src.gamestate.gamestate.gods[self.itemID]["sacrifice"]
        completed = False

        # handle the item requirements
        if needItems:
            itemType = needItems[0]
            amount = needItems[1]-self.numSubSacrifices

            if itemType == "Scrap":
                ##
                # handle scrap special case

                # find scrap to take as saccrifice
                numScrapFound = 0
                scrap = self.container.getItemsByType("Scrap")
                for item in scrap:
                    numScrapFound += item.amount

                # ensure that there is enough scrap around
                if not numScrapFound:
                    if character:
                        text = "no Scrap to offer\n\nPlace the Scrap to offer on the floor of this room."
                        submenue = src.interaction.TextMenu(text)
                        character.macroState["submenue"] = submenue
                        character.addMessage(text)
                    return

                # remove the scrap
                numScrapRemoved = 0
                if removeItems:
                    for item in scrap:
                        if item.amount <= amount-numScrapRemoved:
                            self.container.removeItem(item)
                            numScrapRemoved += item.amount
                            self.numSubSacrifices += item.amount
                        else:
                            item.amount -= amount-numScrapRemoved
                            item.setWalkable()
                            numScrapRemoved += amount-numScrapRemoved
                            self.numSubSacrifices += amount-numScrapRemoved

                        if numScrapRemoved >= amount:
                            completed = True
                            break
                text = f"you sacrifice {numScrapRemoved}/{amount} Scrap"
            else:
                ##
                # handle normal items

                # get the items
                itemsFound = self.container.getItemsByType(itemType,needsUnbolted=True)

                # ensure item requirement can be fullfilled
                if not len(itemsFound):
                    if character:
                        text = f"you need to offer {itemType}.\n\nPlace the offered items on the floor of this room."
                        submenue = src.interaction.TextMenu(text)
                        character.macroState["submenue"] = submenue
                        character.addMessage(text)
                    return

                if len(itemsFound) >= amount:
                    completed = True

                # remove items from requirement
                text = f"you sacrifice {min(amount,len(itemsFound))}/{amount} {itemType}"
                if removeItems:
                    while amount > 0 and itemsFound:
                        self.container.removeItem(itemsFound.pop())
                        amount -= 1
                        self.numSubSacrifices += 1
        return (completed,text)

    def pray(self,character):
        character.changed("prayed",{})

        if self.charges >= 9:
            text = f"the glass statue has maximum charges now"
            submenue = src.interaction.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.addMessage(text)
            return

        result = self.handleItemRequirements(removeItems=True,character=character)
        if not result:
            return
        text = result[1]
        completed = result[0]

        if completed:
            self.charges += 1
            self.numSubSacrifices = 0
            text += f"\n\nThe GlassStatue has {self.charges} charges now."
            if self.charges == 5:
                text += f"\nYou can use the GlassStatue to teleport to the dugeon now."
        else:
            text += f"\n\nyour saccrifice was not enough for another charge"


        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.addMessage(text)

    def render(self):
        color = "#888"
        if self.itemID == 1:
            color = "#f00"
        elif self.itemID == 2:
            color = "#0f0"
        elif self.itemID == 3:
            color = "#00f"
        elif self.itemID == 4:
            color = "#0ff"
        elif self.itemID == 5:
            color = "#f0f"
        elif self.itemID == 6:
            color = "#ff0"
        elif self.itemID == 7:
            color = "#fff"
        displaychars = "GG"

        if not self.hasItem:
            # search for glass hearts in the players inventory
            if self.charges < 5:
                displaychars = f"G{self.charges}"
            else:
                displaychars = "GG"

            mainCharHasItem = False
            for item in src.gamestate.gamestate.mainChar.inventory:
                if not item.type == "SpecialItem":
                    continue
                if not item.itemID == self.itemID:
                    continue
                displaychars = "kk"
                break
        else:
            displaychars = "KK"

        display = [
                (src.interaction.urwid.AttrSpec(color, "black"), displaychars),
            ]
        return display

    def handleEpochChange(self):
        if self.stable:
            return
        if not self.container:
            return

        self.charges -= 1
        if self.charges == 0:
            self.destroy()
            return

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15))+10)
        event.setCallback({"container": self, "method": "handleEpochChange"})
        self.container.addEvent(event)


    def teleport(self,character):
        if self.charges < 5:
            character.addMessage(f"not enough charges ({self.charges}/5)")
            return
        character.addMessage(str(src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"]))

        (x,y) = src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"]
        newTerrain = src.gamestate.gamestate.terrainMap[y][x]

        bigPos = (3,7)

        character.container.removeCharacter(character)
        newTerrain.addCharacter(character,15*bigPos[0]+13,15*bigPos[1]+7)

        self.charges -= 1

        character.changed("glass statue used",{})

    def showInfo(self,character):
        character.addMessage(f"mana: {self.getTerrain().mana}\ncharges: {self.charges}")

        if self.itemID:
            character.addMessage(str(src.gamestate.gamestate.gods[self.itemID]))
        else:
            character.addMessage(str(src.gamestate.gamestate.gods))

        if self.itemID == 1:
            character.addMessage("this god can spawn NPCs")
        if self.itemID == 2:
            character.addMessage("this god can spawn ressources")
        if self.itemID == 3:
            character.addMessage("this god can improve your weapon")
        if self.itemID == 4:
            character.addMessage("this god can improve your attack speed")
        if self.itemID == 5:
            character.addMessage("this god can improve your armor")
        if self.itemID == 6:
            character.addMessage("this god can improve your max health")
        if self.itemID == 7:
            character.addMessage("this god can improve your base damage")


    def showChallenges(self,character):
        character.addMessage(str(self.challenges))

    def getExtraChallenge(self,character):
        character.addMessage(self.itemID)
        if self.itemID < 3:
            character.addMessage("bring me corpses")
        else:
            character.addMessage("bring me mold feeds")
        self.challenges.append(("corpses",src.gamestate.gamestate.tick))

    def dispenseRewards(self,extraInfo):
        character = extraInfo.get("character")

        if "rewardType" not in extraInfo:
            return

        if extraInfo["rewardType"] is None:
            return
        if extraInfo["rewardType"] == "None":
            return

        elif extraInfo["rewardType"] == "spawn resource gathering NPC":
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

        character.changed("got epoch reward",{"rewardType":extraInfo["rewardType"]})
        character.addMessage(text)

    def spawnBurnedInNPC(self, character, duty):
        text = ""
        if not self.charges >= 10:
            text = "not enough glass tears"
        else:
            self.changeCharges(-10)

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
                "WaitQuest",
                "NaiveDropQuest",
                "DropQuestMeta",
            ]

            room = self.container
            terrain = self.container.container

            npc.faction = character.faction
            room.addCharacter(npc,self.xPosition,self.yPosition)
            npc.flask = src.items.itemMap["GooFlask"]()
            npc.flask.uses = 100

            npc.duties = []
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

            text = f"spawning burned in NPC ({duty})"

        if character:
            character.addMessage(text)

    def getReward(self,character):
        if not self.hasItem:
            character.addMessage("Nothing happeend. This statue needs a glass heart")
            return
        corpses = []
        for item in character.inventory:
            if item.type != "MoldFeed":
                continue
            corpses.append(item)

        godInfo = src.gamestate.gamestate.gods.get(self.itemID,None)

        if self.itemID == 1:
            options = []
            options.append(("None","None (exit)"))
            options.append(("spawn resource gathering NPC","spawn gatherer"))
            options.append(("spawn resource fetching NPC","spawn fetcher"))
            options.append(("spawn hauling NPC","spawn hauler"))
            options.append(("spawn room building NPC","spawn room builder"))
            options.append(("spawn scrap hammering NPC","spawn scrap hammerer"))
            options.append(("spawn metal working NPC","spawn metal worker"))
            options.append(("spawn machining NPC","spawn machining worker"))
            options.append(("spawn painting NPC","spawn painter"))
            options.append(("spawn scavenging NPC","spawn scavenger"))
            options.append(("spawn machine operation NPC","spawn machine operator"))
            options.append(("spawn machine placing NPC","spawn machine placer"))
            options.append(("spawn maggot gathering NPC","spawn maggot gatherer"))
            options.append(("spawn cleaning NPC","spawn cleaner"))

            submenue = src.interaction.SelectionMenu("what reward do you desire?",options,targetParamName="rewardType")
            submenue.tag = "rewardSelection"
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"dispenseRewards","params":{"character":character}}
            return
        elif self.itemID == 2:
            pass
        elif self.itemID == 3:
            if not character.weapon:
                character.addMessage("you don't have a weapon to upgrade")
                return

            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1
                if godInfo.get("mana",0) < 200:
                    character.addMessage("your god reserves its remaining power for challenges")

                rewardFactor = 0
                if godInfo.get("mana",0) <= 205:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 220:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 275:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 300:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 450:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 700:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 1*rewardFactor

                if character.weapon.baseDamage >= 30:
                    character.addMessage("you can't improve your weapon further")
                    return

                increaseValue = min(30-character.weapon.baseDamage,increaseValue)

                godInfo["mana"] -= 10
                character.weapon.baseDamage += increaseValue
                character.addMessage(f"your weapons base damage is increased by {increaseValue} to {character.weapon.baseDamage}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return

        elif self.itemID == 4:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.1*rewardFactor

                if character.attackSpeed <= 0.5:
                    character.addMessage("you can't improve your attack speed further")
                    return

                increaseValue = min(character.attackSpeed-0.5,increaseValue)

                godInfo["mana"] -= 10
                character.attackSpeed -= increaseValue
                character.addMessage(f"your attack speed is improved by {increaseValue} to {character.attackSpeed}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return

            pass

        elif self.itemID == 5:
            if not character.armor:
                character.addMessage("you don't have a armor to upgrade")
                return

            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.2*rewardFactor

                if character.armor.armorValue >= 8:
                    character.addMessage("you can't improve your armor further")
                    return

                increaseValue = min(8-character.armor.armorValue,increaseValue)

                godInfo["mana"] -= 10
                character.armor.armorValue += increaseValue
                character.addMessage(f"your armors armor value is increased by {increaseValue} to {character.armor.armorValue}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        elif self.itemID == 6:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 10*rewardFactor

                if character.maxHealth >= 500:
                    character.addMessage("you can't improve your health further")
                    return

                increaseValue = min(500-character.maxHealth,increaseValue)

                godInfo["mana"] -= 10
                character.maxHealth += increaseValue
                character.addMessage(f"your max health is increased by {increaseValue} to {character.maxHealth}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        elif self.itemID == 7:
            numCorpses = 0
            for corpse in corpses:
                numCorpses += 1

                if godInfo.get("mana",0) < 200:
                    character.addMessage("your god reserves its remaining power for challenges")

                if godInfo.get("mana",0) < 10:
                    character.addMessage("your god has not enough power anymore")
                    return

                rewardFactor = 0
                if godInfo.get("mana",0) <= 5:
                    rewardFactor = 0.2
                elif godInfo.get("mana",0) <= 20:
                    rewardFactor = 0.5
                elif godInfo.get("mana",0) <= 50:
                    rewardFactor = 0.75
                elif godInfo.get("mana",0) <= 75:
                    rewardFactor = 0.85
                elif godInfo.get("mana",0) <= 100:
                    rewardFactor = 1
                elif godInfo.get("mana",0) <= 250:
                    rewardFactor = 2
                elif godInfo.get("mana",0) <= 500:
                    rewardFactor = 4
                else:
                    rewardFactor = 6

                increaseValue = 0.1*rewardFactor

                if character.baseDamage >= 10:
                    character.addMessage("you can't improve your base damage further")
                    return

                increaseValue = min(10-character.baseDamage,increaseValue)

                godInfo["mana"] -= 10
                character.baseDamage += increaseValue
                character.addMessage(f"your base damage is increased by {increaseValue} to {character.baseDamage}")
                character.inventory.remove(corpse)

            if not numCorpses:
                character.addMessage("you have no corpses with you")
                return
        else:
            character.addMessage("unknown god")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
            if not self.hasItem:
                options["g"] = ("set glass heart", self.setGlassHeart)
            else:
                options["g"] = ("remove glass heart", self.removeGlassHeart)
                options["r"] = ("release glass heart", self.releaseGlassHeart)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def getSetHeart(self,character):
        if self.hasItem:
            self.removeGlassHeart(character)
        else:
            self.setGlassHeart(character)
            self.stable = True

    def releaseGlassHeart(self,character):
        if self.hasItem:
            src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"] = src.gamestate.gamestate.gods[self.itemID]["home"]
            print(src.gamestate.gamestate.gods[self.itemID])
            self.hasItem = False

    def removeGlassHeart(self,character):
        newItem = src.items.itemMap["SpecialItem"](epoch=src.gamestate.gamestate.tick//(15*15*15))
        newItem.itemID = self.itemID
        self.container.addItem(newItem,character.getPosition())

        self.hasItem = False
        character.movementSpeed = character.movementSpeed*2

    def setGlassHeart(self,character):
        self.getTerrain().mana += 10

        glassHeart = None
        hasHeart = False
        for item in character.inventory:
            #if not item.type == "GlassHeart":
            if item.type != "SpecialItem":
                continue
            if item.itemID != self.itemID:
                continue
            glassHeart = item
            hasHeart = True

        if not hasHeart:
            character.addMessage("you have no glass heart to set")
            return

        if not glassHeart:
            character.addMessage("you do not have the right glass heart to set")
            return

        if glassHeart.epoch < src.gamestate.gamestate.tick//(15*15*15):
            character.addMessage("the heart stpped beating and shatters. Transer the heart faster next time.")
            character.inventory.remove(glassHeart)
            character.movementSpeed = character.movementSpeed/2
            return

        self.hasItem = True
        character.inventory.remove(glassHeart)
        src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"] = (character.getTerrain().xPosition,character.getTerrain().yPosition)
        character.movementSpeed = character.movementSpeed/2
        character.changed("deliveredSpecialItem",{"itemID":self.itemID})

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        godName = src.gamestate.gamestate.gods[self.itemID]["name"]
        sacrifice = src.gamestate.gamestate.gods[self.itemID]["sacrifice"]
        return f"""This is a GlassStatue of the god {godName}
It currenty has {self.charges} charges.
It currenty has {self.numSubSacrifices}/{sacrifice[1]} sub charges.
Offer {sacrifice[0]} and pray.

Offer items by praying at the statue to stabilise it.
If the statue is not stabilised for too long, then it will break.
Currently the GlassStatue will break in {self.charges} epochs.

You can stabilize the GlassStatue fully, by setting its heart.
You can get the statues heart from the GlassHeart dungeon.
Use this GlassStatue to teleport there.

Teleporting to the dungeon requires 5 charges and consumes one charge.
Currently the GlassStatue has {self.charges} charges.
"""

src.items.addType(GlassStatue)

import src

class BecomeStronger(src.quests.MetaQuestSequence):
    type = "BecomeStronger"

    def __init__(self, description="become stronger", creator=None, lifetime=None, reason=None, targetStrength=1):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.targetStrength = targetStrength

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        if character.getNearbyEnemies():
            quest = src.quests.questMap["Fight"](suicidal=True)
            return ([quest],None)

        if character.health < character.maxHealth//2:
            quest = src.quests.questMap["Heal"]()
            return ([quest],None)

        if not character.weapon:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Sword"):
                    quest = src.quests.questMap["Equip"]()
                    return ([quest],None)
            quest = src.quests.questMap["MetalWorking"](toProduce="Sword",produceToInventory=False,amount=1)
            return ([quest],None)
        else:
            shouldSharpen = False
            if character.weapon.baseDamage < 15:
                shouldSharpen = True
            elif character.weapon.baseDamage < 30:
                if character.searchInventory("Grindstone"):
                    shouldSharpen = True

            if shouldSharpen:
                for room in terrain.rooms:
                    for item in room.getItemsByType("SwordSharpener",needsBolted=True):
                        quest = src.quests.questMap["SharpenPersonalSword"]()
                        return ([quest],None)

            if character.weapon.baseDamage < 30:
                for room in terrain.rooms:
                    if room.getNonEmptyOutputslots("Grindstone"):
                        quest = src.quests.questMap["FetchItems"](toCollect="Grindstone")
                        return ([quest],None)

                for x in range(1,14):
                    for y in range(1,14):
                        if terrain.getRoomByPosition((x,y,0)):
                            continue
                        for item in terrain.itemsByBigCoordinate.get((x,y,0),[]):
                            if item.type != "Grindstone":
                                continue
                            quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=(x,y,0),abortOnfullInventory=False,description="fetch grindstone")
                            return ([quest],None)

        if not character.armor:
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Armor"):
                    quest = src.quests.questMap["Equip"]()
                    return ([quest],None)
            quest = src.quests.questMap["MetalWorking"](toProduce="Armor",produceToInventory=False,amount=1)
            return ([quest],None)
        else:
            shouldReinforce = False
            if character.armor.armorValue < 3:
                shouldReinforce = True
            elif character.armor.armorValue < 8:
                if character.searchInventory("ChitinPlates"):
                    shouldReinforce = True

            if shouldReinforce:
                for room in terrain.rooms:
                    for item in room.getItemsByType("ArmorReinforcer",needsBolted=True):
                        quest = src.quests.questMap["ReinforcePersonalArmor"]()
                        return ([quest],None)

            if character.armor.armorValue < 8:
                for room in terrain.rooms:
                    if room.getNonEmptyOutputslots("ChitinPlates"):
                        quest = src.quests.questMap["FetchItems"](toCollect="ChitinPlates")
                        return ([quest],None)

                for x in range(1,14):
                    for y in range(1,14):
                        if terrain.getRoomByPosition((x,y,0)):
                            continue
                        for item in terrain.itemsByBigCoordinate.get((x,y,0),[]):
                            if item.type != "ChitinPlates":
                                continue
                            quest = src.quests.questMap["CleanSpace"](targetPosition=item.getSmallPosition(),targetPositionBig=(x,y,0),abortOnfullInventory=False,description="fetch chitin plates")
                            return ([quest],None)

        if character.maxHealth < 500:
            if character.searchInventory("PermaMaxHealthPotion"):
                quest = src.quests.questMap["ConsumePotion"](potionType="PermaMaxHealthPotion")
                return ([quest],None)

            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("PermaMaxHealthPotion"):
                    quest = src.quests.questMap["FetchItems"](toCollect="PermaMaxHealthPotion")
                    return ([quest],None)

            manaCrystalAvailable = False
            if character.searchInventory("ManaCrystal"):
                manaCrystalAvailable = True
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("ManaCrystal"):
                    manaCrystalAvailable = True
                    break

            outsideManaCrystal = None
            if not manaCrystalAvailable:
                for x in range(1,14):
                    for y in range(1,14):
                        if terrain.getRoomByPosition((x,y,0)):
                            continue
                        for item in terrain.itemsByBigCoordinate.get((x,y,0),[]):
                            if item.type != "ManaCrystal":
                                continue
                            outsideManaCrystal = ((x,y,0),item.getSmallPosition())
                            break

            bloomAvailable = False
            if character.searchInventory("Bloom"):
                bloomAvailable = True
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Bloom"):
                    bloomAvailable = True
                    break
            remoteBloomAvailable = None
            if not bloomAvailable:
                for x in range(1,14):
                    for y in range(1,14):
                        if terrain.getRoomByPosition((x,y,0)):
                            continue
                        for item in terrain.itemsByBigCoordinate.get((x,y,0),[]):
                            if item.type != "Bloom":
                                continue
                            remoteBloomAvailable = ((x,y,0),item.getSmallPosition())
                            break

            flaskAvailable = False
            if character.searchInventory("Flask"):
                flaskAvailable = True
            for room in terrain.rooms:
                if room.getNonEmptyOutputslots("Flask"):
                    flaskAvailable = True
                    break
            remoteFlaskAvailable = None
            if not flaskAvailable:
                for x in range(1,14):
                    for y in range(1,14):
                        if terrain.getRoomByPosition((x,y,0)):
                            continue
                        for item in terrain.itemsByBigCoordinate.get((x,y,0),[]):
                            if item.type != "Flask":
                                continue
                            remoteFlaskAvailable = ((x,y,0),item.getSmallPosition())

            if outsideManaCrystal and (bloomAvailable or remoteBloomAvailable) and (flaskAvailable or remoteFlaskAvailable):
                quest = src.quests.questMap["CleanSpace"](targetPosition=outsideManaCrystal[1],targetPositionBig=outsideManaCrystal[0],abortOnfullInventory=False,description="fetch mana crystal")
                return ([quest],None)
            if (manaCrystalAvailable or outsideManaCrystal) and remoteBloomAvailable and (flaskAvailable or remoteFlaskAvailable):
                quest = src.quests.questMap["CleanSpace"](targetPosition=remoteBloomAvailable[1],targetPositionBig=remoteBloomAvailable[0],abortOnfullInventory=False,description="fetch bloom")
                return ([quest],None)
            if (manaCrystalAvailable or outsideManaCrystal) and (bloomAvailable or remoteBloomAvailable) and remoteFlaskAvailable:
                quest = src.quests.questMap["CleanSpace"](targetPosition=remoteFlaskAvailable[1],targetPositionBig=remoteFlaskAvailable[0],abortOnfullInventory=False,description="fetch flask")
                return ([quest],None)

            if manaCrystalAvailable and bloomAvailable and flaskAvailable:
                for room in terrain.rooms:
                    for item in room.getItemsByType("AlchemyTable",needsBolted=True):
                        quest = src.quests.questMap["BrewPotion"](potionType="PermaMaxHealthPotion")
                        return ([quest],None)

            if (manaCrystalAvailable or outsideManaCrystal) and not (bloomAvailable or remoteBloomAvailable):
                if not terrain.alarm:
                    if character.inventory:
                        quest = src.quests.questMap["ClearInventory"](returnToTile=False,tryHard=True,reason="be able to pick up potion ingredients")
                        return ([quest],None)
                    quest = src.quests.questMap["FarmMold"](lifetime=1000)
                    return ([quest],None)

            if (manaCrystalAvailable or outsideManaCrystal) and not (flaskAvailable or remoteFlaskAvailable):
                quest = src.quests.questMap["MetalWorking"](toProduce="Flask",amount=1,tryHard=True,produceToInventory=True)
                return ([quest],None)

        if character.health < character.maxHealth:
            quest = src.quests.questMap["Heal"]()
            return ([quest],None)

        # count the number of enemies/allies
        npcCount = 0
        enemyCount = 0
        terrain = character.getTerrain()
        for room in terrain.rooms:
            for otherChar in room.characters:
                if otherChar.faction != character.faction:
                    enemyCount += 1
                    if not room.alarm:
                        quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True,description="kill enemies that breached the defences")
                        return ([quest],None)
                else:
                    if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                        npcCount += 1
        for otherChar in terrain.characters:
            if otherChar.faction != character.faction:
                enemyCount += 1
                quest = src.quests.questMap["SecureTile"](toSecure=(6,7,0),endWhenCleared=False,lifetime=100,description="defend the arena",reason="ensure no attackers get into the base")
                return ([quest],None)
            else:
                if otherChar.charType != "Ghoul" and not otherChar.burnedIn:
                    npcCount += 1
        if npcCount < 2:
            quest = src.quests.questMap["SpawnClone"]()
            return ([quest],None)

        # ensure traprooms don't fill up
        for room in terrain.rooms:
            if not room.tag == "traproom":
                continue
            numItems = 0
            for item in room.itemsOnFloor:
                if item.bolted == False:
                    numItems += 1
            if numItems > 2:
                quest = src.quests.questMap["ClearTile"](targetPosition=room.getPosition())
                return ([quest],None)

        # ensure to have free inventory space
        if character.inventory:
            quest = src.quests.questMap["ClearInventory"](returnToTile=False,tryHard=True,reason="be able to collect as much items as possible")
            return ([quest],None)

        # fetch new valuable items
        quest = src.quests.questMap["Adventure"]()
        return ([quest],None)

    def generateTextDescription(self):
        text = ["""
The dungeons are too hard for you. 
You need to be stronger, to take them on.

Get some upgrades to be stronger.
"""]
        if self.targetStrength:
            text.append(f"\nThe target combat value is {self.targetStrength} your current strength is {self.character.getStrengthSelfEstimate()}")
        if self.lifetimeEvent:
            text += f"""\nlifetime: {self.lifetimeEvent.tick - src.gamestate.gamestate.tick} / {self.lifetime}\n"""
        return text

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.getStrengthSelfEstimate() < self.targetStrength:
            return False

        self.postHandler()
        return True

src.quests.addType(BecomeStronger)

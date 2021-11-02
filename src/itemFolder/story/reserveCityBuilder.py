import src
import random

class ReserveCityBuilder(src.items.Item):

    type = "ReserveCityBuilder"
    applyOptions = []

    def __init__(self):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ff2", "black"), "RC"))
        self.broken = True
        self.mapString = ""
        self.firstUsage = True
        self.workerCount = random.randint(100,1000)
        self.neededRepairItems = []
        repairCandidates = ["Rod","Heater","puller","Stripe","Bolt","Tank"]
        #for i in range(0,random.randint(3,5)):
        for i in range(0,0):
            candidate = random.choice(repairCandidates)
            self.neededRepairItems.append(candidate)
            repairCandidates.remove(candidate)
        self.hasMaintenance = True
        self.freeItemSlots = []
        self.usedItemSlots = []
        self.scrapSlots = {}
        self.storageSlots = {}

        if not self.applyOptions:
            self.applyOptions.extend(super().applyOptions)
            self.applyOptions.extend(
                [
                 ("doMaintenance", "do maintenance"),
                 ("showMap", "show map"),
                 ("showRessources", "show ressources"),
                 ("morphToCityBuilder", "morph to city builder"),
                 ("spawnNPC", "spawn worker"),
                ]
            )
        self.applyMap = {
            "showMap": self.showMap,
            "morphToCityBuilder": self.morphToCityBuilder,
            "spawnNPC": self.spawnNPC,
            "doMaintenance": self.doMaintenance,
            "showRessources": self.showRessources,
        }
        self.numScrap = 0
        self.numFood = 0
        self.numGoo = 0
        self.numScrap = 0
        self.numFood = 10000
        self.numGoo = 200

        self.clearedScrap = False
        self.urgentClear = []
        self.nonUrgentClear = []

    def showRessources(self, character):
        character.addMessage("%s Scrap in storage"%(self.numScrap,))
        character.addMessage("%s Food in storage"%(self.numFood,))
        character.addMessage("%s Goo in storage"%(self.numGoo,))
        pass

    def spawnNPC(self, character):
        if not self.numGoo >= 100:
            character.addMessage("not enough goo")
            return
        self.workerCount += 1
        worker = src.characters.Character(name="worker #%s"%(self.workerCount,))
        self.container.addCharacter(worker, self.xPosition, self.yPosition - 1)
        worker.macroState["macros"] = {
            "a": ["J", "s", "j","j","_","a"],
        }

        worker.solvers = [
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

        worker.runCommandString("_a")

    def doFeedNPC(self, character):
        # feed NPCs
        if character.satiation < 1000:
            amount = min(1000-character.satiation,self.numFood)
            character.addSatiation(amount,reason="the reserve city builder fed you")
            self.numFood -= amount

    def doCollectItems(self, character):

        if not character.inventory:
            character.addMessage("empty inventory")
            return

        # collect items from the characters inventory
        numScraps = 0
        foundOther = None
        for item in reversed(character.inventory[:]):
            if item.type == "Scrap":
                numScraps += 1
            elif item.type == "Corpse":
                self.numFood += item.charges
                character.inventory.remove(item)
                return
            elif item.type == "GooFlask":
                self.numGoo += item.uses
                character.inventory.remove(item)
                return
            else:
                foundOther = item
                break

        character.addMessage("drop scraps")
        if not self.freeItemSlots:
            character.addMessage("no item slots left")
            return

        target = None

        if numScraps:
            for (pos,amount) in self.scrapSlots.items():
                if amount < 15:
                    target = pos
                    numScraps = min(numScraps,15-amount)
        elif foundOther:
            for (pos,info) in self.storageSlots.items():
                if info["type"] == foundOther.type and info["amount"] < 15:
                    if foundOther.type == "Armor":
                        if not (foundOther.armorValue == info["armorValue"]):
                            continue
                    if foundOther.type == "Vial":
                        if not (bool(foundOther.uses) == info["hasCharges"]):
                            continue
                    if foundOther.type == "GooFlask":
                        if not (bool(foundOther.uses) == info["hasCharges"]):
                            continue
                    if foundOther.type == "GooFlask":
                        if not ((foundOther.uses == 100) == info["full"]):
                            continue
                    if foundOther.type == "Rod":
                        if not (foundOther.baseDamage == info["baseDamage"]):
                            continue
                    target = pos

        if not target:
            target = self.freeItemSlots.pop()

        while target in self.freeItemSlots:
            self.freeItemSlots.remove(target)
        if not target in self.usedItemSlots:
            self.usedItemSlots.append(target)

        path = self.getProperPath(character.getPosition(),target)

        amount = 1
        if numScraps:
            amount = numScraps

        if numScraps:
            if not target in self.scrapSlots:
                self.scrapSlots[target] = 0
            self.scrapSlots[target] += amount
        elif foundOther:
            if not target in self.storageSlots:
                info = {"type":foundOther.type,"amount":0}

                if foundOther.type == "Armor":
                    info["armorValue"] = foundOther.armorValue
                if foundOther.type == "Vial":
                    info["hasCharges"] = bool(foundOther.uses)
                if foundOther.type == "GooFlask":
                    info["hasCharges"] = bool(foundOther.uses)
                if foundOther.type == "GooFlask":
                    info["full"] = (foundOther.uses == 100)
                if foundOther.type == "Rod":
                    info["baseDamage"] = foundOther.baseDamage

                self.storageSlots[target] = info

            self.storageSlots[target]["amount"] += 1

        command = path[:-1]+("L"+path[-1])*amount
        backCommand = path[::-1].replace("w","x").replace("s","w").replace("x","s").replace("d","x").replace("a","d").replace("x","a")[1:]
        character.runCommandString(command+backCommand)
        character.addMessage(command)
        return


    def doClearScrap2(self,character):
        # clear direct path
        directpath = [(6,5,0),(5,5,0),(5,6,0),(5,7,0),(6,7,0),(7,7,0),(7,6,0),(7,5,0)]
        movementPath = "assddwwa"
        movementPathBack = "dssaawwd"
        numSteps = 0
        scrapFound = None
        for pos in directpath:
            for item in self.container.getItemByPosition(pos):
                scrapFound = item

            if scrapFound:
                break

            numSteps += 1
        
        if scrapFound:
            if numSteps == 0:
                character.runCommandString("k"*10)
                return

            if numSteps > 1:
                character.runCommandString(movementPathBack[-(numSteps-1):])

            character.runCommandString(("K"+movementPath[numSteps-1])*10)

            if numSteps > 1:
                character.runCommandString(movementPath[0:numSteps-1])

            return
        
        targetItem = None
        for item in self.container.itemsOnFloor[:]:
            if item == self:
                continue
            if item.bolted:
                continue
            if item.xPosition == 0 or item.yPosition == 0:
                continue
            if item.xPosition == 12 or item.yPosition == 12:
                continue

            targetItem = item
            break

        if targetItem:
            startPos = list(character.getPosition())
            walkToCommand1 = ""
            walkBackCommand1 = ""

            if targetItem.yPosition < 6:
                pass
            elif targetItem.yPosition > 6:
                walkToCommand1 += "assd."
                walkBackCommand1 += "dwwa."
                startPos[1] += 2
            elif targetItem.yPosition == 6:
                startPos[1] += 1
                if targetItem.xPosition < 6:
                    walkToCommand1 += "as."
                    walkBackCommand1 += "wd."
                    startPos[0] -= 1
                else:
                    walkToCommand1 += "ds."
                    walkBackCommand1 += "wa."
                    startPos[0] += 1

            walkToCommand2 = ""
            walkBackCommand2 = ""

            pathToItem = []
            while startPos[1] < targetItem.yPosition:
                startPos[1] += 1
                walkToCommand2 += "s"
                walkBackCommand2 = "w"+walkBackCommand2
                pathToItem.append(tuple(startPos))
            while startPos[1] > targetItem.yPosition:
                startPos[1] -= 1
                walkToCommand2 += "w"
                walkBackCommand2 = "s"+walkBackCommand2
                pathToItem.append(tuple(startPos))
            while startPos[0] < targetItem.xPosition:
                startPos[0] += 1
                walkToCommand2 += "d"
                walkBackCommand2 = "a"+walkBackCommand2
                pathToItem.append(tuple(startPos))
            while startPos[0] > targetItem.xPosition:
                startPos[0] -= 1
                walkToCommand2 += "a"
                walkBackCommand2 = "d"+walkBackCommand2
                pathToItem.append(tuple(startPos))

            pathLen = 0
            for pos in pathToItem:
                pathLen += 1
                foundScrap = None
                for item in self.container.getItemByPosition(pos):
                    if item.type == "Scrap":
                        foundScrap = item

                if foundScrap:
                   break 

            command = walkToCommand1+walkToCommand2[:pathLen-1]+("K"+walkToCommand2[pathLen-1])*10+walkBackCommand2[-(pathLen-1):]+walkBackCommand1
            character.runCommandString(command)
            return

        self.clearedScrap = True

    def checkForItemSlots(self, character):
        itemSlots = []
        self.urgentClear = []
        self.nonUrgentClear = []

        # check northern part
        for y in reversed(range(1,6)):
            if self.container.getItemByPosition((6,y,0)):
                if not self.container.getPositionWalkable((6,y,0)):
                    self.urgentClear.append((6,y,0))
                    break
                else:
                    self.nonUrgentClear.append((6,y,0))

            if y in (2,4,):
                for x in reversed(range(1,6)):
                    if self.container.getItemByPosition((x,y,0)):
                        if not self.container.getPositionWalkable((x,y,0)):
                            self.urgentClear.append((x,y,0))
                            break
                        else:
                            self.nonUrgentClear.append((x,y,0))

                    if not (x,y+1,0) == (5,5,0):
                        if not self.container.getItemByPosition((x,y+1,0)):
                            itemSlots.append((x,y+1,0))
                        else:
                            if not (x,y+1,0) in self.usedItemSlots:
                                self.urgentClear.append((x,y+1,0))

                    if y in (2,):
                        if not self.container.getItemByPosition((x,y-1,0)):
                            itemSlots.append((x,y-1,0))
                        else:
                            if not (x,y-1,0) in self.usedItemSlots:
                                self.urgentClear.append((x,y-1,0))
                for x in range(7,12):
                    if self.container.getItemByPosition((x,y,0)):
                        if not self.container.getPositionWalkable((x,y,0)):
                            self.urgentClear.append((x,y,0))
                            break
                        else:
                            self.nonUrgentClear.append((x,y,0))

                    if not (x,y+1,0) == (7,5,0):
                        if not self.container.getItemByPosition((x,y+1,0)):
                            itemSlots.append((x,y+1,0))
                        else:
                            if not (x,y+1,0) in self.usedItemSlots:
                                self.urgentClear.append((x,y+1,0))

                    if y in (2,):
                        if not self.container.getItemByPosition((x,y-1,0)):
                            itemSlots.append((x,y-1,0))
                        else:
                            if not (x,y-1,0) in self.usedItemSlots:
                                self.urgentClear.append((x,y-1,0))

        # check roundabout
        roundaboutBlocked = False
        for pos in ((6,5,0),(5,5,0),(5,6,0),(5,7,0),(6,7,0),(7,7,0),(7,6,0),(7,5,0)):
            if self.container.getItemByPosition(pos):
                if not self.container.getPositionWalkable(pos):
                    self.urgentClear.append(pos)
                    roundaboutBlocked = True
                    break
                else:
                    self.nonUrgentClear.append(pos)

        # check southern side
        if not roundaboutBlocked:
            for y in range(7,12):
                if self.container.getItemByPosition((6,y,0)):
                    if not self.container.getPositionWalkable((6,y,0)):
                        self.urgentClear.append((6,y,0))
                        break
                    else:
                        self.nonUrgentClear.append((6,y,0))

                if y in (8,10,):
                    for x in reversed(range(1,6)):
                        if self.container.getItemByPosition((x,y,0)):
                            if not self.container.getPositionWalkable((x,y,0)):
                                self.urgentClear.append((x,y,0))
                                break
                            else:
                                self.nonUrgentClear.append((x,y,0))

                        if y in (10,):
                            if not self.container.getItemByPosition((x,y+1,0)):
                                itemSlots.append((x,y+1,0))
                            else:
                                if not (x,y+1,0) in self.usedItemSlots:
                                    self.urgentClear.append((x,y+1,0))

                        if not (x,y-1,0) == (5,7,0):
                            if not self.container.getItemByPosition((x,y-1,0)):
                                itemSlots.append((x,y-1,0))
                            else:
                                if not (x,y-1,0) in self.usedItemSlots:
                                    self.urgentClear.append((x,y-1,0))
                    for x in range(7,12):
                        if self.container.getItemByPosition((x,y,0)):
                            if not self.container.getPositionWalkable((x,y,0)):
                                self.urgentClear.append((x,y,0))
                                break
                            else:
                                self.nonUrgentClear.append((x,y,0))

                        if y in (10,):
                            if not self.container.getItemByPosition((x,y+1,0)):
                                itemSlots.append((x,y+1,0))
                            else:
                                if not (x,y+1,0) in self.usedItemSlots:
                                    self.urgentClear.append((x,y+1,0))

                        if not (x,y-1,0) == (7,7,0):
                            if not self.container.getItemByPosition((x,y-1,0)):
                                itemSlots.append((x,y-1,0))
                            else:
                                if not (x,y-1,0) in self.usedItemSlots:
                                    self.urgentClear.append((x,y-1,0))
        # check west/east path
        for x in reversed(range(1,5)):
            pos = (x,6,0)
            if self.container.getItemByPosition(pos):
                if not self.container.getPositionWalkable(pos):
                    self.urgentClear.append(pos)
                else:
                    self.nonUrgentClear.append(pos)
        for x in range(8,12):
            pos = (x,6,0)
            if self.container.getItemByPosition(pos):
                if not self.container.getPositionWalkable(pos):
                    self.urgentClear.append(pos)
                else:
                    self.nonUrgentClear.append(pos)

        self.freeItemSlots = itemSlots[:]

        if self.nonUrgentClear or self.urgentClear:
            self.clearedScrap = False

        character.addMessage(self.urgentClear)

    def doClearScrap(self,character):
        if self.urgentClear:
            character.addMessage(str(self.urgentClear))
            target = self.urgentClear.pop()
            character.addMessage("target")
            character.addMessage(target)
            path = self.getProperPath(character.getPosition(),target)
            command = path[:-1]+("K"+path[-1])*10
            backCommand = path[::-1].replace("w","x").replace("s","w").replace("x","s").replace("d","x").replace("a","d").replace("x","a")[1:]
            character.runCommandString(command+backCommand)
        elif self.nonUrgentClear:
            character.addMessage(str(self.nonUrgentClear))
            target = self.nonUrgentClear.pop()
            character.addMessage("target")
            character.addMessage(target)
            path = self.getProperPath(character.getPosition(),target)
            command = path[:-1]+("K"+path[-1])*10
            backCommand = path[::-1].replace("w","x").replace("s","w").replace("x","s").replace("d","x").replace("a","d").replace("x","a")[1:]
            character.runCommandString(command+backCommand)
        else:
            self.clearedScrap = True

    def getProperPath(self, startPos, endPos):
        command = ""
        lastStep = ""

        if endPos == (5,7,0):
            return "ass"
        if endPos == (6,7,0):
            return "assd"

        if endPos[1] == 1:
            nearByPath = (endPos[0],2,0)
            lastStep += "w"
        elif endPos[1] == 3:
            nearByPath = (endPos[0],2,0)
            lastStep += "s"
        elif endPos[1] == 5:
            nearByPath = (endPos[0],4,0)
            lastStep += "s"
        elif endPos[1] == 7:
            nearByPath = (endPos[0],8,0)
            lastStep += "w"
        elif endPos[1] == 9:
            nearByPath = (endPos[0],10,0)
            lastStep += "w"
        elif endPos[1] == 11:
            nearByPath = (endPos[0],10,0)
            lastStep += "s"
        else:
            nearByPath = tuple(endPos)

        if endPos[1] < 6:
            command += "w"*(startPos[1]-nearByPath[1])
            if nearByPath[0] < 6:
                command += "a"*(startPos[0]-nearByPath[0])
            if nearByPath[0] > 6:
                command += "d"*(nearByPath[0]-startPos[0])
        elif endPos[1] > 6:
            command += "assd"
            startPos = (startPos[0],startPos[1]+2,startPos[2])

            command += "s"*(nearByPath[1]-startPos[1])
            if nearByPath[0] < 6:
                command += "a"*(startPos[0]-nearByPath[0])
            if nearByPath[0] > 6:
                command += "d"*(nearByPath[0]-startPos[0])
        elif endPos[0] < 6:
            startPos = (startPos[0]-1,startPos[1]+1)
            command += "as"
            command += "a"*(startPos[0]-nearByPath[0])
        elif endPos[0] > 6:
            command += "assddw"
            startPos = (startPos[0]+1,startPos[1]+1)
            command += "d"*(nearByPath[0]-startPos[0])


        command += lastStep
        return command

    def doMaintenance(self, character):
        self.doFeedNPC(character)
        self.checkForItemSlots(character)
        if len(character.inventory):
            self.doCollectItems(character)
            return

        if not self.clearedScrap:
            self.doClearScrap(character)
            return

        character.runCommandString("assddwwa")

    def showMap(self, character):
        text = self.mapString
        text += "\n"
        text += "\n"
        text += "\n"
        text += "RC = reserve city builder\n"
        text += "CB = city builder\n"
        text += "++ = Road\n"
        text += "rr = room\n"
        text += "MM = military\n"
        text += "mm = factory\n"
        text += "ss = storage\n"
        text += "mc = memory cell production\n"
        text += "pf = pocket frame production\n"
        text += "\n"
        self.submenue = src.interaction.TextMenu(text=text)
        character.macroState["submenue"] = self.submenue

    def morphToCityBuilder(self, character):
        pos = self.getPosition()
        container = self.container
        self.container.removeItem(self)

        character.addMessage("the reserve city builder fully starts up.")
        character.addMessage("you won the hack and slay part of the game.")
        cityBuilder = src.items.itemMap["CityBuilder"]()
        container.addItem(cityBuilder,pos)

    def apply(self, character):
        """
        handle a character trying to go up

        Parameters:
            character: the character using the item
        """

        if self.broken:
            if self.firstUsage:
                item = src.items.itemMap["Note"]()
                item.text = "%s"%(self.neededRepairItems,)
                character.addMessage("The prints a list of needed items")
                pos = (self.xPosition-1,self.yPosition,self.zPosition)
                self.container.addItem(item,pos)
                self.firstUsage = False

            neededItems = self.neededRepairItems[:]
            itemsToConsume = []
            for item in character.inventory:
                if item.type in neededItems:
                    neededItems.remove(item.type)
                    itemsToConsume.append(item)

            if neededItems:
                character.addMessage("This machine is broken")
                character.addMessage("you need to have %s in you inventory to repair the machine"%(neededItems,))
            else:
                character.addMessage("you repair the machine")
                character.addMessage("you won the roguelike part of the game.")
                self.broken = False

                for item in itemsToConsume:
                    character.inventory.remove(item)
        else:
            super().apply(character)
            # set up room
            #  needs roomManger etc
            # replace memory cell
            # => do some hack and slay
            # replace city builder

    def extend(self,character):
        neededItems = [random.choice(["MemoryCell","PocketFrame"])]
        for item in character.inventory:
            if item.type in neededItems:
                neededItems.remove(item.type)

        if neededItems:
            character.addMessage("activate the machine and win the game")
            character.addMessage("you need to have %s in your inventory to activate the machine"%(neededItems,))
        else:
            pass

    def render(self):
        if self.broken:
            return (src.interaction.urwid.AttrSpec("#aa8", "black"), "RC")
        else:
            return (src.interaction.urwid.AttrSpec("#ff2", "black"), "RC")

    def getLongInfo(self):
        test = super().getLongInfo()
        test += "\nfreeItemSlots: %s\nusedItemSlots: %s"%(self.freeItemSlots,self.usedItemSlots)
        test += "\nclearedScrap: %s\nurgentClear: %s\nnonUrgentClear: %s"%(self.clearedScrap,self.urgentClear,self.nonUrgentClear)
        return test


src.items.addType(ReserveCityBuilder)

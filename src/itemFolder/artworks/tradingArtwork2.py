import src
import random


class TradingArtwork2(src.items.Item):
    """
    ingame item that allows the player the convert ressources and
    items by trading
    """

    type = "TradingArtwork2"

    def __init__(self):
        """
        configure the superclass
        """

        self.doAutoTrade = True
        self.tradingHistory = {}

        super().__init__(display="TA")

        self.name = "trading artwork"

        self.availableTrades = [
            {
                "name": "trade scrap",
                "give": [
                    ["Scrap", 2],
                ],
                "recieve": [
                    ["MetalBars", 1],
                ],
                "autoTrade":True
            },
            {
                "name": "trade scrap",
                "give": [
                    ["Scrap", 10],
                ],
                "recieve": [
                    ["MetalBars", 1],
                ],
                "autoTrade":False
            },
            {
                "name": "trade for corpse",
                "give": [
                    ["MetalBars", 4],
                ],
                "recieve": [
                    ["Corpse", 1],
                ],
                "autoTrade":True
            },
            {
                "name": "trade for corpse",
                "give": [
                    ["MetalBars", 1],
                ],
                "recieve": [
                    ["Corpse", 1],
                ],
                "numOffered": 30,
                "autoTrade":True
            },
            {
                "name": "trade for sheet",
                "give": [
                    ["MetalBars", 4],
                ],
                "recieve": [
                    ["Sheet", 1],
                ],
                "autoTrade":True
            },
            {
                "name": "trade for Scrap compactor",
                "give": [
                    ["MetalBars", 4],
                ],
                "recieve": [
                    ["ScrapCompactor", 1],
                ],
                "autoTrade":True
            },
            {
                "name": "trade for corpse animator",
                "give": [
                    ["MetalBars", 10],
                ],
                "recieve": [
                    ["CorpseAnimator", 1],
                ],
                "numOffered": 3,
                "autoTrade":True
            },
            {
                "name": "trade for scratch plate",
                "give": [
                    ["MetalBars", 6],
                ],
                "recieve": [
                    ["ScratchPlate", 1],
                ],
                "numOffered": 3,
                "autoTrade":True
            },
        ]

        while len(self.availableTrades) < 15:
            if len(self.availableTrades) < 10:
                item = random.choice(src.items.commons)
            if len(self.availableTrades) < 13:
                item = random.choice(src.items.semiCommons)
            else:
                item = "Machine"
            dependencies = []

            rawMaterials = src.items.rawMaterialLookup.get(item)

            if not rawMaterials:
                if not item == "MetalBars":
                    rawMaterials = ["MetalBars"]
                else:
                    rawMaterials = ["Scrap"]

            for rawMaterial in rawMaterials:
                dependencies.append([rawMaterial, random.randint(2, 10)])

            recieve = [item, 1]
            if item == "Machine":
                if not random.randint(1, 10) == 5:
                    recieve = [item, 1, random.choice(src.items.commons)]
                    # bad code: information about what can be produced in a machine should be stored and fetched
                    if recieve[2] == "MetalBars":
                        continue
                else:
                    recieve = [item, 1, random.choice(src.items.semiCommons)]

            self.availableTrades.append(
                {
                    "numOffered": 1,
                    "name": "trade for %s" % (item,),
                    "give": dependencies,
                    "recieve": [recieve],
                    "autoTrade":True
                },
            )

        self.attributesToStore.extend([
                "tradingHistory",
                "availableTrades",
                "doAutoTrade",
            ])
                
        self.applyOptions.extend(
                                                [
                                                    ("setAutoTrade", "trade"),
                                                    ("toggleAutoTrade", "toggle auto trade"),
                                                                                                                                                                                                                                                ]
                                )

        self.applyMap = {
                                    "manualTrade": self.manualTrade,
                                    "setAutoTrade": self.setAutoTrade,
                                    "toggleAutoTrade": self.toggleAutoTrade,
                                }

    def toggleAutoTrade(self,character=None):
        if self.doAutoTrade:
            self.doAutoTrade = False
            if character:
                character.addMessage("you disable the auto trade")
        else:
            self.doAutoTrade = True
            if character:
                character.addMessage("you enable the auto trade")

    def setAutoTrade(self,character):
        options = [
        ]
        for trade in self.availableTrades:
            options.append((trade, "%s\n        %s"%(trade["name"],trade)))

        applyOptions = {
                "default":{"description":"do trade manually","callback":{"container":self,"method":"tradeManually","params":{"character":character}}},
                "r":{"description":"toggle auto trade","callback":{"container":self,"method":"setTradeAutoTrade","params":{"character":character}}},
                }

        self.submenue = src.interaction.ListActionMenu(
            options, applyOptions, "", targetParamName="trade"
        )
        character.macroState["submenue"] = self.submenue
        self.character = character

    def setTradeAutoTrade(self,extraInfo):
        if extraInfo["trade"].get("autoTrade"):
            extraInfo["trade"]["autoTrade"] = False
        else:
            extraInfo["trade"]["autoTrade"] = True

    def manualTrade(self,character):
        self.setApplyOptions()
        super().apply(character)

    def tradeManually(self, extraInfo):
        print(extraInfo)
        self.doTrade(extraInfo["character"],extraInfo["trade"])

    def doTrade(self, character, trade):
        """
        do a exchange of ressources

        Parameters:
            character: the character exchanging the ressources
            trade: the trade to run
        """

        import copy
        tradeCopy = copy.deepcopy(trade)

        allItemsFound = []
        # check stockpiles
        slotMap = {}
        didSomething = True
        while didSomething:
            didSomething = False
            for inputSlot in self.container.inputSlots:
                items = self.container.getItemByPosition(inputSlot[0])
            
                for giveSpec in tradeCopy["give"][:]:
                    while items and items[-1].type == giveSpec[0]:
                        item = items[-1]
                        allItemsFound.append(item)
                        didSomething = True

                        if not inputSlot[0] in slotMap:
                            slotMap[inputSlot[0]] = []

                        if not giveSpec[0] == "Scrap":
                            self.container.removeItem(item)
                            giveSpec[1] -= 1
                            slotMap[inputSlot[0]].append(item)
                        else:
                            if item.amount > giveSpec[1]:
                                tradeCopy["give"].remove(giveSpec)
                                item.amount -= giveSpec[1]
                                slotMap[inputSlot[0]].append(src.items.itemMap["Scrap"](amount=giveSpec[1]))
                                break
                            else:
                                giveSpec[1] -= item.amount
                                self.container.removeItem(item)
                                slotMap[inputSlot[0]].append(item)

                        if giveSpec[1] == 0:
                            tradeCopy["give"].remove(giveSpec)
                            break

        if character:
            # check inventory
            inventoryItemsFound = []
            for giveSpec in tradeCopy["give"][:]:
                for item in character.inventory:
                    if item.type == giveSpec[0]:
                        inventoryItemsFound.append(item)
                        giveSpec[1] -= 1

                        if giveSpec[1] == 0:
                            tradeCopy["give"].remove(giveSpec)

        if tradeCopy["give"]:
            for (pos,itemList) in slotMap.items():
                for item in itemList:
                    self.container.addItem(item,pos)
            if character:
                character.addMessage("not enough resources")
            return

        failedAddingItem = False
        for itemSpec in tradeCopy["recieve"]:
            for i in range(0, itemSpec[1]):
                item = src.items.itemMap[itemSpec[0]]()
                if itemSpec[0] == "Machine":
                    item.setToProduce(itemSpec[2])
                item.bolted = False

                addedItem = False

                for outputSlot in self.container.outputSlots:
                    if not outputSlot[1] == itemSpec[0]:
                        continue
                    items = self.container.getItemByPosition(outputSlot[0])
                    if items and items[-1].walkable == False:
                        continue
                    if len(items) > 10:
                        continue
                    self.container.addItem(item,outputSlot[0])
                    addedItem = True
                    break

                if not addedItem and character and len(character.inventory) < 10:
                    character.addToInventory(item)
                    addedItem = True
                    break

                if not addedItem:
                    failedAddingItem = True

        if failedAddingItem:
            for (pos,itemList) in slotMap.items():
                for item in itemList:
                    self.container.addItem(item,pos)
            if character:
                character.addMessage("no space to put the trade result")
            return

        if character:
            # check inventory
            character.removeItemsFromInventory(inventoryItemsFound)

        if character:
            character.addMessage("you did the trade %s" % (trade["name"],))

        if "numOffered" in trade:
            trade["numOffered"] -= 1
            if trade["numOffered"] == 0:
                self.availableTrades.remove(trade)

        return True

    def getLongInfo(self):
        """
        return a longer than normal description of the item

        Returns:
            the description
        """
        text = super().getLongInfo()
        text += """
tradingHistory:
%s
""" % (
            self.tradingHistory,
        )
        return text

    def autoTrade(self):
        if not self.container:
            return
        event = src.events.RunCallbackEvent(self.container.timeIndex + 1)
        event.setCallback({"container": self, "method": "autoTrade"})
        self.container.addEvent(event)

        if not self.doAutoTrade:
            return

        for trade in self.availableTrades[:]:
            if not trade.get("autoTrade"):
                continue
            if self.doTrade(None,trade) and trade in self.availableTrades:
                self.availableTrades.remove(trade)
                self.availableTrades.append(trade)

    def configure(self,character):
        self.autoTrade()

src.items.addType(TradingArtwork2)

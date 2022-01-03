import src
import random


class TradingArtwork(src.items.Item):
    """
    ingame item that allows the player the convert ressources and
    items by trading
    """

    type = "TradingArtwork"

    def __init__(self):
        """
        configure the superclass
        """

        self.tradingHistory = {}

        super().__init__(display="TA")

        self.name = "trading artwork"

        self.availableTrades = [
            {
                "name": "trade scrap",
                "give": [
                    ["Scrap", 10],
                ],
                "recieve": [
                    ["MetalBars", 1],
                ],
            },
            {
                "name": "trade for paving",
                "give": [
                    ["Scrap", 2],
                ],
                "recieve": [
                    ["Paving", 1],
                ],
            },
            {
                "name": "trade for sheet",
                "give": [
                    ["MetalBars", 2],
                ],
                "recieve": [
                    ["Sheet", 1],
                ],
            },
            {
                "name": "trade for goo token",
                "give": [
                    ["MetalBars", 10],
                ],
                "recieve": [
                    ["Token", 1, "Goo"],
                ],
            },
            {
                "name": "trade for Scrap compactor",
                "give": [
                    ["MetalBars", 4],
                ],
                "recieve": [
                    ["ScrapCompactor", 1],
                ],
            },
            {
                "name": "trade for paving generator",
                "give": [
                    ["MetalBars", 5],
                ],
                "recieve": [
                    ["PavingGenerator", 1],
                ],
            },
            {
                "numOffered": 4,
                "name": "trade for typed stockpile manager",
                "give": [
                    ["MetalBars", 10],
                ],
                "recieve": [
                    ["TypedStockpileManager", 1],
                ],
            },
            {
                "numOffered": 4,
                "name": "trade for uniform stockpile manager",
                "give": [
                    ["MetalBars", 10],
                ],
                "recieve": [
                    ["UniformStockpileManager", 1],
                ],
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
                },
            )

        self.attributesToStore.extend([
                "tradingHistory",
                "availableTrades",
            ])

        self.setApplyOptions()

    def setApplyOptions(self):
        """
        recalculate the option for the apply action to show a selection
        of trades currenty available
        """

        self.applyOptions = []
        self.applyMap = {}

        counter = 0
        for trade in self.availableTrades:
            counter += 1
            self.applyOptions.append(
                (
                    str(counter),
                    "%s : %sx        %s => %s\n"
                    % (
                        trade["name"],
                        trade.get("numOffered"),
                        trade["give"],
                        trade["recieve"],
                    ),
                )
            )

            #non trivial: need to break python namespace/scope
            def scopeBreaker(trade):
                def setStuff(character):
                    self.doTrade(character, trade)

                return setStuff

            self.applyMap[str(counter)] = scopeBreaker(trade)

    def apply(self, character):
        """
        reset the menu options and show an action menu

        Parameters:
            character: the character trying to use the item
        """

        self.setApplyOptions()
        super().apply(character)

    def doTrade(self, character, trade):
        """
        do a exchange of ressources

        Parameters:
            character: the character exchanging the ressources
            trade: the trade to run
        """

        allItemsFound = []
        for giveSpec in trade["give"]:
            itemsFound = []
            for item in character.inventory:
                if item.type == giveSpec[0]:
                    itemsFound.append(item)
                    if len(itemsFound) == giveSpec[1]:
                        break
            if not len(itemsFound) == giveSpec[1]:
                character.addMessage("not enough %s" % (giveSpec[0],))
                return
            allItemsFound.extend(itemsFound)
        character.removeItemsFromInventory(allItemsFound)

        for itemSpec in trade["recieve"]:
            for i in range(0, itemSpec[1]):
                item = src.items.itemMap[itemSpec[0]]()
                if itemSpec[0] == "Machine":
                    item.setToProduce(itemSpec[2])
                character.addToInventory(item,force=True)
        character.addMessage("you did the trade %s" % (trade["name"],))

        if "numOffered" in trade:
            trade["numOffered"] -= 1
            if trade["numOffered"] == 0:
                self.availableTrades.remove(trade)

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


src.items.addType(TradingArtwork)

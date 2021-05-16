import src
import random


class TradingArtwork(src.items.Item):
    type = "TradingArtwork"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self, name="trading artwork", noId=False, autoRun=True):
        self.tradingHistory = {}

        super().__init__(display="TA", name=name)

        self.applyOptions.extend(
            [
                ("tradeMetalBars", "trade metal bars"),
                ("tradeScrap", "trade scrap"),
                ("tradeExotics", "trade excotics"),
                ("tradeForWeapon", "trade for weapon"),
                ("tradeForArmor", "trade for armor"),
                ("tradeForVial", "trade for vial"),
                ("tradeForVial", "trade for vial"),
            ]
        )
        self.applyMap = {
            "tradeMetalBars": self.tradeMetalBars,
            "tradeScrap": self.tradeScrap,
            "tradeExotics": self.tradeExotics,
            "tradeForWeapon": self.tradeForWeapon,
            "tradeForArmor": self.tradeForArmor,
            "tradeForVial": self.tradeForVial,
        }

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
                    "numOffered": random.randint(2, 10),
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
            def scopeBreaker(trade, counter):
                def setStuff(character):
                    self.doTrade(character, trade, counter)

                return setStuff

            self.applyMap[str(counter)] = scopeBreaker(trade, counter)

    def apply(self, character):
        self.setApplyOptions()
        super().apply(character)

    def doTrade(self, character, trade, counter):
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

        for itemSpec in trade["recieve"]:
            for i in range(0, itemSpec[1]):
                item = src.items.itemMap[itemSpec[0]]()
                if itemSpec[0] == "Machine":
                    item.setToProduce(itemSpec[2])
                character.addToInventory(item)
        character.removeItemsFromInventory(allItemsFound)
        character.addMessage("you did the trade %s" % (trade["name"],))

        if "numOffered" in trade:
            trade["numOffered"] -= 1
            if trade["numOffered"] == 0:
                self.availableTrades.remove(trade)


    def tradeForVial(self, character):
        flaskFound = None
        corpseFound = None

        for item in character.inventory:
            if item.type == "Corpse":
                corpseFound = item
            if item.type == "GooFlask" and item.uses == 100:
                flaskFound = item

        if not (flaskFound and corpseFound):
            character.addMessage(
                "you need a filled goo flask and a corpse to trade for a vial"
            )
            return

        character.removeItemsFromInventory([flaskFound, corpseFound])
        item = src.items.itemMap["Vial"]()
        item.uses = 2
        character.addToInventory(item)
        character.addMessage("you trade a goo flask and a corpse for a vial")

    def tradeExotics(self, character):
        itemsFound = []
        for item in character.inventory:
            if item.type in self.tradingHistory:
                continue
            itemsFound.append(item)
            self.tradingHistory[item.type] = 1

        for item in itemsFound:
            itemNew = src.items.itemMap["GooFlask"]()
            itemNew.uses = 100
            character.inventory.append(itemNew)

            character.addMessage(
                "you traded a %s for 1 filled goo flask" % (item.type,)
            )

        character.removeItemsFromInventory(itemsFound)

    def tradeForWeapon(self, character):
        foundItems = character.searchInventory("GooFlask", {"uses": 100})

        if not len(foundItems):
            character.addMessage("no filled GooFlasks in inventory")
            return

        quality = len(foundItems)
        character.removeItemsFromInventory(foundItems)

        weapon = src.items.itemMap["Rod"]()
        weapon.baseDamage = 4
        if quality > 1:
            armor.armorValue = 5
        if quality > 3:
            armor.armorValue = 6
        if quality > 6:
            armor.armorValue = 7
        if quality == 10:
            armor.armorValue = 8

        character.addToInventory(weapon)

        character.addMessage(
            "you traded %s filled goo flasks for weapon basedamage %s"
            % (
                quality,
                weapon.baseDamage,
            )
        )

    def tradeForArmor(self, character):
        foundItems = character.searchInventory("GooFlask", {"uses": 100})

        if not len(foundItems):
            character.addMessage("no filled GooFlasks in inventory")
            return

        quality = len(foundItems)
        character.removeItemsFromInventory(foundItems)

        armor = src.items.itemMap["Armor"]()
        armor.armorValue = 1
        if quality > 1:
            armor.armorValue = 2
        if quality > 3:
            armor.armorValue = 3
        if quality > 6:
            armor.armorValue = 4
        if quality == 10:
            armor.armorValue = 5

        character.addToInventory(armor)

        character.addMessage(
            "you traded %s filled goo flasks for armor with armorValue %s"
            % (
                quality,
                armor.armorValue,
            )
        )

    def tradeScrap(self, character):
        foundItems = character.searchInventory("Scrap")

        if len(foundItems) < 10:
            character.addMessage("not enough scrap")
            return

        for item in foundItems:
            character.inventory.remove(item)

        item = src.items.itemMap["MetalBars"]()
        character.inventory.append(item)

        character.addMessage("you traded 10 scrap for 1 metal bar")

    def tradeMetalBars(self, character):
        foundItems = []
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["MetalBars"]):
                foundItems.append(item)

        if len(foundItems) < 10:
            character.addMessage("not enough metal bars")
            return

        for item in foundItems:
            character.inventory.remove(item)

        item = src.items.itemMap["GooFlask"]()
        item.uses = 100
        character.inventory.append(item)

        character.addMessage("you traded 10 metal bars for 1 filled goo flask")

    def getLongInfo(self):
        text = """
tradingHistory:
%s
""" % (
            self.tradingHistory,
        )
        return text


src.items.addType(TradingArtwork)

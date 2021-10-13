import src

class BluePrinter(src.items.Item):
    """
    ingame item to create blueprints which can be used to produce machines
    this item basically represents research in the game
    """

    type = "BluePrinter"

    def __init__(self):
        """
        configure superclass and initialise own state
        """

        super().__init__(display=src.canvas.displayChars.blueprinter)

        self.name = "blueprinter"
        self.description = "this machine creates blueprints"
        self.usageInfo = """
The Blueprinter has two inputs
It needs a sheet on the north to print the blueprint onto.
The items from the blueprint reciepe need to be added to the west or south.
"""

        self.submenue = None
        self.text = None

        self.reciepes = [
            [["MemoryCell", "Connector", "FloorPlate"], "UniformStockpileManager"],
            [["MemoryCell", "Connector", "Command"], "ProductionManager"],
            [["MemoryCell", "Bloom", "SickBloom"], "AutoFarmer"],
            [["MemoryCell", "Tank"], "MemoryBank"],
            [["MemoryCell", "Puller"], "MemoryDump"],
            [["MemoryCell", "Heater"], "SimpleRunner"],
            [["MemoryCell", "Pusher"], "MemoryStack"],
            [["MemoryCell", "Connector"], "MemoryReset"],
            [["Case", "Sheet", "Bloom"], "BloomContainer"],
            [["Case", "Sheet"], "Container"],
            [["Sheet", "pusher"], "Sorter"],
            [["Sheet", "puller"], "Mover"],
            [["Stripe", "Connector"], "RoomControls"],
            [["GooFlask", "Tank"], "GrowthTank"],
            [["Radiator", "Heater"], "StasisTank"],
            [["Mount", "Tank"], "MarkerBean"],
            [["Bolt", "Tank"], "PositioningDevice"],
            [["Bolt", "puller"], "Watch"],
            [["Bolt", "Heater"], "BackTracker"],
            [["Bolt", "pusher"], "Tumbler"],
            [["Sheet", "Heater"], "ItemUpgrader"],
            [["Sheet", "Connector"], "ItemDowngrader"],
            [["Scrap", "MetalBars"], "Scraper"],
            [["Tank", "Connector"], "ReactionChamber"],
            [["Frame", "MetalBars"], "Case"],
            [["Frame"], "PocketFrame"],
            [["Connector", "MetalBars"], "MemoryCell"],
            [["Sheet", "MetalBars"], "Tank"],
            [["Radiator", "MetalBars"], "Heater"],
            [["Mount", "MetalBars"], "Connector"],
            [["Stripe", "MetalBars"], "pusher"],
            [["Bolt", "MetalBars"], "puller"],
            [["Rod", "MetalBars"], "Frame"],
            [["Bloom", "MetalBars"], "SporeExtractor"],
            [["Sheet", "Rod", "Bolt"], "FloorPlate"],
            [["Coal", "SickBloom"], "FireCrystals"],
            [["Command"], "AutoScribe"],
            [["Corpse"], "CorpseShredder"],
            [["Tank"], "GooFlask"],
            [["Heater"], "Boiler"],
            [["Connector"], "Door"],
            [["pusher"], "Drill"],
            [["puller"], "RoomBuilder"],
            [["Explosive"], "Bomb"],
            [["Bomb"], "Mortar"],
            [["Sheet"], "Sheet"],
            [["Radiator"], "Radiator"],
            [["Mount"], "Mount"],
            [["Stripe"], "Stripe"],
            [["Bolt"], "Bolt"],
            [["Rod"], "Rod"],
            [["Scrap"], "ScrapCompactor"],
            [["Coal"], "Furnace"],
            [["BluePrint"], "BluePrinter"],
            [["MetalBars"], "Wall"],
            [["GooFlask"], "GooDispenser"],
            [["Bloom"], "BloomShredder"],
            [["VatMaggot"], "MaggotFermenter"],
            [["BioMass"], "BioPress"],
            [["PressCake"], "GooProducer"],
        ]

    def apply(self, character):
        """
        handle a character trying to research a blueprint
        
        Parameters:
            character: the character trying to use the item
        """

        sheet = None
        for item in self.container.getItemByPosition((self.xPosition, self.yPosition - 1,self.zPosition)):
            if item.type == "Sheet":
                sheet = item
                break

        if not sheet:
            character.addMessage("no sheet - place sheet to the top/north")
            return

        inputThings = []

        inputThings.extend(self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)))
        inputThings.extend(self.container.getItemByPosition((self.xPosition, self.yPosition + 1, self.zPosition)))

        if not inputThings:
            character.addMessage("no items - place items to the left/west")
            return

        abstractedInputThings = {}
        for item in inputThings:
            abstractedInputThings[item.type] = {"item": item}

        reciepeFound = None
        for reciepe in self.reciepes:
            hasMaterials = True
            for requirement in reciepe[0]:
                if requirement not in abstractedInputThings:
                    hasMaterials = False

            if hasMaterials:
                reciepeFound = reciepe
                break

        if reciepeFound:
            # spawn new item
            new = src.items.itemMap["BluePrint"]()
            new.setToProduce(reciepeFound[1])
            new.bolted = False

            targetFull = False
            if (self.xPosition + 1, self.yPosition, self.zPosition) in self.container.itemByCoordinates:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition, self.zPosition)
                        ]
                    )
                    > 15
                ):
                    targetFull = True
                for item in self.container.itemByCoordinates[
                    (self.xPosition + 1, self.yPosition, self.zPosition)
                ]:
                    if item.walkable == False:
                        targetFull = True

            if targetFull:
                character.addMessage(
                    "the target area is full, the machine does not produce anything"
                )
                return

            self.container.addItem(new,(self.xPosition + 1,self.yPosition,self.zPosition))

            for itemType in reciepeFound[0]:
                self.container.removeItem(abstractedInputThings[itemType]["item"])
            self.container.removeItem(sheet)
            character.addMessage("you create a blueprint for " + reciepe[1])
            character.addMessage("items used: " + ", ".join(reciepeFound[0]))
        else:
            character.addMessage("unable to produce blueprint from given items")
            return

src.items.addType(BluePrinter)

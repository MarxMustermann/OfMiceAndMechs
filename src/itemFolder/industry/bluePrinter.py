import src

'''
'''
class BluePrinter(src.items.Item):
    type = "BluePrinter"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,name="BluePrinter",noId=False):
        super().__init__(display=src.canvas.displayChars.blueprinter,name=name)
        self.submenue = None
        self.text = None

        self.reciepes = [
                [["MemoryCell","Connector","FloorPlate"],"UniformStockpileManager"],
                [["MemoryCell","Connector","Command"],"ProductionManager"],
                [["MemoryCell","Bloom","SickBloom"],"AutoFarmer"],

                [["MemoryCell","Tank"],"MemoryBank"],
                [["MemoryCell","Puller"],"MemoryDump"],
                [["MemoryCell","Heater"],"SimpleRunner"],
                [["MemoryCell","Pusher"],"MemoryStack"],
                [["MemoryCell","Connector"],"MemoryReset"],

                [["Case","Sheet","Bloom"],"BloomContainer"],
                [["Case","Sheet"],"Container"],

                [["Sheet","pusher"],"Sorter"],
                [["Sheet","puller"],"Mover"],
                [["Stripe","Connector"],"RoomControls"],
                [["GooFlask","Tank"],"GrowthTank"],
                [["Radiator","Heater"],"StasisTank"],
                [["Mount","Tank"],"MarkerBean"],
                [["Bolt","Tank"],"PositioningDevice"],
                [["Bolt","puller"],"Watch"],
                [["Bolt","Heater"],"BackTracker"],
                [["Bolt","pusher"],"Tumbler"],
                [["Sheet","Heater"],"ItemUpgrader"],
                [["Sheet","Connector"],"ItemDowngrader"],
                [["Scrap","MetalBars"],"Scraper"],
                [["Tank","Connector"],"ReactionChamber"],

                [["Frame","MetalBars"],"Case"],
                [["Frame"],"PocketFrame"],
                [["Connector","MetalBars"],"MemoryCell"],

                [["Sheet","MetalBars"],"Tank"],
                [["Radiator","MetalBars"],"Heater"],
                [["Mount","MetalBars"],"Connector"],
                [["Stripe","MetalBars"],"pusher"],
                [["Bolt","MetalBars"],"puller"],
                [["Rod","MetalBars"],"Frame"],

                [["Bloom","MetalBars"],"SporeExtractor"],
                [["Sheet","Rod","Bolt"],"FloorPlate"],
                [["Coal","SickBloom"],"FireCrystals"],

                [["Command"],"AutoScribe"],
                [["Corpse"],"CorpseShredder"],

                [["Tank"],"GooFlask"],
                [["Heater"],"Boiler"],
                [["Connector"],"Door"],
                [["pusher"],"Drill"],
                [["puller"],"RoomBuilder"],

                [["Explosive"],"Bomb"],
                [["Bomb"],"Mortar"],

                [["Sheet"],"Sheet"],
                [["Radiator"],"Radiator"],
                [["Mount"],"Mount"],
                [["Stripe"],"Stripe"],
                [["Bolt"],"Bolt"],
                [["Rod"],"Rod"],

                [["Scrap"],"ScrapCompactor"],
                [["Coal"],"Furnace"],
                [["BluePrint"],"BluePrinter"],
                [["MetalBars"],"Wall"],

                [["GooFlask"],"GooDispenser"],
                [["Bloom"],"BloomShredder"],
                [["VatMaggot"],"MaggotFermenter"],
                [["BioMass"],"BioPress"],
                [["PressCake"],"GooProducer"],
            ]

    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        sheet = None
        if (self.xPosition,self.yPosition-1) in self.room.itemByCoordinates:
            for item in self.room.itemByCoordinates[(self.xPosition,self.yPosition-1)]:
                if item.type == "Sheet":
                    sheet = item
                    break

        if not sheet:
            character.addMessage("no sheet - place sheet to the top/north")
            return

        inputThings = []
        if (self.xPosition-1,self.yPosition) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition-1,self.yPosition)])
        if (self.xPosition,self.yPosition+1) in self.room.itemByCoordinates:
            inputThings.extend(self.room.itemByCoordinates[(self.xPosition,self.yPosition+1)])

        if not inputThings:
            character.addMessage("no items - place items to the left/west")
            return

        abstractedInputThings = {}
        for item in inputThings:
            abstractedInputThings[item.type] = {"item":item}

        reciepeFound = None
        for reciepe in self.reciepes:
            hasMaterials = True
            for requirement in reciepe[0]:
                if not requirement in abstractedInputThings:
                    hasMaterials = False

            if hasMaterials:
                reciepeFound = reciepe
                break

        if reciepeFound:
            # spawn new item
            new = BluePrint(creator=self)
            new.setToProduce(reciepeFound[1])
            new.xPosition = self.xPosition+1
            new.yPosition = self.yPosition
            new.bolted = False

            targetFull = False
            if (self.xPosition+1,self.yPosition) in self.room.itemByCoordinates:
                if len(self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]) > 15:
                    targetFull = True
                for item in self.room.itemByCoordinates[(self.xPosition+1,self.yPosition)]:
                    if item.walkable == False:
                        targetFull = True

            if targetFull:
                character.addMessage("the target area is full, the machine does not produce anything")
                return

            self.room.addItems([new])

            for itemType in reciepeFound[0]:
                self.room.removeItem(abstractedInputThings[itemType]["item"])
            self.room.removeItem(sheet)
            character.addMessage("you create a blueprint for "+reciepe[1])
            character.addMessage("items used: "+", ".join(reciepeFound[0]))
        else:
            character.addMessage("unable to produce blueprint from given items")
            return

    def getLongInfo(self):
        text = """

This machine creates Blueprints.

The Blueprinter has two inputs
It needs a sheet on the north to print the blueprint onto.
The items from the blueprint reciepe need to be added to the west or south.

"""
        return text

src.items.addType(BluePrinter)

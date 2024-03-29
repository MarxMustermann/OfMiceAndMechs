import src


class ManufacturingManager(src.items.Item):
    """
    """


    type = "ManufacturingManager"

    def __init__(self, name="ManufacturingManager", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="MM", name=name)

        self.applyOptions.extend(
                        [
                                                                ("showList", "show list"),
                                                                ("changeProduction", "change production"),
                        ]
                        )
        self.applyMap = {
                    "showList": self.showList,
                    "changeProduction": self.changeProduction,
                        }

    def changeProduction(self,character):
        self.changeProductionLoop({"character":character})

    def changeProductionLoop(self,params,selected=None):
        manufacturingTables = self.container.getItemsByType("ManufacturingTable",needsBolted=True)
        numActiveTables = {}
        numTablesUsed = 0
        for item in manufacturingTables:
            if not item.toProduce:
                continue
            numActiveTables[item.toProduce] = numActiveTables.get(item.toProduce,0) + 1
            numTablesUsed += 1

        character = params["character"]
        if "type" not in params:
            options = []
            options.append((None,f"exit menu"))
            basicOptions = ["MetalBars","Rod","Frame","Case","Wall","ManufacturingTable","Bolt"]
            for option in basicOptions:
                options.append((option,f"{option} {numActiveTables.get(option,0)}"))

            submenue = src.interaction.SelectionMenu(f"Manufacturingtables {numTablesUsed}/{len(manufacturingTables)}:\n(select and press j to increase)\n(select and press k to decrease)\n",options,targetParamName="type",selected=selected)
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"changeProductionLoop","params":params}
            return

        if params["type"] == None:
            return

        if params["key"] == "j":
            for table in manufacturingTables:
                if table.toProduce:
                    continue
                table.toProduce = params["type"]
                character.addMessage("added workshop")
                break
            tablePos = table.getPosition()
            self.container.addStorageSlot((tablePos[0]+1,tablePos[1],tablePos[2]),params["type"])
            materialsNeeded = src.items.rawMaterialLookup.get(params["type"])
            if params["type"] == "MetalBars":
                materialsNeeded = ["Scrap"]
            if not materialsNeeded:
                materialsNeeded = ["MetalBars"]
            self.container.addInputSlot((tablePos[0]-1,tablePos[1],tablePos[2]),materialsNeeded[0])
        if params["key"] == "k":
            for table in manufacturingTables:
                if not table.toProduce == params["type"]:
                    continue

                neighbours = []
                tablePos = table.getPosition()
                neighbours.append((tablePos[0]-1,tablePos[1],tablePos[2]))
                neighbours.append((tablePos[0]+1,tablePos[1],tablePos[2]))

                for slot in self.container.storageSlots[:]:
                    print(slot)
                    if slot[0] in neighbours:
                        self.container.storageSlots.remove(slot)

                for slot in self.container.inputSlots[:]:
                    if slot[0] in neighbours:
                        self.container.inputSlots.remove(slot)

                table.toProduce = None
                character.addMessage("removed workshop")
                break
        self.changeProductionLoop({"character":character},selected=params["type"])

    def showList(self,character):
        manufacturingTables = self.container.getItemsByType("ManufacturingTable",needsBolted=True)
        numActiveTables = 0
        for item in manufacturingTables:
            if not item.toProduce:
                continue
            numActiveTables += 1

        text = "This room has {len(manufacturingTables)} ManufacturingTables. {numActiveTables} used.\n"
        text = "This room has the following ManufacturingTables:\n"

        for item in manufacturingTables:
            if not item.toProduce:
                continue
            text += f"{item.toProduce} - numUsed: {min(50,item.numUsed)} pos: {item.getPosition()}\n"

        submenue = src.interaction.TextMenu(text)
        character.macroState["submenue"] = submenue
        return

        if "type" not in params:
            params["type"] = "random"
            options = []
            index = 0
            for _item in self.prefabs["ScrapToMetalBars"]:
                index += 1
                options.append((index,f"prefab{index}"))
            submenue = src.interaction.SelectionMenu("what floorplan to use?",options,targetParamName="type")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"addScrapCompactorFromMap","params":params}
            return

        if params["type"] == "random":
            params["type"] = random.randint(1,len(self.prefabs["ScrapToMetalBars"]))

        character = params["character"]

        room = self.addRoom(params["coordinate"])

        floorPlan = copy.deepcopy(self.prefabs["ScrapToMetalBars"][params["type"]-1])
        room.resetDirect()
        room.floorPlan = floorPlan

        if instaSpawn:
            room.spawnPlaned()
            room.spawnPlaned()
            room.addRandomItems()
            room.spawnGhouls(character)

        #self.container.sources.append((room.getPosition(),"MetalBars"))

        for otherRoom in self.rooms:
            otherRoom.sources.append((room.getPosition(),"MetalBars"))
        self.sourcesList.append((room.getPosition(),"MetalBars"))

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
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})
        self.numUsed = 0

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})
        self.numUsed = 0


src.items.addType(ManufacturingManager)

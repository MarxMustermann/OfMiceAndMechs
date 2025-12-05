import src


class Glassifier(src.items.Item):
    """
    """


    type = "Glassifier"

    def __init__(self, name="Glassifier", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="<>", name=name)

        self.applyOptions.extend(
                        [
                                                                ("pray", "pray"),
                                                                ("startGlassifier", "start glassifier"),
                                                                ("stabilize", "stabilize glassifier"),
                        ]
                        )
        self.applyMap = {
                    "startGlassifier": self.startGlassifier,
                    "pray": self.pray,
                    "stabilize": self.stabilize,
                        }

        self.phase = 0
        self.numPrayed = 0
        self.unstable = False
        self.unstableLevel = 0

    def stabilize(self,character,repeat=False):
        if not self.unstable:
            character.addMessage("the glassifier is already stable")
            return

        requiredItems = {}
        if self.phase > 1:
            requiredItems["Scrap"] = 10

        if self.phase > 2:
            requiredItems["VatMaggot"] = 10

        if self.phase > 3:
            requiredItems["MetalBars"] = 10

        if self.phase > 4:
            requiredItems["Rod"] = 10

        if self.phase > 5:
            requiredItems["ManufacturingTable"] = 10

        if self.phase > 6:
            requiredItems["Bolt"] = 10

        if self.phase > 7:
            requiredItems["Wall"] = 10

        if self.phase > 8:
            requiredItems["LightningRod"] = 10

        if self.phase > 9:
            requiredItems["GooFlask"] = 1

        requiredItems_orig = requiredItems.copy()

        foundScrap = []
        foundItems = []
        for item in self.container.itemsOnFloor:
            if item.bolted:
                continue

            if item.type == "Scrap":
                foundScrap.append(item)
                if "Scrap" in requiredItems:
                    if requiredItems["Scrap"] > item.amount:
                        requiredItems["Scrap"] -= item.amount
                    else:
                        del requiredItems["Scrap"]
                continue

            if item.type == "GooFlask":
                if not item.uses == 100:
                    continue

            if item.type in requiredItems:
                if requiredItems[item.type] == 1:
                    del requiredItems[item.type]
                else:
                    requiredItems[item.type] -= 1
                foundItems.append(item)

        if requiredItems:
            character.addMessage(requiredItems)
            character.addMessage("you are missing some items:")
            return

        for (k,v) in requiredItems_orig.items():
            character.addMessage(f"{k} - {v}")
        character.addMessage("you stabilize the glassifier by using the following items:")

        self.container.removeItems(foundItems)
        amountRemoved = 0
        for scrap in foundScrap[:]:
            if scrap.amount+amountRemoved > 10:
                scrap.amount -= 10-amountRemoved
                break
            amountRemoved += scrap.amount
            self.container.removeItem(scrap)

        self.unstableLevel -= 1
        if self.unstableLevel == 0:
            self.unstable = False

        if repeat:
            character.runCommandString("Jwj")

    def pray(self,character):
        if self.unstable:
            self.stabilize(character,repeat=True)
            if self.unstable:
                character.addMessage("you need to stabilize the glassifier")
                return
        if self.phase == 0:
            character.addMessage("you have to start the glassifier")
            return

        if self.phase == 1:
            items = []
            amountScrap = 0
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Scrap":
                    continue
                items.append(item)
                amountScrap += item.amount
                if amountScrap >= 10:
                    break
            if amountScrap < 10:
                text = self.getPhaseInstruction()
                submenue = src.menuFolder.textMenu.TextMenu(text)
                character.macroState["submenue"] = submenue

                character.addMessage("you need 10 units of Scrap in the room to pray.")
                return

            removedScrap = 0
            for item in items:
                if removedScrap + item.amount <= 10:
                    removedScrap += item.amount
                    self.container.removeItem(item)
                else:
                    item.amount -= 10-removedScrap
                    item.setWalkable()

        if self.phase == 2:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "VatMaggot":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 VatMaggot in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 3:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "MetalBars":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 MetalBars in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 4:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Rod":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 Rod in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 5:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "ManufacturingTable":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 ManufacturingTable in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 6:
            rods = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Bolt":
                    continue
                rods.append(item)
                if len(rods) >= 10:
                    break
            if len(rods) < 10:
                character.addMessage("you need 10 Bolt in the room to pray.")
                return
            self.container.removeItems(rods)

        if self.phase == 7:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Wall":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 Wall in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 8:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "LightningRod":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                character.addMessage("you need 10 LightningRod in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 9:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "GooFlask":
                    continue
                if not item.uses == 100:
                    continue
                items.append(item)
                if len(items) >= 1:
                    break
            if len(items) < 1:
                character.addMessage("you need 1 GooFlask in the room to pray.")
                return
            self.container.removeItems(items)

        if self.phase == 10:
            emptyRoom = None
            for room in self.getTerrain().rooms:
                if len(room.itemsOnFloor) <= 13+13+11+11:
                    emptyRoom = room
                    break

            if not emptyRoom:
                character.addMessage("your base needs 1 empty room to pray.")
                return
            self.getTerrain().removeRoom(emptyRoom)

        if self.phase == 11:
            itemsToRemove = []
            room = self.container
            for item in room.itemsOnFloor:
                if item.xPosition == 0 or item.xPosition == 12 or item.yPosition == 0 or item.yPosition == 12:
                    continue
                itemsToRemove.append(item)
            room.removeItems(itemsToRemove)
            room.inputSlots = []
            temple = room

            item = src.items.itemMap["Shrine"]()
            item.god = 1
            temple.addItem(item,(1,2,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 1
            temple.addItem(item,(2,2,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 2
            temple.addItem(item,(3,2,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 2
            temple.addItem(item,(4,2,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 3
            temple.addItem(item,(7,1,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 3
            temple.addItem(item,(7,2,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 4
            temple.addItem(item,(10,1,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 4
            temple.addItem(item,(10,2,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 5
            temple.addItem(item,(11,5,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 5
            temple.addItem(item,(10,5,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 6
            temple.addItem(item,(7,5,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 6
            temple.addItem(item,(7,4,0))

            item = src.items.itemMap["Shrine"]()
            item.god = 7
            temple.addItem(item,(8,4,0))

            item = src.items.itemMap["GlassStatue"]()
            item.itemID = 7
            temple.addItem(item,(8,5,0))

            item = src.items.itemMap["Throne"]()
            temple.addItem(item,(6,6,0))

            return

        self.pray_wait({"character":character,"timeTaken":0,"prayerTime":100})

    def pray_wait(self,params):
        character = params["character"]
        character.runCommandString(".",nativeKey=True)
        progressbar = ""
        progressbar += f"phase:  {self.phase}\n"
        progressbar += f"prayer: {self.numPrayed+1}\n\n"
        progressbar += "X"*(params["timeTaken"]//10)+"."*((params["prayerTime"]//10)-(params["timeTaken"]//10))
        if params["prayerTime"] - params["timeTaken"] > 10:
            character.takeTime(10,"praying")
            params["timeTaken"] += 10
            submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(progressbar,targetParamName="abortKey")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"pray_wait","params":params}
        else:
            character.takeTime(params["prayerTime"] - params["timeTaken"],"praying")
            params["timeTaken"] += params["prayerTime"] - params["timeTaken"]
            submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(progressbar,targetParamName="abortKey")
            character.macroState["submenue"] = submenue
            character.macroState["submenue"].followUp = {"container":self,"method":"pray_done","params":params}

    def pray_done(self,params):
        character = params["character"]

        self.numPrayed += 1
        terrain = self.getTerrain()
        terrain.mana += 1
        character.addMessage("you gained 1 mana for praying")

        if self.numPrayed < 10:
            character.runCommandString("Jwj")

        if self.numPrayed < 10:
            character.addMessage(f"You prayed {self.numPrayed} times.")
            return

        terrain.mana += 5
        character.addMessage("you gained 5 mana for praying")
        character.addMessage(f"You prayed 5 times. The glassifier enters the next phase.")

        self.phase += 1
        self.numPrayed = 0

        text = self.getPhaseInstruction()
        submenue = src.menuFolder.textMenu.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.addMessage(text)

    def handleEpochChange(self):
        if self.phase == 11:
            return
        if self.unstable:
            if self.unstableLevel == 1:
                character = src.gamestate.gamestate.mainChar

                submenue = src.menuFolder.textMenu.TextMenu("The glassfifier is unstable. Stabilise it this epoch!")
                character.macroState["submenue"] = submenue
                self.unstableLevel += 1
            else:
                print("the word ends")
                1/0
        else:
            self.unstable = True
            self.unstableLevel = 1

            character = src.gamestate.gamestate.mainChar
            character.addMessage("a new epoch starts. The Glassifier starts beeing unstable")

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15))+10)
        event.setCallback({"container": self, "method": "handleEpochChange"})
        currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
        currentTerrain.addEvent(event)


    def startGlassifier(self,character):
        if self.phase == 0:
            self.phase = 1
            self.numPrayed = 0

            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15))+10)
            event.setCallback({"container": self, "method": "handleEpochChange"})
            currentTerrain = src.gamestate.gamestate.terrainMap[7][7]
            currentTerrain.addEvent(event)

            text = self.getPhaseInstruction()
            submenue = src.menuFolder.textMenu.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.addMessage(text)

            return

        character.addMessage("you already started the glassifier")
        return

    def render(self):
        if not self.container:
            return "<>"

        if self.unstable:
            if self.unstableLevel == 1:
                return "II"
            if self.unstableLevel == 2:
                return "!!"

        if self.phase == 0:
            return "()"
        if self.phase == 1:
            items = []
            amountScrap = 0
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Scrap":
                    continue
                items.append(item)
                amountScrap += item.amount
                if amountScrap >= 10:
                    break
            if amountScrap < 10:
                return "<>"
            return "()"
        if self.phase == 2:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "VatMaggot":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 3:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "MetalBars":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 4:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Rod":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 5:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "ManufacturingTable":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 6:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Bolt":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 7:
            items = []
            for item in self.container.itemsOnFloor:
                if item.bolted:
                    continue
                if not item.type == "Wall":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 8:
            items = []
            for item in self.container.itemsOnFloor:
                if not item.type == "LightningRod":
                    continue
                items.append(item)
                if len(items) >= 10:
                    break
            if len(items) < 10:
                return "<>"
            return "()"
        if self.phase == 9:
            items = []
            for item in self.container.itemsOnFloor:
                if not item.type == "GooFlask":
                    continue
                if not item.uses == 100:
                    continue
                items.append(item)
                if len(items) >= 1:
                    break
            if len(items) < 1:
                return "<>"
            return "()"

        if self.phase == 10:
            emptyRoom = None
            terrain = self.getTerrain()
            for room in terrain.rooms:
                print(len(room.itemsOnFloor))
                if len(room.itemsOnFloor) <= 13+13+11+11:
                    emptyRoom = room
                    break
            if not emptyRoom:
                return "<>"
            return "()"
        return "()"

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
           a longer than normal description text
        """

        text = super().getLongInfo()

        text += f"""
The Glassifier is needed to build a temple.
Place it in a room and activate it.

After that, place the items it demands in the room and pray.
Each epoch the glassifier will become unstable.
In that case place the items it demands in the room and stabilze it.

In case you succeed long enough it will build a temple.
If the glassifier becomes fully unstable, it will explode.
"""
        text += self.getPhaseInstruction()

        return text

    def getPhaseInstruction(self):
        text = ""

        if self.phase == 0:
            text += """
The Glassifier is not fully active yet. Activate it.
"""
        if self.phase == 1:
            text += """
The Glassifier is active. Bring Scrap.

Put 10 Scrap in the room and pray.

Scrap is gathered by NPCs with the "ressource gathering" duty.
Those NPCs will bring Scrap into this room, too.

Use the DutyArtwork (DA) to assign that duty to some NPCs.
"""
        if self.phase == 2:
            text += """
The Glassifier needs 10 VatMaggot per prayer now.
Put 10 VatMaggot in the room and pray.

VatMaggots are gathered by NPCs with the "maggot gathering" duty.
Those NPCs will bring VatMaggots into this room, too.

Assign that duty to a few NPCs at the DutyArtwork.
Be sure to remove the other duties from those NPCs.

Assigning more than 2 NPCs to that duty has no point.
The VatMagots grow in a Tree and reproduce at a limited rate.
Harvesting too much reduces the reproduction rate.
"""

        if self.phase == 3:
            text += """
The Glassifier needs 10 MetalBars per prayer now.

Those MetalBars need to be produced.
This is more complicated than just gathering items.

Ensure you have NPCs for the following duties:

* resource gathering
This ensures that enough scrap is available

* scrap hammering
This ensures that NPCs will produce MetalBars (==) from Scrap at the Anvil (WA)

* resouce fetching
This ensures that NPCs carry the MetalBars (==) to their destination
"""

        if self.phase == 4:
            text += """
The Glassifier needs 10 Rod per prayer now.

Those need to be produced from Metalbars.
ManufacturingTables (mT) are used to do that.
Your base has some ManufacturingTables configured to produce Rod.

NPCs with the "manufacturing" duty will use those ManufacturingTables.
Set the "manufacturing" duty to some NPCs.

Ensure you keep producing MetalBars, though.
So keep NPCs for the following duties:

* resource gathering
* scrap hammering
* resouce fetching
"""

        if self.phase == 5:
            text += """
The Glassifier needs 10 ManufacturingTables per prayer now.

Those need to be produced from Metalbars.
ManufacturingTables are produced at ManufacturingTables.
You base starts with only a single ManufacturingTable that is set to produce ManufacturingTables.

Your base has free ManufacturingTables that can be assigned to produce items.
Those can be found in the manufacturingHall anlongside the ManufacturingTables that are set to produce Rod.

The manufacturingHall also contains a ManufacturingManager (MM).
The ManufacturingManger allows to set what the ManufacturingTables in the manufacturingHall produce.
Use that to increase the amount of ManufacturinTables producing ManufacturingTables by 6.
"""

        if self.phase == 6:
            text += """
The Glassifier needs 10 Bolt per prayer now.

Allocate the remaining ManufacturingTables to producing Bolts.
"""

        if self.phase == 7:
            text += """
The Glassifier needs 10 Wall per prayer now.

The production chain for walls is a bit more complicated.
Metalbars need to be produced from Scrap
Rods need to be produced from MetalBars
Frames need to be produced from Rods.
Cases need to be produced from Frames.
Finally Walls can be produced from Cases and MetalBars.

You do not have to produce them, though.
There are a lot of Walls strewn around on this terrain.
Set your NPCs to the duty "scavenging" and they will collect those Walls.
"""

        if self.phase == 8:
            text += """
The Glassifier needs 10 LightningRods per prayer now.

LightningRods can not just be manufactured at a ManufacturingTable.
They are produced by an Electifier from Rods.
Your base has no
"""

        if self.phase == 9:
            text += """
full goo flasks
"""

        if self.phase == 10:
            text += """
empty rooms
"""

        return text

src.items.addType(Glassifier)

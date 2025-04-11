import random

import src

class ReportArchive(src.items.Item):
    type = "ReportArchive"
    name = "report archive"
    description = "Use it to read achived reports"
    walkable = False
    bolted = True

    def __init__(self):
        super().__init__(display="RA")

        self.applyOptions = [
            ("show reports", "show reports"),
            ("unlock report", "add memory fragment"),
        ]

        self.applyMap = {
            "show reports": self.showReports,
            "unlock report": self.unlockReport,
        }

        self.fragments_unlocked = 0

        self.reports = None

    def generateReports(self):
        self.reports = []

        ownPos = self.getTerrain().getPosition()
        emptyPlaces = []
        spiderPits = []
        labs = []

        for x in range(1,14):
            for y in range(1,14):
                checkTerrain = src.gamestate.gamestate.terrainMap[y][x]

                match checkTerrain.tag:
                    case "nothingness":
                        emptyPlaces.append(checkTerrain.getPosition())
                    case "spider pit":
                        spiderPits.append(checkTerrain.getPosition())
                    case "lab":
                        labs.append(checkTerrain.getPosition())

        random.shuffle(emptyPlaces)
        emptyPlaces = emptyPlaces[:min(3,len(emptyPlaces))]

        emptyPlacesString = ""
        for place in emptyPlaces:
            emptyPlacesString += f"{place}, "
        if len(emptyPlacesString) > 0:
            emptyPlacesString = emptyPlacesString[:-2]
                
        self.reports.append(
                ("Survey complete",f"The terrain {ownPos} is pretty unremarkable, but has the ressource we need.\nSome scrap to proccess, enough moisture to grow mold.\nEven a small forrest to harvest maggots from is here!\n\nThat is a nice change from the terrains {emptyPlacesString}\nthose were so dry you couldn't grow a single mold bloom on it.")
            )
        self.reports.append(
                ("Base established",f"The base has been established, technically.\nThe colony mech has arrived and was placed.\nThere is little space available and production capacity is severly limited.\n\nThat half of the crew were killed by Spiders doesn't help either,\nbut they will continue to be useful as ghuls.\nAll spider eggs will have to be destroyed or they will be a long term problem.\n\nAt least it is not as bad as on {random.choice(spiderPits)}.\nThe Spiders there had a posion strong enough to kill a clone with a single bite!")
            )
        self.reports.append(
                ("Base extension complete","The Base now has several additional rooms to allow for more storage and production.\n\nWe were ordered to experiment with the room layouts.\nSo we will use the wall production FloorPlan from (x,y,z)\nand the storage room layout like the one we have seen on terrain (x,y,z)")
            )
        self.reports.append(
                ("Remote bases established","To get some ressources we are missing here remote bases were established.\n\n(x,y,z) for XYZ\n(x,y,z) for XYZ\n(x,y,z) for XYZ\n\nI hope they will stay active even without additional protection.")
            )
        self.reports.append(
                ("Expedition started",f"The base leader and the leading officers are starting an expedition to {random.choice(labs)} soon.\nWe are ordered to stay on standby until they return."),
            )

    def showReports(self,character):

        if self.reports == None:
            self.generateReports()

        if self.fragments_unlocked < 1:
            submenue = src.menuFolder.textMenu.TextMenu(
                "== database error ==\n\n\nThe database cannot be accessed.\n\nCollect MemoryFragments to repair the database and make it accessible again."
            )
            character.macroState["submenue"] = submenue
            character.runCommandString("~", nativeKey=True)
            return
        else:
            options = []
            report_counter = 0
            while report_counter < self.fragments_unlocked:
                options.append((report_counter+1,self.reports[report_counter][0]))
                report_counter += 1

            text = ""
            if self.fragments_unlocked < len(self.reports):
                text += """== partial database error ==\n\nThe database cannot be fully accessed\n\nCollect more MemoryFragments to fully repair the database.\n\n"""
            text += """Select what report to show:\n"""
            submenue = src.menuFolder.selectionMenu.SelectionMenu(
                text = text,
                options=options
            )

            submenue.followUp = {
                "container": self,
                "method": "openReport",
                "params": {"character":character},
            }

            character.macroState["submenue"] = submenue
            character.runCommandString("~", nativeKey=True)
            return

    def openReport(self,extraParams):
        if extraParams["selection"] == None:
            return
        self.read(extraParams["selection"]-1,extraParams["character"])

    def read(self, fragment_number, character):
        report = self.reports[fragment_number]
        submenue = src.menuFolder.textMenu.TextMenu(
            f"== {report[0]} ==\n\n{report[1]}"
        )
        submenue.tag = "message"
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)

    def unlockReport(self, character):

        if self.reports == None:
            self.generateReports()

        if self.fragments_unlocked >= len(self.reports):
            character.addMessage("You can't unlock more reports")
            return

        fragments = []
        for item in character.inventory:
            if item.type == "MemoryFragment":
                fragments.append(item)

        if not fragments:
            character.addMessage("You need to have fragments in your inventory to decrypt them")
            return

        character.inventory.remove(fragments[-1])

        self.fragments_unlocked += 1

        self.read(self.fragments_unlocked-1, character)

src.items.addType(ReportArchive)

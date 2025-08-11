import random

import src

class ReportArchive(src.items.Item):
    '''
    ingame item to give the player hints to te location on the good-ending lab
    '''
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
        '''
        generates the reports to show
        '''

        # gather information obout what terrains are where
        ownPos = self.getTerrain().getPosition()
        emptyPlaces = []
        spiderPits = []
        labs = []
        remoteBases = []
        for x in range(1,14):
            for y in range(1,14):
                checkTerrain = src.gamestate.gamestate.terrainMap[y][x]

                bucket = None
                match checkTerrain.tag:
                    case "nothingness":
                        bucket = emptyPlaces
                    case "spider pit":
                        bucket = spiderPits
                    case "lab":
                        bucket = labs
                    case "remote base":
                        bucket = remoteBases
                if bucket is not None:
                    bucket.append((checkTerrain.getPosition(),checkTerrain.tag))

        # set up a container for the reports
        self.reports = []

        # generate a report hinting at empty places
        random.shuffle(emptyPlaces)
        emptyPlaces = emptyPlaces[:min(3,len(emptyPlaces))]
        emptyPlacesString = ""
        for place,tag in emptyPlaces:
            emptyPlacesString += f"{place}, "
        if len(emptyPlacesString) > 0:
            emptyPlacesString = emptyPlacesString[:-2]
        self.reports.append(
                ("Survey complete",f"The terrain {ownPos} is pretty unremarkable, but has the ressource we need.\nSome scrap to proccess, enough moisture to grow mold.\nEven a small forrest to harvest maggots from is here!\n\nThat is a nice change from the terrains {emptyPlacesString}\nthose were so dry you couldn't grow a single mold bloom on it.",emptyPlaces)
            )

        # generate a report hinting at spider pits
        spiderPit = random.choice(spiderPits)
        self.reports.append(
                ("Base established",f"The base has been established, technically.\nThe colony mech has arrived and was placed.\nThere is little space available and production capacity is severly limited.\n\nThat half of the crew were killed by Spiders doesn't help either,\nbut they will continue to be useful as ghuls.\nAll spider eggs will have to be destroyed or they will be a long term problem.\n\nAt least it is not as bad as on {spiderPit[0]}.\nThe Spiders there had a posion strong enough to kill a clone with a single bite!",[spiderPit])
            )

        # generate a report hinting at remote bases
        random.shuffle(remoteBases)
        remoteBases = remoteBases[:min(3,len(remoteBases))]
        remoteBasesString = ""
        for place,tag in remoteBases:
            remoteBasesString += f"{place}, "
        if len(remoteBasesString) > 0:
            remoteBasesString = remoteBasesString[:-2]
        self.reports.append(
                ("Remote bases established",f"To get some ressources we are missing here remote bases were established:\n\n{remoteBasesString}\n\nI hope they will stay active even without additional protection.",remoteBases)
            )

        # generate a report at the lab
        lab = random.choice(labs)
        self.reports.append(
                ("Expedition started",f"The base leader and the leading officers are starting an expedition to {lab[0]} soon.\nWe are ordered to stay on standby until they return.",[lab]),
            )

    def showReports(self,character):
        '''
        show UI to browse the unlocked reports
        '''

        # generate the reports
        if self.reports == None:
            self.generateReports()

        # show basic description
        if self.fragments_unlocked < 1:
            submenue = src.menuFolder.textMenu.TextMenu(
                "== database error ==\n\n\nThe database cannot be accessed.\n\nCollect MemoryFragments to repair the database and make it accessible again."
            )
            character.macroState["submenue"] = submenue
            character.runCommandString("~", nativeKey=True)
            return

        # compile a list of reports to select from
        options = []
        report_counter = 0
        while report_counter < self.fragments_unlocked:
            options.append((report_counter+1,self.reports[report_counter][0]))
            report_counter += 1

        # generate the menu to select what report to show
        text = ""
        if self.fragments_unlocked < len(self.reports):
            text += """== partial database error ==\n\nThe database cannot be fully accessed\n\nCollect more MemoryFragments to fully repair the database.\n\n"""
        text += """Select what report to show:\n"""
        submenue = src.menuFolder.selectionMenu.SelectionMenu(
            text = text,
            options=options
        )

        # show the UI to select what report to show
        submenue.followUp = {
            "container": self,
            "method": "openReport",
            "params": {"character":character},
        }
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)
        return

    def openReport(self,extraParams):
        '''
        triggers opening the UI to show a report
        '''
        if extraParams["selection"] == None:
            return
        self.read(extraParams["selection"]-1,extraParams["character"])

    def read(self, fragment_number, character):
        '''
        show the UI to view a report
        '''

        # get the report
        report = self.reports[fragment_number]

        # unveil the coordinates mantioned 
        for (coordinate,tag) in report[2]:
            if coordinate in character.terrainInfo:
                continue
            character.terrainInfo[coordinate] = {"tag":tag}

        # open UI to read the report
        submenue = src.menuFolder.textMenu.TextMenu(
            f"== {report[0]} ==\n\n{report[1]}"
        )
        submenue.tag = "message"
        character.macroState["submenue"] = submenue
        character.runCommandString("~", nativeKey=True)

    def unlockReport(self, character):
        '''
        unlocks a report
        '''
        if self.reports == None:
            self.generateReports()

        if self.fragments_unlocked >= len(self.reports):
            text = "You can't unlock more reports"
            submenue = src.menuFolder.textMenu.TextMenu(
                text = text,
            )
            character.macroState["submenue"] = submenue
            character.addMessage(text)
            return

        fragments = []
        for item in character.inventory:
            if item.type == "MemoryFragment":
                fragments.append(item)

        if not fragments:
            text = "You need to have fragments in your inventory to decrypt them"
            submenue = src.menuFolder.textMenu.TextMenu(
                text = text,
            )
            character.macroState["submenue"] = submenue
            character.addMessage(text)
            return

        character.removeItemFromInventory(fragments[-1])

        self.fragments_unlocked += 1

        self.read(self.fragments_unlocked-1, character)

# register item type
src.items.addType(ReportArchive)

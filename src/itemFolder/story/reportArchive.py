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

        self.reports = [("example report 1","this is example message 1"), ("example report 2","this is example message 2"), ("example report 3","this is example message 3")]

    def showReports(self,character):
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

import src


class ScrapCommander(src.items.Item):
    type = "ScrapCommander"

    def __init__(self):
        super().__init__(display=";;")
        self.name = "scrap commander"

        self.bolted = True
        self.walkable = True
        self.numScrapStored = 0
        self.attributesToStore.extend(["numScrapStored"])

    def apply(self, character):
        options = [("addScrap", "add scrap"), ("fetchScrap", "fetch scrap")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def setScrapPath(self, numScrap):
        fieldNum = numScrap // 20

        rowNum = fieldNum // 11
        rowRemain = fieldNum % 11

    def runCommandString(self, command, character):
        character.runCommandString(command)

    def apply2(self):
        if self.submenue.selection == "addScrap":
            self.character.addMessage("should add now")
            self.numScrapStored += 1
            self.setScrapPath(self.numScrapStored)
        elif self.submenue.selection == "fetchScrap":
            if self.numScrapStored == 0:
                self.character.addMessage("no scrap available")
                return

            self.numScrapStored -= 1

            move = ""
            move += "a" * (11 - 2 - self.numScrapStored // (20 * 11))
            remaining = self.numScrapStored % (20 * 11)
            self.character.addMessage(remaining)
            if remaining > 10 * 20 - 1:
                move += "Ka"
            else:
                move += "a"
                if remaining > 5 * 20 - 1:
                    move += "s" * (-(remaining // 20 - 5 - 4))
                    move += "Ks"
                    move += "w" * (-(remaining // 20 - 5 - 4))
                else:
                    move += "w" * (-(remaining // 20 - 4))
                    move += "Kw"
                    move += "s" * (-(remaining // 20 - 4))
                move += "d"
            move += "d" * (11 - 2 - self.numScrapStored // (20 * 11))

            self.character.addMessage(move)
            self.runCommandString(move, self.character)


src.items.addType(ScrapCommander)

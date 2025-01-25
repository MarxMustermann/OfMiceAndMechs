import src


class WorkShop(src.items.Item):
    type = "WorkShop"
    name = "WorkShop"

    def produceItem_wait(self, params):
        character = params["character"]

        if not "hitCounter" in params:
            params["hitCounter"] = character.numAttackedWithoutResponse

        if params["hitCounter"] != character.numAttackedWithoutResponse:
            character.addMessage("You got hit while working")
            return
        ticksLeft = params["productionTime"] - params["doneProductionTime"]
        character.timeTaken += 1
        params["doneProductionTime"] += 1

        barLength = params["productionTime"]//10
        if params["productionTime"]%10:
            barLength += 1
        baseProgressbar = "X"*(params["doneProductionTime"]//10)+"."*(barLength-(params["doneProductionTime"]//10))
        progressBar = ""
        while len(baseProgressbar) > 10:
            progressBar += baseProgressbar[:10]+"\n"
            baseProgressbar = baseProgressbar[10:]
        progressBar += baseProgressbar

        submenue = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu(progressBar, targetParamName="abortKey")
        submenue.tag = "metalWorkingProductWait"
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {
            "container": self,
            "method": "produceItem_done" if ticksLeft <= 0 else "produceItem_wait",
            "params": params,
        }
        character.runCommandString(".", nativeKey=True)
        if ticksLeft % 10 != 9 and src.gamestate.gamestate.mainChar == character:
            src.interaction.skipNextRender = True


    def getConfigurationOptions(self, character):
        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self, character):
        self.bolted = True
        character.addMessage("you bolt down the " + self.name)
        character.changed("boltedItem", {"character": character, "item": self})
        if hasattr(self,"numUsed"):
            self.numUsed = 0

    def unboltAction(self, character):
        self.bolted = False
        character.addMessage("you unbolt the " + self.name)
        character.changed("unboltedItem", {"character": character, "item": self})
        if hasattr(self,"numUsed"):
            self.numUsed = 0


src.items.addType(WorkShop)

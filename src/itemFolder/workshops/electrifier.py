import src


class Electrifier(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Electrifier"
    name = "Electrifier"
    description = "Use it to build simple things"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display = "EE")
        self.processStartedAt = None
        self.processing = False
        self.disabled = False

    def apply(self,character):
        if not self.bolted:
            character.addMessage("not bolted")
            return

        if not self.processing:
            rodsFound = []
            for item in self.container.getItemByPosition(
                    (self.xPosition - 1, self.yPosition, self.zPosition)
                ):
                if not item.type == "Rod":
                    continue
                rodsFound.append(item)
                if len(rodsFound) >= 10:
                    break

            if len(rodsFound) < 10:
                character.addMessage("not enough rods")
                character.changed("operated machine",{"character":character,"machine":self})
                return

            self.container.removeItems(rodsFound)
            self.processStartedAt = src.gamestate.gamestate.tick
            self.processing = True
            character.changed("operated machine",{"character":character,"machine":self})
        else:
            if src.gamestate.gamestate.tick < self.processStartedAt + 1000:
                character.addMessage(f"the rods are not electrified yet.\nWait till tick {(self.processStartedAt+1000)//(15*15*15)+1} / {(self.processStartedAt+1000)%(15*15*15)}")
                character.changed("operated machine",{"character":character,"machine":self})
                return

            if self.container.getItemByPosition(
                    (self.xPosition + 1, self.yPosition, self.zPosition)
                ):
                character.addMessage("output full")
                return

            if src.gamestate.gamestate.tick < self.processStartedAt + 2000:
                for i in range(0,10):
                    newItem = src.items.itemMap["LightningRod"]()
                    self.container.addItem(newItem,(self.xPosition + 1, self.yPosition, self.zPosition))
                character.addMessage("You eject the lighning rods")
            else:
                newItem = src.items.itemMap["Scrap"](amount=5)
                self.container.addItem(newItem,(self.xPosition + 1, self.yPosition, self.zPosition))
                character.addMessage("The LightningRods have been destroyed.\nBe faster next time.")

            self.processStartedAt = None
            self.processing = False
            character.changed("operated machine",{"character":character,"machine":self})

    def readyToUse(self):
        try:
            self.disabled
        except:
            self.disabled = False
        if not self.container:
            return False
        if not self.bolted:
            return False

        if not self.processing:
            rodsFound = []
            for item in self.container.getItemByPosition(
                    (self.xPosition - 1, self.yPosition, self.zPosition)
                ):
                if not item.type == "Rod":
                    continue
                rodsFound.append(item)
                if len(rodsFound) >= 10:
                    break

            if len(rodsFound) < 10:
                return False

            return True
        else:
            if self.container.getItemByPosition(
                    (self.xPosition + 1, self.yPosition, self.zPosition)
                ):
                return False

            if src.gamestate.gamestate.tick < self.processStartedAt + 1000:
                return False

            return True

    def render(self):
        if not self.processing:
            if self.readyToUse():
                return "EE"
            return "ee"
        else:
            if self.readyToUse():
                return "FF"
            return "ff"

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
        if self.disabled:
            options["d"] = ("enable", self.enable)
        else:
            options["d"] = ("disable", self.disable)
        options["s"] = ("draw stockpiles", self.drawStockpiles)
        return options

    def drawStockpiles(self,character):

        ##
        # add output

        # calculate position to add the output to
        stockpilePos = (self.xPosition + 1, self.yPosition, self.zPosition)

        # remove old markings
        self.container.clearMarkings(stockpilePos)

        # add output stockpile
        self.container.addStorageSlot(stockpilePos,"LightningRod")

        ##
        # add input

        # calculate position to add the input to
        stockpilePos = (self.xPosition - 1, self.yPosition, self.zPosition)

        # remove old markings
        self.container.clearMarkings(stockpilePos)

        # add output stockpile
        self.container.addInputSlot(stockpilePos,"Rod")


    def enable(self,character):
        character.addMessage("you enable the Machine")
        self.disabled = False

    def disable(self,character):
        character.addMessage("you disable the Machine")
        self.disabled = True

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Machine")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Machine")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        """
        generate simple text description

        Returns:
            the decription text
        """

        text = super().getLongInfo()
        if not self.processing:
            text += f"""
status: idle
"""
        else:
            text += f"""
ready at: {(self.processStartedAt+1000)//(15*15*15)+1} / {(self.processStartedAt+1000)%(15*15*15)}
"""

        return text

src.items.addType(Electrifier)

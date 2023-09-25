import src

class ProductionArtwork(src.items.Item):
    """
    godmode object producing anything from metal bars
    is used in gameplay since it has a very heavy cooldown
    bad pattern: serves as dummy for actual production lines
    """

    type = "ProductionArtwork"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display=src.canvas.displayChars.productionArtwork)

        self.coolDown = 10000
        self.coolDownTimer = -self.coolDown
        self.charges = 10
        self.godMode = False
        self.name = "production artwork"
        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This machine can build almost anything, but is very slow."""
        self.usageInfo = """
Prepare for production by placing metal bars to the west/left of this machine.
Activate the machine to start producing. You will be shown a list of things to produce.
Select the thing to produce and confirm."""

    def apply(self, character):
        """
        trigger production of a player selected item

        Parameters:
            character: the character producing something
        """

        if not self.godMode:

            # gather a metal bar
            metalBar = None

            for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
                if isinstance(item, src.items.itemMap["MetalBars"]):
                    metalBar = item
                    break
            if not metalBar:
                character.addMessage("no metal bars on the left/west")
                return

            if (
                src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown
                and not self.charges
            ):
                character.addMessage(
                    "cooldown not reached. Wait {} ticks".format(
                        self.coolDown
                        - (src.gamestate.gamestate.tick - self.coolDownTimer),
                    )
                )
                return

        self.character = character

        excludeList = (
            "ProductionArtwork",
            "Machine",
            "Tree",
            "Scrap",
            "xCorpse",
            "Acid",
            "Item",
            "Pile",
            "InfoScreen",
            "CoalMine",
            "BluePrint",
            "GlobalMacroStorage",
            "Note",
            "Command",
            "Hutch",
            "Lever",
            "CommLink",
            "Display",
            "Pipe",
            "Chain",
            "AutoTutor",
            "Winch",
            "Spray",
            "ObjectDispenser",
            "Token",
            "PressCake",
            "BioMass",
            "VatMaggot",
            "Moss",
            "Mold",
            "MossSeed",
            "MoldSpore",
            "Bloom",
            "Sprout",
            "Sprout2",
            "SickBloom",
            "PoisonBloom",
            "Bush",
            "PoisonBush",
            "EncrustedBush",
            "Test",
            "EncrustedPoisonBush",
            "Chemical",
            "Spawner",
            "Explosion",
        )

        options = []
        for key, value in src.items.itemMap.items():
            if key in excludeList and not self.godMode:
                continue
            options.append((value, key))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.produceSelection
        self.targetItemType = None

    def produceSelection(self):
        """
        handle the UI for selecting an item to produce and trigger production of the selected item
        """

        if not self.targetItemType:
            self.targetItemType = self.submenue.selection
            if self.targetItemType == src.items.itemMap["Machine"]:
                options = []
                for key, value in src.items.itemMap.items():
                    options.append((key, key))
                self.submenue = src.interaction.SelectionMenu(
                    "select the item the machine should produce", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.produceSelection
                self.targetMachineItemType = None
                return
            if self.targetItemType == src.items.itemMap["ResourceTerminal"]:
                options = []
                for key, value in src.items.itemMap.items():
                    options.append((key, key))
                self.submenue = src.interaction.SelectionMenu(
                    "select resource the terminal is for", options
                )
                self.character.macroState["submenue"] = self.submenue
                self.character.macroState["submenue"].followUp = self.produceSelection
                self.targetMachineItemType = None
                return

        if self.targetItemType == src.items.itemMap["Machine"]:
            self.targetMachineItemType = self.submenue.selection
        if self.targetItemType == src.items.itemMap["ResourceTerminal"]:
            self.targetResourceType = self.submenue.selection

        if self.targetItemType:
            self.produce(self.targetItemType)

    def produce(self, itemType):
        """
        spawn the item to produce

        Parameters:
            itemType: the type of item to produce
        """

        if not self.godMode:
            # gather a metal bar
            metalBar = None

            for item in self.container.getItemByPosition((self.xPosition - 1, self.yPosition, self.zPosition)):
                if isinstance(item, src.items.itemMap["MetalBars"]):
                    metalBar = item
                    break

            # refuse production without resources
            if not metalBar:
                self.character.addMessage(
                    "no metal bars available - place a metal bar to left/west"
                )
                return

            targetFull = False
            if (self.xPosition + 1, self.yPosition) in self.container.itemByCoordinates:
                if (
                    len(
                        self.container.itemByCoordinates[
                            (self.xPosition + 1, self.yPosition)
                        ]
                    )
                    > 0
                ):
                    targetFull = True

            if targetFull:
                self.character.addMessage(
                    "the target area is full, the machine does not produce anything"
                )
                return

            if self.charges:
                self.charges -= 1
            else:
                self.coolDownTimer = src.gamestate.gamestate.tick

            self.character.addMessage(f"you produce a {itemType.type}")

            # remove resources
            self.container.removeItem(item)

        # spawn new item
        new = itemType()
        new.bolted = False

        if self.godMode:
            if itemType == src.items.itemMap["GrowthTank"]:
                new.filled = True
            if itemType == src.items.itemMap["GooFlask"]:
                new.uses = 100
            if itemType == src.items.itemMap["GooDispenser"]:
                new.charges = 100
            if itemType == src.items.itemMap["Machine"]:
                new.setToProduce(self.targetMachineItemType)
            if itemType == src.items.itemMap["ResourceTerminal"]:
                new.setResource(self.targetResourceType)
            if itemType == src.items.itemMap["GooFaucet"]:
                new.balance = 10000
            if itemType == src.items.itemMap["ResourceTerminal"]:
                new.balance = 1000

        self.container.addItem(new, (self.xPosition + 1, self.yPosition, self.zPosition))

    def getRemainingCooldown(self):
        """
        calculate the remaining cooldown

        Returns:
            the remaining cooldown in ticks
        """

        return self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer)

    def getLongInfo(self):
        """
        returns a longer than normal text description
        """

        text = super().getLongInfo()

        text += f"""
After using this machine you need to wait {self.coolDown} ticks till you can use this machine again.
"""

        coolDownLeft = self.getRemainingCooldown()
        if coolDownLeft > 0:
            text += f"""
Currently you need to wait {coolDownLeft} ticks to use this machine again.

"""
        else:
            text += """
Currently you do not have to wait to use this machine.

"""

        if self.charges:
            text += """
Currently the machine has %s charges

""" % (
                self.charges
            )
        else:
            text += """
Currently the machine has no charges

"""

        return text


src.items.addType(ProductionArtwork)

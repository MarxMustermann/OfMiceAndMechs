import src


class TeleporterManufacturer(src.items.itemMap["WorkShop"]):
    type = "TeleporterManufacturer"
    name = "Teleporter Manufacturer"
    description = "Use it to build Teleporters"
    walkable = False
    bolted = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="TM")

        self.applyOptions.extend(
            [
                ("produce teleporter", "produce teleporter"),
            ]
        )
        self.applyMap = {"produce teleporter": self.produceTeleporter}

    def produceTeleporter(self, character):
        params = {"character": character}

        if not self.wantItemTypeWithAmount(character, {"Implant": 2, "Rod": 10}):
            character.addMessage("can't create teleporter because of missing components")
            return

        params["productionTime"] = 100
        params["doneProductionTime"] = 0
        params["hitCounter"] = character.numAttackedWithoutResponse
        self.produceItem_wait(params)

    def produceItem_done(self, params):
        character = params["character"]

        character.addMessage("You produce a teleporter")
        character.addMessage("It took you {} turns to do that".format(params["doneProductionTime"]))

        character.inventory.append(src.items.itemMap["DimensionTeleporter"]())

    def apply(self, character):  # TODO delete function to enable it
        character.addMessage("the machine is disabled")


src.items.addType(TeleporterManufacturer, nonManufactured=True)

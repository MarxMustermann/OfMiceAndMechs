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

        params["delayTime"] = 100
        params["action"]= "output_produced_item"
        self.delayedAction(params)

    def output_produced_item(self,params):
        character = params["character"]

        character.addMessage("You produce a teleporter")
        character.addMessage("It took you {} turns to do that".format(params["doneTime"]))

        character.stats["items produced"]["DimensionTeleporter"] = (
            self.stats["items produced"].get("DimensionTeleporter", 0) + 1
        )

        character.addToInventory(src.items.itemMap["DimensionTeleporter"]())


src.items.addType(TeleporterManufacturer, nonManufactured=True)

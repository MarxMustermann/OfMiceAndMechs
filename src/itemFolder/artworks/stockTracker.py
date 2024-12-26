import src


class StockTracker(src.items.Item):
    """
    """


    type = "StockTracker"

    def __init__(self, name="StockTracker", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="ST", name=name)

        self.applyOptions.extend(
                        [
                                                                ("viewInventory", "view inventory"),
                        ]
                        )
        self.applyMap = {
                    "viewInventory": self.viewInventory,
                        }

        self.faction = ""

    def viewInventory(self,character):
        text = "STOCK:\n\n"

        itemsFound = {}
        for room in self.getTerrain().rooms:
            for storageSlot in room.storageSlots:
                for item in room.getItemByPosition(storageSlot[0]):
                    itemsFound[item.type] = itemsFound.get(item.type,0)+1

        character.addMessage(itemsFound)

        for (itemType,num) in itemsFound.items():
            text += f"{itemType}: {num}\n"

        submenue = src.menuFolder.textMenu.TextMenu(text)
        character.macroState["submenue"] = submenue


src.items.addType(StockTracker)

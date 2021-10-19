import src


class SpecialItem(src.items.Item):
    """
    ingame item transforming into a rip in reality when using a key
    """

    type = "SpecialItem"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "special item slot"

        self.walkable = True
        self.bolted = False
        self.itemID = None

    def apply(self, character):
        """
        handle a chracter trying to unlock the item

        Parameters:
            character: the character trying to unlock the item
        """

        staticSpark = None
        for item in character.inventory:
            if isinstance(item, StaticSpark) and item.strength >= self.strength - 1:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        newItem = src.items.itemMap["RipInReality"]()
        newItem.depth = self.strength
        self.container.addItem(newItem,self.getPosition())
        self.container.removeItem(self)


src.items.addType(SpecialItem)

import src


class SparkPlug(src.items.Item):
    """
    ingame item transforming into a rip in reality when using a key
    """

    type = "SparkPlug"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "spark plug"

        self.walkable = True
        self.bolted = True
        self.strength = 1

    def apply(self, character):
        """
        handle a chracter trying to unlock the item

        Parameters:
            character: the character trying to unlock the item
        """

        staticSpark = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["StaticSpark"]) and item.strength >= self.strength - 1:
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


src.items.addType(SparkPlug)

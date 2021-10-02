import src


class SpiderNet(src.items.Item):
    """
    """

    type = "SpiderNet"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "spider net"

        self.walkable = True
        self.bolted = True
        self.hasStepOnAction = True

    def stepedOn(self, character):
        character.addMessage("you step into a spiders net")
        character.hurt(10,"acid burns")

src.items.addType(SpiderNet)

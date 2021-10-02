import src


class AcidBladder(src.items.Item):
    """
    """

    type = "AcidBladder"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display="öö")
        self.name = "spider net"

        self.walkable = True
        self.bolted = True
        self.hasStepOnAction = True

    def stepedOn(self, character):
        character.addMessage("you step onto the acid bladder")
        character.hurt(50,"acid burns")

src.items.addType(AcidBladder)

import src

"""
"""


class BluePrint(src.items.Item):
    type = "BluePrint"

    """
    call superclass constructor with modified parameters
    """

    def __init__(
        self, xPosition=None, yPosition=None, name="BluePrint", creator=None, noId=False
    ):
        super().__init__(
            src.canvas.displayChars.blueprint,
            xPosition,
            yPosition,
            name=name,
            creator=creator,
        )

        self.endProduct = None
        self.walkable = True
        self.baseName = name
        self.level = 1

        self.attributesToStore.extend(["endProduct", "level"])

        self.setDescription()

    def setDescription(self):
        if not self.endProduct:
            self.description = self.baseName
        else:
            self.description = self.baseName + " for %s" % (self.endProduct,)

    def setToProduce(self, toProduce):
        self.endProduct = toProduce

        self.setDescription()

    def apply(self, character):
        super().apply(character, silent=True)

        character.addMessage("a blueprint for " + str(self.endProduct))

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
item: Blueprint

decription:
This Blueprint holds the information on how to produce an item in machine readable form.

It needs to be loaded into a machine machine.
After loading the blueprint the machine machine is able to produce a machine that produces the the item the blue

this blueprint is for %s

This is a level %s item

""" % (
            self.endProduct,
            self.level,
        )
        return text

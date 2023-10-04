import src


class BluePrint(src.items.Item):
    """
    ingame item representing research done
    a sheet blueprint allows to build a machine that produces sheets
    """

    type = "BluePrint"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(
            display=src.canvas.displayChars.blueprint,
        )

        self.name = "blue print"
        self.description = "This Blueprint holds the information on how to produce an item in machine readable form"
        self.usageInfo = """
It needs to be loaded into a machine machine.
After loading the blueprint the machine machine is able to produce a machine that produces the the item the blue
"""

        self.endProduct = None
        self.walkable = True
        self.baseName = self.name
        self.level = 1

        self.setDescription()

    def setDescription(self):
        """
        change this items description
        """

        if not self.endProduct:
            self.description = self.baseName
        else:
            self.description = self.baseName + f" for {self.endProduct}"

    def setToProduce(self, toProduce):
        """
        set the type of item the blueprint is for

        Parameters:
            toProduce: the type of item the blueprint is for
        """

        self.endProduct = toProduce

        self.setDescription()

    def apply(self, character):
        """
        show the items description to a character

        Parameters:
            character: the character trying to use the item
        """

        character.addMessage("a blueprint for " + str(self.endProduct))

    def getLongInfo(self):
        """
        Returns a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

this blueprint is for {self.endProduct}

This is a level {self.level} item

"""
        return text

src.items.addType(BluePrint)

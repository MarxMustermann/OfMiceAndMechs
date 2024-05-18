import src

class Flask(src.items.Item):
    type = "Flask"

    def __init__(self,uses=0):
        """
        configure super class
        """

        self.uses = uses
        super().__init__(display=src.canvas.displayChars.gooflask_empty)

        self.name = "flask"
        self.walkable = True
        self.bolted = False
        self.description = "A flask that can hold liquids"

    def render(self):
        """
        render based on fill amount

        Returns:
            what the item should look like
        """

        return "o "

    def getDetailedInfo(self):
        """
        get info including the charges on the flask
        """

        return super().getDetailedInfo() + " (" + str(self.uses) + " charges)"

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        return text

src.items.addType(Flask)

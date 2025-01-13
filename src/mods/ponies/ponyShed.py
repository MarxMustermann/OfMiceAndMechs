import src

class PonyShed(src.items.Item):
    """
    an item to stop statues
    """

    type = "PonyShed"

    def __init__(self):
        """
        configure the super class
        """

        super().__init__(display="PS")
        self.name = "pony shed"

        self.walkable = False
        self.bolted = True

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""
This spawns the terrible ponies
"""
        return text

    def apply(self, character):
        character.addMessage("just kidding, lol")

        offsets = [(1,0,0),(0,1,0),(-1,0,0),(0,-1,0)]
        for offset in offsets:
            newCharacter = src.characters.characterMap["Pony"]()
            newCharacterPosition = self.getPosition(offset=offset)
            self.container.addCharacter(newCharacter,newCharacterPosition[0],newCharacterPosition[1])

src.items.addType(PonyShed)

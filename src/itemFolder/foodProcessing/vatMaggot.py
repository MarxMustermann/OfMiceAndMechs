import src

'''
'''
class VatMaggot(src.items.Item):
    type = "VatMaggot"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self):
        super().__init__(display=src.canvas.displayChars.vatMaggot)
        self.name = "vat maggot"

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character,resultType=None):

        # remove resources
        character.addMessage("you consume the vat maggot")
        character.satiation += 1
        character.frustration -= 25
        if self.xPosition and self.yPosition:
            if self.room:
                self.room.removeItem(self)
            elif self.terrain:
                self.terrain.removeItem(self)
        else:
            if self in character.inventory:
                character.inventory.remove(self)
        if (src.gamestate.gamestate.tick%5 == 0):
            character.addMessage("you wretch")
            character.satiation -= 25
            character.frustration += 75
            character.addMessage("you wretch from eating a vat magot")

        super().apply(character,silent=True)

    def getLongInfo(self):
        text = """
A vat maggot is the basis for food.

You can eat it, but it may kill you. Activate it to eat it.

Can be processed into bio mass by a maggot fermenter.

"""
        return text

src.items.addType(VatMaggot)


import src

class BioMass(src.items.Item):
    '''
    simple processed food item nothing special
    '''
    type = "BioMass"

    def __init__(self):
        '''
        simple superclass configuration
        '''
        super().__init__()
                
        self.display = src.canvas.displayChars.bioMass
        self.name = "bio mass"
        self.description = """
A bio mass is basis for food production.

Can be processed into press cake by a bio press."""

        self.bolted = False
        self.walkable = True

        self.isFood = True
        self.nutrition = 200

src.items.addType(BioMass)

import src

'''
'''
class BioMass(src.items.Item):
    type = "BioMass"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="bio mass",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.bioMass,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        # change state
        character.satiation += 200
        if character.satiation > 1000:
            character.satiation = 1000
        character.changed()
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the bio mass")

    def getLongInfo(self):
        text = """
item: BioMass

description:
A bio mass is basis for food production.

Can be processed into press cake by a bio press.
"""
        return text

src.items.addType(BioMass)

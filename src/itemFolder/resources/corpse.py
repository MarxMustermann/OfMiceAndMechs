import src

'''
'''
class Corpse(src.items.Item):
    type = "Corpse"

    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,name="corpse",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.corpse,xPosition,yPosition,name=name,creator=creator)
        self.charges = 1000
        self.attributesToStore.extend([
               "activated","charges"])
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        text = """
item: Corpse

description:
A corpse. Activate it to eat from it. Eating from a Corpse will gain you 15 Satiation.

can be processed in a corpse shredder

The corpse has %s charges left.

"""%(self.charges)
        return text

    def apply(self,character):
        if isinstance(character,src.characters.Monster):
            if character.phase == 3:
                character.enterPhase4()
            else:
                if self.container and character.satiation < 950:
                    character.macroState["commandKeyQueue"] = [("j",[]),("m",[])] + character.macroState["commandKeyQueue"]
            character.frustration -= 1
        else:
            character.frustration += 1

        if self.charges:
            character.satiation += 15
            if character.satiation > 1000:
                character.satiation = 1000
            self.charges -= 1
            character.addMessage("you eat from the corpse and gain 15 satiation")
        else:
            self.destroy(generateSrcap=False)

src.items.addType(Corpse)

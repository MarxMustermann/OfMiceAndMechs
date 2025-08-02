import src
import random

class FactionSetter(src.items.Item):
    '''
    ingame item to set the factions of NPCs
    '''
    type = "FactionSetter"
    def __init__(self,epoch=0):
        super().__init__(display="FS")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        '''
        set the faction of a character
        '''
        character.faction = self.faction
        character.addMessage(f"your faction was changed to {self.faction}")
        character.changed("set faction")

        self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"OO"})
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"OO"})

        text = f"""
You insert your head into the machine.
It claws into your head and connects to your implant.

It changes your implant and sets your faction marker to {self.faction}.
"""
        character.macroState["submenue"] = src.menuFolder.textMenu.TextMenu(text)

    def getConfigurationOptions(self, character):
        '''
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        '''

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        options["f"] = ("set faction",self.setFaction)
        return options

    def boltAction(self,character):
        '''
        bolt the item down
        '''
        self.bolted = True
        character.addMessage("you bolt down the FactionSetter")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        '''
        unbolt the item
        '''
        self.bolted = False
        character.addMessage("you unbolt the FactionSetter")
        character.changed("unboltedItem",{"character":character,"item":self})

    def setFaction(self,character):
        '''
        set the faction of the faction setter
        '''
        character.addMessage("you insert your head into the machine and it sets itself to your faction")
        self.faction = character.faction

# register the item
src.items.addType(FactionSetter)

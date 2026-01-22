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
        # change faction
        character.faction = self.faction
        character.addMessage(f"your faction was changed to {self.faction}")
        character.changed("set faction",{"character":character})

        # show user feedback
        self.container.addAnimation(character.getPosition(),"showchar",1,{"char":"OO"})
        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"OO"})
        text = f"""
You insert your head into the machine.
It claws into your head and connects to your implant.

It changes your implant and sets your faction marker to {self.faction}.
"""
        submenue = src.menuFolder.textMenu.TextMenu(text)
        character.macroState["submenue"] = submenue

        # reset rank
        character.rank = 6
        character.hasSpecialAttacks = False
        character.hasSwapAttack = False
        character.hasRun = False
        character.hasJump = False
        character.hasLineShot = False
        character.hasRandomShot = False
        character.hasMaxHealthBoost = False
        character.hasMovementSpeedBoost = False

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

    def setFaction(self,character):
        '''
        set the faction of the faction setter
        '''
        character.addMessage("you insert your head into the machine and it sets itself to your faction")
        self.faction = character.faction

# register the item
src.items.addType(FactionSetter)

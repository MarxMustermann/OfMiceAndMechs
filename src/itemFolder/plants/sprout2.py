import src

import random

class Sprout2(src.items.Item):
    """
    intermediate plant evolution
    """

    type = "Sprout2"
    name = "sprout2"
    description = "This is a mold patch that developed a bloom sprout."
    usageInfo = """
you can eat it to gain 25 satiation.
"""
    walkable = True

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.sprout2)

    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        if not self.container:
            character.addMessage("this needs to be placed to be used")
            return

        character.satiation += 25
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateScrap=False)
        character.addMessage("you eat the sprout and gain 25 satiation")

    def destroy(self, generateScrap=True):
        """
        destroy this item

        Parameters:
            generateScrap: flag to leave no residue
        """

        # damage nearby characters
        if self.container.isRoom == False:
            # show animations
            color_pool = ["#252","#030","#474","#240","#383"]
            character_pool = ["`",",",".","+","*","~","'",":",";","-"]
            for offset in [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
                chars = []
                for i in range(0,int(random.random()*3)+2):
                    chars.append((src.interaction.urwid.AttrSpec(random.choice(color_pool),"black"),random.choice(character_pool)+random.choice(character_pool)))
                self.container.addAnimation(self.getPosition(offset=offset),"charsequence",2,{"chars":chars})

            # do the actual damage
            for character in self.container.getCharactersOnTile(self.getBigPosition()):
                if character.getDistance(self.getPosition()) <= 1:
                    character.hurt(20,"inhale spores")

        # add new and active mold
        new = src.items.itemMap["Mold"]()
        self.container.addItem(new, self.getPosition())
        new.startSpawn()

        super().destroy(generateScrap=False)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        options["b"] = ("destroy", self.destroy)
        return options

src.items.addType(Sprout2)

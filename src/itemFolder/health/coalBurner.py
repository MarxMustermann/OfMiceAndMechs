import math

import src


class CoalBurner(src.items.Item):
    """
    ingame item to provide characters with an oportunity to heal
    """

    type = "CoalBurner"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display="##")

        self.name = "coal burner"
        self.description = "the smoke heals you"

        self.walkable = False
        self.bolted = False

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""
This item can heal you.
Collect MoldFeed and burn it to heal.

To heal use this item place with MoldFeed next to the item
or use this item with MoldFeed in your inventory.

"""
        return text

    def getMoldFeed(self,character):
        if not self.container:
            return []

        moldFeed = []

        for offset in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
            items = self.container.getItemByPosition(self.getPosition(offset))
            for item in items:
                if item.type == "MoldFeed":
                    moldFeed.append(item)

        if not moldFeed:
            for item in character.inventory:
                if item.type == "MoldFeed":
                    moldFeed.append(item)

        return moldFeed

    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        moldFeed = self.getMoldFeed(character)
        if len(moldFeed) == 0:
            character.addMessage("you need to have a MoldFeed in your inventory or in the coal burners input stockpile")
            return

        amount_to_burn = min(len(moldFeed), math.ceil((character.maxHealth - character.health) / 5))
        
        if not amount_to_burn:
            character.addMessage("you need no healing and burn no corpses")
            return

        for i in range(amount_to_burn):
            current_moldFeed = moldFeed[i]
            if current_moldFeed in character.inventory:
                character.inventory.remove(current_moldFeed)
            else:
                self.container.removeItem(current_moldFeed)

        character.addMessage("you burn the corpses and inhale the smoke")
        character.heal(5 * amount_to_burn,reason="inhaling the smoke of " + str(amount_to_burn) + " corpse")
        character.takeTime(30,"burnig a corpse")

        character.container.addAnimation(character.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "#fff"), "++")]})
        for _i in range(1,10):
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            self.container.addAnimation(self.getPosition(),"smoke",8,{})

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the CoalBurner")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the CoalBurner")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(CoalBurner)

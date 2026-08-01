import math
import numpy as np

import src

coal_burner_texture = {}

class CoalBurner(src.items.Item):
    '''
    ingame item to provide characters with an oportunity to heal
    '''

    type = "CoalBurner"
    description = "Emits healing smoke"
    def __init__(self):
        super().__init__(display="##")

        self.name = "coal burner"

        self.walkable = False
        self.bolted = False

    def getLongInfo(self, character=None):
        '''
        return a longer than normal description text

        Returns:
            the description text
        '''

        text = super().getLongInfo(character)
        text += f"""
This item can heal you.
Collect MoldFeed and burn it to heal.

To heal use this item place with MoldFeed next to the item
or use this item with MoldFeed in your inventory.

"""
        return text

    def readyToUse(self, character=None):
        if not self.bolted:
            return False
        if self.getMoldFeed(character):
            return True
        return False

    def getMoldFeed(self, character=None):
        '''
        get input ressources
        '''
        if not self.container:
            return []
        if not self.bolted:
            return []

        moldFeed = []

        for offset in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
            items = self.container.getItemByPosition(self.getPosition(offset))
            for item in items:
                if item.type == "MoldFeed":
                    moldFeed.append(item)

        if not moldFeed and character:
            for item in character.inventory:
                if item.type == "MoldFeed":
                    moldFeed.append(item)

        return moldFeed

    def apply(self, character):
        '''
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        '''

        # ensure the item is bolted down
        if not self.bolted:
            character.notify("This items needs to be bolted down to be used.")
            return

        # ensure there is mold feed to burn
        moldFeed = self.getMoldFeed(character)
        if len(moldFeed) == 0:
            character.notify("you need to have a MoldFeed in your inventory or in the coal burners input stockpile")
            return

        # eastimate how much mold feed to burn
        amount_to_burn = min(len(moldFeed), math.ceil((character.adjustedMaxHealth - character.health) / 5))
        if not amount_to_burn:
            character.notify("you need no healing and burn no MoldFeeds")
            return

        # remove the mold feed to burn from the world
        for i in range(amount_to_burn):
            current_moldFeed = moldFeed[i]
            if current_moldFeed in character.inventory:
                character.removeItemFromInventory(current_moldFeed)
            else:
                self.container.removeItem(current_moldFeed)

        # show burning animation
        character.container.addAnimation(character.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "#fff"), "++")]})
        for _i in range(1,10):
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            self.container.addAnimation(self.getPosition(),"smoke",8,{})

        # call the remaining logic as delayed
        params = {"character":character,"amount_to_burn":amount_to_burn,"delayTime":30,"action":"doHealing"}
        params["description"] = "You burn some MoldFeed\n"
        self.delayedAction(params)

    def doHealing(self,params):

        # heal the character using this item
        amount_to_burn = params["amount_to_burn"]
        character = params["character"]
        heal_amount = 5 * amount_to_burn
        character.heal(heal_amount,reason="inhaling the smoke of " + str(amount_to_burn) + " MoldFeeds")

        # show a success message to the player
        character.showTextMenu([f"""
You burn {amount_to_burn} MoldFeeds and """,(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"inhale the smoke"),f""".

This will heal you for up to {heal_amount} HP.
"""])
        character.runCommandString(".",nativeKey=False)

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
        return options

# register the item type
src.items.addType(CoalBurner)

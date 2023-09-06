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
        self.charges = 0

    # abstraction: super class functionality should be used
    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        moldFeed = None
        for item in character.inventory:
            if not item.type == "MoldFeed":
                continue
            moldFeed = item
            break

        if not moldFeed:
            character.addMessage("you need to have a MoldFeed in your inventory")
            return

        character.inventory.remove(item)
        character.addMessage("you burn the corpse and inhale the smoke")
        character.heal(30,reason="inhaling the smoke")
        character.timeTaken += 30

        character.container.addAnimation(character.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "#fff"), "++")]})
        for i in range(1,10):
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            self.container.addAnimation(self.getPosition(),"smoke",8,{})

src.items.addType(CoalBurner)

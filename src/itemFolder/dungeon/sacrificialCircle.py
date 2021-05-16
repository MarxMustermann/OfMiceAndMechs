import src


class SaccrificialCircle(src.items.Item):
    """
    ingame item allowing the player to saccrifice corpses for rewards
    """

    type = "SaccrificialCircle"

    def __init__(self):
        """
        configure superclass
        """

        super().__init__(display="&°")

        self.name = "SaccrificialCircle"

        self.walkable = True
        self.bolted = True
        self.level = 1
        self.uses = 2

    def apply(self, character):
        """
        handle a character sacrifying something

        Parameters:
            character: the character trying to saccrisfy something
        """

        foundItem = None
        for item in character.inventory:
            if item.type == "Corpse":
                foundItem = item
                break

        if not foundItem:
            character.addMessage("no corpse in inventory")
            return

        character.inventory.remove(foundItem)
        spark = src.items.itemMap["StaticSpark"]()
        spark.level = self.level
        character.inventory.append(spark)
        character.addMessage("corpse sacrificed for spark")
        self.uses -= 1

    def render(self):
        """
        render depending on how much was saccrifysed already

        Returns:
            how the item should look like
        """

        if self.uses == 2:
            return (src.interaction.urwid.AttrSpec("#aaf", "black"), "&°")
        elif self.uses == 1:
            return [
                (src.interaction.urwid.AttrSpec("#aaf", "black"), "&"),
                (src.interaction.urwid.AttrSpec("#f00", "black"), "°"),
            ]
        else:
            return (src.interaction.urwid.AttrSpec("#f00", "black"), "&°")


src.items.addType(SaccrificialCircle)

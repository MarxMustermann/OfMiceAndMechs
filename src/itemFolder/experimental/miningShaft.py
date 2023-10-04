import src


# NIY: very incomplete
class MiningShaft(src.items.Item):
    """
    ingame item to change z-levels
    """

    type = "MiningShaft"

    # bad code: hack
    def apply(self, character):
        """
        handle a character trying to go up

        Parameters:
            character: the character using the item
        """

        character.zPosition -= 1

    # bad code: hack
    def configure(self, character):
        """
        handle a character trying to go down

        Parameters:
            character: the character using the item
        """

        character.zPosition += 1


src.items.addType(MiningShaft)

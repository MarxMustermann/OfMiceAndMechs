import src


# NIY: mostly nonfunctional
class SparcRewardLock(src.items.Item):
    """
    ingame item dispensing the main reward of the dungeon
    """

    type = "SparcRewardLock"

    def __init__(self):
        """
        configure superclass
        """

        super().__init__(display="%°")

        self.name = "SaccrificialCircle"
        self.walkable = True
        self.bolted = True

    def apply(self, character):
        """
        handle a chracter trying to claim the reward

        Parameters:
            character: the character trying to claim the reward
        """

        foundItem = None
        for item in character.inventory:
            if item.type == "StaticCrystal":
                foundItem = item
                break

        if not foundItem:
            character.addMessage(
                "no static crystal in inventory - insert to claim reward"
            )
            return

        character.inventory.append(foundItem)
        character.addMessage("well done")


src.items.addType(SparcRewardLock)

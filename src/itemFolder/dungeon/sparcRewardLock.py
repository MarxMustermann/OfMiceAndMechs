import src


# NIY: mostly nonfunctional
class SparcRewardLock(src.items.Item):
    """
    ingame item dispensing the main reward of the dungeon
    """

    type = "SparcRewardLock"

    def __init__(self,treasure=None):
        """
        configure superclass
        """

        super().__init__(display="%°")

        self.name = "SparcRewardLock"
        self.walkable = True
        self.bolted = True
        self.treasure = treasure

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

        character.inventory.remove(foundItem)
        if not self.treasure:
            character.addMessage("there is no reward")
        else:
            character.addMessage("the locks opens and you recieve your reward")
            character.inventory.extend(self.treasure)
            self.treasure = None


src.items.addType(SparcRewardLock)

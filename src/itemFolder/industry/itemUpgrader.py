import random

import src


class ItemUpgrader(src.items.Item):
    """
    ingame item that can be used to upgrade other items
    """

    type = "ItemUpgrader"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__()
        self.display = src.canvas.displayChars.itemUpgrader
        self.name = "item upgrader"
        self.description = "Can be used to upgrade items"
        self.usageInfo = """
An upgrader works from time to time. A failed upgrade will destroy the item but increase the chances of success
Place item to upgrade to the west and the upgraded item will be placed to the east.
If the upgrade fails the remains of the item will be placed to the south.
"""
        self.charges = 3
        self.level = 1

    def apply(self, character):
        """
        handle a character trying to us this machine to upgrade another machine

        Parameters:
            character: the character trying to use the machine
        """

        if self.xPosition is None:
            character.addMessage("this machine has to be placed to be used")
            return

        inputItem = None

        itemsFound = self.container.getItemByPosition((self.xPosition - 1, self.yPosition,0))
        if itemsFound:
            inputItem = itemsFound[0]

        if not inputItem:
            character.addMessage("place item to upgrade on the left")
            return

        if not hasattr(inputItem, "level"):
            character.addMessage("cannot upgrade %s" % (inputItem.type))
            return

        if inputItem.level > self.level:
            character.addMessage(
                "item upgrader needs to be upgraded to upgrade this item further"
            )
            return

        if inputItem.level == 1:
            chance = -1
        elif inputItem.level == 2:
            chance = 0
        elif inputItem.level == 3:
            chance = 1
        elif inputItem.level == 4:
            chance = 2
        else:
            chance = 100

        success = False
        if random.randint(1,1000) % (self.charges + 2) > chance:
            success = True

        targetFull = False
        itemList = self.container.getItemByPosition((self.xPosition + 1, self.yPosition,0))
        if itemList:
            if inputItem.walkable:
                if (len(itemList) > 15):
                    targetFull = True
                for item in itemList:
                    if item.walkable == False:
                        targetFull = True
            else:
                if ( len(itemList) > 1 ):
                    targetFull = True

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        self.container.removeItem(inputItem)

        if success:
            inputItem.upgrade()
            character.addMessage(f"{inputItem.type} upgraded")
            self.charges = 0
            self.container.addItem(inputItem,(self.xPosition + 1,self.yPosition,self.zPosition))
        else:
            self.charges += 1
            character.addMessage(
                f"failed to upgrade {inputItem.type} - has {self.charges} charges now"
            )
            self.container.addItem(inputItem,(self.xPosition,self.yPosition+1,self.zPosition))
            inputItem.destroy()

    def getLongInfo(self):
        """
        return a longer than normal descritio text

        Returns:
            the desription text
        """

        text = super().getLongInfo()

        text += """
it has %s charges.
""" % (
            self.charges
        )
        return text


src.items.addType(ItemUpgrader)

import src

class Merger(src.items.Item):
    """
    ingame item to move other items a short distance
    inteded to help with coding edgecases
    """

    type = "Merger"

    def __init__(self):
        """
        call superclass constructor with modified parameters
        """

        super().__init__(display=src.canvas.displayChars.sorter)
        self.name = "merger"
        self.description = "A merger merges items from 2 spots"
        self.usageInfo = """
Place items to the north and west of the Merger.
Activate the mover to move one item from the north and one item to the south to the east of the mover.
"""

    def apply(self, character):
        """
        handle a character trying to us this item to move items
        by trying to move the items

        Parameters:
            character: the character trying to use this item
        """

        if self.xPosition is None:
            character.addMessage("this machine needs to be placed to be used")
            return

        # fetch input
        items1 = self.container.getItemByPosition( (self.xPosition, self.yPosition - 1, 0) )
        items2 = self.container.getItemByPosition( (self.xPosition, self.yPosition + 1, 0) )

        if not items1:
            character.addMessage("no item north")
            return
        if not items2:
            character.addMessage("no item south")
            return

        out_pos = (self.xPosition+1, self.yPosition, 0)
        items3 = self.container.getItemByPosition( out_pos )
        if len(items3) > 20:
            character.addMessage("output blocked")
            return
        for item in items3:
            if item.walkable:
                continue
            character.addMessage("output blocked")
            return

        # remove input
        item1 = items1.pop()
        item2 = items2.pop()
        
        # add output
        self.container.addItem(item1,out_pos)
        self.container.addItem(item2,out_pos)

src.items.addType(Merger)

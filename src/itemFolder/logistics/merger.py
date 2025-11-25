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

        super().__init__(display="M\\")
        self.name = "merger"
        self.description = "A merger merges items from 2 spots"
        self.usageInfo = """
Place items to the north and west of the Merger.
Activate the mover to move one item from the north and one item to the south to the east of the mover.
"""

    def _get_input_items1(self,character=None):
        if not self.xPosition:
            return []

        items1 = self.container.getItemByPosition( (self.xPosition, self.yPosition - 1, 0) )
        return items1

    def _get_input_items2(self):
        if not self.xPosition:
            return []

        items2 = self.container.getItemByPosition( (self.xPosition, self.yPosition + 1, 0) )
        return items2

    def _get_output_position(self):
        out_pos = (self.xPosition+1, self.yPosition, 0)
        return out_pos

    def _has_output_space(self):
        out_pos = self._get_output_position()
        items3 = self.container.getItemByPosition( out_pos )
        if len(items3) > 20:
            return False

        for item in items3:
            if item.walkable:
                continue
            return False

        items1 = self._get_input_items1()
        if items1 and not items1[0].walkable:
            if items3:
                return False
        items2 = self._get_input_items2()
        if items2 and not items2[0].walkable:
            if items3:
                return False

        return True

    def readyToUse(self):
        if not self._get_input_items1():
            return False

        if not self._get_input_items2():
            return False

        if not self._has_output_space():
            return False

        return True

    def render(self):
        '''
        get how the item should be rendered
        '''
        if self.readyToUse():
            return "M\\"
        else:
            return (src.interaction.urwid.AttrSpec("#888", "black"), "M\\")

    def apply(self, character):
        """
        handle a character trying to us this item to move items
        by trying to move the items

        Parameters:
            character: the character trying to use this item
        """

        character.changed("operated machine",{"character":character,"machine":self})

        if self.xPosition is None:
            character.addMessage("this machine needs to be placed to be used")
            return

        # fetch input
        items1 = self._get_input_items1()
        items2 = self._get_input_items2()

        if not items1:
            character.addMessage("no item north")
            return
        if not items2:
            character.addMessage("no item south")
            return

        if not self._has_output_space():
            character.addMessage("output blocked")
            return

        # remove input
        item1 = items1[0]
        item2 = items2[0]
        self.container.removeItem(item1)
        self.container.removeItem(item2)
        
        # add output
        out_pos = self._get_output_position()
        self.container.addItem(item1,out_pos)
        self.container.addItem(item2,out_pos)

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
        character.addMessage("you bolt down the Merger")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Merger")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Merger)

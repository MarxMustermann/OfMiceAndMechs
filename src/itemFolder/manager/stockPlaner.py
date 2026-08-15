import src

class StockPlaner(src.items.Item):
    '''
    ingame item to control what should be stored

    Parameters:
        name: the name of the item to be shown in the UI
    '''
    type = "StockPlaner"
    description = "Managment item for managing a bases storage system"
    def __init__(self, name="stock planer"):
        super().__init__(display="SP", name=name)

        self.applyOptions.extend(
                        [
                                                    ("show inventory", "show item inventory"),
                                                    ("set limits", "set stockpiling limits"),
                        ]
                        )
        self.applyMap = {
                    "show inventory": self.showInventory,
                    "set limits": self.setLimits,
                        }

        self.stock_limits = {}

    def setLimits(self,character):
        '''
        show the menu to set stock limits
        '''
        description = ["""
The storage limits ensure the storage space is not taken up by a single item type.
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You can set the storage limits for each item type in this menu."),"""

If you have more items in storage than your storage limit,
Clones with the "storage management" duty will remove excess items.


"""]
        title = "SET STOCKPILE LIMITS"
        choices = list(src.items.itemMap.keys())
        menu = src.menues.menuMap["NameNumberPairSetter"](character,self.stock_limits, description=description, title=title,choices=choices)
        character.add_submenu(menu)

    def getStockLimitViolations(self):
        '''
        get a list of the violations against the stockpile limit
        '''
        terrain = self.getTerrain()
        violations = []
        item_inventory = terrain.getInventory(count_only=True)
        for (item_type,limit) in self.stock_limits.items():
            stocked_amount = item_inventory.get(item_type,0)
            if stocked_amount > limit:
                violations.append((item_type,stocked_amount-limit))
        return violations

    def showInventory(self,character):
        '''
        show the bases inventory to the player
        '''

        # set up helper variable
        terrain = self.getTerrain()

        # handle edge cases
        if not terrain:
            character.notify("this item needs to be placed to be used")
            return

        # show the actual text
        text = []
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),f"items in storage:\n\n"))
        item_inventory = list(terrain.getInventory(count_only=True).items())
        item_inventory.sort(key=lambda x: x[1],reverse=True)
        for (item_type,amount) in item_inventory:
            limit = self.stock_limits.get(item_type,"-")
            spacer = " "*(20-len(item_type))
            color = "white"
            if isinstance(limit,int) and  amount > limit:
                color = src.interaction.warning_ui_color
            text.extend([f"{item_type}:{spacer} ",(src.pseudoUrwid.AttrSpec(color,"black"),f"{amount}/{limit}\n")])
        character.showTextMenu(text)

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

# register the item
src.items.addType(StockPlaner)

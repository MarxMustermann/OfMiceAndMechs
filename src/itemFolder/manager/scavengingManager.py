import src


class ScavengingManager(src.items.Item):
    '''
    ingame item to control what is to be scavenged

    Parameters:
        name: the name of the item to be shown in the UI
    '''
    type = "ScavengingManager"
    description = "Managment item for setting scavenging behaviour"
    def __init__(self, name="ScavengingManager"):
        super().__init__(display="CM", name=name)

        self.applyOptions.extend(
                        [
                                            ("show scavenging settings", "show scavenging settings"),
                                            ("set scavenging target", "set scavenging target"),
                                            ("set scavenging limits", "set scavenging limits"),
                        ]
                        )
        self.applyMap = {
                    "set scavenging target": self.setScavengingTarget,
                    "set scavenging limits": self.setScavengingLimits,
                    "show scavenging settings": self.showScavengingSettings,
                        }

        self.scavenging_min_target = {"Wall":10,"Door":4,"Scrap":15,"Metalbars":20,"Bolts":20}
        self.scavenging_max = {"Scrap":30,"MetalBars":50}

    def showScavengingSettings(self,character):
        '''
        show the current configuration to the player
        '''

        # set up helper variable
        terrain = self.getTerrain()

        # handle edge cases
        if not terrain:
            character.notify("this item needs to be placed to be used")
            return

        # show the scavenging target
        inventory = terrain.getInventory(count_only=True)
        text = []
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"== current scavenging targets ==\n"))
        for (item_type,amount) in self.scavenging_min_target.items():
            amount_in_stock = inventory.get(item_type,0)
            text.append(f"{item_type}: {amount_in_stock}/{amount}\n")
        text.append("\n")
        text.append((src.pseudoUrwid.AttrSpec(src.interaction.shadowed_ui_color,"black"),"== scavenging limit ==\n"))
        for (item_type,amount) in self.scavenging_max.items():
            amount_in_stock = inventory.get(item_type,0)
            text.append(f"{item_type}: {amount_in_stock}/{amount}\n")

        character.showTextMenu(text)

    def getScavengingLimits(self):
        '''
        simple getter for checking the scavenging target
        '''
        return self.scavenging_max

    def getAvoidItemtypes(self):
        '''
        get item types to scavenge
        '''
        terrain = self.getTerrain()
        avoid_itemtypes = []
        item_inventory = terrain.getInventory(count_only=True)
        for (item_type,limit) in self.getScavengingLimits().items():
            stocked_amount = item_inventory.get(item_type,0)
            if stocked_amount > limit:
                avoid_itemtypes.append(item_type)
        return avoid_itemtypes

    def getScavengingTarget(self):
        '''
        simple getter for checking the scavenging target
        '''
        return self.scavenging_min_target

    def getItemtypesToScavenge(self):
        '''
        get item types to scavenge
        '''
        terrain = self.getTerrain()
        toScavenge = []
        item_inventory = terrain.getInventory(count_only=True)
        for (item_type,target) in self.getScavengingTarget().items():
            stocked_amount = item_inventory.get(item_type,0)
            if stocked_amount < target:
                toScavenge.append((item_type,target-stocked_amount))
        return toScavenge

    def setScavengingTarget(self,character):
        '''
        show the menu to set stock limits

        Parameters:
            character: the character triggering the action
        '''
        description = ["""
Clones with the "scavenging" duty bring all kinds of items into the base.
But they might not bring what the actually needs.
The scavenging targets ensure that the Clones will focus on the important items.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Set scavenging targets"),""" to Control what item the Clones collect.
They will collect the item needed to satisfy the scavenging targets first.

"""]
        title = "SET SCAVENGING TARGETS"
        choices = list(src.items.itemMap.keys())
        menu = src.menues.menuMap["NameNumberPairSetter"](character,self.scavenging_min_target, description=description, title=title,choices=choices)
        character.add_submenu(menu)

    def setScavengingLimits(self,character):
        '''
        show the menu to set stock limits

        Parameters:
            character: the character triggering the action
        '''
        description = ["""
Clones with the "scavenging" duty bring all kinds of items into the base.
That can be an issue, if that fills up the storage with useless items.
You can get rid of those useless items using a StockPlaner,
but it would be best to just not collect them.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Set scavenging limits"),""" to Control what items the Clones collect.
They will stop collecting items, if they reached their scavenging limit.

"""]
        title = "SET SCAVENGING LIMIT"
        choices = list(src.items.itemMap.keys())
        menu = src.menues.menuMap["NameNumberPairSetter"](character, self.scavenging_max, description=description, title=title, choices=choices)
        character.add_submenu(menu)

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
src.items.addType(ScavengingManager)

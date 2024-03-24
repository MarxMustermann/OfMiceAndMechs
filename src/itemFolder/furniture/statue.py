import src


class Statue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Statue"
    description = "Used to build rooms."
    name = "statue"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__("@@")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
            options["p"] = ("pray", self.pray)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def pray(self,character):
        options = []
        options.append((1,"1 - god of fertility\n15 scrap"))
        options.append((2,"2 - god of desolution"))
        options.append((3,"3 - god of construction"))
        options.append((4,"4 - god of fighting"))
        options.append((5,"5 - god of battle gear"))
        options.append((6,"6 - god of life"))
        options.append((7,"7 - god of crushing"))

        submenu = src.interaction.SelectionMenu(
            "Select what god to pray to", options,
            targetParamName="god",
        )
        character.macroState["submenue"] = submenu
        character.macroState["submenue"].followUp = {
                "container": self,
                "method": "pray2",
                "params": {"character":character},
        }

    def pray2(self,extraInfo):
        godID = extraInfo["god"]
        character = extraInfo["character"]
        if godID == 1:

            # find scrap to take as saccrifice
            numScrapFound = 0
            scrap = self.container.getItemsByType("Scrap")
            for item in scrap:
                numScrapFound += item.amount

            # ensure that there is enough scrap around
            if not numScrapFound >= 15:
                character.addMessage("not enough scrap")
                return

            # remove the scrap
            numScrapRemoved = 0
            for item in scrap:
                if item.amount <= 15-numScrapRemoved:
                    self.container.removeItem(item)
                    numScrapRemoved += item.amount
                else:
                    item.amount -= 15-numScrapRemoved
                    item.setWalkable()
                    numScrapRemoved += 15-numScrapRemoved

                if numScrapRemoved >= 15:
                    break
            character.addMessage("you sacrifice {numScrapRemoved} Scrap")

        character.addMessage("the Statue turns into a GlassStatue")
        new = src.items.itemMap["GlassStatue"](itemID=godID)
        self.container.addItem(new,self.getPosition())
        self.container.removeItem(self)

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(Statue)

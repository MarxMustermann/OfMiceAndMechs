import src

class GooFaucet(src.items.Item):
    """
    ingame item to get goo from in a convinient way
    """

    type = "GooFaucet"
    attributesToStore = []
    objectsToStore = []
    commandOptions = []
    applyOptions = []

    def __init__(self):
        """
        call superclass constructor with modified paramters
        """

        super().__init__(display="GF")

        self.name = "goo flask"
        self.description = "use it to collect items"

        self.bolted = False
        self.walkable = False
        self.commands = {}
        self.balance = 0
        self.character = None

        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(
                [
                    "balance",
                    "commands",
                ]
            )

        if not self.objectsToStore:
            self.objectsToStore.extend(super().objectsToStore)
            self.objectsToStore.append("character")

        # set up interaction menu
        if not self.applyOptions:
            self.applyOptions.extend(super().applyOptions)
            self.applyOptions.extend(
                [
                    ("drink", "drink from the faucet"),
                    ("fillFlask", "fill goo flask"),
                    ("addTokens", "add goo tokens"),
                    ("showBalance", "show balance"),
                ]
            )
        self.applyMap = {
            "drink": self.drink,
            "fillFlask": self.fillFlask,
            "addTokens": self.addTokens,
            "showBalance": self.showBalance,
        }

        self.runsCommands = True
        if not self.commandOptions:
            self.attributesToStore.extend(super().commandOptions)
            self.commandOptions = [
                ("balanceTooLow", "balance too low"),
            ]

    def drink(self, character):
        """
        handle a character drinking from the goo faucet

        Parameters:
            character: the character trying to drink
        """

        if self.balance < 2:
            character.addMessage("balance too low")
            self.runCommand("balanceTooLow",character)
            return

        character.addSatiation(1000)
        self.balance -= 2

    def fillFlask(self, character):
        """
        handle a character trying to fill its goo flask from the faucet

        Parameters:
            character: the character trying to drink
        """

        filled = False
        fillAmount = 100
        for item in self.character.inventory:
            if isinstance(item, GooFlask) and not item.uses >= fillAmount:
                fillAmount = fillAmount - item.uses
                if fillAmount * 2 > self.balance:
                    self.character.addMessage("balance too low")
                    self.runCommand("ballanceTooLow")
                    return
                item.uses += fillAmount
                filled = True
                self.balance -= fillAmount * 2
                break
        if filled:
            self.character.addMessage("you fill the goo flask")

    # NIY: add tokens to refill
    # abstraction opportunity: many things could accept tokens
    def addTokens(self, character):
        """
        !!!Not implemented yet!!!
        handle a character

        Parameters:
            character: the character trying to drink
        """

        pass
    
    # bad code: should be viewable with examine
    def showBalance(self, character):
        """
        handle a character trying to see how much credit the machine still has

        Parameters:
            character: the character trying to drink
        """

        self.character.addMessage("your balance is %s" % (self.balance,))

src.items.addType(GooFaucet)

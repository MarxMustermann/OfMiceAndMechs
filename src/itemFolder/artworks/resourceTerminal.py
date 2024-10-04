import src


class ResourceTerminal(src.items.Item):
    """
    """

    type = "ResourceTerminal"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display="RT")
        self.name = "scrap terminal"
        self.description = "A resource Terminal"

        self.balance = 0
        self.resource = "Scrap"

    def setResource(self, resource):
        """
        set the ressource to hande

        Parameters:
            ressource (string): the ressource to handle
        """
        self.resource = resource

    # abstraction: should use superclass ability
    def apply(self, character):
        """
        spawn a selection of actions that trigger apply actions

        Parameters:
            character: the character using the item
        """

        super().apply(character)
        options = [
            ("showBalance", "show balance"),
            ("addResource", "add %s" % (self.resource)),
            ("getResource", "get %s" % (self.resource)),
            ("getTokens", "get token"),
            ("addTokens", "add token"),
        ]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    # bad code: should be splited
    def apply2(self):
        """
        do the apply actions
        """

        if self.submenue.selection == "showBalance":
            self.character.addMessage(f"your balance is {self.balance}")

        if self.submenue.selection == "addResource":
            toRemove = []
            for item in self.character.inventory:
                if isinstance(item, src.items.itemMap[self.resource]):
                    toRemove.append(item)

            self.character.addMessage(
                f"you add {len(toRemove)} {self.resource}"
            )
            for item in toRemove:
                self.character.inventory.remove(item)
            self.balance += len(toRemove) // 2
            self.character.addMessage(f"your balance is now {self.balance}")
        if self.submenue.selection == "getTokens":
            self.character.inventory.append(
                src.items.Token(
                    None, None, tokenType=self.resource + "Token", payload=self.balance
                )
            )
            self.balance = 0
        if self.submenue.selection == "addTokens":
            for item in self.character.inventory:
                if (
                    isinstance(item, src.items.Token)
                    and item.tokenType == self.resource + "Token"
                ):
                    self.balance += item.payload
                    self.character.inventory.remove(item)
            pass
        if self.submenue.selection == "getResource":

            numAdded = 0
            for _i in range(len(self.character.inventory), 10):
                if self.balance < 2:
                    self.character.addMessage("your balance is too low")
                    break

                numAdded += 1
                self.balance -= 2
                self.character.inventory.append(src.items.itemMap[self.resource]())

            self.character.addMessage(f"your balance is now {self.balance}")

src.items.addType(ResourceTerminal)

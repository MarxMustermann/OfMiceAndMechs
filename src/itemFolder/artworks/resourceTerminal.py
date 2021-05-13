import src

'''
'''
class ResourceTerminal(src.items.Item):
    type = "ResourceTerminal"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self):
        super().__init__(display="RT")

        self.name = "scrap terminal"

        self.balance = 0
        self.resource = "Scrap"
        self.attributesToStore.extend([
               "balance","resource"])

    def setResource(self,resource):
        self.resource = resource

    '''
    '''
    def apply(self,character):
        super().apply(character,silent=True)
        options = [
                   ("showBalance","show balance"),
                   ("addResource","add %s"%(self.resource)),
                   ("getResource","get %s"%(self.resource)),
                   ("getTokens","get token"),
                   ("addTokens","add token"),
                  ]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character


    def apply2(self):
        if self.submenue.selection == "showBalance":
            self.character.addMessage("your balance is %s"%((self.balance,)))

        if self.submenue.selection == "addResource":
            toRemove = []
            for item in self.character.inventory:
                if isinstance(item,src.items.itemMap[self.resource]):
                    toRemove.append(item)

            self.character.addMessage("you add %s %s"%((len(toRemove),self.resource,)))
            for item in toRemove:
                self.character.inventory.remove(item)
            self.balance += len(toRemove)//2
            self.character.addMessage("your balance is now %s"%(self.balance,))
        if self.submenue.selection == "getTokens":
            self.character.inventory.append(src.items.Token(None,None,tokenType=self.resource+"Token",payload=self.balance))
            self.balance = 0
        if self.submenue.selection == "addTokens":
            for item in self.character.inventory:
                if isinstance(item,src.items.Token) and item.tokenType == self.resource+"Token":
                    self.balance += item.payload
                    self.character.inventory.remove(item)
            pass
        if self.submenue.selection == "getResource":

            numAdded = 0
            for i in range(len(self.character.inventory),10):
                if self.balance < 2:
                    self.character.addMessage("your balance is too low")
                    break

                numAdded += 1
                self.balance -= 2
                self.character.inventory.append(src.items.itemMap[self.resource]())

            self.character.addMessage("your balance is now %s"%(self.balance,))

    def getLongInfo(self):
        text = """
item: ResourceTerminal

description:
A resource Terminal.
"""

src.items.addType(ResourceTerminal)

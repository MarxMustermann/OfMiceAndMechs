import src

'''
'''
class GooFaucet(src.items.Item):
    type = "GooFaucet"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="GooFaucet",creator=None,noId=False):
        super().__init__("GF",xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False
        self.commands = {}
        self.balance = 0
        self.character = None

        self.attributesToStore.extend([
               "balance","commands",
               ])

        self.objectsToStore.extend([
               "character",
               ])

    '''
    collect items
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        options = [("drink","drink from the faucet"),("fillFlask","fill goo flask"),("addTokens","add goo tokens"),("showBalance","show balance")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        if self.submenue.selection == "drink":
            if self.balance < 2:
                self.character.addMessage("balance too low")
                self.runCommand("ballanceTooLow")
                return
            self.character.satiation = 1000
            self.balance -= 2
        if self.submenue.selection == "fillFlask":
            filled = False
            fillAmount = 100
            for item in self.character.inventory:
                if isinstance(item,GooFlask) and not item.uses >= fillAmount:
                    fillAmount = fillAmount-item.uses
                    if fillAmount*2 > self.balance:
                        self.character.addMessage("balance too low")
                        self.runCommand("ballanceTooLow")
                        return
                    item.uses += fillAmount
                    filled = True
                    self.balance -= fillAmount*2
                    break
            if filled:
                self.character.addMessage("you fill the goo flask")
        if self.submenue.selection == "addTokens":
            pass
        if self.submenue.selection == "showBalance":
            self.character.addMessage("your balance is %s"%(self.balance,))

    def configure(self,character):
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            #options.append(("empty","no items left"))
            options.append(("fullInventory","inventory full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        itemType = self.submenue.selection
        
        commandItem = None
        for item in self.container.getItemByPosition((self.xPosition,self.yPosition-1)):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage("added command for %s - %s"%(itemType,commandItem.command))
        return

    def runCommand(self,trigger,character=None):
        if character == None:
            character = self.character

        if not trigger in self.commands:
            return

        command = self.commands[trigger]

        convertedCommand = []
        for char in command:
            convertedCommand.append((char,"norecord"))

        character.macroState["commandKeyQueue"] = convertedCommand + character.macroState["commandKeyQueue"]
        character.addMessage("running command to handle trigger %s - %s"%(trigger,command))

    def getLongInfo(self):
        text = """
item: GooFaucet

description:
use it to collect items
"""

src.items.addType(GooFaucet)

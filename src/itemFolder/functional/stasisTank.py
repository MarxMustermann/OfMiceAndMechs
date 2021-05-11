import src

'''
'''
class StasisTank(src.items.Item):
    type = "StasisTank"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="stasis tank",creator=None,noId=False):
        self.character = None
        super().__init__(src.canvas.displayChars.stasisTank,xPosition,yPosition,name=name,creator=creator)

        self.bolted = True
        self.walkable = False
        self.character = None
        self.characterTimeEntered = None

    def eject(self):
        if self.character:
            self.room.addCharacter(self.character,self.xPosition,self.yPosition+1)
            self.character.stasis = False
            self.character = None
            self.characterTimeEntered = None

    def apply(self,character):
        if not self.room:
            character.addMessage("you can not use item outside of rooms")
            return

        if self.character and self.character.stasis:
            self.eject()
        else:
            options = []
            options.append(("enter","yes"))
            options.append(("noEnter","no"))
            self.submenue = src.interaction.SelectionMenu("The stasis tank is empty. You will not be able to leave it on your on.\nDo you want to enter it?",options)
            self.character = character
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.enterSelection

    def enterSelection(self):
        if self.submenue.selection == "enter":
            self.character.stasis = True
            self.room.removeCharacter(self.character)
            self.character.addMessage("you entered the stasis tank. You will not be able to move until somebody activates it")
            self.characterTimeEntered = src.gamestate.gamestate.tick
        else:
            self.character.addMessage("you do not enter the stasis tank")

    def configure(self,character):
        character.addMessage(src.gamestate.gamestate.tick)
        character.addMessage(self.characterTimeEntered)
        if src.gamestate.gamestate.tick > self.characterTimeEntered+100:
            self.eject()
        """
        options = [("addCommand","add command")]
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character
        """

    def configure2(self):
        if self.submenue.selection == "addCommand":
            options = []
            options.append(("empty","no items left"))
            options.append(("fullInventory","inventory full"))
            self.submenue = src.interaction.SelectionMenu("Setting command for handling triggers.",options)
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def getState(self):
        state = super().getState()

        if self.character:
            state["character"] = self.character.getState()
        else:
            state["character"] = None

        return state

    def setState(self,state):
        super().setState(state)

        if "character" in state and state["character"]:
            char = characters.Character()
            char.setState(state["character"])
            src.saveing.loadingRegistry.register(char)

            self.character = char
        else:
            state["character"] = None

    def getLongInfo(self):
        text = """

This machine allow to enter stasis. In stasis you do not need food and can not do anything.

You cannot leave the stasis tank on your own.

If the stasis tank is empty you can activate it to enter the stasis tank.

If the stasis tank is occupied, you can activate it to eject the character from the tank.
The ejected character will be placed to the south of the stasis tank and will start to act again.

"""
        return text
        

'''
'''
class PositioningDevice(Item):
    type = "PositioningDevice"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="positioning device",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.positioningDevice,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True

    def apply(self,character):

        if not "x" in character.registers:
            character.registers["x"] = [0]
        character.registers["x"][-1] = character.xPosition
        if not "y" in character.registers:
            character.registers["y"] = [0]
        character.registers["y"][-1] = character.yPosition

        character.addMessage("your position is %s/%s"%(character.xPosition,character.yPosition,))

    def getLongInfo(self):
        text = """

this device allows you to determine your postion. Use it to get your position.

use it to determine your position. Your position will be shown as a message.

Also the position will be written to your registers.
The x-position will be written to the register x.
The y-position will be written to the register y.

"""
        return text

src.items.addType(StasisTank)

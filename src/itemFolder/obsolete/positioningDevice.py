import src

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

src.items.addType(PositioningDevice)

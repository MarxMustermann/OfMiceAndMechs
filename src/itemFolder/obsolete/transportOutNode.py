import src

class TransportOutNode(src.items.Item):
    type = "TransportOutNode"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport Out Node",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        if not character.inventory:
            character.addMessage("no items in inventory")
            return

        toDrop = character.inventory[-1]

        if not self.xPosition:
            character.addMessage("this machine needs to be placed to be used")
            return

        position = (self.xPosition,self.yPosition+1)
        items = self.container.getItemByPosition(position)
        if len(items) > 9:
            character.addMessage("not enough space on dropoff point (south)")

        toDrop.xPosition = self.xPosition
        toDrop.yPosition = self.yPosition+1
        character.inventory.remove(toDrop)
        self.container.addItems([toDrop])
        character.addMessage("you take a item")

    def fetchSpecialRegisterInformation(self):
        result = {}

        position = (self.xPosition,self.yPosition+1)
        result["NUM ITEMs"] = len(self.container.getItemByPosition(position))
        return result

src.items.addType(TransportOutNode)

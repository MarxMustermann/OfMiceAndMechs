import src

class TransportInNode(src.items.Item):
    type = "TransportInNode"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="Transport In Node",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.wall,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = False

    def apply(self,character):
        if not (character.xPosition == self.xPosition and character.yPosition == self.yPosition+1):
            character.addMessage("item has to be activated from south")
            return

        position = (self.xPosition,self.yPosition-1)
        items = self.container.getItemByPosition(position)
        if not items:
            character.addMessage("no items to fetch")
            return

        itemToMove = items[0]

        self.container.removeItem(itemToMove)
        character.inventory.append(itemToMove)
        character.addMessage("you take an item")

    def fetchSpecialRegisterInformation(self):
        result = {}

        position = (self.xPosition,self.yPosition-1)
        result["NUM ITEMs"] = len(self.container.getItemByPosition(position))
        return result

src.items.addType(TransportInNode)


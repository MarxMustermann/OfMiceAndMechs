import src

'''
'''
class Token(Item):
    type = "Token"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="token",creator=None,noId=False,tokenType="generic",payload=None):
        super().__init__(src.canvas.displayChars.token,xPosition,yPosition,name=name,creator=creator)

        self.bolted = False
        self.walkable = True
        self.tokenType = tokenType
        self.payload = payload

        self.attributesToStore.extend([
                "tokenType","payload"])

    def getLongInfo(self):
        text = """
A token. Only has value in the eyes of the beholder.

"""
        return text

src.items.addType(Token)

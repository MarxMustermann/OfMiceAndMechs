import src

'''
'''
class Token(src.items.Item):
    type = "Token"

    def __init__(self,tokenType="generic",payload=None):
        '''
        simple superclass configuration
        '''
        super().__init__(display=src.canvas.displayChars.token)

        self.name = "token"
        self.description = """
A token. Only has value in the eyes of the beholder.
"""

        self.bolted = False
        self.walkable = True
        self.tokenType = tokenType
        self.payload = payload

        self.attributesToStore.extend([
                "tokenType","payload"])

src.items.addType(Token)

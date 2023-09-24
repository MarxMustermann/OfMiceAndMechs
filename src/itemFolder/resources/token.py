import src

# obolete: in use but long term future is unsure
class Token(src.items.Item):
    """
    ingame item serving as a placeholer for a ressource. Basically money
    """

    type = "Token"
    name = "token"
    description = """
A token. Only has value in the eyes of the beholder.
"""

    bolted = False
    walkable = True

    def __init__(self, tokenType="generic", payload=None):
        """
        simple superclass configuration

        Parameters:
            tokenType: the color of the token
            payload: additional data like the amount
        """
        super().__init__(display=src.canvas.displayChars.token)

        self.tokenType = tokenType
        self.payload = payload

src.items.addType(Token)

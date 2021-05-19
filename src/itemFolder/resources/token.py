import src

# obolete: in use but long term future is unsure
class Token(src.items.Item):
    """
    ingame item serving as a placeholer for a ressource. Basically money
    """

    type = "Token"

    def __init__(self, tokenType="generic", payload=None):
        """
        simple superclass configuration

        Parameters:
            tokenType: the color of the token
            payload: additional data like the amount
        """
        super().__init__(display=src.canvas.displayChars.token)

        self.name = "token"
        self.description = """
A token. Only has value in the eyes of the beholder.
"""

        self.bolted = False
        self.walkable = True
        self.tokenType = tokenType
        self.payload = payload

        self.attributesToStore.extend(["tokenType", "payload"])

src.items.addType(Token)

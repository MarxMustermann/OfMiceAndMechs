import src
import copy
import json

class GlassHeart(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "GlassHeart"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__("gh")
        self.walkable = False
        self.bolted = False
        self.name = "glass heart"
        self.description = """
A glass heart. You need it to win the game.
"""

src.items.addType(GlassHeart)

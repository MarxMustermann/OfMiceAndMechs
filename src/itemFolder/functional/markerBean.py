import src

"""
marker ment to be placed by characters and to control actions with
"""


class MarkerBean(src.items.Item):
    type = "MarkerBean"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="bean", noId=False):
        self.activated = False
        super().__init__(src.canvas.displayChars.markerBean_inactive, name=name)
        self.walkable = True
        self.bolted = False

        # set up meta information for saving
        self.attributesToStore.extend(["activated"])

    def render(self):
        """
        render the marker
        """
        if self.activated:
            if src.gamestate.gamestate.tick%2 == 1:
                return src.canvas.displayChars.markerBean_active
            else:
                return src.canvas.displayChars.markerBean_inactive
        else:
            return src.canvas.displayChars.markerBean_inactive

    """
    activate marker
    """

    def apply(self, character):
        super().apply(character)
        character.addMessage(character.name + " activates a marker bean")
        self.activated = True

    def getLongInfo(self):
        text = """
item: MarkerBean

description:
A marker been. It can be used to mark things.

"""
        return text


src.items.addType(MarkerBean)

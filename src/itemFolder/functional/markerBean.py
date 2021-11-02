import src

class MarkerBean(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "MarkerBean"
    attributesToStore = []

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        self.activated = False
        super().__init__(src.canvas.displayChars.markerBean_inactive)
        self.walkable = True
        self.bolted = False
        self.name = "marker bean"
        self.description = """
A marker been. It can be used to mark things.
"""
        self.usageInfo = """
use the marker bean to activate it
"""

        # set up meta information for saving
        if not self.attributesToStore:
            self.attributesToStore.extend(super().attributesToStore)
            self.attributesToStore.extend(["activated"])

    def render(self):
        """
        render the marker as animation if active

        Returns:
            how the item should currently be rendered
        """
        if self.activated:
            if src.gamestate.gamestate.tick%2 == 1:
                return src.canvas.displayChars.markerBean_active
            else:
                return src.canvas.displayChars.markerBean_inactive
        else:
            return src.canvas.displayChars.markerBean_inactive

    def apply(self, character):
        """
        activate the marker bean

        Parameters:
            character: the character activating the marker bean
        """

        super().apply(character)
        character.addMessage(character.name + " activates a marker bean")
        self.activated = True

src.items.addType(MarkerBean)

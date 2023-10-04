import src


class CollectionBeacon(src.items.Item):
    """
    ingame item ment to be placed by characters and to mark things with
    """

    type = "CollectionBeacon"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        super().__init__("CB")
        self.walkable = False
        self.bolted = False
        self.name = "collection beacon"

    def apply(self,character):
        pos = self.getBigPosition()
        terrain = self.getTerrain()
        terrain.collectionSpots.append(pos)

src.items.addType(CollectionBeacon)

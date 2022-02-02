import src

"""
used to connect rooms and items to drag them around
"""


class Chain(src.items.Item):
    type = "Chain"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self):
        super().__init__(
            display = src.canvas.displayChars.chains,
        )

        self.name = "chain"

        self.walkable = True
        self.bolted = False

        self.chainedTo = []
        self.fixed = False

    """
    attach/detach chain
    bad code: attaching and detaching should be methods
    bad code: only works on terrains
    """

    def apply(self, character):
        if not self.terrain:
            character.addMessage("chains can only be used on terrain")
            return

        super().apply(character)
        # chain to surrounding items/rooms
        # bad pattern: the user needs to be able to select to what to chain to
        if not self.fixed:
            if self.container:
                # bad code: NIY
                character.addMessage("TODO")
            else:
                # flag self as chained onto something
                self.fixed = True

                # gather items to chain to
                items = []
                for coordinate in [
                    (self.xPosition - 1, self.yPosition),
                    (self.xPosition + 1, self.yPosition),
                    (self.xPosition, self.yPosition - 1),
                    (self.xPosition, self.yPosition + 1),
                ]:
                    if coordinate in self.terrain.itemByCoordinates:
                        items.extend(self.terrain.itemByCoordinates[coordinate])

                # gather nearby rooms
                roomCandidates = []
                bigX = self.xPosition // 15
                bigY = self.yPosition // 15
                for coordinate in [
                    (bigX, bigY),
                    (bigX - 1, bigY),
                    (bigX + 1, bigY),
                    (bigX, bigY - 1),
                    (bigX, bigY + 1),
                ]:
                    if coordinate in self.terrain.roomByCoordinates:
                        roomCandidates.extend(
                            self.terrain.roomByCoordinates[coordinate]
                        )

                # gather rooms to chain to
                rooms = []
                for room in roomCandidates:
                    if (room.xPosition * 15 + room.offsetX == self.xPosition + 1) and (
                        self.yPosition > room.yPosition * 15 + room.offsetY - 1
                        and self.yPosition
                        < room.yPosition * 15 + room.offsetY + room.sizeY
                    ):
                        rooms.append(room)
                    if (
                        room.xPosition * 15 + room.offsetX + room.sizeX
                        == self.xPosition
                    ) and (
                        self.yPosition > room.yPosition * 15 + room.offsetY - 1
                        and self.yPosition
                        < room.yPosition * 15 + room.offsetY + room.sizeY
                    ):
                        rooms.append(room)
                    if (room.yPosition * 15 + room.offsetY == self.yPosition + 1) and (
                        self.xPosition > room.xPosition * 15 + room.offsetX - 1
                        and self.xPosition
                        < room.xPosition * 15 + room.offsetX + room.sizeX
                    ):
                        rooms.append(room)
                    if (
                        room.yPosition * 15 + room.offsetY + room.sizeY
                        == self.yPosition
                    ) and (
                        self.xPosition > room.xPosition * 15 + room.offsetX - 1
                        and self.xPosition
                        < room.xPosition * 15 + room.offsetX + room.sizeX
                    ):
                        rooms.append(room)

                # set chaining for self
                self.chainedTo = []
                self.chainedTo.extend(items)
                self.chainedTo.extend(rooms)

                # set chaining for chained objects
                for thing in self.chainedTo:
                    thing.chainedTo.append(self)
                    character.addMessage(thing.chainedTo)

        # unchain from chained items
        else:
            # clear chaining information
            self.fixed = False
            for thing in self.chainedTo:
                if self in thing.chainedTo:
                    thing.chainedTo.remove(self)
            self.chainedTo = []

    def getLongInfo(self):
        text = """
item: Chain

description:
can be used to chain rooms together. Place it next to one or more rooms and activate it to chain rooms together.

"""
        return text

src.items.addType(Chain)

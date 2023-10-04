import src


# NIY: not properly implemented
class Mortar(src.items.Item):
    """
    ingame item allowing to do ranged attacks with explosives
    """

    type = "Mortar"
    name = "mortar"
    description = "allow to deliver exlosives over a distance"

    bolted = False
    loaded = False
    loadedWith = None
    precision = 5

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.mortar)

    def apply(self, character):
        """
        handle a character trying to use this item
        by doing the ranged attack
        """

        if not self.loaded:
            itemFound = None
            for item in character.inventory:
                if item.type == "Bomb":
                    itemFound = item
                    continue

            if not itemFound:
                character.addMessage("could not load mortar. no bomb in inventory")
                return

            character.addMessage("you load the mortar")

            character.inventory.remove(itemFound)
            self.loadedWith = itemFound
            self.loaded = True
        else:
            if not self.loadedWith:
                self.loaded = False
                return
            character.addMessage("you fire the mortar")
            bomb = self.loadedWith
            self.loadedWith = None
            self.loaded = False

            bomb.yPosition = self.yPosition
            bomb.xPosition = self.xPosition
            bomb.bolted = False

            distance = 10
            if (
                src.gamestate.gamestate.tick + self.yPosition + self.xPosition
            ) % self.precision == 0:
                character.addMessage("you missfire (0)")
                self.precision += 10
                distance -= src.gamestate.gamestate.tick % 10 - 10 // 2
                character.addMessage(
                    (distance, src.gamestate.gamestate.tick % 10, 10 // 2)
                )
            elif (
                src.gamestate.gamestate.tick + self.yPosition + self.xPosition
            ) % self.precision == 1:
                character.addMessage("you missfire (1)")
                self.precision += 5
                distance -= src.gamestate.gamestate.tick % 7 - 7 // 2
                character.addMessage(
                    (distance, src.gamestate.gamestate.tick % 7, 7 // 2)
                )
            elif (
                src.gamestate.gamestate.tick + self.yPosition + self.xPosition
            ) % self.precision < 10:
                character.addMessage("you missfire (10)")
                self.precision += 2
                distance -= src.gamestate.gamestate.tick % 3 - 3 // 2
                character.addMessage(
                    (distance, src.gamestate.gamestate.tick % 3, 3 // 2)
                )
            elif (
                src.gamestate.gamestate.tick + self.yPosition + self.xPosition
            ) % self.precision < 100:
                character.addMessage("you missfire (100)")
                self.precision += 1
                distance -= src.gamestate.gamestate.tick % 2 - 2 // 2
                character.addMessage(
                    (distance, src.gamestate.gamestate.tick % 2, 2 // 2)
                )

            bomb.yPosition += distance

            self.container.addItems([bomb])

            bomb.destroy()

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
            the description text
        """

        text = (
            """

It fires 10 steps to the south. Its current precision is """
            + str(self.precision)
            + """.

"""
        )
        return text

src.items.addType(Mortar)

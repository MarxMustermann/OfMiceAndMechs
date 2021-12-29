import src


# bad code: ugly hack that causes problems
# NIY: implement a proper way of adding such effects
class Explosion(src.items.Item):
    """
    technically a ingame but is only shown for 1 tick to simulate an explosion event
    """

    type = "Explosion"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.explosion)
        self.name = "explosion"
        self.walkable = True

    def pickUp(self, character):
        """
        do nothing when picked up

        Parameters:
            the character trying to interact
        """

        pass

    # bad code: i don't know why this code exists
    def apply(self, character):
        """
        explode on activation

        Parameters:
            the character trying to interact
        """

        self.explode()
        pass

    def drop(self, character):
        """
        do nothing when droped

        Parameters:
            the character trying to interact
        """
        pass

    def explode(self):
        """
        do the actual explosion and damage things
        """

        if self.container:
            self.container.damage()

        if self.xPosition and self.yPosition:
            for character in self.container.characters:
                if (
                    character.xPosition == self.xPosition
                    and character.yPosition == self.yPosition
                ):
                    character.hurt(50,reason="explosion")

            for item in self.container.getItemByPosition(
                (self.xPosition, self.yPosition, self.zPosition)
            ):
                if item == self:
                    continue
                if item.type == "Explosion":
                    continue
                item.destroy()

        if self.container:
            self.container.removeItem(self)

src.items.addType(Explosion)

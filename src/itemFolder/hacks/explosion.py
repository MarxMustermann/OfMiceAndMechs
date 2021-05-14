import src


class Explosion(src.items.Item):
    type = "Explosion"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.explosion)
        self.name = "explosion"

    def pickUp(self, character):
        pass

    def apply(self, character):
        self.explode()
        pass

    def drop(self, character):
        pass

    def explode(self):

        if self.room:
            self.room.damage()
        elif self.terrain:
            for room in self.terrain.getRoomsOnFineCoordinate(
                (self.xPosition, self.yPosition)
            ):
                room.damage()

        if self.xPosition and self.yPosition:
            for character in self.container.characters:
                if (
                    character.xPosition == self.xPosition
                    and character.yPosition == self.yPosition
                ):
                    character.die()

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

import src


class MoldFeed(src.items.Item):
    type = "MoldFeed"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.moldFeed)
        self.name = "mold feed"

        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        return """
item: MoldFeed

description:

This is a good base for mold growth. If mold grows onto it, it will grow into a bloom.

can be eaten
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

    def apply(self, character):
        character.satiation += 1000
        if character.satiation > 1000:
            character.satiation = 1000
        character.addMessage("you eat the mold feed and gain satiation")
        self.destroy()


src.items.addType(MoldFeed)

import src


class GooFlask(src.items.Item):
    type = "GooFlask"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="goo flask", noId=False):
        self.uses = 0
        super().__init__(display=src.canvas.displayChars.gooflask_empty, name=name)
        self.walkable = True
        self.bolted = False
        self.description = "a flask containing goo"
        self.level = 1
        self.maxUses = 100

        # set up meta information for saving
        self.attributesToStore.extend(["uses", "level", "maxUses"])

    """
    drink from flask
    """

    def apply(self, character):
        super().apply(character, silent=True)

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.addMessage("you drink from your flask, but it is empty")
            return

        # print feedback
        if character.watched:
            if not self.uses == 1:
                character.addMessage("you drink from your flask")
            else:
                character.addMessage("you drink from your flask and empty it")

        # change state
        self.uses -= 1
        self.changed()
        character.heal(1, reason="drank from flask")
        if character.frustration > 5000:
            character.frustration -= 15
        character.satiation = 1000
        character.changed()

    def render(self):
        """
        render based on fill amount
        """
        displayByUses = [
            src.canvas.displayChars.gooflask_empty,
            src.canvas.displayChars.gooflask_part1,
            src.canvas.displayChars.gooflask_part2,
            src.canvas.displayChars.gooflask_part3,
            src.canvas.displayChars.gooflask_part4,
            src.canvas.displayChars.gooflask_full,
        ]
        return displayByUses[self.uses // 20]

    """
    get info including the charges on the flask
    """

    def getDetailedInfo(self):
        return super().getDetailedInfo() + " (" + str(self.uses) + " charges)"

    def getLongInfo(self):
        text = """
item: GooFlask

description:
A goo flask holds goo. Goo is nourishment for you.

If you do not drink from the flask every 1000 ticks you will starve.

A goo flask can be refilled at a goo dispenser and can hold a maximum of %s charges.

this is a level %s item.

""" % (
            self.maxUses,
            self.level,
        )
        return text

    def upgrade(self):
        super().upgrade()

        self.maxUses += 10

    def downgrade(self):
        super().downgrade()

        self.maxUses -= 10


src.items.addType(GooFlask)

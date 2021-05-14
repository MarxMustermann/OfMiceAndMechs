import src

"""
Vial with health to carry around and drink from
"""


class Vial(src.items.Item):
    type = "Vial"

    """
    call superclass constructor with modified paramters and set some state
    """

    def __init__(self, name="vial", noId=False):
        super().__init__(display=src.canvas.displayChars.gooflask_empty, name=name)
        self.walkable = True
        self.bolted = False
        self.description = "a vial containing health"
        self.maxUses = 10
        self.uses = 0
        self.level = 1

        # set up meta information for saving
        self.attributesToStore.extend(["uses", "level", "maxUses"])

    """
    drink from flask
    """

    def apply(self, character):
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
        character.heal(10)
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
        return displayByUses[self.uses // 2]

    """
    get info including the charges on the flask
    """

    def getDetailedInfo(self):
        return super().getDetailedInfo() + " (" + str(self.uses) + " charges)"

    def getLongInfo(self):
        text = """
item: Vial

description:
A vial holds health. You can heal yourself with it

A goo flask can be refilled at a health station and can hold a maximum of %s charges.

this is a level %s item.

""" % (
            self.maxUses,
            self.level,
        )
        return text

    def upgrade(self):
        super().upgrade()

        self.maxUses += 1

    def downgrade(self):
        super().downgrade()

        self.maxUses -= 1


src.items.addType(Vial)

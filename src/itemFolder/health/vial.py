import src


class Vial(src.items.Item):
    """
    ingame item with health to carry around and drink from
    """

    type = "Vial"

    def __init__(self, name="vial", noId=False):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.gooflask_empty, name=name)
        self.walkable = True
        self.bolted = False
        self.description = "a vial containing health"
        self.usageInfo = "use the vial to heal yourself"
        self.maxUses = 10
        self.uses = 0
        self.level = 1

    def apply(self, character):
        """
        handle a character trying to drink from the flask

        Parameters:
            character: the character trying to use the item    
        """

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.addMessage("you drink from your flask, but it is empty")
            return

        # print feedback
        if character.watched:
            if not self.uses == 1:
                character.addMessage("you drink from the vial")
            else:
                character.addMessage("you drink from the vial and empty it")

        # change state
        self.uses -= 1
        self.changed()
        character.heal(10+min((character.maxHealth-character.health)//10,10))
        character.changed()

    def render(self):
        """
        render based on fill amount

        Returns:
            what the item should look like
        """

        displayByUses = [
            src.canvas.displayChars.vial_empty,
            src.canvas.displayChars.vial_part1,
            src.canvas.displayChars.vial_part2,
            src.canvas.displayChars.vial_part3,
            src.canvas.displayChars.vial_part4,
            src.canvas.displayChars.vial_full,
        ]
        return displayByUses[self.uses // 2]


    def getDetailedInfo(self):
        """
        get info including the charges on the flask

        Returns:
            the description text
        """

        return super().getDetailedInfo() + " (" + str(self.uses) + " charges)"

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += """
A goo flask can be refilled at a health station and can hold a maximum of %s charges.

this is a level %s item.

""" % (
            self.maxUses,
            self.level,
        )
        return text

    def upgrade(self):
        """
        increase max uses when upgraded
        """
        super().upgrade()

        self.maxUses += 1

    def downgrade(self):
        """
        increase max uses when downgraded
        """
        super().downgrade()

        self.maxUses -= 1


src.items.addType(Vial)

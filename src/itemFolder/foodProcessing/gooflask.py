import src


class GooFlask(src.items.Item):
    type = "GooFlask"

    def __init__(self,uses=0):
        """
        configure super class
        """

        self.uses = uses
        super().__init__(display=src.canvas.displayChars.gooflask_empty)

        self.name = "goo flask"
        self.walkable = True
        self.bolted = False
        self.description = "A flask holds goo. Goo is nourishment for you"
        self.level = 1
        self.maxUses = 100

    def apply(self, character):
        """
        handle a character tyring to drink from the flask

        Parameters:
            character: the character trying to drink from the flask
        """

        super().apply(character)

        # handle edge case
        if self.uses <= 0:
            if character.watched:
                character.addMessage("you drink from your flask, but it is empty")
            return

        if character.flask and character.flask != self:
            amount = min(character.flask.maxUses-character.flask.uses,self.uses)
            character.flask.uses += amount
            self.uses -= amount
            character.addMessage(f"you fill your flask with {amount} uses. {self.uses} uses remain.")
            return

        # print feedback
        if character.watched:
            if self.uses != 1:
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
        character.addMessage("you are satiated")
        character.changed()

    def render(self):
        """
        render based on fill amount

        Returns:
            what the item should look like
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

    def getDetailedInfo(self):
        """
        get info including the charges on the flask
        """

        return super().getDetailedInfo() + " (" + str(self.uses) + " charges)"

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

If you do not drink from the flask every 1000 ticks you will starve.

A goo flask can be refilled at a goo dispenser and can hold a maximum of {self.maxUses} charges.
The flask has {self.uses} charges.

this is a level {self.level} item.

"""
        return text

    def upgrade(self):
        """
        increase max uses on upgrade
        """

        super().upgrade()

        self.maxUses += 10

    def downgrade(self):
        """
        decrease max uses on upgrade
        """

        super().downgrade()

        self.maxUses -= 10

src.items.addType(GooFlask)

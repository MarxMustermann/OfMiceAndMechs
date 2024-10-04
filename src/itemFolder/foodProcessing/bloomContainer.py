import src


class BloomContainer(src.items.Item):
    """
    a item to carry bloom items with
    """

    type = "BloomContainer"

    def __init__(self):
        """
        simple superclass configuration
        """

        super().__init__()

        self.display = src.canvas.displayChars.bloomContainer
        self.name = "bloom container"
        self.description = "The bloom container is used to carry an store blooms"
        self.usageInfo = """
= loading blooms =
prepare by placing the bloom container on the ground and placing blooms around the container.
Activate the bloom container and select the option "load bloom" to load the blooms into the container.

= unload blooms =
prepare by placing the bloom container on the ground.
Activate the bloom container and select the option "unload bloom" to unload the blooms to the east.
"""

        self.charges = 0
        self.maxCharges = 15
        self.level = 1

    def getLongInfo(self):
        """
        returns a log text description of the item

        Returns:
            the description
        """

        text = super().getLongInfo()

        text += f"""
it has {self.charges} blooms (charges) in it. It can hold a maximum of {self.maxCharges} blooms.

This is a level {self.level} item.
"""

    def apply(self, character):
        """
        handle a character trying to use the item

        Parameters:
            character: the character trying to use the item
        """

        options = []
        options.append(("load", "load blooms"))
        options.append(("unload", "unload blooms"))
        self.submenue = src.interaction.SelectionMenu(
            "select the item to produce", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doSelection
        self.character = character

    # bad code: should be splitted up
    # abstraction: should use superclass function
    def doSelection(self):
        """
        either unload or load depending on a previous selection
        """

        selection = self.submenue.selection
        if selection == "load":
            if self.charges >= self.maxCharges:
                self.character.addMessage("bloom container full. no blooms loaded")
                return

            blooms = []
            positions = [
                (self.xPosition + 1, self.yPosition),
                (self.xPosition - 1, self.yPosition),
                (self.xPosition, self.yPosition + 1),
                (self.xPosition, self.yPosition - 1),
            ]
            for position in positions:
                for item in self.container.getItemByPosition(position):
                    if item.type == "Bloom":
                        blooms.append(item)

            if not blooms:
                self.character.addMessage("no blooms to load")
                return

            for bloom in blooms:
                if self.charges >= self.maxCharges:
                    self.character.addMessage(
                        "bloom container full. not all blooms loaded"
                    )
                    return

                self.container.removeItem(bloom)
                self.charges += 1

            self.character.addMessage("blooms loaded")
            return

        elif selection == "unload":

            if self.charges == 0:
                self.character.addMessage("no blooms to unload")
                return

            foundWalkable = 0
            foundNonWalkable = 0
            for item in self.container.getItemByPosition(
                (self.xPosition + 1, self.yPosition)
            ):
                if item.walkable:
                    foundWalkable += 1
                else:
                    foundNonWalkable += 1

            if foundWalkable > 0 or foundNonWalkable >= 15:
                self.character.addMessage("target area full. no blooms unloaded")
                return

            toAdd = []
            while foundNonWalkable <= 15 and self.charges:
                new = src.items.itemMap["Bloom"]()
                new.dead = True

                toAdd.append((new,(self.xPosition+1,self.yPosition,self.zPosition)))
                self.charges -= 1
            self.container.addItems(toAdd)


src.items.addType(BloomContainer)

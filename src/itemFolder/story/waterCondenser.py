import src


class WaterCondenser(src.items.Item):
    """
    ingame item used as a source for water
    """

    type = "WaterCondenser"

    def __init__(self):
        """
        set up initial state
        """

        super().__init__(display="WW")

        self.name = "water condenser"
        self.description = "you can drink condensed water from it, but the water is poisoned"

        self.walkable = False
        self.bolted = True
        self.rods = 0
        self.lastUsage = src.gamestate.gamestate.tick

    def apply(self, character):
        """
        handle a character trying to use the item
        by offering a selection of possible actions

        Parameters:
            character: the character trying to use the item
        """

        options = [("drink", "drink"), ("rod", "add rod")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        """
        handle a character selected an action to do
        by doing it
        """

        if not self.terrain:
            self.character.addMessage(
                "the water condenser needs to be placed outside to work"
            )
            return

        self.bolted = True

        if self.submenue.selection == "drink":
            if self.terrain.heatmap[self.xPosition // 15][self.yPosition // 15] > 4:
                self.character.addMessage("there is no water left")
                return

            amount = (
                (src.gamestate.gamestate.tick - self.lastUsage)
                // 100
                * (self.rods + 1 + 5)
            )
            self.character.addMessage(
                f"you drink from the water condenser. You gain {amount} satiation, but are poisoned"
            )
            self.character.satiation += amount
            if self.character.satiation > 1000:
                self.character.satiation = 1000
            self.character.hurt(amount // 100 + 1, reason="poisoned")

            self.lastUsage = src.gamestate.gamestate.tick

        if self.submenue.selection == "rod":
            if self.rods > 9:
                self.character.addMessage("the water condenser cannot take more rods")
                return

            for item in self.character.inventory:
                if isinstance(item, src.items.Rod):

                    self.character.addMessage(
                        f"you insert a rod into the water condenser increasing its output to {self.rods + 1 + 5} per 100 ticks"
                    )
                    self.rods += 1
                    self.character.inventory.remove(item)
                    self.lastUsage = src.gamestate.gamestate.tick
                    return
            self.character.addMessage("you have no rods in your inventory")

    def getLongInfo(self):
        """
        returns a longer than usual description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

it generates {self.rods + 1 + 5} satiation for every 100 ticks left alone

"""
        return text

src.items.addType(WaterCondenser)

import src


class Bush(src.items.Item):
    """
    ingame item basically acting as a grown barrier
    """

    type = "Bush"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.bush)

        self.name = "bush"
        self.description = "This a patch of mold with multiple blooms and a network vains connecting them"

        self.walkable = False
        self.charges = 10
        self.attributesToStore.extend(["charges"])

    def apply(self, character):
        """
        handle a character trying to use the bush

        Parameters:
            character: the character trying to use the item
        """

        if self.charges > 10:
            new = itemMap["EncrustedBush"]()
            self.container.addItem(new,self.getPosition())

            self.container.removeItem(self)

            character.addMessage("the bush encrusts")

        if self.charges:
            character.satiation += 5
            self.charges -= 1
            character.addMessage("you eat from the bush and gain 5 satiation")
        else:
            self.destroy()

    def getLongInfo(self):
        """
        returns a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += """
charges: %s""" % (self.charges)
        return text

    def destroy(self, generateSrcap=True):
        """
        destroy this item
        """

        new = itemMap["Coal"]()
        self.container.addItem(new,self.getPosition())
        super().destroy(generateSrcap=False)

src.items.addType(Bush)

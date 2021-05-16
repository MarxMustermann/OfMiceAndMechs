import src


class HealingStation(src.items.Item):
    """
    ingame item to provide characters with an oportunity to heal
    """

    type = "HealingStation"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.healingStation)

        self.name = "healing station"
        self.description = "heals you"

        self.walkable = False
        self.bolted = True
        self.charges = 0

    # abstraction: super class functionality should be used
    def apply(self, character):
        """
        handle a character trying to use this item

        Parameters:
            character: the character trying to use this item
        """

        options = [("heal", "heal me"), ("vial", "fill vial")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    # abstraction: super class functionality should be used
    def apply2(self):
        """
        do the selected action
        """

        if self.submenue.selection == "heal":
            self.heal(self.character)
        if self.submenue.selection == "vial":
            self.fill(self.character)

    def heal(self, character):
        """
        handle a character trying to heal

        Parameters:
            character: the character trying to heal
        """

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        character.addMessage("the machine heals you")
        character.health = 100
        self.charges -= 1

    def fill(self, character):
        """
        handle a character trying to fill a goo flask

        Parameters:
            character: the character trying to use this item
        """

        if self.charges < 1:
            character.addMessage("no charges left")
            return

        for item in character.inventory:
            if not isinstance(item, src.items.Vial):
                continue
            if self.charges > item.maxUses - item.uses:
                self.charges -= item.maxUses - item.uses
                item.uses = item.maxUses
                character.addMessage("you fill your vial with the healing")
                return
            else:
                item.uses += self.charges
                self.charges = 0
                character.addMessage("you drain the healing into your vial")
                return

        character.addMessage("you have no vial in your inventory")

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        
        text +="""
charges:
%s

""" % (
            self.charges
        )

        return text


src.items.addType(HealingStation)

import src


class StaticMover(src.items.Item):
    """
    ingame item behaving like a wall trying to block the player in
    """

    type = "StaticMover"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.forceField2)

        self.name = "static mover"
        self.description = "Moves towards you and leeches your energy"

        self.walkable = False
        self.bolted = True
        self.strength = 1
        self.energy = 1

    def apply(self, character):
        """
        handle a character trying to destroy the mover

        Parameters:
            character: the character trying to destroy the mover
        """

        staticSpark = None
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["StaticSpark"]) and item.strength >= self.strength:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            character.addMessage("no suitable static spark")
            return

        character.inventory.remove(item)
        self.container.removeItem(self)
        character.addMessage(
            "you use a static spark on the static wall and it dissapears"
        )

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += """
energy:
%s

""" % (
            self.energy
        )

        return text


src.items.addType(StaticMover)

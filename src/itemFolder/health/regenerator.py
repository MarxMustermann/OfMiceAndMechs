import src


class Regenerator(src.items.Item):
    type = "Regenerator"
    description = "Gives healing vibes to all characters"
    name = "regenerator"

    healing_amount = 25

    def __init__(self):
        self.bolted = True
        self.activated = False
        super().__init__(display="()")

    def addTickingEvent(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick + 15)
        event.setCallback({"container": self, "method": "handleTicking"})
        self.container.addEvent(event)

    def apply(self, character):
        if not self.activated:
            self.addTickingEvent()
            character.addMessage("You activated the regenerator")
            submenue = src.menuFolder.TextMenu.TextMenu(
                f"You activated the Regenerator.\nIt will heal every creature in this room when it pulses.\nIt pulses every 15 ticks"
            )
            character.macroState["submenue"] = submenue
            character.runCommandString("~",nativeKey=True)
            self.activated = True
            character.changed("regenerator activated",{})

    def handleTicking(self):
        self.addTickingEvent()
        self.container.addAnimation(
            self.getPosition(), "showchar", 1, {"char": ")("}
        )

        for character in self.container.characters:
            character.heal(self.healing_amount, reason="by the regenerator")
            self.container.addAnimation(
                character.getPosition(), "showchar", 1, {"char": [(src.interaction.urwid.AttrSpec("#f00", "#fff"), "^^")]}
            )


src.items.addType(Regenerator)

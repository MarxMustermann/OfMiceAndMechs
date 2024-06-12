import src


class PoissonTower(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "PoissonTower"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="/\\")

    def apply(self, character=None):
        foundChars = []
        for checkChar in self.container.characters:
            foundChars.append(checkChar)

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})
        if character:
            character.addMessage("everyone in the room is posissoned")

        while foundChars:
            target = foundChars.pop()
            self.container.addAnimation(target.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#afa", "black"), "%%")]})
            target.hurt(70,reason="poission")
        self.destroy()

    def remoteActivate(self):
        self.apply()

    def render(self):
        return (src.interaction.urwid.AttrSpec("#fff", "#000"), "PT")

src.items.addType(PoissonTower)

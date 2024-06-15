import src


class RodTower(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "RodTower"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="/\\")
        self.charges = 0

    def apply(self, character=None):
        if self.charges < 1:
            if character:
                character.addMessage("no charges")
            return

        neighbours = []
        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
            neighbours.append(self.getPosition(offset=offset))

        for neighbour in neighbours:
            self.container.addAnimation(neighbour,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "%%")]})
            targets = self.container.getCharactersOnPosition(neighbour)
            for target in targets:
                target.hurt(20,reason="hit by rod")

    def remoteActivate(self,extraParams=None):
        self.apply()

    def render(self):
        return (src.interaction.urwid.AttrSpec("#fff", "#000"), "RT")

src.items.addType(RodTower)

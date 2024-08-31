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
        self.coolDown = 10
        self.lastUsed = 0

    def apply(self, character=None):
        try:
            self.lastUsed
        except:
            self.lastUsed = 0
        try:
            self.coolDown
        except:
            self.coolDown = 10

        if self.isInCoolDown():
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "black"), "XX")]})
            return

        self.lastUsed = src.gamestate.gamestate.tick

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "XX")]})

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

    def isInCoolDown(self):
        if not (src.gamestate.gamestate.tick - self.lastUsed) > self.coolDown:
            return True
        else:
            return False

    def render(self):
        try:
            self.lastUsed
        except:
            self.lastUsed = 0
        try:
            self.coolDown
        except:
            self.coolDown = 10

        if self.isInCoolDown():
            return (src.interaction.urwid.AttrSpec("#444", "#000"), "RT")
        else:
            return (src.interaction.urwid.AttrSpec("#fff", "#000"), "RT")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(RodTower)

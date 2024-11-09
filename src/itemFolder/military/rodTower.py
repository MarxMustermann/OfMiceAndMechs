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
        self.weapon = None

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
            baseDamage = 2
            if self.weapon:
                baseDamage = self.weapon.baseDamage
                self.weapon.baseDamage -= 1
                if self.weapon.baseDamage == 10:
                    self.weapon = None

            for target in targets:
                target.hurt(baseDamage*2,reason="hit by RodTower")

    def remoteActivate(self,extraParams=None):
        self.apply()

    def isInCoolDown(self):
        if not (src.gamestate.gamestate.tick - self.lastUsed) > self.coolDown:
            return True
        else:
            return False

    def render(self):
        try:
            self.weapon
        except:
            self.weapon = None
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
            color = "#777"
            if self.weapon:
                color = "#888"
                if self.weapon.baseDamage >= 13:
                    color = "#999"
                if self.weapon.baseDamage >= 17:
                    color = "#aaa"
                if self.weapon.baseDamage >= 18:
                    color = "#bbb"
                if self.weapon.baseDamage >= 19:
                    color = "#ccc"
                if self.weapon.baseDamage >= 21:
                    color = "#ddd"
                if self.weapon.baseDamage >= 23:
                    color = "#eee"
                if self.weapon.baseDamage >= 25:
                    color = "#fff"

            return (src.interaction.urwid.AttrSpec(color, "#000"), "RT")

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
        options["w"] = ("replace weapon", self.replaceWeapon)
        return options

    def replaceWeapon(self,character):
        try:
            self.weapon
        except:
            self.weapon = None

        bestSword = None
        for item in character.inventory:
            if not item.type == "Sword":
                continue
            if bestSword == None:
                bestSword = item
                continue

            if item.baseDamage <= bestSword.baseDamage:
                continue

            bestSword = item

        if self.weapon:
            character.inventory.append(self.weapon)

        if bestSword:
            self.weapon = bestSword
            character.inventory.remove(self.weapon)
        else:
            self.weapon = None

    def getLongInfo(self):
        try:
            self.weapon
        except:
            self.weapon = None

        if self.weapon:
            result = f"""
weapon: {self.weapon.baseDamage}
"""
        else:
            result = f"""
weapon: None
"""
        return result

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the ScrapCompactor")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the ScrapCompactor")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(RodTower)

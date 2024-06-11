import src


class ShockTower(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "ShockTower"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="/\\")
        self.charges = 7
        self.faction = None

    def apply(self, character=None):
        if self.charges < 1:
            if character:
                character.addMessage("no charges")
            return

        foundChars = []
        for checkChar in self.container.characters:
            if checkChar.faction == self.faction:
                continue

            foundChars.append(checkChar)

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})
        self.charges -= 1

        if not foundChars:
            if character:
                character.addMessage("no valid targets found")
            return

        while self.charges and foundChars:
            target = foundChars.pop()
            self.shock(target,character=character)

    def remoteActivate(self):
        self.apply()

    def shock(self,target,character=None):
        if self.charges < 1:
            return

        damage = 50
        self.charges -= 1
        target.hurt(damage,reason="shocked")
        self.container.addAnimation(target.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})
        self.container.addAnimation(target.getPosition(),"smoke",damage,{})

        if character:
            character.addMessage("the shock tower shocks an enemy")

    def configure(self, character):
        """

        Parameters:
            character: the character trying to use the item
        """

        if not self.faction == character.faction:
            self.faction = character.faction
            character.addMessage("you set the faction for the ShockTower")
            return

        compressorFound = None
        for item in character.inventory:
            if isinstance(item,src.items.itemMap["LightningRod"]):
                compressorFound = item
                break

        if not compressorFound:
            character.addMessage("you have no LightningRod")
            return

        self.charges += 1
        character.addMessage("you charge the ShockTower")
        character.inventory.remove(compressorFound)

    def render(self):
        return (src.interaction.urwid.AttrSpec("#fff", "#000"), "ST")

    def getLongInfo(self):
        return """
The shocker has %s charges
""" % (
            self.charges
        )



src.items.addType(ShockTower)

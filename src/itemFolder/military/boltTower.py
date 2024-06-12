import src


class BoltTower(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "BoltTower"

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

        direction = (0,1,0)
        if character:
            characterPos = character.getPosition()
            ownPos = self.getPosition()
            direction = (ownPos[0]-characterPos[0],ownPos[1]-characterPos[1],ownPos[2]-characterPos[2])

        currentPos = self.getPosition()
        while True:
            targets = self.container.getCharactersOnPosition(currentPos)
            if targets:
                self.container.addAnimation(currentPos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "XX")]})
                for target in targets:
                    target.hurt(20,reason="hit by bolt")
                    break
                break

            self.container.addAnimation(currentPos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "##")]})
            print(currentPos)

            currentPos = (currentPos[0]+direction[0],currentPos[1]+direction[1],currentPos[2]+direction[2])

            if currentPos[1] >= 12:
                break
            if currentPos[1] <= 0:
                break
            if currentPos[0] >= 12:
                break
            if currentPos[0] <= 0:
                break
        return
        1/0

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

    def configure(self, character):
        """

        Parameters:
            character: the character trying to use the item
        """

        if not self.faction == character.faction:
            self.faction = character.faction
            character.addMessage("you set the faction for the ShockTower")
            return

        boltFound = None
        for item in character.inventory:
            if isinstance(item,src.items.itemMap["Bolt"]):
                boltFound = item
                break

        if not boltFound:
            character.addMessage("you have no Bolt")
            return

        self.charges += 1
        character.addMessage("you charge the BoltTower")
        character.inventory.remove(boltFound)

    def render(self):
        return (src.interaction.urwid.AttrSpec("#fff", "#000"), "BT")

src.items.addType(BoltTower)

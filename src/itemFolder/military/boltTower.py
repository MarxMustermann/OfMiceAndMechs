import src
from src.rooms import Room

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

    def apply(self, character):
        self.showTargetingHud({"character":character})

    def showTargetingHud(self,params):
        character = params["character"]

        extraText = ""
        key = params.get("keyPressed")
        if key:
            if key in ("enter","esc","lESC","rESC"):
                return
            if key == "w":
                character.timeTaken += 1
                extraText = self.shoot({"character":character,"direction":(0,-1,0)})
            if key == "a":
                character.timeTaken += 1
                extraText = self.shoot({"character":character,"direction":(-1,0,0)})
            if key == "s":
                character.timeTaken += 1
                extraText = self.shoot({"character":character,"direction":(0,1,0)})
            if key == "d":
                character.timeTaken += 1
                extraText = self.shoot({"character":character,"direction":(1,0,0)})
            if key == ".":
                character.timeTaken += 1

        def rerender():
            if isinstance(self.container,Room) :
                rendering = self.container.render(advanceAnimations = False)
            else:
                rendering = self.container.render(size=(14,14),coordinateOffset = ((self.getPosition()[1]//15)* 15 ,(self.getPosition()[0]//15)* 15 ))

            for line in rendering:
                line.append("\n")

            if self.charges>0:
                charges_text = self.charges
            else:
                charges_text = "no"
            return [rendering,"\n",extraText,"\n\n",f"you have {charges_text} shots left","\npress wasd to shoot            \npress . to wait"]

        submenue = src.menuFolder.OneKeystrokeMenu.OneKeystrokeMenu(rerender())
        submenue.rerenderFunction = rerender
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"showTargetingHud","params":params}

    def shoot(self, extraParams=None):
        character = None
        if extraParams:
            character = extraParams.get("character")

        if self.charges < 1:
            if character:
                character.addMessage("no charges")
            return "no charges"

        direction = None
        if extraParams:
            direction = extraParams.get("direction")

        if not direction and character:
            characterPos = character.getPosition()
            ownPos = self.getPosition()
            direction = (ownPos[0]-characterPos[0],ownPos[1]-characterPos[1],ownPos[2]-characterPos[2])

        if not direction and extraParams:
            targetPos = extraParams.get("pos")
            if targetPos:
                ownPos = self.getPosition()
                direction = (ownPos[0]-targetPos[0],ownPos[1]-targetPos[1],ownPos[2]-targetPos[2])
                if abs(direction[0]) > 0 and direction[1] == 0:
                    direction = (-int(direction[0]/abs(direction[0])),0,0)
                elif abs(direction[1]) > 0 and direction[0] == 0:
                    direction = (0,-int(direction[1]/abs(direction[1])),0)
                else:
                    return

        if not direction:
            1/0

        if isinstance(self.container,Room):
            containerSize = 11
        else:
            containerSize = 13


        self.charges -= 1
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

            currentPos = (currentPos[0]+direction[0],currentPos[1]+direction[1],currentPos[2]+direction[2])

            if currentPos[1]%15 > containerSize:
                break
            if currentPos[1]%15 <= 0:
                break
            if currentPos[0]%15 > containerSize:
                break
            if currentPos[0]%15 <= 0:
                break
        return "you shoot"

    def remoteActivate(self,extraParams=None):
        self.shoot(extraParams=extraParams)

    def configure(self, character):
        """

        Parameters:
            character: the character trying to use the item
        """

        self.bolted = True

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

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
        self.charges = 0

    def apply(self,character):
        self.showTargetingHud({"character":character})

    def loadNearbyAmmo(self):
        ammoDropSpots = [(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]
        numLoaded = 0
        for dropSpot in ammoDropSpots:
            items = self.container.getItemByPosition(self.getPosition(offset=dropSpot))
            if not items:
                continue

            while items and items[-1].type == "LightningRod":
                self.charges += 1
                self.container.removeItem(items[-1])
                numLoaded += 1

        if numLoaded:
            return f"you load {numLoaded} lightningRods"
        else:
            return f"no lightningRods found"

    def showTargetingHud(self,params):
        pos = params.get("pos")
        if not pos:
            pos = self.getPosition()
        character = params["character"]

        cursorSymbol = "XX"
        extraText = ""
        key = params.get("keyPressed")
        if key:
            if key in ("enter","esc","lESC","rESC"):
                return
            if key == "w":
                pos = self.Constrain_Within_Room((pos[0],pos[1]-1,0))
            if key == "a":
                pos = self.Constrain_Within_Room((pos[0]-1,pos[1],0))
            if key == "s":
                pos = self.Constrain_Within_Room((pos[0],pos[1]+1,0))
            if key == "d":
                pos = self.Constrain_Within_Room((pos[0]+1,pos[1],0))
            if key == "r":
                extraText = self.loadNearbyAmmo()
            if key == ".":
                character.timeTaken += 1
            if key == "j":
                character.timeTaken += 1
                extraText = self.shock(pos,character)
        params["pos"] = pos

        def rerender():
            rendering = self.container.render(advanceAnimations=False)
            if not self.container.animations:
                rendering[pos[1]][pos[0]] = cursorSymbol

            for line in rendering:
                line.append("\n")

            if self.charges > 0:
                charges_text = self.charges
            else:
                charges_text = "no"
            return [rendering,"\n",extraText,"\n\n",f"you have {charges_text} charges left","""
press wasd to move cursor
press j to shock coordinate
press r to reload from nearby fields
press . to wait"""]

        submenue = src.interaction.OneKeystrokeMenu(rerender())
        submenue.rerenderFunction = rerender
        character.macroState["submenue"] = submenue
        character.macroState["submenue"].followUp = {"container":self,"method":"showTargetingHud","params":params}

    def remoteActivate(self,extraParams=None):
        if self.charges:
            if extraParams and extraParams.get("pos"):
                pos = extraParams.get("pos")
                self.shock(pos)
        else:
            self.loadNearbyAmmo()

    def shock(self,targetPos,character=None):
        if self.charges < 1:
            if character:
                character.addMessage("no charges")
            return "no charges"

        if character:
            character.addMessage(f"you shock the coordinate {targetPos}")

        self.charges -= 1
        damage = 50
        self.container.addAnimation(targetPos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#aaf", "black"), "%%")]})

        targets = self.container.getCharactersOnPosition(targetPos)
        if targets:
            for target in targets:
                target.hurt(damage,reason="shocked")
                self.container.addAnimation(target.getPosition(),"smoke",10,{})

                if character:
                    character.addMessage("an enemy is getting shocked")

        return "you trigger the shock tower"

    def configure(self, character):
        """

        Parameters:
            character: the character trying to use the item
        """

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

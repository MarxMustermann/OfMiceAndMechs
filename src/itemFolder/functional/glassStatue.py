import src
import random


class GlassStatue(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "GlassStatue"
    description = "Used to pray to the gods."
    name = "glassStatue"

    def __init__(self,itemID=None):
        '''
        set up internal state
        '''
        super().__init__("GG")

        self.applyOptions.extend(
                        [
                                                                ("showInfo", "show Info"),
                                                                ("pray", "pray"),
                                                                ("getSetHeart", "remove/set glass heart"),
                                                                ("teleport", "teleport to dungeon"),
                        ]
                        )
        self.applyMap = {
                    "showInfo": self.showInfo,
                    "pray": self.pray,
                    "teleport": self.teleport,
                    "getSetHeart": self.getSetHeart,
                        }
        self.itemID = itemID
        self.challenges = []
        self.hasItem = False
        self.charges = 2
        self.stable = False
        self.numSubSacrifices = 0
        self.numTeleportsDone = 0

    def handleItemRequirements(self,removeItems=False,character=None):
        # determine what items are needed
        if self.itemID == None:
            return
        needItems = src.gamestate.gamestate.gods[self.itemID]["sacrifice"]
        completed = False

        # handle the item requirements
        if needItems:
            itemType = needItems[0]
            amount = needItems[1]-self.numSubSacrifices

            if itemType == "Scrap":
                ##
                # handle scrap special case

                # find scrap to take as saccrifice
                numScrapFound = 0
                scrap = self.container.getItemsByType("Scrap")
                for item in scrap:
                    numScrapFound += item.amount

                # ensure that there is enough scrap around
                if not numScrapFound:
                    if character:
                        text = "no Scrap to offer\n\nPlace the Scrap to offer on the floor of this room."
                        submenue = src.menuFolder.textMenu.TextMenu(text)
                        character.macroState["submenue"] = submenue
                        character.addMessage(text)
                    return

                # remove the scrap
                numScrapRemoved = 0
                if removeItems:
                    for item in scrap:
                        if item.amount <= amount-numScrapRemoved:
                            self.container.removeItem(item)
                            numScrapRemoved += item.amount
                            self.numSubSacrifices += item.amount
                        else:
                            item.amount -= amount-numScrapRemoved
                            item.setWalkable()
                            numScrapRemoved += amount-numScrapRemoved
                            self.numSubSacrifices += amount-numScrapRemoved

                        if numScrapRemoved >= amount:
                            completed = True
                            break
                text = f"you sacrifice {numScrapRemoved}/{amount} Scrap"
            else:
                ##
                # handle normal items

                # get the items
                itemsFound = self.container.getItemsByType(itemType,needsUnbolted=True)

                # ensure item requirement can be fullfilled
                if not len(itemsFound):
                    if character:
                        text = f"you need to offer {itemType}.\n\nPlace the offered items on the floor of this room."
                        submenue = src.menuFolder.textMenu.TextMenu(text)
                        character.macroState["submenue"] = submenue
                        character.addMessage(text)
                    return

                if len(itemsFound) >= amount:
                    completed = True

                # remove items from requirement
                text = f"you sacrifice {min(amount,len(itemsFound))}/{amount} {itemType}"
                if removeItems:
                    while amount > 0 and itemsFound:
                        self.container.removeItem(itemsFound.pop())
                        amount -= 1
                        self.numSubSacrifices += 1
        return (completed,text)

    def pray(self,character):
        character.changed("prayed",{})

        if self.charges >= 9:
            text = f"the glass statue has maximum charges now"
            submenue = src.menuFolder.textMenu.TextMenu(text)
            character.macroState["submenue"] = submenue
            character.addMessage(text)
            return

        result = self.handleItemRequirements(removeItems=True,character=character)
        if not result:
            return
        text = result[1]
        completed = result[0]

        if completed:
            self.charges += 1
            self.numSubSacrifices = 0
            text += f"\n\nThe GlassStatue has {self.charges} charges now."
            if self.charges == 5:
                text += f"\nYou can use the GlassStatue to teleport to the dungeon now."
        else:
            text += f"\n\nyour saccrifice was not enough for another charge"


        submenue = src.menuFolder.textMenu.TextMenu(text)
        character.macroState["submenue"] = submenue
        character.addMessage(text)

    def render(self):
        color = "#888"
        if self.itemID == 1:
            color = "#f00"
        elif self.itemID == 2:
            color = "#0f0"
        elif self.itemID == 3:
            color = "#00f"
        elif self.itemID == 4:
            color = "#0ff"
        elif self.itemID == 5:
            color = "#f0f"
        elif self.itemID == 6:
            color = "#ff0"
        elif self.itemID == 7:
            color = "#fff"
        displaychars = "GG"

        if not self.hasItem:
            # search for glass hearts in the players inventory
            if self.charges < 5:
                displaychars = f"G{self.charges}"
            else:
                displaychars = "GG"

            mainCharHasItem = False
            for item in src.gamestate.gamestate.mainChar.inventory:
                if not item.type == "SpecialItem":
                    continue
                if not item.itemID == self.itemID:
                    continue
                displaychars = "kk"
                break
        else:
            displaychars = "KK"

        display = [
                (src.interaction.urwid.AttrSpec(color, "black"), displaychars),
            ]
        return display

    def handleEpochChange(self):
        if self.stable:
            return
        if not self.container:
            return

        self.charges -= 1
        if self.charges == 0:
            self.destroy()
            return

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(15*15*15-src.gamestate.gamestate.tick%(15*15*15))+10)
        event.setCallback({"container": self, "method": "handleEpochChange"})
        self.container.addEvent(event)


    def teleport(self,character):
        if self.charges < 5:
            character.addMessage(f"not enough charges ({self.charges}/5)")
            return
        character.addMessage(str(src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"]))

        (x,y) = src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"]
        newTerrain = src.gamestate.gamestate.terrainMap[y][x]

        candidates = []
        for x in range(1,14):
            for y in range(1,14):
                if newTerrain.getRoomByPosition((x,y,0)):
                    continue
                candidates.append((x,y,0))
        bigPos = random.choice(candidates)

        character.container.removeCharacter(character)
        newTerrain.addCharacter(character,15*bigPos[0]+13,15*bigPos[1]+7)

        self.charges -= 1
        self.numTeleportsDone += 1

        character.changed("glass statue used",{})
        character.changed("changedTerrain",{"character":character})

    def showInfo(self,character):
        character.addMessage(f"mana: {self.getTerrain().mana}\ncharges: {self.charges}")

        if self.itemID:
            character.addMessage(str(src.gamestate.gamestate.gods[self.itemID]))
        else:
            character.addMessage(str(src.gamestate.gamestate.gods))

        if self.itemID == 1:
            character.addMessage("this god can spawn NPCs")
        if self.itemID == 2:
            character.addMessage("this god can spawn ressources")
        if self.itemID == 3:
            character.addMessage("this god can improve your weapon")
        if self.itemID == 4:
            character.addMessage("this god can improve your attack speed")
        if self.itemID == 5:
            character.addMessage("this god can improve your armor")
        if self.itemID == 6:
            character.addMessage("this god can improve your max health")
        if self.itemID == 7:
            character.addMessage("this god can improve your base damage")

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
            if not self.hasItem:
                options["g"] = ("set glass heart", self.setGlassHeart)
            else:
                options["g"] = ("remove glass heart", self.removeGlassHeart)
                options["r"] = ("release glass heart", self.releaseGlassHeart)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def getSetHeart(self,character):
        if self.hasItem:
            self.removeGlassHeart(character)
        else:
            self.setGlassHeart(character)
            self.stable = True

    def releaseGlassHeart(self,character):
        if self.hasItem:
            src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"] = src.gamestate.gamestate.gods[self.itemID]["home"]
            print(src.gamestate.gamestate.gods[self.itemID])
            self.hasItem = False

    def removeGlassHeart(self,character):
        newItem = src.items.itemMap["SpecialItem"](epoch=src.gamestate.gamestate.tick//(15*15*15))
        newItem.itemID = self.itemID
        if not character.getFreeInventorySpace() > 0:
            self.container.addItem(newItem,character.getPosition())
        else:
            character.inventory.append(newItem)
        self.hasItem = False

    def setGlassHeart(self,character):
        self.getTerrain().mana += 10

        glassHeart = None
        hasHeart = False
        for item in character.inventory:
            #if not item.type == "GlassHeart":
            if item.type != "SpecialItem":
                continue
            if item.itemID != self.itemID:
                continue
            glassHeart = item
            hasHeart = True

        if not hasHeart:
            character.addMessage("you have no glass heart to set")
            return

        if not glassHeart:
            character.addMessage("you do not have the right glass heart to set")
            return

        if glassHeart.epoch < src.gamestate.gamestate.tick//(15*15*15):
            character.addMessage("the heart stpped beating and shatters. Transer the heart faster next time.")
            character.inventory.remove(glassHeart)
            return

        self.hasItem = True
        character.inventory.remove(glassHeart)
        src.gamestate.gamestate.gods[self.itemID]["lastHeartPos"] = (character.getTerrain().xPosition,character.getTerrain().yPosition)
        character.changed("deliveredSpecialItem",{"itemID":self.itemID})

        submenue = src.menuFolder.textMenu.TextMenu("""
You insert the GlassHeart into the GlassStatue and make it whole.

The GlassHeart scream and its agony takes physical form.

A wave of enemies is approaching to steal the GlassHeart.
""")
        character.macroState["submenue"] = submenue

        src.magic.spawnWaves()

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the Statue")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the Statue")
        character.changed("unboltedItem",{"character":character,"item":self})

    def getLongInfo(self):
        if not self.itemID:
            return f"""no god set"""
        godName = src.gamestate.gamestate.gods[self.itemID]["name"]
        sacrifice = src.gamestate.gamestate.gods[self.itemID]["sacrifice"]
        return f"""This is a GlassStatue of the god {godName}
It currenty has {self.charges} charges.
It currenty has {self.numSubSacrifices}/{sacrifice[1]} sub charges.
Offer {sacrifice[0]} and pray.

Offer items by praying at the statue to stabilise it.
If the statue is not stabilised for too long, then it will break.
Currently the GlassStatue will break in {self.charges} epochs.

You can stabilize the GlassStatue fully, by setting its heart.
You can get the statues heart from the GlassHeart dungeon.
Use this GlassStatue to teleport there.

Teleporting to the dungeon requires 5 charges and consumes one charge.
Currently the GlassStatue has {self.charges} charges.
This GlassStatue was used teleported {self.numTeleportsDone} times.
"""

src.items.addType(GlassStatue)

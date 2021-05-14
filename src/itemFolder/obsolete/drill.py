import src

"""
"""


class Drill(src.items.Item):
    type = "Drill"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):

        self.coolDown = 100
        self.coolDownTimer = -self.coolDown
        self.isBroken = False
        self.isCleaned = True

        super().__init__(display=src.canvas.displayChars.drill)
        self.name = "drill"
        self.baseName = self.name

        self.attributesToStore.extend(
            ["coolDown", "coolDownTimer", "isBroken", "isCleaned"]
        )

        self.setDescription()

    def setDescription(self):
        addition = ""
        if self.isBroken:
            addition = " (broken)"
        self.description = self.baseName + addition

    def setToProduce(self, toProduce):
        self.setDescription()

    """
    trigger production of a player selected item
    """

    def apply(self, character):
        super().apply(character, silent=True)

        if not self.xPosition:
            character.addMessage("this machine has to be placed to be used")
            return

        if self.room:
            character.addMessage("this machine can not be used in rooms")
            return

        if self.isBroken:
            if not self.isCleaned:

                targetFull = False
                scrapFound = None
                if (
                    self.xPosition,
                    self.yPosition + 1,
                ) in self.terrain.itemByCoordinates:
                    if (
                        len(
                            self.terrain.itemByCoordinates[
                                (self.xPosition, self.yPosition + 1)
                            ]
                        )
                        > 15
                    ):
                        targetFull = True
                    for item in self.terrain.itemByCoordinates[
                        (self.xPosition, self.yPosition + 1)
                    ]:
                        if item.walkable == False:
                            targetFull = True
                        if item.type == "Scrap":
                            scrapFound = item

                if targetFull:
                    character.addMessage(
                        "the target area is full, the machine does not produce anything"
                    )
                    return

                character.addMessage("you remove the broken rod")

                if scrapFound:
                    item.amount += 1
                else:
                    # spawn new item
                    new = itemMap["Scrap"](
                        self.xPosition, self.yPosition, 1, creator=self
                    )
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition + 1
                    new.bolted = False

                    self.terrain.addItems([new])

                self.isCleaned = True

            else:

                character.addMessage("you repair the machine")

                rod = None
                if (
                    self.xPosition - 1,
                    self.yPosition,
                ) in self.terrain.itemByCoordinates:
                    for item in self.terrain.itemByCoordinates[
                        (self.xPosition - 1, self.yPosition)
                    ]:
                        if isinstance(item, Rod):
                            rod = item
                            break

                # refuse production without resources
                if not rod:
                    character.addMessage("needs repairs Rod -> repaired")
                    character.addMessage("no rod available")
                    return

                # remove resources
                self.terrain.removeItem(item)

                self.isBroken = False

            self.setDescription()
            return

        if src.gamestate.gamestate.tick < self.coolDownTimer + self.coolDown:
            character.addMessage(
                "cooldown not reached. Wait %s ticks"
                % (self.coolDown - (src.gamestate.gamestate.tick - self.coolDownTimer),)
            )
            return
        self.coolDownTimer = src.gamestate.gamestate.tick

        # spawn new item
        possibleProducts = [
            src.items.itemMap["Scrap"],
            src.items.itemMap["Coal"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Radiator"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Mount"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Sheet"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Rod"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Bolt"],
            src.items.itemMap["Scrap"],
            src.items.itemMap["Stripe"],
            src.items.itemMap["Scrap"],
        ]
        productIndex = src.gamestate.gamestate.tick % len(possibleProducts)
        new = possibleProducts[productIndex](
            self.xPosition, self.yPosition, creator=self
        )
        new.xPosition = self.xPosition + 1
        new.yPosition = self.yPosition
        new.bolted = False

        foundScrap = None
        targetFull = False
        if (self.xPosition + 1, self.yPosition) in self.terrain.itemByCoordinates:
            if (
                len(
                    self.terrain.itemByCoordinates[(self.xPosition + 1, self.yPosition)]
                )
                > 15
            ):
                targetFull = True
            for item in self.terrain.itemByCoordinates[
                (self.xPosition + 1, self.yPosition)
            ]:
                if item.walkable == False:
                    targetFull = True
                if item.type == "Scrap":
                    foundScrap = item

        if targetFull:
            character.addMessage(
                "the target area is full, the machine does not produce anything"
            )
            return

        if new.type == "Scrap" and foundScrap:
            foundScrap.amount += new.amount
        else:
            self.terrain.addItems([new])

        self.isBroken = True
        self.isCleaned = False

        self.setDescription()

    """
    set state from dict
    """

    def setState(self, state):
        super().setState(state)

        self.setDescription()

    def getLongInfo(self):
        text = """
This drills items from the ground. You get different things from time to time.

Activate the drill to drill something up. Most likely you will dig up scrap.

After the every use the rod in the drill will break.
You need to replace the rod in the drill to repair it.
Use the drill to eject the broken rod from the drill.
place a rod to the left/west of the drill and activate the drill, to repair it

"""
        return text


src.items.addType(Drill)

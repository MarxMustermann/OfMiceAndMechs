import src
import random


class EncrustedBush(src.items.Item):
    type = "EncrustedBush"

    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display=src.canvas.displayChars.encrustedBush)
        self.name = "encrusted bush"
        self.description = "This is a cluster of blooms. The veins developed a protecive shell and are dense enough to form a solid wall"

        self.walkable = False

    def destroy(self, generateScrap=True):
        """
        destroy this item

        Parameters:
            generateScrap: flag to toggle leaving residue
        """

        new = src.items.itemMap["Coal"]()
        self.container.addItem(new,self.getPosition())

        character = src.characters.Monster()

        character.solvers = [
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "NaiveMurderQuest",
            "NaiveDropQuest",
        ]

        character.faction = "monster"

        character.macroState["macros"]["w"] = list("wj")
        character.macroState["macros"]["a"] = list("aj")
        character.macroState["macros"]["s"] = list("sj")
        character.macroState["macros"]["d"] = list("dj")

        counter = 1
        command = ""
        directions = ["w", "a", "s", "d"]
        while counter < 8:
            command += "j%s_%sk" % (
                random.randint(1, counter * 4),
                directions[random.randint(0, 3)],
            )
            counter += 1
        character.macroState["macros"]["m"] = list(command + "_m")

        character.macroState["commandKeyQueue"] = [("_", []), ("m", [])]
        character.satiation = 10
        self.container.addCharacter(character, self.xPosition, self.yPosition)

        super().destroy(generateScrap=False)

    def tryToGrowRoom(self, spawnPoint):
        """
        try to evolve the neighbouring plants into a room

        Parameters:
            spawnPoint: the plant that is the core of the room
        """
        
        if not self.container:
            return

        upperLeftEdge = [self.xPosition, self.yPosition]
        sizeX = 1
        sizeY = 1

        growBlock = None

        continueExpanding = True
        while continueExpanding:
            continueExpanding = False

            # expand west
            if upperLeftEdge[0] % 15 > 0:
                rowOk = True
                for y in range(0, sizeY):
                    items = self.container.getItemByPosition(
                        (upperLeftEdge[0] - 1, upperLeftEdge[1] + y,0)
                    )
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeX += 1
                    upperLeftEdge[0] -= 1
                    continueExpanding = True

            # expand north
            if upperLeftEdge[1] % 15 > 0:
                rowOk = True
                for x in range(0, sizeX):
                    items = self.container.getItemByPosition(
                        (upperLeftEdge[0] + x, upperLeftEdge[1] - 1,0)
                    )
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeY += 1
                    upperLeftEdge[1] -= 1
                    continueExpanding = True

            # expand south
            if upperLeftEdge[1] % 15 + sizeY < 14:
                rowOk = True
                for x in range(0, sizeX):
                    items = self.container.getItemByPosition(
                        (upperLeftEdge[0] + x, upperLeftEdge[1] + sizeY,0)
                    )
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeY += 1
                    continueExpanding = True

            # expand east
            if upperLeftEdge[0] % 15 + sizeX < 14:
                rowOk = True
                for y in range(0, sizeY):
                    items = self.container.getItemByPosition(
                        (upperLeftEdge[0] + sizeX, upperLeftEdge[1] + y,0)
                    )
                    if not (len(items) > 0 and items[0].type == "EncrustedBush"):
                        if items and items[0].type == "Bush":
                            growBlock = items[0]
                        rowOk = False
                if rowOk:
                    sizeX += 1
                    continueExpanding = True

        if sizeX < 3 or sizeY < 3:
            if growBlock:
                new = src.items.itemMap["EncrustedBush"]()
                self.container.addItem(new,growBlock.getPosition())
                growBlock.container.removeItem(growBlock)
            return

        keepItems = []
        doorPos = ()
        for x in range(0, sizeX):
            for y in range(0, sizeY):
                if x == 0 or y == 0 or x == sizeX - 1 or y == sizeY - 1:
                    if x == 0 and y == 1:
                        item = src.items.itemMap["Door"](bio=True)
                    else:
                        items = self.container.getItemByPosition(
                            (upperLeftEdge[0] + x, upperLeftEdge[1] + y,0)
                        )
                        if not items:
                            return
                        item = items[0]
                        item.container.removeItem(item)
                    keepItems.append((item,(x,y,0)))

        room = src.rooms.EmptyRoom(
            upperLeftEdge[0] // 15,
            upperLeftEdge[1] // 15,
            upperLeftEdge[0] % 15,
            upperLeftEdge[1] % 15,
            bio=True,
        )
        self.terrain.addRooms([room])
        room.reconfigure(sizeX, sizeY, keepItems)

src.items.addType(EncrustedBush)

import src


class RipInReality(src.items.Item):
    type = "RipInReality"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.ripInReality)
        self.name = "rip in reality"
        self.target = None
        self.targetPos = None

        self.walkable = True
        self.bolted = True
        self.depth = 1
        self.lastUse = 0
        self.stable = False
        self.submenu = None
        self.killInventory = False
        self.storedItems = []

    def render(self):
        if self.stable:
            return "|#"
        else:
            return self.display

    def apply(self, character):
        self.container.removeCharacter(character)
        character.staggered += 1
        character.addMessage("the reality shift staggers you")

        if (
            not self.stable
            and src.gamestate.gamestate.tick - self.lastUse > 100 * self.depth
        ):
            self.target = None
            self.targetPos = None
        if not self.target:
            import random

            character.addMessage("you enter the rip in reality")

            if self.depth == 1:
                self.stable = True
                self.killInventory = True

                startPosition = (5, 5)

                newRoom = src.rooms.StaticRoom(creator=self, depth=self.depth + 1)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition, self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True
                backRip.killInventory = True

                newRoom.reconfigure(11, 11)
                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItems([backRip])

                newRoom.addItems([src.items.itemMap["SaccrificialCircle"](5, 4)])

                newRoom.addItems([src.items.itemMap["SparcRewardLock"](5, 6)])

                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                positions = [
                    (2, 2),
                    (2, 4),
                    (2, 6),
                    (2, 8),
                    (8, 2),
                    (8, 4),
                    (8, 6),
                    (8, 8),
                    (4, 2),
                    (6, 2),
                    (4, 8),
                    (6, 8),
                ]

                for position in positions:
                    if random.randint(1, 2) == 1:
                        rip = RipInReality(creator=self)
                        rip.xPosition = position[0]
                        rip.yPosition = position[1]
                        rip.depth = 2
                        newRoom.addItems([rip])
                    else:
                        plug = SparkPlug(creator=self)
                        plug.xPosition = position[0]
                        plug.yPosition = position[1]
                        plug.strength = 2
                        newRoom.addItems([plug])

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 2:
                startPosition = (5, 5)

                newRoom = src.rooms.StaticRoom(creator=self, depth=self.depth + 1)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition, self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True

                newRoom.reconfigure(9, 9)

                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItems([backRip])
                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                numMice = random.randint(1, 5)
                for i in range(0, numMice):
                    enemy = src.characters.Mouse()
                    enemy.frustration = 100000
                    enemy.aggro = 20
                    if i % 2 == 1:
                        enemy.runCommandString("ope$=aa$=dd$=ss$=wwmm30.m100.")
                    newRoom.addCharacter(
                        enemy, random.randint(1, 8), random.randint(1, 8)
                    )

                rewardItem = None
                if random.randint(1, 15) == 1:
                    rewardItem = src.items.itemMap["Rod"](
                        random.randint(1, 8), random.randint(1, 8)
                    )
                elif random.randint(1, 15) == 1:
                    rewardItem = src.items.itemMap["Vial"](
                        random.randint(1, 8), random.randint(1, 8)
                    )
                    rewardItem.uses = 1
                elif random.randint(1, 15) == 1:
                    rewardItem = src.items.itemMap["Armor"](
                        random.randint(1, 8), random.randint(1, 8)
                    )
                if rewardItem:
                    newRoom.addItems([rewardItem])

                self.target = newRoom
                self.targetPos = startPosition

            elif random.randint(1, 5) == 5 and 1 == 0:
                sizeX = random.randint(4, 13)
                sizeY = random.randint(4, 13)

                startPosition = (
                    random.randint(1, sizeX - 2),
                    random.randint(1, sizeY - 2),
                )

                # generate solvable captcha room
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition, self.yPosition)
                backRip.xPosition = random.randint(1, sizeX - 2)
                backRip.yPosition = random.randint(1, sizeY - 2)
                backRip.stable = True

                newRoom.reconfigure(sizeX, sizeY)
                newRoom = src.rooms.StaticRoom(creator=self, depth=self.depth + 1)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([backRip])
                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 10:
                sizeX = 5
                sizeY = 5
                startPosition = (1, 1)
                crystal = StaticCrystal(creator=self)
                crystal.xPosition = 3
                crystal.yPosition = 3

                newRoom.reconfigure(sizeX, sizeY)
                newRoom = src.rooms.StaticRoom(creator=self, depth=self.depth + 1)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([crystal])
                newRoom.addCharacter(character, 1, 1)
            else:
                sizeX = random.randint(5, 13)
                sizeY = random.randint(5, 13)

                startPosition = (
                    random.randint(1, sizeX - 2),
                    random.randint(1, sizeY - 2),
                )

                # generate maybe solvable riddle room
                newRoom = src.rooms.StaticRoom(creator=self, depth=self.depth + 1)
                # newRoom.reconfigure(self,sizeX=3,sizeY=3,items=[],bio=False)
                backRip = RipInReality(creator=self)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition, self.yPosition)
                backRip.xPosition = startPosition[0]
                backRip.yPosition = startPosition[1]
                backRip.stable = True
                backRip.depth = self.depth + 1

                newRoom.reconfigure(sizeX, sizeY)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItems([backRip])

                for i in range(1, self.depth):
                    wall = StaticMover(creator=self)
                    newPos = (
                        random.randint(0, sizeX - 1),
                        random.randint(0, sizeY - 1),
                    )
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    wall.xPosition = newPos[0]
                    wall.yPosition = newPos[1]
                    wall.energy = self.depth * 2
                    newRoom.addItems([wall])

                while not random.randint(1, 3) == 3:
                    if random.randint(1, 2) == 1:
                        if random.randint(1, 2) == 1:
                            spark = StaticSpark(creator=self)
                            spark.strength = self.depth
                            spark.name = "static spark %s" % (spark.strength)
                        else:
                            spark = SparkPlug(creator=self)
                            spark.strength = self.depth + 1
                            spark.name = "spark plug %s" % (spark.strength)
                    else:
                        spark = RipInReality(creator=self)
                        spark.depth = self.depth + 1
                        spark.name = "rip in reality %s" % (spark.depth)

                    sparkPos = None
                    counter = 0
                    while (
                        not sparkPos
                        or sparkPos == startPosition
                        or newRoom.getItemByPosition(sparkPos)
                    ):
                        sparkPos = (
                            random.randint(1, sizeX - 2),
                            random.randint(1, sizeY - 2),
                        )
                    spark.xPosition = sparkPos[0]
                    spark.yPosition = sparkPos[1]
                    newRoom.addItems([spark])

                    while not random.randint(1, self.depth + 1) == 1:
                        wall = StaticWall(creator=self)
                        wall.strength = self.depth + 2
                        newPos = (
                            random.randint(0, sizeX - 1),
                            random.randint(0, sizeY - 1),
                        )
                        if newPos == startPosition or newRoom.getItemByPosition(newPos):
                            continue
                        wall.xPosition = newPos[0]
                        wall.yPosition = newPos[1]
                        newRoom.addItems([wall])

                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                self.target = newRoom
                self.targetPos = startPosition

                while not random.randint(1, self.depth + 5) == 1:
                    wall = StaticWall(creator=self)
                    wall.strength = self.depth + 2
                    newPos = (
                        random.randint(0, sizeX - 1),
                        random.randint(0, sizeY - 1),
                    )
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    wall.xPosition = newPos[0]
                    wall.yPosition = newPos[1]
                    newRoom.addItems([wall])
        else:
            self.target.addCharacter(character, self.targetPos[0], self.targetPos[1])

        if self.killInventory:
            character.inventory = []

        self.lastUse = src.gamestate.gamestate.tick

    def configure(self, character):
        options = [("destabilize", "destabilize"), ("stablize", "stablize")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    def apply2(self):
        staticSpark = None
        for item in self.character.inventory:
            if isinstance(item, StaticSpark) and item.strength >= self.depth:
                if not staticSpark or staticSpark.strength > item.strength:
                    staticSpark = item

        if not staticSpark:
            self.submenue = None
            self.character.addMessage("no suitable static spark")
            return

        self.character.inventory.remove(staticSpark)

        if self.submenue.selection == "destabilize":
            if self.stable:
                self.stable = False
                self.character.addMessage("Rip in reality not stable anymore")
            else:
                self.target = None
                self.targetPos = None
                self.character.addMessage("Rip in reality destabilized")
        elif self.submenue.selection == "stablize":
            self.stable = True
            self.character.addMessage("Rip in reality was stabilized")
        self.submenue = None

    def getLongInfo(self):
        return """
item: RipInReality

description:
You can enter it

depth:
%s

stable:
%s

%s
%s
""" % (
            self.depth,
            self.stable,
            self.target,
            self.targetPos,
        )


src.items.addType(RipInReality)

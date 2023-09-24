import src


class RipInReality(src.items.Item):
    """
    ingame item that teleports the character to a dungeon or within a dungeon
    """

    type = "RipInReality"

    def __init__(self,rootRip=None,treasure=None):
        """
        configuration of the superclass
        """
        
        super().__init__(display=src.canvas.displayChars.ripInReality)
        self.name = "rip in reality"
        self.description = "You can enter it"
        self.target = None
        self.targetPos = None

        if not rootRip == None:
            self.rootRip = rootRip
            self.treasureRoom = None
        else:
            self.rootRip = self

            newRoom = src.rooms.StaticRoom(depth=7)
            newRoom.reconfigure(7, 7)
            for item in newRoom.itemsOnFloor[:]:
                newRoom.removeItem(item)

            crystal = src.items.itemMap["StaticCrystal"]()
            newRoom.addItem(crystal,(3,3,0))
            self.treasureRoom = newRoom
            self.treasure = treasure

        self.walkable = True
        self.bolted = True
        self.depth = 1
        self.lastUse = 0
        self.stable = False
        self.submenu = None
        self.killInventory = False
        self.storedItems = []

    def render(self):
        """
        render the rip depending on whether or not it is stable
        """

        if self.stable:
            return "|#"
        else:
            return self.display

    def apply(self, character):
        """
        teleport a character using the rip
        if not teleport target exists the rip will create a new room

        Parameters:
            character: the character using the rip
        """

        self.container.removeCharacter(character)

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

                startPosition = (5, 5, 0)

                newRoom = src.rooms.StaticRoom(depth=self.depth + 1)
                backRip = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                backRip.target = self.container
                backRip.targetPos = self.getPosition()
                backRip.stable = True
                backRip.killInventory = True

                newRoom.reconfigure(11, 11)
                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItem(backRip,startPosition)

                newRoom.addItem(src.items.itemMap["SaccrificialCircle"](),(5, 4, 0))

                lock = src.items.itemMap["SparcRewardLock"](treasure=self.treasure)
                newRoom.addItem(lock,(5, 6, 0))

                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                positions = [
                    (2, 2, 0),
                    (2, 4, 0),
                    (2, 6, 0),
                    (2, 8, 0),
                    (8, 2, 0),
                    (8, 4, 0),
                    (8, 6, 0),
                    (8, 8, 0),
                    (4, 2, 0),
                    (6, 2, 0),
                    (4, 8, 0),
                    (6, 8, 0),
                ]

                for position in positions:
                    if random.randint(1, 2) == 1:
                        rip = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                        rip.xPosition = position[0]
                        rip.yPosition = position[1]
                        rip.depth = 2
                        newRoom.addItem(rip,position)
                    else:
                        plug = src.items.itemMap["SparkPlug"]()
                        plug.xPosition = position[0]
                        plug.yPosition = position[1]
                        plug.strength = 2
                        newRoom.addItem(plug,position)

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 2 and 1==0:
                startPosition = (5, 5, 0)

                newRoom = src.rooms.StaticRoom(depth=self.depth + 1)
                backRip = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                backRip.target = self.container
                backRip.targetPos = self.getPosition()
                backRip.stable = True

                newRoom.reconfigure(9, 9)

                toRemove = []
                for items in newRoom.itemByCoordinates.values():
                    toRemove.extend(items)
                newRoom.removeItems(toRemove)

                newRoom.addItem(backRip,startPosition)
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
                    rewardItem = src.items.itemMap["Rod"]()
                elif random.randint(1, 15) == 1:
                    rewardItem = src.items.itemMap["Vial"]()
                    rewardItem.uses = 1
                elif random.randint(1, 15) == 1:
                    rewardItem = src.items.itemMap["Armor"]()
                if rewardItem:
                    newRoom.addItem(rewardItem,(random.randint(1, 8), random.randint(1, 8),0))

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
                backRip = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                backRip.target = self.container
                backRip.targetPos = self.getPosition()
                backRip.stable = True

                self.target = newRoom
                self.targetPos = startPosition
            elif self.depth == 7:
                backRip = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                backRip.target = self.container
                backRip.targetPos = self.getPosition()
                backRip.stable = True

                newRoom = self.rootRip.treasureRoom

                newRoom.addCharacter(character, 1, 1)
                newRoom.addItem(backRip, (1, 1, 0))
            else:
                sizeX = random.randint(5, 13)
                sizeY = random.randint(5, 13)

                startPosition = (
                    random.randint(1, sizeX - 2),
                    random.randint(1, sizeY - 2),
                    0
                )

                # generate maybe solvable riddle room
                newRoom = src.rooms.StaticRoom(depth=self.depth + 1)
                # newRoom.reconfigure(self,sizeX=3,sizeY=3,items=[],bio=False)
                backRip = RipInReality(rootRip=self.rootRip)
                backRip.target = self.container
                backRip.targetPos = (self.xPosition, self.yPosition)
                backRip.stable = True
                backRip.depth = self.depth + 1

                newRoom.reconfigure(sizeX, sizeY)
                for item in newRoom.itemsOnFloor[:]:
                    newRoom.removeItem(item)

                newRoom.addItem(backRip,startPosition)

                for i in range(1, self.depth):
                    wall = src.items.itemMap["StaticMover"]()
                    newPos = (
                        random.randint(0, sizeX - 1),
                        random.randint(0, sizeY - 1),
                        0
                    )
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    wall.energy = self.depth * 2
                    newRoom.addItem(wall,newPos)

                while not random.randint(1, 4) == 3:
                    if random.random() > 0.3:
                        if random.random() > 0.3:
                            spark = src.items.itemMap["StaticSpark"]()
                            spark.strength = self.depth
                            spark.name = "static spark %s" % (spark.strength)
                        else:
                            spark = src.items.itemMap["SparkPlug"]()
                            spark.strength = self.depth + 1
                            spark.name = "spark plug %s" % (spark.strength)
                    else:
                        spark = src.items.itemMap["RipInReality"](rootRip=self.rootRip)
                        spark.depth = self.depth + 1
                        spark.name = "rip in reality %s" % (spark.depth)

                    sparkPos = None
                    counter = 0
                    while (
                        not sparkPos
                        or sparkPos == startPosition
                        or newRoom.getItemByPosition(sparkPos)
                    ):
                        if counter > 10:
                            break
                        counter += 1
                        sparkPos = (
                            random.randint(1, sizeX - 2),
                            random.randint(1, sizeY - 2),
                            0,
                        )

                    if sparkPos:
                        newRoom.addItem(spark,sparkPos)

                    while not random.randint(1, self.depth + 1) == 1:
                        wall = src.items.itemMap["StaticWall"]()
                        wall.strength = self.depth + 2
                        newPos = (
                            random.randint(0, sizeX - 1),
                            random.randint(0, sizeY - 1),
                            0,
                        )
                        if newPos == startPosition or newRoom.getItemByPosition(newPos):
                            continue
                        newRoom.addItem(wall,newPos)

                newRoom.addCharacter(character, startPosition[0], startPosition[1])

                self.target = newRoom
                self.targetPos = startPosition

                while not random.randint(1, self.depth) == 1:
                    wall = src.items.itemMap["StaticWall"]()
                    wall.strength = self.depth + 2
                    newPos = (
                        random.randint(0, sizeX - 1),
                        random.randint(0, sizeY - 1),
                        0,
                    )
                    if newPos == startPosition or newRoom.getItemByPosition(newPos):
                        continue
                    newRoom.addItem(wall,newPos)
        else:
            self.target.addCharacter(character, self.targetPos[0], self.targetPos[1])

        if self.killInventory:
            keepItems = []
            if self.depth == 1:
                for item in character.inventory:
                    if item in self.rootRip.treasure:
                        keepItems.append(item)
            if keepItems:
                self.rootRip.destroy()
                character.addMessage("the rip in reality collapses")
            character.inventory = keepItems

        self.lastUse = src.gamestate.gamestate.tick

    # abstraction: should use superclass functionality
    def configure(self, character):
        """
        offer a selection a actions to a character and set the trigger to run them

        Parameters:
                character: the character the selection is offered to
        """
        
        options = [("destabilize", "destabilize"), ("stablize", "stablize")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.apply2
        self.character = character

    # bad code: should be splitted
    def apply2(self):
        """
        run a selected action from a list of actions
        """

        staticSpark = None
        for item in self.character.inventory:
            if isinstance(item, src.items.itemMap["StaticSpark"]) and item.strength >= self.depth:
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
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()

        text += f"""

depth:
{self.depth}

stable:
{self.stable}

{self.target}
{self.targetPos}
"""
        
        return text

src.items.addType(RipInReality)

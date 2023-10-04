import random

import src


class CommandBloom(src.items.Item):
    """
    ingame item taking control over the characters
    """

    type = "CommandBloom"
    walkable = True
    bolted = True
    charges = 0
    numCoal = 0
    numSick = 0
    numCommandBlooms = 0
    lastFeeding = 0
    masterCommand = None
    expectedNext = 0
    blocked = False
    cluttered = False
    lastExplosion = 0

    def __init__(self):
        """
        ingame item that takes control over npcs
        a plant reprogramming npc to expand and farm the mold
        """

        super().__init__(display=src.canvas.displayChars.commandBloom)
        self.name = "command bloom"

        self.faction = ""
        for _i in range(5):
            char = random.choice("abcdefghijklmopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.faction += char

    def apply(self, character):
        """
        handle a character trying to use the item
        by reprogramming the the character

        Parameters:
            character: the character trying to use the item
        """

        selfDestroy = False

        if not self.xPosition:
            return
        if not self.container:
            return

        items = self.container.getItemByPosition(
            (
                self.xPosition - self.xPosition % 15 + 7,
                self.yPosition - self.yPosition % 15 + 7,
                self.zPosition,
            )
        )
        centralBloom = None
        if items and (
            items[0].type == "CommandBloom" or items[-1].type == "CommandBloom"
        ):
            centralBloom = items[0]

        if (
            len(
                self.container.getItemByPosition(
                    (self.xPosition, self.yPosition, self.zPosition)
                )
            )
            > 1
        ):
            selfDestroy = True

        if self.xPosition % 15 == 1 and self.yPosition % 15 == 7:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6d9kj"
        elif self.xPosition % 15 == 13 and self.yPosition % 15 == 7:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6a9kj"
        elif self.xPosition % 15 == 7 and self.yPosition % 15 == 13:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6w9kj"
        elif self.xPosition % 15 == 7 and self.yPosition % 15 == 1:
            if not centralBloom or self.masterCommand:
                selfDestroy = True
            command = "6s9kj"
        elif self.xPosition % 15 == 7 and self.yPosition % 15 == 7:
            command = None

            removeItems = []
            index = 0
            for item in character.inventory:
                if item.type == "Bloom":
                    removeItems.append(item)
                    self.charges += 1
                elif self.numSick < 5 and item.type == "SickBloom":
                    removeItems.append(item)
                    self.numSick += 1
                elif self.numCoal < 5 and item.type == "Coal":
                    removeItems.append(item)
                    self.numCoal += 1
                elif item.type == "HiveMind":
                    while self.charges and character.satiation < 900:
                        character.satiation += 100
                        self.charges -= 1

                    if (
                        self.xPosition // 15 == 7 or self.yPosition // 15 == 7
                    ):  # place hive mind
                        self.bolted = False
                        command = "kil" + index * "s" + "jj"
                    elif self.masterCommand:  # follow network
                        command = self.masterCommand
                    else:  # wait for hive mind to develop
                        command = "gg"*100

                elif item.type == "CommandBloom":
                    if (
                        "PATHx" in character.registers
                        and len(character.registers["PATHx"]) > 10
                        and random.randint(1, 10) == 1
                    ):
                        numIncluded = 0
                        for i in range(1, len(character.registers["PATHx"])):
                            if (
                                character.registers["PATHx"][i] == self.xPosition // 15
                                and character.registers["PATHy"][i]
                                == self.yPosition // 15
                            ):
                                numIncluded += 1
                                if numIncluded > 2:
                                    break
                        if numIncluded > 2:
                            self.masterCommand = None
                    if self.masterCommand:
                        command = self.masterCommand
                        if "PATHx" in character.registers:
                            character.registers["PATHx"].append(self.xPosition // 15)
                            character.registers["PATHy"].append(self.yPosition // 15)
                            character.registers["NUM COAL"].append(self.numCoal)
                            character.registers["NUM SICK"].append(self.numSick)
                            character.registers["BLOCKED"].append(self.blocked)
                            character.registers["CLUTTERED"].append(self.cluttered)
                    else:
                        removeItems.append(item)
                        self.numCommandBlooms += 1
                        command = "j"

                    if self.numCommandBlooms > 2:
                        new = src.items.itemMap["HiveMind"]()
                        pos = self.getPosition()
                        container = self.container
                        new.createdAt = src.gamestate.gamestate.tick
                        new.territory.append((pos[0] // 15, pos[1] // 15))
                        new.paths[(pos[0] // 15, pos[1] // 15)] = []
                        new.faction = self.faction
                        self.container.removeItem(self)
                        container.addItem(new,pos)
                index += 1
            for item in removeItems:
                character.inventory.remove(item)

            self.beganCluttered = True
            if len(character.inventory) > 7 and not command:
                if not self.numSick:
                    self.cluttered = True
                if self.masterCommand and self.numSick:
                    command = self.masterCommand
                    if self.numSick:
                        items = []
                        for _i in range(2):
                            items.append(character.inventory.pop())
                        crawler = self.runCommandOnNewCrawler("j",character.faction)
                        crawler.inventory.extend(items)
                else:
                    command = random.choice(["W", "A", "S", "D"])

            if (
                character.inventory
                and character.inventory[-1].type == "Coal"
                and hasattr(character, "phase")
                and character.phase == 1
            ) and self.numSick > 4:
                command = "wal20jsdj"
                self.runCommandOnNewCrawler("j",character.faction)

            if isinstance(character, src.characters.Exploder):
                if self.blocked:
                    foundItem = None
                    length = 1
                    pos = [self.xPosition, self.yPosition]
                    path = []
                    path.append((pos[0], pos[1]))
                    while length < 13:
                        if length % 2 == 1:
                            for _i in range(length):
                                pos[1] -= 1
                                path.append((pos[0], pos[1]))
                            for _i in range(length):
                                pos[0] -= 1
                                path.append((pos[0], pos[1]))
                        else:
                            for _i in range(length):
                                pos[1] += 1
                                path.append((pos[0], pos[1]))
                            for _i in range(length):
                                pos[0] += 1
                                path.append((pos[0], pos[1]))
                        length += 1
                    for _i in range(length - 1):
                        pos[1] -= 1
                        path.append((pos[0], pos[1]))

                    targets = []
                    for pos in path:
                        items = self.container.getItemByPosition((pos[0],pos[1],0))
                        if (
                            items
                            and (items[0].bolted or not items[0].walkable)
                            and not items[0].type
                            in (
                                "Scrap",
                                "Mold",
                                "Bush",
                                "Sprout",
                                "Sprout2",
                                "CommandBloom",
                                "PoisonBloom",
                                "Corpse",
                            )
                        ):
                            if (
                                items[0].xPosition % 15 == 7
                                and items[0].yPosition % 15 == 7
                            ):
                                continue
                            targets.append(items[0])

                    if targets:
                        if random.random() < 0.5:
                            foundItem = random.choice(targets)
                        else:
                            foundItem = targets[0]

                    if not foundItem:
                        directions = []
                        if self.xPosition // 15 != 0:
                            directions.append("a")
                            if self.xPosition // 15 > 7:
                                directions.append("a")
                        if self.xPosition // 15 != 14:
                            directions.append("d")
                            if self.xPosition // 15 < 7:
                                directions.append("d")
                        if self.yPosition // 15 != 0:
                            directions.append("w")
                            if self.yPosition // 15 > 7:
                                directions.append("w")
                        if self.yPosition // 15 != 14:
                            directions.append("s")
                            if self.yPosition // 15 > 7:
                                directions.append("s")
                        command = "13" + random.choice(directions) + "9kkj"
                        self.blocked = False
                    else:
                        command = ""
                        if foundItem.yPosition and self.yPosition > foundItem.yPosition:
                            command += str(self.yPosition - foundItem.yPosition) + "w"
                        if self.xPosition > foundItem.xPosition:
                            command += str(self.xPosition - foundItem.xPosition) + "a"
                        if self.yPosition < foundItem.yPosition:
                            command += str(foundItem.yPosition - self.yPosition) + "s"
                        if self.xPosition < foundItem.xPosition:
                            command += str(foundItem.xPosition - self.xPosition) + "d"
                        character.explode = True
                        command += "2000."
                else:
                    while self.charges and character.satiation < 900:
                        self.charges -= 1
                        character.satiation += 100

                    if self.masterCommand and random.randint(1, 3) == 1:
                        command = self.masterCommand
                    else:
                        directions = []
                        if self.xPosition // 15 != 0:
                            directions.append("a")
                            if self.xPosition // 15 > 7:
                                directions.append("a")
                        if self.xPosition // 15 != 14:
                            directions.append("d")
                            if self.xPosition // 15 < 7:
                                directions.append("d")
                        if self.yPosition // 15 != 0:
                            directions.append("w")
                            if self.yPosition // 15 > 7:
                                directions.append("w")
                        if self.yPosition // 15 != 14:
                            directions.append("s")
                            if self.yPosition // 15 > 7:
                                directions.append("s")
                        command = "13" + random.choice(directions) + "9kkj"

            if (
                not command
                and self.expectedNext
                and self.expectedNext > src.gamestate.gamestate.tick
                and not self.cluttered
            ):
                if self.masterCommand and random.randint(1, 3) != 1:
                    command = self.masterCommand
                else:
                    command = 13 * random.choice(["w", "a", "s", "d"]) + "9kkj"

            if self.charges < 1 and not command:
                command = ""
                length = 1
                pos = [self.xPosition, self.yPosition]
                path = []
                path.append((pos[0], pos[1]))

                bloomsSkipped = 0

                while length < 13:
                    if length % 2 == 1:
                        for _i in range(length):
                            pos[1] -= 1
                            path.append((pos[0], pos[1], 0))
                        for _i in range(length):
                            pos[0] -= 1
                            path.append((pos[0], pos[1], 0))
                    else:
                        for _i in range(length):
                            pos[1] += 1
                            path.append((pos[0], pos[1], 0))
                        for _i in range(length):
                            pos[0] += 1
                            path.append((pos[0], pos[1], 0))
                    length += 1
                for _i in range(length - 1):
                    pos[1] -= 1
                    path.append((pos[0], pos[1], 0))

                if character.satiation < 300 and self.charges:
                    if src.gamestate.gamestate.tick - self.lastFeeding < 60:
                        if self.charges < 15:
                            direction = random.choice(["w", "a", "s", "d"])
                            command += 10 * (13 * direction + "j")
                        else:
                            command = ""
                            direction = random.choice(["w", "a", "s", "d"])
                            command += 10 * (
                                13 * direction + "opx$=aa$=ww$=ss$=ddwjajsjsjdjdjwjwjas"
                            )
                    else:
                        while character.satiation < 500 and self.charges:
                            character.satiation += 100
                            self.charges -= 1
                        self.lastFeeding = src.gamestate.gamestate.tick

                foundSomething = False
                lastCharacterPosition = path[0]
                explode = False
                lastpos = None
                count = 0
                for pos in path[1:]:
                    count += 1
                    items = self.container.getItemByPosition(pos)
                    if not items:
                        continue
                    elif items[0].type in ("CommandBloom",):
                        continue
                    elif items[0].type in ("Mold", "Sprout2") and not (
                        items[0].xPosition % 15 == 7
                        or items[0].yPosition % 15 == 7
                        or (items[0].xPosition % 15, items[0].yPosition % 15)
                        in ((6, 6), (6, 8), (8, 6), (8, 8))
                    ):
                        continue
                    elif items[0].type in (
                        "Sprout",
                        "SickBloom",
                        "Bloom",
                        "FireCrystals",
                        "Coal",
                        "Mold",
                        "Sprout2",
                    ):
                        if items[0].type == "Mold" and (pos[0] % 15, pos[1] % 15) in (
                            (1, 7),
                            (7, 1),
                            (7, 13),
                            (13, 7),
                        ):
                            continue
                        if items[0].type == "Sprout" and (pos[0] % 15, pos[1] % 15) in (
                            (1, 7),
                            (7, 1),
                            (7, 13),
                            (13, 7),
                        ):
                            continue
                        if (
                            not bloomsSkipped > 1
                            and (pos[0] % 15 != 7 and pos[1] % 15 != 7)
                            and items[0].type == "Bloom"
                            and self.masterCommand
                            and self.charges > 5
                        ):
                            bloomsSkipped += 1
                            continue
                        if (
                            not bloomsSkipped > 1
                            and (pos[0] % 15 != 7 and pos[1] % 15 != 7)
                            and items[0].type == "SickBloom"
                            and self.masterCommand
                            and self.numSick > 4
                        ):
                            bloomsSkipped += 1
                            continue
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1] - pos[1]) + "w"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0] - pos[0]) + "a"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1] - lastCharacterPosition[1]) + "s"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0] - lastCharacterPosition[0]) + "d"

                        foundSomething = True

                        if items[0].type in ("Coal"):
                            east = self.container.getItemByPosition(
                                (pos[0] + 1, pos[1], 0)
                            )
                            west = self.container.getItemByPosition(
                                (pos[0] - 1, pos[1], 0)
                            )
                            south = self.container.getItemByPosition(
                                (pos[0], pos[1] + 1, 0)
                            )
                            north = self.container.getItemByPosition(
                                (pos[0], pos[1] - 1, 0)
                            )
                            if (
                                (
                                    west
                                    and west[0].type
                                    in (
                                        "EncrustedBush",
                                        "PoisonBush",
                                        "EncrustedPoisonBush",
                                    )
                                )
                                or (
                                    east
                                    and east[0].type
                                    in (
                                        "EncrustedBush",
                                        "PoisonBush",
                                        "EncrustedPoisonBush",
                                    )
                                )
                                or (
                                    north
                                    and north[0].type
                                    in (
                                        "EncrustedBush",
                                        "PoisonBush",
                                        "EncrustedPoisonBush",
                                    )
                                )
                                or (
                                    south
                                    and south[0].type
                                    in (
                                        "EncrustedBush",
                                        "PoisonBush",
                                        "EncrustedPoisonBush",
                                    )
                                )
                                or (
                                    west
                                    and (not west[0].walkable or west[0].bolted)
                                    and not west[0].type
                                    in (
                                        "Scrap",
                                        "PoisonBloom",
                                        "Mold",
                                        "Sprout",
                                        "Sprout2",
                                        "Bloom",
                                        "SickBloom",
                                    )
                                )
                                or (
                                    east
                                    and (not east[0].walkable or east[0].bolted)
                                    and not east[0].type
                                    in (
                                        "Scrap",
                                        "PoisonBloom",
                                        "Mold",
                                        "Sprout",
                                        "Sprout2",
                                        "Bloom",
                                        "SickBloom",
                                    )
                                )
                                or (
                                    north
                                    and (not north[0].walkable or north[0].bolted)
                                    and not north[0].type
                                    in (
                                        "Scrap",
                                        "PoisonBloom",
                                        "Mold",
                                        "Sprout",
                                        "Sprout2",
                                        "Bloom",
                                        "SickBloom",
                                    )
                                )
                                or (
                                    south
                                    and (not south[0].walkable or south[0].bolted)
                                    and not south[0].type
                                    in (
                                        "Scrap",
                                        "PoisonBloom",
                                        "Mold",
                                        "Sprout",
                                        "Sprout2",
                                        "Bloom",
                                        "SickBloom",
                                    )
                                )
                            ):
                                if not self.numSick:
                                    self.lastExplosion = src.gamestate.gamestate.tick
                                    if (
                                        hasattr(character, "phase")
                                        and character.phase == 1
                                    ):
                                        if lastCharacterPosition[1] > pos[1]:
                                            command += "JwJwJwJwJw"
                                        if lastCharacterPosition[0] > pos[0]:
                                            command += "JaJaJaJaJa"
                                        if lastCharacterPosition[1] < pos[1]:
                                            command += "JsJsJsJsJs"
                                        if lastCharacterPosition[0] < pos[0]:
                                            command += "JdJdJdJdJd"
                                        command += "20j2000."
                                        explode = True
                                        break
                                    else:
                                        continue
                                else:
                                    newCommand = ""
                                    direction = (
                                        items[-1].xPosition - self.xPosition,
                                        items[-1].yPosition - self.yPosition,
                                    )
                                    if direction[1] < 0:
                                        newCommand += str(-direction[1]) + "wJwJwJwJw"
                                    if direction[0] < 0:
                                        newCommand += str(-direction[0]) + "aJaJaJaJa"
                                    if direction[1] > 0:
                                        newCommand += str(direction[1]) + "sJsJsJsJs"
                                    if direction[0] > 0:
                                        newCommand += str(direction[0]) + "dJdJdJdJd"
                                    newCommand += "20j2000."
                                    self.runCommandOnNewCrawler(newCommand,character.faction)
                                    break

                        lastCharacterPosition = pos

                        if items[0].type in ("Bloom", "SickBloom", "Coal"):
                            command += "k"
                        else:
                            command += "j"
                    elif items[0].type in ("Bush"):
                        foundSomething = True
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1] - pos[1]) + "w"
                            lastDirection = "w"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0] - pos[0]) + "a"
                            lastDirection = "a"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1] - lastCharacterPosition[1]) + "s"
                            lastDirection = "s"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0] - lastCharacterPosition[0]) + "d"
                            lastDirection = "d"
                        command += "j"
                        for _i in range(11):
                            command += "J" + lastDirection
                        command += lastDirection
                        lastCharacterPosition = pos
                        break

                    elif (not items[0].walkable or items[0].bolted) and not items[
                        0
                    ].type in (
                        "Scrap",
                        "PoisonBloom",
                        "Corpse",
                    ):
                        self.blocked = True

                        if (
                            not self.numCoal
                            or not self.numSick
                            or src.gamestate.gamestate.tick - self.lastExplosion < 1000
                        ):
                            break

                        self.lastExplosion = src.gamestate.gamestate.tick

                        lowestIndex = None
                        for pos in (
                            (items[0].xPosition - 1, items[0].yPosition),
                            (items[0].xPosition + 1, items[0].yPosition),
                            (items[0].xPosition, items[0].yPosition + 1),
                            (items[0].xPosition, items[0].yPosition + 1),
                        ):
                            if pos not in path:
                                continue
                            if lowestIndex is None or path.index(pos) < lowestIndex:
                                lowestIndex = path.index(pos)
                        if lowestIndex is None:
                            break
                        targetPos = path[lowestIndex]

                        newCommand = ""
                        direction = (
                            targetPos[0] - self.xPosition,
                            targetPos[1] - self.yPosition,
                        )
                        if direction[1] < 0:
                            newCommand += str(-direction[1]) + "w"
                        if direction[0] < 0:
                            newCommand += str(-direction[0]) + "a"
                        if direction[1] > 0:
                            newCommand += str(direction[1]) + "s"
                        if direction[0] > 0:
                            newCommand += str(direction[0]) + "d"
                        newCommand += "l20j2000."
                        newChar = self.runCommandOnNewCrawler(newCommand,character.faction)
                        newChar.inventory.append(src.items.itemMap["Coal"]())
                        self.numCoal -= 1
                        break
                    else:
                        foundSomething = True
                        if lastCharacterPosition[1] > pos[1]:
                            command += str(lastCharacterPosition[1] - pos[1]) + "wk"
                        if lastCharacterPosition[0] > pos[0]:
                            command += str(lastCharacterPosition[0] - pos[0]) + "ak"
                        if lastCharacterPosition[1] < pos[1]:
                            command += str(pos[1] - lastCharacterPosition[1]) + "sk"
                        if lastCharacterPosition[0] < pos[0]:
                            command += str(pos[0] - lastCharacterPosition[0]) + "dk"
                        command += "k"
                        break

                if not explode:
                    if self.cluttered:
                        command += "opx$=aa$=ww$=ss$=dd"
                        direction = random.choice(["a", "w", "s", "d"])
                        reverseDirection = {"w": "s", "s": "w", "a": "d", "d": "a"}
                        command += (
                            6 * (direction + "k")
                            + "opx$="
                            + 2 * (reverseDirection[direction])
                        )

                    pos = (self.xPosition, self.yPosition)
                    if lastCharacterPosition[1] > pos[1]:
                        command += str(lastCharacterPosition[1] - pos[1]) + "w"
                    if lastCharacterPosition[0] > pos[0]:
                        command += str(lastCharacterPosition[0] - pos[0]) + "a"
                    if lastCharacterPosition[1] < pos[1]:
                        command += str(pos[1] - lastCharacterPosition[1]) + "s"
                    if lastCharacterPosition[0] < pos[0]:
                        command += str(pos[0] - lastCharacterPosition[0]) + "d"

                    command += "opx$=aa$=ww$=ss$=ddk"
                    if foundSomething:
                        command += "j"
                    if not foundSomething:
                        if character.satiation > 100:
                            command += (
                                "gg"*(min(
                                        character.satiation - 30,
                                        random.randint(100, 200),
                                    )//10)
                                + "j"
                            )
                        else:
                            command = random.choice(["W", "A", "S", "D"])

                    self.expectedNext = src.gamestate.gamestate.tick + len(command) - 25

                if count == 168:
                    self.cluttered = False

            elif not command:
                command = ""
                new = CommandBloom()

                directions = []
                if self.xPosition // 15 != 0:
                    directions.append("a")
                    if self.xPosition // 15 > 7:
                        directions.append("a")
                        if self.yPosition // 15 == 7:
                            directions.append("a")
                            directions.append("a")
                            directions.append("a")
                if self.xPosition // 15 != 14:
                    directions.append("d")
                    if self.xPosition // 15 < 7:
                        directions.append("d")
                        if self.xPosition // 15 == 7:
                            directions.append("d")
                            directions.append("d")
                            directions.append("d")
                if self.yPosition // 15 != 0:
                    directions.append("w")
                    if self.yPosition // 15 > 7:
                        directions.append("w")
                        if self.xPosition // 15 == 7:
                            directions.append("w")
                            directions.append("w")
                            directions.append("w")
                if self.yPosition // 15 != 14:
                    directions.append("s")
                    if self.yPosition // 15 > 7:
                        directions.append("s")
                        if self.yPosition // 15 == 7:
                            directions.append("s")
                            directions.append("s")
                            directions.append("s")
                direction = random.choice(directions)
                reversedDirection = {"w": "s", "s": "w", "a": "d", "d": "a"}
                command += 13 * direction + "9kkjjjilj.j"
                new.masterCommand = 13 * reversedDirection[direction] + "9kj"
                new.faction = self.faction

                walker = character
                walker.inventory.insert(0, new)
                walker.registers["SOURCEx"] = [self.xPosition // 15]
                walker.registers["SOURCEy"] = [self.yPosition // 15]
                walker.registers["PATHx"] = [self.xPosition // 15]
                walker.registers["PATHy"] = [self.yPosition // 15]
                walker.registers["NUM COAL"] = [self.numCoal]
                walker.registers["NUM SICK"] = [self.numSick]
                walker.registers["BLOCKED"] = [self.blocked]
                walker.registers["CLUTTERED"] = [self.beganCluttered]

                if self.numSick:
                    self.runCommandOnNewCrawler("j",character.faction)

                if "NaiveDropQuest" not in walker.solvers:
                    walker.solvers.append("NaiveDropQuest")

                self.charges -= 1

                while walker.satiation < 900 and self.charges:
                    walker.satiation += 100
                    self.charges -= 1
        else:
            selfDestroy = True

        if selfDestroy:
            new = src.items.itemMap["FireCrystals"]()
            self.container.addItem(new,self.getPosition())
            self.container.removeItem(self)
            direction = random.choice(["w", "a", "s", "d"])
            reverseDirection = {"a": "d", "w": "s", "d": "a", "s": "w"}
            command = (
                "j"
                + 3 * direction
                + "40."
                + 3 * reverseDirection[direction]
                + "KaKwKsKd"
            )
            for _i in range(1, 10):
                direction = random.choice(["w", "a", "s", "d"])
                command += direction + "k"

        character.runCommandString(command)

    def runCommandOnNewCrawler(self, newCommand, faction):
        """
        create a new npc and run a command on it

        Parameters:
            newCommand: the command to run on the new crawler
        """

        if not self.numSick:
            return None
        newCharacter = src.characters.Monster()

        newCharacter.solvers = [
            "NaiveActivateQuest",
            "NaiveExamineQuest",
            "ExamineQuestMeta",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "NaiveMurderQuest",
            "NaiveDropQuest",
        ]

        newCharacter.faction = faction
        newCharacter.satiation = 100

        newCharacter.runCommandString(command, clear=True)

        newCharacter.xPosition = self.xPosition
        newCharacter.yPosition = self.yPosition
        self.container.addCharacter(newCharacter, self.xPosition, self.yPosition)

        self.numSick -= 1

        return newCharacter

    def getLongInfo(self):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""

charges: {self.charges}
numCoal: {self.numCoal}
numSick: {self.numSick}
masterCommand: {self.masterCommand}
numCommandBlooms: {self.numCommandBlooms}
blocked: {self.blocked}
cluttered: {self.cluttered}
faction: {self.faction}
"""

src.items.addType(CommandBloom)

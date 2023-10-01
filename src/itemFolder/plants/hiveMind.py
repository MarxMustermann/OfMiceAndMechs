import src
import random

# NIY: not implemented yet
class HiveMind(src.items.Item):
    """
    ingame item that is intended to be a thinking node of a mold civilisation
    """

    type = "HiveMind"
    name = "command bloom"
    createdAt = 0
    walkable = True
    bolted = True
    lastMoldClear = 0
    charges = 0
    lastBlocked = (7, 7)
    lastCluttered = (7, 7)
    lastExpansion = None
    colonizeIndex = 0

    def __init__(self):
        """
        set up initial state
        """

        self.territory = []
        self.paths = {}
        super().__init__(display=src.canvas.displayChars.floor_node)
        self.toCheck = []
        self.cluttered = []
        self.blocked = []
        self.needSick = []
        self.needCoal = []

        self.faction = ""
        for i in range(5):
            char = random.choice("abcdefghijklmopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.faction += char

    def apply(self, character):
        """
        handle a character trying to use this item
        by using it to expand the mold

        Parameters:
            character: the character trying to use this item
        """

        if not self.xPosition:
            character.addMessage("this needs to be placed to be used")
            return
        command = None
        done = False
        selfDestroy = False

        if (self.xPosition % 15, self.yPosition % 15) != (7, 7):
            selfDestroy = True

        # get the path from the creature
        path = []
        pos = None
        while "PATHx" in character.registers:
            if not character.registers["PATHx"]:
                del character.registers["PATHx"]
                del character.registers["PATHy"]
                del character.registers["CLUTTERED"]
                del character.registers["BLOCKED"]
                del character.registers["NUM SICK"]
                del character.registers["NUM COAL"]
                break

            pos = (
                character.registers["PATHx"].pop(),
                character.registers["PATHy"].pop(),
            )

            if character.registers["CLUTTERED"].pop() and pos not in self.cluttered:
                self.cluttered.append(pos)
            if character.registers["BLOCKED"].pop() and pos not in self.blocked:
                self.blocked.append(pos)
            if character.registers["NUM SICK"].pop() < 4 and pos not in self.needSick:
                self.needSick.append(pos)
            if character.registers["NUM COAL"].pop() < 4 and pos not in self.needCoal:
                self.needCoal.append(pos)

            path.append(pos)
            if pos not in self.territory:
                self.territory.append(pos)
                self.toCheck.append(pos)
                self.lastExpansion = src.gamestate.gamestate.tick
        if pos:
            self.paths[pos] = path

        if not self.bolted:
            self.bolted = True
            self.paths = {(self.xPosition // 15, self.yPosition // 15): []}
            self.lastExpansion = None
            if (self.xPosition // 15, self.yPosition // 15) not in self.territory:
                self.territory.append((self.xPosition // 15, self.yPosition // 15))

        broughtBloom = False
        for item in character.inventory[:]:
            if item.type == "CommandBloom":
                self.charges += 1
                character.inventory.remove(item)
                broughtBloom = True
            if item.type == "HiveMind":
                self.charges += item.charges
                character.inventory.remove(item)

        if character.inventory and character.inventory[-1].type == "Scrap":
            character.inventory.pop()
            character.inventory.append(src.items.itemMap["Coal"]())

        numItems = 0
        for item in reversed(character.inventory):
            if (not item.walkable) and item.type in (
                "SickBloom",
                "Bloom",
                "Coal",
                "CommandBloom",
                "Corpse",
            ):
                break

        if self.lastExpansion is None:
            self.lastExpansion = src.gamestate.gamestate.tick
        selfReplace = False
        if (src.gamestate.gamestate.tick - self.lastExpansion) > len(
            self.territory
        ) * 1000:
            if self.xPosition // 15 == 7 and self.yPosition // 15 == 7:
                self.lastExpansion = None
            else:
                selfReplace = True

        if selfReplace:
            new = src.items.itemMap["CommandBloom"]()
            new.faction = self.faction

            directions = []
            if self.xPosition // 15 > 7:
                directions.append("a")
            if self.yPosition // 15 > 7:
                directions.append("w")
            if self.xPosition // 15 < 7:
                directions.append("d")
            if self.yPosition // 15 < 7:
                directions.append("s")
            direction = random.choice(directions)
            new.masterCommand = "13" + direction + "9kkj"

            character.inventory.append(new)

            self.bolted = False
            command = "kilwwj.13" + direction + "lj"

        elif (
            hasattr(character, "phase")
            and character.phase == 1
            and character.inventory
            and character.inventory[-1].type == "Coal"
        ):
            command = "l20j"
        elif (
            hasattr(character, "phase")
            and character.phase == 2
            and character.inventory
            and character.inventory[-1].type == "SickBloom"
        ):
            command = "ljj"
        elif isinstance(character, src.characters.Exploder):

            if self.territory:
                command = ""

                if self.blocked:
                    target = self.blocked.pop()
                    self.lastBlocked = target
                    if target not in self.toCheck:
                        self.toCheck.append(target)
                elif random.randint(1, 2) == 1:
                    target = self.lastBlocked
                else:
                    target = random.choice(self.territory)

                (movementCommand, lastNode) = self.calculateMovementUsingPaths(target)
                if movementCommand:
                    command += movementCommand

                command += 13 * (random.choice(["w", "a", "s", "d"]) + "k") + "kkj"
            else:
                command = random.choice(["W", "A", "S", "D"])

        elif (
            src.gamestate.gamestate.tick - self.lastMoldClear > 1000
        ):  # clear tile from mold
            command = (
                6 * "wjjkkk"
                + "opx$=ss"
                + 6 * "sjjkkk"
                + "opx$=ww"
                + 6 * "ajjkkk"
                + "opx$=dd"
                + 6 * "djjkkk"
                + "opx$=aaj"
            )
            self.lastMoldClear = src.gamestate.gamestate.tick
            done = True
        elif not self.charges and self.territory:  # send creature somewhere
            command = ""

            supplyRun = False
            if (
                character.inventory
                and self.needCoal
                and character.inventory[-1].type == "Coal"
            ):
                target = self.needCoal.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
                supplyRun = True
            elif (
                character.inventory
                and self.needSick
                and character.inventory[-1].type == "SickBloom"
            ):
                target = self.needSick.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
                supplyRun = True
            elif self.cluttered:
                target = self.cluttered.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
                self.lastCluttered = target
                supplyRun = True
            elif random.randint(1, 2) == 1:
                target = self.lastCluttered
            else:
                target = random.choice(self.territory)

            (movementCommand, lastNode) = self.calculateMovementUsingPaths(target)
            if movementCommand:
                command += movementCommand

            if command == "":
                command = random.choice(["W", "A", "S", "D"])

            choice = random.randint(1, 2)
            if choice == 1 or supplyRun:
                command += "kkj"
            else:
                extraCommand = ""
                for i in range(2):
                    direction = random.choice(["w", "a", "s", "d"])
                    extraCommand += 13 * (direction + "k")

                command += "kk" + 20 * extraCommand

        elif self.territory and (
            len(self.territory) < 10 or (broughtBloom and random.randint(0, 1) == 1)
        ):  # expand the territory
            command = ""
            anchor = random.choice(self.territory)

            if len(self.territory) < 10:
                targetPos = random.choice([self.territory[0], [7, 7]])
                while targetPos in self.territory:
                    targetPos = [random.randint(1, 12), random.randint(1, 12)]
            elif random.randint(1, 2) and (self.xPosition // 15, self.yPosition // 15) != (7, 7):
                targetPos = [7, 7]
                anchor = (self.xPosition // 15, self.yPosition // 15)
            else:
                length = 1
                pos = [7, 7]
                index = 0
                while length < 13:
                    if length % 2 == 1:
                        for i in range(length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[1] -= 1
                        for i in range(length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[0] += 1
                    else:
                        for i in range(length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[1] += 1
                        for i in range(length):
                            if index == self.colonizeIndex:
                                break
                            index += 1
                            pos[0] -= 1
                    length += 1
                for i in range(length - 1):
                    if index == self.colonizeIndex:
                        break
                    index += 1
                    pos[1] -= 1

                self.colonizeIndex += 1
                if self.colonizeIndex == 169:
                    self.colonizeIndex = 0
                targetPos = pos

            if (self.xPosition // 15, self.yPosition // 15) == (7, 7):
                anchor = (7, 7)

            if anchor not in self.territory or anchor not in self.paths:
                anchor = (self.xPosition // 15, self.yPosition // 15)

                if anchor not in self.territory or anchor not in self.paths:
                    return

            character.addMessage(str(anchor) + " -> " + str(targetPos))

            neighbourPos = targetPos[:]
            while not (
                tuple(neighbourPos) in self.territory
                and tuple(neighbourPos) in self.paths
            ):
                index = random.randint(0, 1)
                targetPos = neighbourPos[:]
                if neighbourPos[index] - anchor[index] > 0:
                    neighbourPos[index] -= 1
                elif neighbourPos[index] - anchor[index] < 0:
                    neighbourPos[index] += 1
            character.addMessage(f"{neighbourPos} => {targetPos}")

            (movementCommand, lastNode) = self.calculateMovementUsingPaths(
                tuple(neighbourPos)
            )
            if movementCommand:
                command += movementCommand

            new = src.items.itemMap["CommandBloom"]()
            self.charges -= 1
            new.faction = self.faction

            character.inventory.insert(0, new)
            character.registers["PATHx"] = []
            character.registers["PATHy"] = []
            character.registers["NUM COAL"] = []
            character.registers["NUM SICK"] = []
            character.registers["BLOCKED"] = []
            character.registers["CLUTTERED"] = []
            if targetPos[0] > neighbourPos[0]:
                command += 13 * "dk"
                new.masterCommand = 13 * "a" + "9kj"
            if targetPos[0] < neighbourPos[0]:
                command += 13 * "ak"
                new.masterCommand = 13 * "d" + "9kj"
            if targetPos[1] > neighbourPos[1]:
                command += 13 * "sk"
                new.masterCommand = 13 * "w" + "9kj"
            if targetPos[1] < neighbourPos[1]:
                command += 13 * "wk"
                new.masterCommand = 13 * "s" + "9kj"
            command += "9kjjjilj.j"

            if self.charges > 10:
                new2 = src.items.itemMap["CommandBloom"]()
                new2.masterCommand = new.masterCommand
                new2.faction = self.faction
                character.inventory.append(new2)
                self.charges -= 1
            character.addMessage(command)
        elif (
            (not broughtBloom and self.charges < 20) or random.randint(0, 1) == 1
        ) and self.territory:  # move the character somewhere to help/supply
            command = ""

            if (
                character.inventory
                and self.needCoal
                and character.inventory[-1].type == "Coal"
            ):
                target = self.needCoal.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
            elif (
                character.inventory
                and self.needSick
                and character.inventory[-1].type == "SickBloom"
            ):
                target = self.needSick.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
            elif self.cluttered:
                target = self.cluttered.pop()
                if target not in self.toCheck:
                    self.toCheck.append(target)
                self.lastCluttered = target
            elif random.randint(1, 2) == 1:
                target = self.lastCluttered
            else:
                target = random.choice(self.territory)

            (movementCommand, lastNode) = self.calculateMovementUsingPaths(target)
            command += movementCommand

            if command == "":
                command = random.choice(["W", "A", "S", "D"])
            command += "kkj"
        elif self.territory:
            command = self.doHealthCheckLazy(character)

        else:  # stand around, look confused
            command = "wwaassdd100.j"

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
            for i in range(1, 10):
                direction = random.choice(["w", "a", "s", "d"])
                command += direction + "k"

        character.runCommandString(command)

    def doHealthCheckLazy(self, character):
        """
        check if the territory is still complete and working

        Parameters:
            character: the character that can be used to do the action
        """

        if not self.toCheck:
            self.toCheck = self.territory[:]

        target = (self.xPosition // 15, self.yPosition // 15)
        while self.toCheck and (
            target == (self.xPosition // 15, self.yPosition // 15)
            or target not in self.paths
        ):
            target = self.toCheck.pop()

        if target == (self.xPosition // 15, self.yPosition // 15):
            command = "wwaassdd100.j"
        else:
            command = self.doHealthCheck(character, target)
        return command

    def doHealthCheck(self, character, target):
        """
        check if a specific par of the territory is still complete and working

        Parameters:
            character: the character that can be used to do the action
            target: the part of the territory to check
        """

        character.addMessage(target)
        (movementCommand, secondToLastNode) = self.calculateMovementUsingPaths(target)
        command = movementCommand

        new = src.items.itemMap["CommandBloom"]()
        character.inventory.insert(0, new)
        self.charges -= 1
        command += "9kjjjilj.lj"
        new.faction = self.faction

        direction = ""
        if not secondToLastNode:
            command = random.choice(["A", "W", "S", "D"])
        else:
            if target[1] == secondToLastNode[1]:
                if target[0] == secondToLastNode[0] - 1:
                    direction = "d"
                if target[0] == secondToLastNode[0] + 1:
                    direction = "a"
            elif target[0] == secondToLastNode[0]:
                if target[1] == secondToLastNode[1] - 1:
                    direction = "s"
                if target[1] == secondToLastNode[1] + 1:
                    direction = "w"

        character.addMessage(command)
        new.masterCommand = 13 * direction + "9kj"
        return command

    def calculateMovementUsingPaths(self, target):
        """
        get the movement to a specific point on the terrain
        """

        if target not in self.paths:
            return ("", None)

        command = ""
        path = self.paths[target]

        lastNode = (self.xPosition // 15, self.yPosition // 15)
        secondToLastNode = None
        targetNodeDone = False
        for node in path + [target]:
            if node[0] - lastNode[0] > 0:
                command += str(13 * (node[0] - lastNode[0])) + "d"
            if lastNode[0] - node[0] > 0:
                command += str(13 * (lastNode[0] - node[0])) + "a"
            if node[1] - lastNode[1] > 0:
                command += str(13 * (node[1] - lastNode[1])) + "s"
            if lastNode[1] - node[1] > 0:
                command += str(13 * (lastNode[1] - node[1])) + "w"
            secondToLastNode = lastNode
            lastNode = node
            if targetNodeDone:
                break
            if node == target:
                targetNodeDone = True

        return (command, secondToLastNode)

    def getLongInfo(self):
        """
        get a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo()
        text += f"""
charges: {self.charges}
createdAt: {self.createdAt}
territory: {self.territory}
len(territory): {len(self.territory)}
lastMoldClear: {self.lastMoldClear}
blocked: {self.blocked}
lastBlocked: {self.lastBlocked}
lastCluttered: {self.lastCluttered}
lastExpansion: {self.lastExpansion}
cluttered: {self.cluttered}
needCoal: {self.needCoal}
needSick: {self.needSick}
len(needSick): {len(self.needSick)}
toCheck: {self.toCheck}
len(toCheck): {len(self.toCheck)}
colonizeIndex: {self.colonizeIndex}
faction: {self.faction}
paths:
"""

        for path, value in self.paths.items():
            text += f" * {path} - {value}\n"
        return text

src.items.addType(HiveMind)

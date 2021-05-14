import src


class AutoFarmer(src.items.Item):
    """
    helper item to allow the player to harvest blooms without coding too much
    """

    type = "AutoFarmer"

    def __init__(self):
        """
        simple configuration of superclass
        """
        super().__init__()
        self.display = src.canvas.displayChars.autoFarmer
        self.name = "auto farmer"
        self.walkable = True
        self.bolted = True

    def apply(self, character):
        """
        use the autofarmer to gather nearby blooms

        Parameters:
            character: the character using the item
        """

        if not self.terrain:
            character.addMessage("the auto farmer cannot be used within rooms")
            return

        if not (self.xPosition % 15 == 7 and self.yPosition % 15 == 7):
            character.addMessage(
                "the auto farmer needs to be placed in the middle of a tile"
            )
            return

        if not self.bolted:
            character.addMessage(
                "the auto farmer digs into the ground and is now ready for use"
            )
            self.bolted = True

        if isinstance(character, src.characters.Monster):
            character.die()
            return

        if len(character.inventory) > 9:
            character.addMessage("inventory full")
            return

        command = ""
        length = 1
        pos = [self.xPosition, self.yPosition]
        path = []
        path.append((pos[0], pos[1]))
        while length < 13:
            if length % 2 == 1:
                for i in range(0, length):
                    pos[1] -= 1
                    path.append((pos[0], pos[1]))
                for i in range(0, length):
                    pos[0] += 1
                    path.append((pos[0], pos[1]))
            else:
                for i in range(0, length):
                    pos[1] += 1
                    path.append((pos[0], pos[1]))
                for i in range(0, length):
                    pos[0] -= 1
                    path.append((pos[0], pos[1]))
            length += 1
        for i in range(0, length - 1):
            pos[1] -= 1
            path.append((pos[0], pos[1]))

        foundSomething = False
        lastCharacterPosition = path[0]
        for pos in path[1:]:
            items = self.container.getItemByPosition(pos)
            if not items:
                continue
            item = items[0]
            if item.type in ("Bloom", "SickBloom", "Coal"):
                if lastCharacterPosition[0] > pos[0]:
                    command += str(lastCharacterPosition[0] - pos[0]) + "a"
                if lastCharacterPosition[0] < pos[0]:
                    command += str(pos[0] - lastCharacterPosition[0]) + "d"
                if lastCharacterPosition[1] > pos[1]:
                    command += str(lastCharacterPosition[1] - pos[1]) + "w"
                if lastCharacterPosition[1] < pos[1]:
                    command += str(pos[1] - lastCharacterPosition[1]) + "s"

                if items[0].type in ("Sprout", "Sprout2", "Mold"):
                    command += "j"
                if items[0].type == "Bloom":
                    command += "k"
                if items[0].type == "SickBloom":
                    command += "k"
                if items[0].type == "Coal":
                    command += "k"
                foundSomething = True

                lastCharacterPosition = pos

            if items[0].type in ("Bush"):
                if lastCharacterPosition[0] > pos[0]:
                    command += str(lastCharacterPosition[0] - pos[0]) + "a"
                    lastDirection = "a"
                if lastCharacterPosition[0] < pos[0]:
                    command += str(pos[0] - lastCharacterPosition[0]) + "d"
                    lastDirection = "d"
                if lastCharacterPosition[1] > pos[1]:
                    command += str(lastCharacterPosition[1] - pos[1]) + "w"
                    lastDirection = "w"
                if lastCharacterPosition[1] < pos[1]:
                    command += str(pos[1] - lastCharacterPosition[1]) + "s"
                    lastDirection = "s"
                command += "j"
                for i in range(0, 11):
                    command += "J" + lastDirection
                command += lastDirection + "k"

            if items[0].type in ("EncrustedBush"):
                break

        found = False

        pos = (self.xPosition, self.yPosition)
        if lastCharacterPosition[0] > pos[0]:
            command += str(lastCharacterPosition[0] - pos[0]) + "a"
        if lastCharacterPosition[0] < pos[0]:
            command += str(pos[0] - lastCharacterPosition[0]) + "d"
        if lastCharacterPosition[1] > pos[1]:
            command += str(lastCharacterPosition[1] - pos[1]) + "w"
        if lastCharacterPosition[1] < pos[1]:
            command += str(pos[1] - lastCharacterPosition[1]) + "s"

        if not foundSomething:
            command += "100."
        command += "opx$=ww$=aa$=ss$=dd"
        command += "opx$=ss$=aa$=ww$=dd"
        command += "opx$=ww$=dd$=ss$=aa"
        command += "opx$=ss$=dd$=ww$=aa"

        convertedCommand = []
        for item in command:
            convertedCommand.append((item, ["norecord"]))

        character.macroState["commandKeyQueue"] = (
            convertedCommand + character.macroState["commandKeyQueue"]
        )


src.items.addType(AutoFarmer)

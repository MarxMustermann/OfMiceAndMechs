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
        handle a character using the autofarmer to gather nearby blooms

        Parameters:
            character: the character using the item
        """

        if not isinstance(self.container,src.terrains.Terrain):
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

        if isinstance(character, src.characters.characterMap["Monster"]):
            #character.die()
            #self.destroy()
            return

        if len(character.inventory) > 9:
            character.addMessage("inventory full")
            return

        command = ""
        length = 1
        pos = [self.xPosition, self.yPosition]
        path = []
        path.append((pos[0], pos[1],0))
        while length < 13:
            if length % 2 == 1:
                for _i in range(length):
                    pos[1] -= 1
                    path.append((pos[0], pos[1],0))
                for _i in range(length):
                    pos[0] += 1
                    path.append((pos[0], pos[1],0))
            else:
                for _i in range(length):
                    pos[1] += 1
                    path.append((pos[0], pos[1],0))
                for _i in range(length):
                    pos[0] -= 1
                    path.append((pos[0], pos[1],0))
            length += 1
        for _i in range(length - 1):
            pos[1] -= 1
            path.append((pos[0], pos[1],0))

        pluggedSprouts = 0
        foundSomething = False
        lastCharacterPosition = path[0]
        for pos in path[1:]:
            items = self.container.getItemByPosition(pos)
            if not items:
                continue
            item = items[0]

            if item.type in ("Bloom", "SickBloom", "Coal", "Sprout","Sprout2","Mold",):
                if item.type in ("Mold",):
                    continue
                if item.type in ("Sprout","Sprout2",) and pluggedSprouts > 0:
                    continue
                pluggedSprouts += 1

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

            elif items[0].type in ("Bush"):
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
                for _i in range(11):
                    command += "J" + lastDirection
                command += lastDirection + "k"
                lastCharacterPosition = pos

            elif items[0].type in ("EncrustedBush"):
                break

            elif not items[0].walkable:
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

        #if not foundSomething:
        #    command += "100."
        #command += "opx$=ww$=aa$=ss$=dd"
        #command += "opx$=ss$=aa$=ww$=dd"
        #command += "opx$=ww$=dd$=ss$=aa"
        #command += "opx$=ss$=dd$=ww$=aa"

        character.runCommandString(command)

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the AutoFarmer")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the AutoFarmer")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(AutoFarmer)

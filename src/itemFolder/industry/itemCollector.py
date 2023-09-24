import src


class ItemCollector(src.items.Item):
    """
    a helper item to offer the player the ability to gather items without progamming too much
    """

    type = "ItemCollector"

    def __init__(self):
        """
        simple superclass configuration
        """
        super().__init__(display="ic")

        self.name = "item collector"
        self.description = "use it to collect items."

        self.bolted = False
        self.walkable = True

    def apply(self, character):
        """
        collect items

        Parameters:
            character: the character trying to collect items
        """

        if not (self.xPosition % 15 == 7 and self.yPosition % 15 == 7):
            character.addMessage(
                "the item collector needs to be placed in the middle of a tile"
            )
            return

        if not self.bolted:
            character.addMessage(
                "the item collector digs into the ground and is now ready for use"
            )
            self.bolted = True

        if isinstance(character, src.characters.Monster):
            character.die()
            return

        if len(character.inventory) > 9:
            character.addMessage("inventory full")
            self.runCommand("fullInventory", character)
            return

        command = ""
        length = 1
        pos = [self.xPosition, self.yPosition]
        path = []
        path.append((pos[0], pos[1]))
        for x in range(pos[0], pos[0] + 7):
            path.append((x, pos[1]))
        for x in reversed(range(pos[0] - 6, pos[0])):
            path.append((x, pos[1]))
        for y in range(pos[1], pos[1] + 7):
            path.append((pos[0], y))
        for y in reversed(range(pos[1] - 6, pos[1])):
            path.append((pos[0], y))
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

        character.addMessage(path[:5])

        lastCharacterPosition = path[0]
        foundItem = None
        lastPos = path[0]
        for pos in path[1:]:
            items = self.container.getItemByPosition((pos[0], pos[1], 0))
            if not items or pos == path[0]:
                lastPos = pos
                continue
            foundItem = items[0]
            break

        if not foundItem:
            character.addMessage("no items found")
            self.runCommand("empty", character)
            return

        if foundItem:
            newCharacterPosition = [lastCharacterPosition[0], lastCharacterPosition[1]]
            if lastCharacterPosition[0] > pos[0]:
                numMoves = lastCharacterPosition[0] - pos[0] - 1
                if numMoves > 0:
                    command += "a" * numMoves
                    newCharacterPosition[0] -= numMoves
            if lastCharacterPosition[0] < pos[0]:
                numMoves = pos[0] - lastCharacterPosition[0] - 1
                if numMoves > 0:
                    command += "d" * numMoves
                    newCharacterPosition[0] += numMoves
            if lastCharacterPosition[1] > pos[1]:
                numMoves = lastCharacterPosition[1] - pos[1] - 1
                if numMoves > 0:
                    command += "w" * numMoves
                    newCharacterPosition[1] -= numMoves
            if lastCharacterPosition[1] < pos[1]:
                numMoves = pos[1] - lastCharacterPosition[1] - 1
                if numMoves > 0:
                    command += "s" * numMoves
                    newCharacterPosition[1] += numMoves
            lastCharacterPosition = newCharacterPosition

            newCharacterPosition = [lastCharacterPosition[0], lastCharacterPosition[1]]
            if lastCharacterPosition[0] < pos[0] and lastCharacterPosition[1] < pos[1]:
                command += "d"
                newCharacterPosition[0] += 1
            if lastCharacterPosition[0] > pos[0] and lastCharacterPosition[1] < pos[1]:
                command += "s"
                newCharacterPosition[1] += 1
            if lastCharacterPosition[0] < pos[0] and lastCharacterPosition[1] > pos[1]:
                command += "w"
                newCharacterPosition[1] -= 1
            if lastCharacterPosition[0] > pos[0] and lastCharacterPosition[1] > pos[1]:
                command += "a"
                newCharacterPosition[0] -= 1
            lastCharacterPosition = newCharacterPosition

            if lastCharacterPosition[0] < pos[0]:
                command += "Kd"
            if lastCharacterPosition[0] > pos[0]:
                command += "Ka"
            if lastCharacterPosition[1] < pos[1]:
                command += "Ks"
            if lastCharacterPosition[1] > pos[1]:
                command += "Kw"

        pos = (self.xPosition, self.yPosition)
        if lastCharacterPosition[0] > pos[0]:
            command += str(lastCharacterPosition[0] - pos[0]) + "a"
        if lastCharacterPosition[0] < pos[0]:
            command += str(pos[0] - lastCharacterPosition[0]) + "d"
        if lastCharacterPosition[1] > pos[1]:
            command += str(lastCharacterPosition[1] - pos[1]) + "w"
        if lastCharacterPosition[1] < pos[1]:
            command += str(pos[1] - lastCharacterPosition[1]) + "s"

        character.runCommandString(command)

    # abstraction: should use super class function
    def configure(self, character):
        """
        handle character trying to to a complex interation with the item
        by offering a selections o actions to do

        Parameters:
            character: a character trying to use the item
        """

        options = [("addCommand", "add command")]
        self.submenue = src.interaction.SelectionMenu(
            "what do you want to do?", options
        )
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.configure2
        self.character = character

    def configure2(self):
        """
        handle a character having selected a complex action to run
        """

        if self.submenue.selection == "addCommand":
            options = []
            options.append(("empty", "no items left"))
            options.append(("fullInventory", "inventory full"))
            self.submenue = src.interaction.SelectionMenu(
                "Setting command for handling triggers.", options
            )
            self.character.macroState["submenue"] = self.submenue
            self.character.macroState["submenue"].followUp = self.setCommand

    def setCommand(self):
        """
        set a command to run in certain situations
        """

        itemType = self.submenue.selection

        commandItem = None
        for item in self.container.getItemByPosition(
            (self.xPosition, self.yPosition - 1)
        ):
            if item.type == "Command":
                commandItem = item

        if not commandItem:
            self.character.addMessage("no command found - place command to the north")
            return

        self.commands[itemType] = commandItem.command
        self.container.removeItem(commandItem)

        self.character.addMessage(
            f"added command for {itemType} - {commandItem.command}"
        )
        return


src.items.addType(ItemCollector)

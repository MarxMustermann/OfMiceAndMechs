import random
from functools import partial

import src

class DimensionTeleporter(src.items.Item):
    type = "DimensionTeleporter"
    name = "Dimension Teleporter"

    ReceiverMode = 1
    SenderMode = 0

    default_offsets = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]

    def __init__(self):
        super().__init__(display="DH", name=self.name)
        self.mode = self.SenderMode
        self.group = None
        self.bolted = False
        self.direction = None

        self.charges = 100
        self.chargePerLightingRod = 100
        self.numUsed = 0
        self.applyOptions.extend(
            [
                ("examine properties", "examine properties"),
                ("change frequency", "change frequency"),
                ("change to receiver", "change to receiver"),
                ("change input direction", "change input direction"),
            ]
        )
        self.applyMap = {
            "examine properties": self.showProperties,
            "change frequency": self.changeGroup,
            "change to receiver": self.changeMode,
            "change to sender": self.changeMode,
            "change input direction": self.changeInputDirection,
            "change output direction": self.changeOutputDirection,
        }

    def d_change(self, offset):
        self.direction = offset

    def changeInputDirection(self, character):
        character.macroState["submenue"] = src.menuFolder.directionMenu.DirectionMenu(
            "choose input direction", self.direction, self.d_change
        )

    def changeOutputDirection(self, character):
        character.macroState["submenue"] = src.menuFolder.directionMenu.DirectionMenu(
            "choose output direction", self.direction, self.d_change
        )

    def getConfigurationOptions(self, character):
        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self, character):
        self.bolted = True
        if character:
            character.addMessage("you bolt down the " + self.name + " and activate it")
            character.changed("boltedItem", {"character": character, "item": self})
        if hasattr(self, "numUsed"):
            self.numUsed = 0

        if self.group:
            self.addToGroup()

    def unboltAction(self, character):
        self.bolted = False
        if character:
            character.addMessage("you unbolt the " + self.name)
            character.changed("unboltedItem", {"character": character, "item": self})
        if hasattr(self, "numUsed"):
            self.numUsed = 0

        self.removeFromGroup()

    def removeFromGroup(self):
        if self.group:
            src.gamestate.gamestate.teleporterGroups[self.group][self.mode].remove(self)

    def addToGroup(self):
        if self.group not in src.gamestate.gamestate.teleporterGroups:
            src.gamestate.gamestate.teleporterGroups[self.group] = ([], [])
        src.gamestate.gamestate.teleporterGroups[self.group][self.mode].append(self)

    def changeGroup(self, character):
        character.macroState["submenue"] = src.menuFolder.teleporterGroupMenu.TeleporterGroupMenu(self)

    def changeMode(self, character):
        if self.group:
            if self in src.gamestate.gamestate.teleporterGroups[self.group][self.mode]:
                src.gamestate.gamestate.teleporterGroups[self.group][self.mode].remove(self)

            if self.mode == self.SenderMode:
                self.mode = self.ReceiverMode
                self.applyOptions[2] = ("change to sender", "change to sender")
            else:
                self.mode = self.SenderMode
                self.applyOptions[2] = ("change to receiver", "change to receiver")

            src.gamestate.gamestate.teleporterGroups[self.group][self.mode].append(self)

    def getInputItems(self):
        result = []

        offset_to_check = [self.direction] if self.direction else self.default_offsets

        for offset in offset_to_check:
            for item in self.container.getItemByPosition(
                (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition + offset[2])
            ):
                if item.bolted:
                    continue
                result.append((item, offset))
        return result

    def TeleportItem(self, item_offset):
        item, offset = item_offset

        if self.direction:
            pos = (
                self.xPosition + self.direction[0],
                self.yPosition + self.direction[1],
                self.zPosition + self.direction[2],
            )
        else:
            pos = (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition + offset[2])

        for i in range(2):
            if isinstance(self.container, src.rooms.Room):
                if not (pos[i] >= 1 and pos[i] <= 14):
                    return False
            elif not (pos[i] % 15 >= 1 and pos[i] % 15 <= 14):
                return False

        if any(item.bolted for item in self.container.getItemByPosition(pos)):
            return False

        item.container.removeItem(item)

        self.container.addItem(item, pos)
        return True

    def tick(self):
        if self.charges:
            items = self.getInputItems()
            if len(items):
                (_senders, receivers) = src.gamestate.gamestate.teleporterGroups[self.group]
                sending_tries = 0
                if len(receivers):
                    while sending_tries != len(receivers):
                        random_receiver: DimensionTeleporter = random.choice(receivers)
                        random_item = items.pop(random.randint(0, len(items) - 1))
                        if not random_receiver.TeleportItem(random_item):
                            sending_tries += 1
                        else:
                            self.charges -= 1
                            self.numUsed += 1
                            return
        else:
            for offset in self.default_offsets:
                for item in self.container.getItemByPosition(
                    (self.xPosition + offset[0], self.yPosition + offset[1], self.zPosition + offset[2])
                ):
                    if item.type == "Rod":
                        item.container.removeItem(item)
                        self.charges = self.chargePerLightingRod
                        return

    def showProperties(self, character):
        network = ""
        if self.group:
            g = src.gamestate.gamestate.teleporterGroups[self.group]
            mapContent = []
            for x in range(15):
                mapContent.append([])
                for y in range(15):
                    if x not in (0, 14) and y not in (0, 14):
                        displayChar = "  "
                    elif x != 7 and y != 7:
                        displayChar = "##"
                    else:
                        displayChar = "  "
                    mapContent[x].append(displayChar)

            for pos in character.terrainInfo:
                mapContent[pos[1]][pos[0]] = "  "

            def show(li, code):
                for t in li:
                    pos = t.getTerrainPosition()
                    if pos in character.terrainInfo:
                        mapContent[pos[1]][pos[0]] = code
                    else:
                        r = range(-1, 2)
                        # pos = (pos[0] + random.choice(r), pos[1] + random.choice(r), 0)
                        for dx in r:
                            for dy in r:
                                new_pos_x = src.helpers.clamp(pos[0] + dx, 1, 13)
                                new_pos_y = src.helpers.clamp(pos[1] + dy, 1, 13)
                                if (new_pos_x, new_pos_y, 0) not in character.terrainInfo:
                                    mapContent[new_pos_y][new_pos_x] = " ?"

            show(g[self.SenderMode], "SE")
            show(g[self.ReceiverMode], "RE")

            network = "\n".join(["".join(x) for x in mapContent])
            network += "\n? Indicate possible teleporter place\nRE indicate a receiver\nSE indicate a sender"
        character.macroState["submenue"] = src.menuFolder.warningMenu.WarningMenu(
            self.getLongInfo() + f"\nCharges: {self.charges}\n\n{network}"
        )

    def getLongInfo(self):
        text = "Operation Mode:"
        if self.group:
            text += " Sender" if self.mode == self.SenderMode else " Receiver"
        else:
            text += "OFF"
        text += "\n"

        code = "Input Direction:" if self.mode == self.SenderMode else "Output Direction:"

        if self.direction:
            cases = {(0, -1, 0): "North", (-1, 0, 0): "West", (1, 0, 0): "East", (0, 1, 0): "South"}

            text += code + " " + cases[self.direction]
        else:
            if self.mode == self.SenderMode:
                text += code + " From all Directions"
            else:
                text += code + " To all Directions"

        f_text = str(self.group) if self.group else "Not Set"
        text += "\nFrequency: " + f_text

        if self.group:
            g = src.gamestate.gamestate.teleporterGroups[self.group]
            network_size = len(g[0]) + len(g[1])
            text += f"\nNetwork Size: {network_size}"
        return text

src.items.addType(DimensionTeleporter, nonManufactured=True)

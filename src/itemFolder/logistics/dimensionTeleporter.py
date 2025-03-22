import random
from functools import partial

import src
import src.rooms


class DimensionTeleporter(src.items.Item):
    type = "DimensionTeleporter"
    name = "Dimension Teleporter"

    capacity = 15
    cost_per_terrain = 1.15

    ReceiverMode = 1
    SenderMode = 0

    def __init__(self):
        super().__init__(display="DH", name=self.name)
        self.mode = self.SenderMode
        self.group = "default"
        self.bolted = False
        self.direction = None

        self.applyOptions.extend(
            [
                ("change to receiver", "change to receiver"),
                ("change input direction", "change input direction"),
            ]
        )
        self.applyMap = {
            "change to receiver": partial(self.changeMode, self.ReceiverMode),
            "change to sender": partial(self.changeMode, self.SenderMode),
            "change input direction": self.changeInputDirection,
            "change output direction": self.changeOutputDirection,
        }

    def changeInputDirection(self, character):
        def d_change(offset):
            self.direction = offset

        character.macroState["submenue"] = src.menuFolder.directionMenu.DirectionMenu(
            "choose input direction", self.direction, d_change
        )

    def changeOutputDirection(self, f, character):
        def d_change(offset):
            self.direction = offset

        character.macroState["submenue"] = src.menuFolder.directionMenu.DirectionMenu(
            "choose output direction", self.direction, d_change
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
        character.addMessage("you bolt down the " + self.name + " and activate it")
        character.changed("boltedItem", {"character": character, "item": self})
        if hasattr(self, "numUsed"):
            self.numUsed = 0

        src.gamestate.gamestate.teleporterGroups[self.group][self.mode].append(self)

    def unboltAction(self, character):
        self.bolted = False
        character.addMessage("you unbolt the " + self.name)
        character.changed("unboltedItem", {"character": character, "item": self})
        if hasattr(self, "numUsed"):
            self.numUsed = 0

        src.gamestate.gamestate.teleporterGroups[self.group][self.mode].remove(self)

    def changeMode(self, mode, character):
        character.macroState["submenue"] = src.menuFolder.teleporterGroupMenu.TeleporterGroupMenu(self, mode)

    def getInputItems(self):
        result = []

        offset_to_check = [self.direction] if self.direction else [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0)]

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
        items = self.getInputItems()
        if len(items):
            # TODO add charges
            (_senders, receivers) = src.gamestate.gamestate.teleporterGroups[self.group]
            sending_tries = 0
            if len(receivers):
                while sending_tries != len(receivers):
                    random_receiver: DimensionTeleporter = random.choice(receivers)
                    random_item = items.pop(random.randint(0, len(items) - 1))
                    if not random_receiver.TeleportItem(random_item):
                        sending_tries += 1
                    else:
                        break


src.items.addType(DimensionTeleporter)

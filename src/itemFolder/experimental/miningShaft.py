import src


class MiningShaft(src.items.Item):
    type = "MiningShaft"

    def apply(self, character):
        character.zPosition -= 1

    def configure(self, character):
        character.zPosition += 1


src.items.addType(MiningShaft)

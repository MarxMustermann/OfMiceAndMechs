import src


class SuicideBooth(src.items.Item):
    type = "SuicideBooth"

    def __init__(self):
        super().__init__(display="SB")
        self.name = "suicide booth"

    def apply(self, character):
        character.addMessage("you die")
        character.die(reason="used suicide booth")


src.items.addType(SuicideBooth)

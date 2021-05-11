import src

class SuicideBooth(src.items.Item):
    type = "SuicideBooth"

    def __init__(self,xPosition=0,yPosition=0,name="SuicideBooth",creator=None,noId=False):
        super().__init__("SB",xPosition,yPosition,name=name,creator=creator)

    def apply(self,character):
        character.addMessage("you die")
        character.die(reason="used suicide booth")

src.items.addType(SuicideBooth)

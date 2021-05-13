import src

class MoldSpore(src.items.Item):
    type = "MoldSpore"

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.moldSpore)

        self.name = "mold spore"
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        if not self.terrain:
            character.addMessage("this needs to be placed outside to be used")
            return
        self.startSpawn()
        character.addMessage("you activate the mold spore")

    def startSpawn(self):
        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%10,creator=self)
        event.setCallback({"container":self,"method":"spawn"})
        self.terrain.addEvent(event)

    def spawn(self):
        new = itemMap["Mold"](creator=self)
        new.xPosition = self.xPosition
        new.yPosition = self.yPosition
        self.container.addItems([new])
        new.startSpawn()
        self.destroy(generateSrcap=False)

    def getLongInfo(self):
        return """
item: MoldSpore

description:
This is a mold spore

put it on the ground and activate it to plant it
"""

src.items.addType(MoldSpore)

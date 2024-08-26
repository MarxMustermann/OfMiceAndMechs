import src
import random

class Contraption(src.items.Item):
    """
    """

    type = "Contraption"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "contraption"

        self.walkable = False
        self.bolted = True
        self.meltdownLevel = 0

    def startMeltdown(self):
        if self.meltdownLevel:
            return
        self.meltdownLevel = 1
        self.handleTick()

    def handleTick(self):
        if not self.container:
            return

        for i in range(1,self.meltdownLevel):
            self.container.addAnimation(self.getPosition(),"smoke",i,{})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

        if self.meltdownLevel == 10:
            self.destroy()
            return

        self.meltdownLevel += 1

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1)
        event.setCallback({"container": self, "method": "handleTick"})
        currentTerrain = self.getTerrain()
        currentTerrain.addEvent(event)

    def render(self):
        if self.meltdownLevel:
            return (src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")
        return super().render()

src.items.addType(Contraption)

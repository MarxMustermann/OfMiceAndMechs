import src

"""
"""


class Watch(src.items.Item):
    type = "Watch"

    """
    call superclass constructor with modified parameters
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.watch)

        self.creationTime = 0
        self.maxSize = 100

        self.name = "watch"

        self.attributesToStore.extend(["creationTime"])

        self.bolted = False
        self.walkable = True
        try:
            self.creationTime = src.gamestate.gamestate.tick
        except:
            pass

    def apply(self, character):

        time = src.gamestate.gamestate.tick - self.creationTime
        while time > self.maxSize:
            self.creationTime += self.maxSize
            time -= self.maxSize

        if not "t" in character.registers:
            character.registers["t"] = [0]
        character.registers["t"][-1] = src.gamestate.gamestate.tick - self.creationTime

        character.addMessage("it shows %s ticks" % (character.registers["t"][-1]))

    def getLongInfo(self):
        text = """
This device tracks ticks since creation. You can use it to measure time.
Activate it to get a message with the number of ticks passed.
Also the number of ticks will be written to the register t.
"""
        return text


src.items.addType(Watch)

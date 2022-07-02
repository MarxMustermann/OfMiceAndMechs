import src


class MonsterSpawner(src.items.Item):
    """
    """

    type = "MonsterSpawner"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "monster spawner"

        self.walkable = False
        self.bolted = True

    def apply(self, character):
        if isinstance(character,src.characters.Monster):
            return
        character.addMessage("you rip the spawner apart")

        new = src.items.itemMap["Explosion"]()
        self.container.addItem(new,(self.xPosition,self.yPosition,self.zPosition))
        event = src.events.RunCallbackEvent(
                src.gamestate.gamestate.tick + 1
            )
        event.setCallback({"container": new, "method": "explode"})
        self.container.addEvent(event)
        self.destroy()

    def render(self):
        return "MS"

src.items.addType(MonsterSpawner)

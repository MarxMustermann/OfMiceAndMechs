import src
import random

class MonsterSpawner(src.items.Item):
    '''
    ingame item to spawn monsters

    Parameters:
        strength: the strenth of the boss to spawn (None for random)
    '''
    type = "MonsterSpawner"
    def __init__(self,strength=None):
        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "monster spawner"

        # set random strength
        if strength is None:
            strength = random.randint(1,10)

        self.walkable = False
        self.bolted = True
        self.disabled = False
        self.strength = 1

    def apply(self, character):
        '''
        do the monster spawning
        '''

        if character.xPosition > self.xPosition:
            character.addMessage("you cannot use this machine from the east")
            return

        # spawn the monster
        pos = self.getPosition()
        room = self.container
        enemy = src.characters.characterMap["Guardian"](modifier=self.strength)
        enemy.runCommandString("..ddd10.")
        room.addCharacter(enemy,pos[0]+1,pos[1])

        # make monster kill
        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(enemy)
        quest.activate()
        enemy.quests.append(quest)

        # increase strength
        self.strength += 1

    def render(self):
        '''
        return a custom render
        '''
        try:
            self.strength
        except:
            self.strength = random.randint(1,10)

        shade = max(0,255-(30*(self.strength-1)))
        color = (255,shade,shade)
        return (src.interaction.urwid.AttrSpec(color, "black"), "MS")

    def getLongInfo(self):
        '''
        generate simple text description

        Returns:
            the decription text
        '''
        try:
            self.strength
        except:
            self.strength = random.randint(1,10)

        text = super().getLongInfo()
        text += f"""
strength: {self.strength}
"""
        return text

    def getConfigurationOptions(self, character):
        '''
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        '''

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def boltAction(self,character):
        '''
        bolt the item down
        '''
        self.bolted = True
        character.addMessage("you bolt down the MonsterSpawner")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        '''
        unbolt the item
        '''
        self.bolted = False
        character.addMessage("you unbolt the MonsterSpawner")
        character.changed("unboltedItem",{"character":character,"item":self})

# register the item
src.items.addType(MonsterSpawner)

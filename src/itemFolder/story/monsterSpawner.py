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
        try:
            self.strength
        except:
            self.strength = random.randint(1,10)

        # spawn the monster
        pos = self.getPosition()
        room = self.container
        enemy = src.characters.characterMap["Guardian"](modifier=self.strength)
        room.addCharacter(enemy,pos[0],pos[1])

        # make monster kill
        quest = src.quests.questMap["ClearTerrain"]()
        quest.autoSolve = True
        quest.assignToCharacter(enemy)
        quest.activate()
        enemy.quests.append(quest)

        # self destruct
        self.destroy()

    def render(self):
        '''
        return a custom render
        '''
        return "MS"

# register the item
src.items.addType(MonsterSpawner)

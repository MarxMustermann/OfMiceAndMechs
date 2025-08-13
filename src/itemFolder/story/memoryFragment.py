import src
import random


class MemoryFragment(src.items.Item):
    '''
    ingame item mainy used as ressource to buy reports
    '''
    type = "MemoryFragment"
    def __init__(self):
        super().__init__(display="mf", name="Memory Fragment")
        self.walkable = True
        self.bolted = False

    def apply(self,character):
        '''
        uncover some terrain as secondary usage
        '''

        # uncover random position
        pos = (random.randint(1,13),random.randint(1,13))
        terrain = src.gamestate.gamestate.terrainMap[pos[1]][pos[0]]
        currentInfo = character.terrainInfo.get(terrain.getPosition())
        if not currentInfo:
            character.terrainInfo[terrain.getPosition()] = {"tag":terrain.tag}
            text = f"you uncovered the terrain {pos}.\nIt is a {terrain.tag}"
        else:
            character.terrainInfo[terrain.getPosition()] = {"tag":terrain.tag}
            text = f"you uncovered the terrain {pos}.\nIt is already known"
        character.addMessage(text)

        # self destruct
        self.destroy()

# register the item class
src.items.addType(MemoryFragment, nonManufactured=True)

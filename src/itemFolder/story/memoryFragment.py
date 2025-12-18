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
        is_new_info = False
        if not currentInfo and not pos == (7,7):
            character.terrainInfo[terrain.getPosition()] = {"tag":terrain.tag}
            text = f"you uncovered the terrain {pos}.\nIt is a {terrain.tag}"
            is_new_info = True
        else:
            text = f"you already know about the uncover terrain."

            # convert memory fragment to mana to make up for loosing out
            terrain = character.getTerrain()
            if terrain.mana >= 2:
                manaCrystal = src.items.itemMap["ManaCrystal"]()
                character.container.addItem(manaCrystal,character.getPosition())
                text += f"the memory fragment crystalises."
            else:
                text += f"the memory fragment starts to crystalise. But there is no mana in this terrain"

        if is_new_info:
            pseudo_map = []
            for y in range(0,15):
                pseudo_map.append(["  "])
                for x in range(0,15):
                    if pos == (x,y):
                        pseudo_map[y].append("XX")
                    elif y == 7 or x == 7:
                        pseudo_map[y].append("  ")
                    elif y in (0,14) or x in (0,14):
                        pseudo_map[y].append("~~")
                    else:
                        pseudo_map[y].append("  ")
                pseudo_map[y].append("\n")
            character.showTextMenu([text,"\n\n\n",pseudo_map])
        character.addMessage(text)

        # self destruct
        self.destroy(generateScrap=False)

# register the item class
src.items.addType(MemoryFragment, nonManufactured=True)

import random

import src


class MapTable(src.items.Item):
    '''
    ingame to store and show the terrain map
    '''
    type = "MapTable"
    name = "MapTable"
    bolted = True
    walkable = False
    def __init__(self):
        self.terrainInfo = {}
        super().__init__(display="MP")
        self.applyOptions.extend(
                        [
                                ("studyMap", "study map"),
                                ("writeMap", "extend map"),
                                ("readMap", "study map"),
                        ]
                    )
        self.applyMap = {
                    "studyMap": self.studyMap,
                    "writeMap":self.writeMap,
                    "readMap":self.readMap,
                        }

    def studyMap(self, character):
        self.writeMap(character)
        self.readMap(character)
        character.lastMapSync = src.gamestate.gamestate.tick

    def showMap(self, character, cursor = None):
        '''
        show a UI to see the map
        '''
        terrain = self.getTerrain()

        # render empty map
        mapContent = []
        for x in range(15):
            mapContent.append([])
            for y in range(15):
                if x not in (0, 14) and y not in (0, 14):
                    char = "  "
                elif x != 7 and y != 7:
                    char = "##"
                else:
                    char = "  "
                mapContent[x].append(char)

        functionMap = {}

        self.submenue = src.menuFolder.mapMenu.MapMenu(mapContent=mapContent,functionMap=functionMap)
        character.macroState["submenue"] = self.submenue

    def writeMap(self, character):
        '''
        add the memory of the npc to the map
        '''
        for (coordinate,info)  in character.terrainInfo.items():
            if coordinate not in self.terrainInfo:
                self.terrainInfo[coordinate] = {}
            for (key,value)  in info.items():
                self.terrainInfo[coordinate][key] = value

    def readMap(self, character):
        '''
        add the map to the npcs memory
        '''
        for (coordinate,info)  in self.terrainInfo.items():
            if coordinate not in character.terrainInfo:
                character.terrainInfo[coordinate] = {}
            for (key,value)  in info.items():
                character.terrainInfo[coordinate][key] = value

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
        bult down item
        '''
        self.bolted = True
        character.addMessage("you bolt down the MapTable")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        '''
        bult down item
        '''
        self.bolted = False
        character.addMessage("you unbolt the MapTable")
        character.changed("unboltedItem",{"character":character,"item":self})

# register item type
src.items.addType(MapTable)

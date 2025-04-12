import random

import src


class MapTable(src.items.Item):

    type = "MapTable"
    name = "MapTable"
    bolted = True
    walkable = False

    def __init__(self):
        """
        set up internal state
        """

        self.terrainInfo = {}
        super().__init__(display="MP")

        self.applyOptions.extend(
                        [
                                                                ("showMap", "show map"),
                                                                ("writeMap", "extend map"),
                                                                ("readMap", "study map"),
                        ]
                        )
        self.applyMap = {
                    "showMap": self.showMap,
                    "writeMap":self.writeMap,
                    "readMap":self.readMap,
                        }


    def showMap(self, character, cursor = None):
        """
        """
        print(self.terrainInfo)

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

        self.submenue = src.menuFolder.mapMenu.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=cursor)
        character.macroState["submenue"] = self.submenue

    def writeMap(self, character):
        for (coordinate,info)  in character.terrainInfo.items():
            if coordinate not in self.terrainInfo:
                self.terrainInfo[coordinate] = {}
            for (key,value)  in info.items():
                self.terrainInfo[coordinate][key] = value

    def readMap(self, character):
        for (coordinate,info)  in self.terrainInfo.items():
            if coordinate not in character.terrainInfo:
                character.terrainInfo[coordinate] = {}
            for (key,value)  in info.items():
                character.terrainInfo[coordinate][key] = value

    def boltAction(self,character):
        self.bolted = True
        character.addMessage("you bolt down the MapTable")
        character.changed("boltedItem",{"character":character,"item":self})

    def unboltAction(self,character):
        self.bolted = False
        character.addMessage("you unbolt the MapTable")
        character.changed("unboltedItem",{"character":character,"item":self})

src.items.addType(MapTable)

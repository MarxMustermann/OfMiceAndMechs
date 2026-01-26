import src

class ObserveMenu(src.subMenu.SubMenu):
    type = "ObserveMenu"

    def __init__(self,character):
        super().__init__()
        self.index = character.getSpacePosition()
        self.index_big = character.getBigPosition()
        self.character = character

    def handleKey(self, key, noRender=False, character = None):

        # exit the submenu
        if key in ("esc"," ",):
            return True

        # move small cursor
        if key in ("w",):
            self.index = (self.index[0],self.index[1]-1,0)
        if key in ("s",):
            self.index = (self.index[0],self.index[1]+1,0)
        if key in ("a",):
            self.index = (self.index[0]-1,self.index[1],0)
        if key in ("d",):
            self.index = (self.index[0]+1,self.index[1],0)

        # handle out of bounds by small cursor
        if self.index[0] < 1:
            self.index_big = (self.index_big[0]-1,self.index_big[1],0)
            self.index = (13,self.index[1],0)
        if self.index[0] > 13:
            self.index_big = (self.index_big[0]+1,self.index_big[1],0)
            self.index = (1,self.index[1],0)
        if self.index[1] < 1:
            self.index_big = (self.index_big[0],self.index_big[1]-1,0)
            self.index = (self.index[0],13,0)
        if self.index[1] > 13:
            self.index_big = (self.index_big[0],self.index_big[1]+1,0)
            self.index = (self.index[0],1,0)

        # move big cursor
        if key in ("W",):
            self.index_big = (self.index_big[0],self.index_big[1]-1,0)
        if key in ("S",):
            self.index_big = (self.index_big[0],self.index_big[1]+1,0)
        if key in ("A",):
            self.index_big = (self.index_big[0]-1,self.index_big[1],0)
        if key in ("D",):
            self.index_big = (self.index_big[0]+1,self.index_big[1],0)

        # hanldle out of bound by the big cursor
        if self.index_big[0] < 1:
            self.index_big = (13,self.index_big[1],0)
        if self.index_big[0] > 13:
            self.index_big = (1,self.index_big[1],0) 
        if self.index_big[1] < 1:
            self.index_big = (self.index_big[0],13,0)
        if self.index_big[1] > 13:
            self.index_big = (self.index_big[0],1,0)

        # signal menu is still active
        return False

    def render(self):

        # getting some helper variables
        terrain = self.character.getTerrain()
        rooms = terrain.getRoomByPosition(self.index_big)

        # set the besaic text
        text = []
        text.append(f"  {self.index} {self.index_big}                                                \n\n")

        # render rooms
        if rooms:
            rawRender = rooms[0].render(padding=1)
            container = rooms[0]
        else:
            rawRender = terrain.render(coordinateOffset=(15*self.index_big[1],15*self.index_big[0]),size=(14,14))
            container = terrain
        miniMapRender = terrain.renderTiles()

        # show the maps
        maprender = []
        y = 0
        for line in rawRender:

            # show local map
            maprender.append("  ")
            x = 0
            for entry in line:
                char = entry
                if (x,y,0) == self.index:
                    char = "XX"
                maprender.append(char)
                x += 1

            # show terrain map
            if self.index_big != self.character.getBigPosition():
                maprender.append("  |  ")
                x = 0
                for entry in miniMapRender[y]:
                    char = entry
                    if (x,y,0) == self.index_big:
                        char = "XX"
                    maprender.append(char)
                    x += 1

            # start next line
            maprender.append("\n")
            y += 1
        text.extend(maprender)

        # get the items to display
        pos = self.index
        if not rooms:
            pos = (self.index_big[0]*15+self.index[0], self.index_big[1]*15+self.index[1], 0)
        items = container.getItemByPosition(pos)

        # list found items
        if not items:
            text.append("no items found\n")
        for item in items:
            text.append(item.name)
            text.append("\n")

        # return rendered text
        return text

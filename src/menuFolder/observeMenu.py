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

        # show the coordinate line
        coordinate_line = ""
        first_coordinate = f"  {self.index}"
        first_coordinate_bit = f"{first_coordinate}"+" "*(34-len(first_coordinate))
        coordinate_line = first_coordinate_bit
        if self.index_big != self.character.getBigPosition():
            coordinate_line += f"|  {self.index_big}"
        coordinate_line += " "*(68-len(coordinate_line))+"\n"
        text.append(coordinate_line)

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
            actual_y = y
            if rooms:
                x -= 1
                actual_y -= 1
            for entry in line:
                char = entry
                if (x,actual_y,0) == self.index:
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

        # get actual postion
        pos = self.index
        if not rooms:
            pos = (self.index_big[0]*15+self.index[0], self.index_big[1]*15+self.index[1], 0)

        # list found items
        text.append("\n")
        items = container.getItemByPosition(pos)
        if not items:
            text.append("no items found\n")
        else:
            text.append("items:\n\n")
        for item in items:
            text.append("- ")
            text.append(item.name)
            text.append("\n")

        # list characters on postion
        text.append("\n")
        show_characters = container.getCharactersOnPosition(pos)
        if not show_characters:
            text.append("no characters found\n")
        else:
            text.append("characters:\n\n")
        for show_character in show_characters:
            text.append("- ")
            text.append(show_character.charType)
            if show_character == self.character:
                text.append(" (You)")
            elif show_character.faction == self.character.faction:
                text.append(" (ally)")
            else:
                text.append(" (enemy)")

            text.append("\n")

        # list markers on floor
        text.append("\n")
        markers = []
        if rooms:
            markers = container.getMarkersOnPosition(pos)
        if not markers:
            text.append("no markers found\n")
        else:
            text.append("markers:\n\n")
        for marker in markers:
            text.append("- ")
            text.append(str(marker[0]))
            text.append("\n")

        # return rendered text
        return text

import src

class ExperimentalObserveMenu(src.menues.SubMenu):
    type = "ExperimentalObserveMenu"

    def __init__(self,char):
        super().__init__()
        self.index = char.getSpacePosition()
        self.index_big = char.getBigPosition()
        self.character = char

    def getTitle(self):
        return "EXPERIMENTAL OBSERVE"

    def get_map_position(self):
        big_position = self.index_big
        small_position = self.index
        pos = (big_position[0]*15+small_position[0], big_position[1]*15+small_position[1], big_position[2]*15+small_position[2])
        return pos

    def handleKey(self, key, noRender=False, character = None):
        # exit the submenu
        if key in ("esc"," ",):
            return True

        # signal menu is still active
        return False

    def render(self,size=None):

        # getting some helper variables
        terrain = self.character.getTerrain()
        rooms = terrain.getRoomByPosition(self.index_big)
        container = terrain
        if rooms:
            container = rooms[0]

        # set the besaic text
        text = []

        # show the coordinate line
        coordinate_line = ""
        first_coordinate = f"  {self.index}"
        first_coordinate_bit = f"observed coordinate: {first_coordinate}"
        first_coordinate_bit += " "*(34-len(first_coordinate_bit))
        coordinate_line = first_coordinate_bit
        if self.index_big != self.character.getBigPosition():
            coordinate_line += f"|  {self.index_big}"
        if container.isRoom:
            if container.tag:
                coordinate_line += f" {container.tag}"
            else:
                coordinate_line += f" room"
            coordinate_line += f" (inside)"
        else:
            coordinate_line += f" mud field (outside)"
        coordinate_line += " "*(68-len(coordinate_line))+"\n"
        text.append(coordinate_line)

        # get click position
        click_position = self.index
        if not rooms:
            click_position = (self.index_big[0]*15+self.index[0],self.index_big[1]*15+self.index[1],0)

        # check for boundary clicks
        boundary_click = False
        if (click_position[0]%15 in (0,14,) or click_position[1]%15 in (0,14,)):
            boundary_click = True

        # handle click on a boundary
        if boundary_click:
            text.append("\n")
            text.append(f"A wall of static energy dividing the world into tiles.\n")
            text.append((src.interaction.highlighted_ui_attr,f"You cannot interact with this spot\n"))
            text.append("\n")
            passable = False
            if (click_position[0]%15 in (7,) or click_position[1]%15 in (7,)):
                passable = True
                offset = None
                if click_position[0]%15 == 0:
                    offset = (-1,0,0)
                if click_position[1]%15 == 0:
                    offset = (0,-1,0)
                if click_position[0]%15 == 14:
                    offset = (1,0,0)
                if click_position[1]%15 == 14:
                    offset = (0,1,0)
                if not terrain.isTileTransferPossible(self.index_big,offset):
                    passable = False
            if passable:
                text.append(f"You can cross into to neighbour tile here.")
            else:
                text.append(f"You cannot cross this spot")

        # handle click on the actual map
        if not boundary_click:

            # list characters on postion
            text.append("\n")
            show_characters = container.getCharactersOnPosition(click_position)
            if not show_characters:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"no characters found\n"))
            else:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"characters:\n\n"))
            for show_character in show_characters:
                text.append("- ")
                text.append(show_character.charType)
                if show_character == self.character:
                    text.append(" (You)")
                elif show_character.faction == self.character.faction:
                    text.append(f" - {show_character.name}")
                    text.append(" (ally)")
                else:
                    text.append(" (enemy)")

                text.append("\n")

            # list found items
            text.append("\n")
            items = container.getItemByPosition(click_position)
            if not items:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"no items found\n"))
            else:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"items:\n\n"))
            for item in items:
                text.append("- ")
                text.append(item.metaRender())
                text.append(" ")
                text.append(item.name)
                text.append(" => ")
                text.append(item.description)
                text.append("\n")

            # list markers on floor
            text.append("\n")
            markers = []
            if rooms:
                markers = container.getMarkersOnPosition(click_position)
            if not markers:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"no markings found\n"))
            else:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"markings:\n\n"))
            for marker in markers:
                text.append("- ")
                text.append(str(marker[0]))
                text.append("\n")

            text.append("\n")
            if container.isRoom:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"steel floor (inside)\n"))
            else:
                text.append((src.pseudoUrwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"mud floor (outside)\n"))

        # return rendered text
        return text

# register the menu type
src.menues.add_menu(ExperimentalObserveMenu)

import src

import numpy as np

door_texture = {}

class Door(src.items.Item):
    """
    a door for opening/closing and locking people in/out
    """

    type = "Door"
    name = "door"
    walkable = False
    description = "used to enter and leave rooms."

    def __init__(self, bio=False):
        """
        set up initial state

        Parameters:
            bio: whether this item is grown or manmade
        """

        super().__init__()
        self.bio = bio

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        border_width = tileSize//10+1

        identifier = (self.walkable,fg_color,bg_color)
        texture = door_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path
            if self.walkable:
                path += "Door.png"
            else:
                path += "Door_Closed.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            door_texture[identifier] = texture
            print("rebuilding","Door.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

        renderer.draw_color = fg_color

        if self.bolted and not self.walkable:
            items = self.container.getItemByPosition(self.getPosition(offset=(0,-1,0)))
            if not (len(items) == 1 and items[0].type == "Wall" and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(-1,0,0)))
            if not (len(items) == 1 and items[0].type == "Wall" and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))

            items = self.container.getItemByPosition(self.getPosition(offset=(0,1,0)))
            if not (len(items) == 1 and items[0].type == "Wall" and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(1,0,0)))
            if not (len(items) == 1 and items[0].type == "Wall" and items[0].bolted):
                renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted and self.walkable:
            options["x"] = ("block door", self.blockDoor)
        else:
            options["x"] = ("unblock door", self.unblockDoor)
        if self.bolted :
            if self.walkable:
                options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

    def unboltAction(self,character):
        super().unboltAction(character)
        if not self.bolted:
            self.walkable = False


    def blockDoor(self,character):
        character.addMessage("You block the Door")
        character.changed("blockedDoor",{"character":character,"item":self})
        self.walkable = False

    def unblockDoor(self,character):
        character.addMessage("You unblock the Door")
        character.changed("unblockedDoor",{"character":character,"item":self})
        self.walkable = True

    def apply(self,character):
        if not self.walkable:
            text = "The door is blocked and needs to be unblocked to open.\nUse a complex interaction to unblock it"
            character.addMessage(text)
            character.showTextMenu(text)
            return
        super().apply(character)

    def render(self):
        """
        render depending on state

        Returns:
            what the item should look like
        """

        if self.bio:
            if self.walkable:
                displayChar = src.canvas.displayChars.bioDoor_opened
            else:
                displayChar = src.canvas.displayChars.bioDoor_closed
        else:
            if self.walkable:
                displayChar = src.canvas.displayChars.door_opened
            else:
                if self.bolted and (self.xPosition in (0,12,) or self.yPosition in (0,12,)):
                    displayChar = src.canvas.displayChars.outer_door_closed
                else:
                    displayChar = src.canvas.displayChars.door_closed
        return displayChar

    '''
    def gatherApplyActions(self, character):
        """
        handle a character trying to use this item, by
        add open or close action depending on state

        Parameters:
            character: the character trying to use this item
        """
        applyActions = super().gatherApplyActions()
        if self.walkable:
            applyActions.append(self.close)
        else:
            applyActions.append(self.open)
        return applyActions
    '''

    def open(self, character):
        """
        open door

        Parameters:
            character: the character opening the door
        """

        if not isinstance(self.container, src.rooms.Room):
            if character:
                character.addMessage("you can only use doors within rooms")
            return

        if character:
            if not (character.container == self.container):
                character.addMessage("you can only open the door from inside the room")
                return

        # open the door
        #self.walkable = True

    def close(self, character=None):
        """
        close the door

        Parameters:
            character: the character closing the door
        """
        return

        self.walkable = False


src.items.addType(Door)

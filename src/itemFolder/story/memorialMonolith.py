import src

import numpy as np

memorialMonolith_texture = {}

class MemorialMonolith(src.items.Item):
    """
    ingame item used to give the player hints to treasure
    """
    type = "MemorialMonolith"
    def __init__(self,inscription=None):
        super().__init__(display=(src.interaction.urwid.AttrSpec("#ca0","#000"),"MM"))
        self.name = "memorial monolith"
        self.description = "holds a memorial engraving and is lavishly decorated"

        self.bolted = True
        self.walkable = False
        self.inscription = inscription

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        identifier = (fg_color,bg_color)
        texture = memorialMonolith_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path+"MemorialMonolith.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            memorialMonolith_texture[identifier] = texture
            print("rebuilding","ScrapCompactor.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

    def apply(self, character):
        """
        handle a character trying to use this item
        by showing some info

        Parameters:
            character: the character trying to use the item
        """

        if self.inscription:
            character.addMessage(self.inscription)
            character.showTextMenu(self.inscription)
        else:
            character.addMessage("The monolith has no inscription")

src.items.addType(MemorialMonolith)

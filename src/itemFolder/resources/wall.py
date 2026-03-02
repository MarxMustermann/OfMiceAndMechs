import src

import numpy as np

wall_texture = {}

class Wall(src.items.Item):
    '''
    basic item with different appearance
    '''

    type = "Wall"
    description = "used to build rooms"
    name = "wall"

    def __init__(self):
        '''
        set up internal state
        '''
        super().__init__(display=src.canvas.displayChars.wall)


    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        border_width = tileSize//10+1

        identifier = (fg_color,bg_color)
        texture = wall_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path+"Wall_background.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            wall_texture[identifier] = texture
            print("rebuilding","Wall.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

        renderer.draw_color = fg_color

        renderer.fill_rect((basePos[0],basePos[1],border_width*2,border_width*2))
        renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width*2,border_width*2,border_width*2))
        renderer.fill_rect((basePos[0]+tileSize-border_width*2,basePos[1],border_width*2,border_width*2))
        renderer.fill_rect((basePos[0]+tileSize-border_width*2,basePos[1]+tileSize-border_width*2,border_width*2,border_width*2))

        renderer.draw_line((basePos[0]+border_width,basePos[1]+border_width), (basePos[0]+tileSize-border_width,basePos[1]+tileSize-border_width))
        renderer.draw_line((basePos[0]+border_width+1,basePos[1]+border_width), (basePos[0]+tileSize-border_width,basePos[1]+tileSize-border_width-1))
        renderer.draw_line((basePos[0]+border_width,basePos[1]+border_width+1), (basePos[0]+tileSize-border_width-1,basePos[1]+tileSize-border_width))

        renderer.draw_line((basePos[0]+tileSize-border_width,basePos[1]+border_width), (basePos[0]+border_width,basePos[1]+tileSize-border_width))
        renderer.draw_line((basePos[0]+tileSize-border_width-1,basePos[1]+border_width), (basePos[0]+border_width,basePos[1]+tileSize-border_width-1))
        renderer.draw_line((basePos[0]+tileSize-border_width,basePos[1]+border_width+1), (basePos[0]+border_width+1,basePos[1]+tileSize-border_width))

        if self.bolted:
            items = self.container.getItemByPosition(self.getPosition(offset=(0,-1,0)))
            if not (len(items) == 1 and items[0].type in ("Door","Wall",) and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            else:
                renderer.fill_rect((basePos[0]+tileSize//2-border_width//2,basePos[1],border_width,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(-1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Door","Wall",) and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            else:
                renderer.fill_rect((basePos[0],basePos[1]+tileSize//2-border_width//2,border_width,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(0,1,0)))
            if not (len(items) == 1 and items[0].type in ("Door","Wall",) and items[0].bolted):
                renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
            else:
                renderer.fill_rect((basePos[0]+tileSize//2-border_width//2,basePos[1]+tileSize-border_width,border_width,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Door","Wall",) and items[0].bolted):
                renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))
            else:
                renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1]+tileSize//2-border_width//2,border_width,border_width))
        else:
            renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
            renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))

    def getConfigurationOptions(self, character):
        """
        register the configuration options with superclass

        Parameters:
            character: the character trying to conigure the machine
        """

        options = super().getConfigurationOptions(character)
        if self.bolted:
            options["b"] = ("unbolt", self.unboltAction)
        else:
            options["b"] = ("bolt down", self.boltAction)
        return options

src.items.addType(Wall)

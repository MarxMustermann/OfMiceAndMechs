import src
import random
import numpy as np

contraption_texture = {}

class Contraption(src.items.Item):
    """
    """

    type = "Contraption"
    description = "weird machinery. You don't know what it is used for"
    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "contraption"

        self.walkable = False
        self.bolted = True
        self.meltdownLevel = 0

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        border_width = tileSize//10+1

        identifier = (fg_color,bg_color)
        texture = contraption_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path+"Contraption.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            contraption_texture[identifier] = texture
            print("rebuilding","Contraption.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

        renderer.draw_color = fg_color

        if self.bolted:
            items = self.container.getItemByPosition(self.getPosition(offset=(0,-1,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            else:
                renderer.fill_rect((basePos[0]+tileSize//2-border_width//2,basePos[1]+tileSize//4,border_width,border_width*3))

            items = self.container.getItemByPosition(self.getPosition(offset=(-1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            else:
                renderer.fill_rect((basePos[0]+tileSize//4,basePos[1]+tileSize//2-border_width//2,border_width*3,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(0,1,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
            else:
                renderer.fill_rect((basePos[0]+tileSize//2-border_width//2,basePos[1]+tileSize-border_width*3-tileSize//4,border_width,border_width*3))

            items = self.container.getItemByPosition(self.getPosition(offset=(1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0]+2*tileSize//2-border_width,basePos[1],border_width,tileSize))
            else:
                renderer.fill_rect((basePos[0]+tileSize//4+tileSize//4,basePos[1]+tileSize//2-border_width//2,border_width*3,border_width))
        else:
            renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
            renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))

    def startMeltdown(self):
        if self.meltdownLevel:
            return
        self.meltdownLevel = 1
        self.handleTick()

    def handleTick(self):
        if not self.container:
            return

        if self.container.isRoom:
            for i in range(1,self.meltdownLevel):
                self.container.addAnimation(self.getPosition(),"smoke",i,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

        if self.meltdownLevel == 5:
            self.destroy()
            return

        self.meltdownLevel += 1

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1)
        event.setCallback({"container": self, "method": "handleTick"})
        currentTerrain = self.getTerrain()
        currentTerrain.addEvent(event)

    def render(self):
        if self.meltdownLevel:
            return (src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")
        return super().render()

src.items.addType(Contraption)

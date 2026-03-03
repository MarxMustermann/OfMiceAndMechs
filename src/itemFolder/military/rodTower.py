import numpy as np

import src

rodTower_texture = {}

class RodTower(src.items.Item):
    """
    ingame item used as ressource to build bombs and stuff
    should have the habit to explode at inconvienent times
    """

    type = "RodTower"
    name = "rod tower"
    description = "Hits the surrounding fields when activated"
    def __init__(self):
        """
        set up internal state
        """

        super().__init__(display="/\\")
        self.charges = 0
        self.coolDown = 10
        self.lastUsed = 0
        self.weapon = None

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        border_width = tileSize//10+1

        identifier = (fg_color,bg_color)
        texture = rodTower_texture.get(identifier)
        if not texture: 
            base_path = "config/tiles/"
            path = base_path+"RodTower.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            rodTower_texture[identifier] = texture
            print("rebuilding","RodTower.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

        renderer.draw_color = fg_color
        
        renderer.fill_rect((basePos[0],basePos[1],border_width,border_width))
        renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,border_width,border_width))
        renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,border_width))
        renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1]+tileSize-border_width,border_width,border_width))
            
        rod_color = (80,80,80,255)
            
        if self.bolted: 
            if self.container.getPositionWalkable(self.getPosition(offset=(0,-1,0))):
                renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
                renderer.draw_color = rod_color
                renderer.fill_rect((basePos[0]+tileSize-border_width//2,basePos[1],border_width,border_width*2))
                renderer.draw_color = fg_color
                        
            if self.container.getPositionWalkable(self.getPosition(offset=(-1,0,0))):
                renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
                renderer.draw_color = rod_color
                renderer.fill_rect((basePos[0],basePos[1]+tileSize//2-border_width//2,border_width*2,border_width))
                renderer.draw_color = fg_color

            if self.container.getPositionWalkable(self.getPosition(offset=(0,1,0))):
                renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
                renderer.draw_color = rod_color
                renderer.fill_rect((basePos[0]+tileSize//2-border_width//2,basePos[1]+tileSize-border_width*2,border_width,border_width*2))
                renderer.draw_color = fg_color

            if self.container.getPositionWalkable(self.getPosition(offset=(1,0,0))):
                renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))
                renderer.draw_color = rod_color
                renderer.fill_rect((basePos[0]+tileSize-border_width*2,basePos[1]+tileSize//2-border_width//2,border_width*2,border_width))
                renderer.draw_color = fg_color
        else:
            renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            renderer.fill_rect((basePos[0],basePos[1]+tileHeight-border_width,tileSize,border_width))
            renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))

    def apply(self, character):
        character.macroState["submenue"] = src.menuFolder.oneKeystrokeMenu.OneKeystrokeMenu("\npress j to confirm manually activating the RodTower",ignoreFirstKey=False,do_not_scale=True,tag="confirm_RodTower")
        character.macroState["submenue"].followUp = {"container":self,"method":"activate","params":{"character":character}}

    def activate(self,extraParams):
        if "keyPressed" in extraParams and extraParams["keyPressed"] != "j":
            return
        try:
            self.lastUsed
        except:
            self.lastUsed = 0
        try:
            self.coolDown
        except:
            self.coolDown = 10

        if not self.container:
            return

        if self.isInCoolDown():
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#f00", "black"), "XX")]})
            return

        self.lastUsed = src.gamestate.gamestate.tick

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "XX")]})

        neighbours = []
        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
            neighbours.append(self.getPosition(offset=offset))

        for neighbour in neighbours:
            if not self.container.getPositionWalkable(neighbour):
                continue
            self.container.addAnimation(neighbour,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#fff", "black"), "%%")]})
            targets = self.container.getCharactersOnPosition(neighbour)
            baseDamage = 2
            if self.weapon:
                baseDamage = self.weapon.baseDamage
                self.weapon.baseDamage -= 1
                if self.weapon.baseDamage == 10:
                    self.weapon = None
            baseDamage *= 4

            for target in targets:
                target.hurt(baseDamage*2,reason="hit by RodTower")

    def remoteActivate(self,extraParams=None):
        self.activate({})

    def isInCoolDown(self):
        if not (src.gamestate.gamestate.tick - self.lastUsed) > self.coolDown:
            return True
        else:
            return False

    def render(self):

        if self.isInCoolDown():
            return (src.interaction.urwid.AttrSpec("#444", "#000"), "RT")
        else:
            color = "#777"
            if self.weapon:
                color = "#888"
                if self.weapon.baseDamage >= 13:
                    color = "#999"
                if self.weapon.baseDamage >= 17:
                    color = "#aaa"
                if self.weapon.baseDamage >= 18:
                    color = "#bbb"
                if self.weapon.baseDamage >= 19:
                    color = "#ccc"
                if self.weapon.baseDamage >= 21:
                    color = "#ddd"
                if self.weapon.baseDamage >= 23:
                    color = "#eee"
                if self.weapon.baseDamage >= 25:
                    color = "#fff"

            return (src.interaction.urwid.AttrSpec(color, "#000"), "RT")

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
        options["w"] = ("replace weapon", self.replaceWeapon)
        return options

    def replaceWeapon(self,character):

        bestSword = None
        for item in character.inventory:
            if not item.type == "Sword":
                continue
            if bestSword == None:
                bestSword = item
                continue

            if item.baseDamage <= bestSword.baseDamage:
                continue

            bestSword = item

        if self.weapon:
            character.addToInventory(self.weapon)

        if bestSword:
            self.weapon = bestSword
            character.removeItemFromInventory(self.weapon)
        else:
            self.weapon = None

    def getLongInfo(self, character=None):

        result = ""
        result += "A contraption that hits all neighbouring fields when activated\n"
        if self.weapon:
            result += f"""
weapon: {self.weapon.baseDamage}
"""
        else:
            result += f"""
weapon: None
"""
        return result

src.items.addType(RodTower)

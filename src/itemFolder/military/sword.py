import random
import numpy as np

import src

sword_texture = {}

class Sword(src.items.Item):
    """
    ingame item used as ressource. basically does nothing
    """

    type = "Sword"

    name = "sword"
    description = "Used to hit people"
    usageInfo = "Activate the Sword to equip it"

    bolted = False
    walkable = True

    def __init__(self,generateFrom=None,badQuality=False):
        """
        set initial state
        """

        super().__init__(display="wt")

        if badQuality:
            self.baseDamage = 11
        else:
            self.baseDamage = int(random.triangular(10,25,15))

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        renderer.draw_color = bg_color
        renderer.fill_rect((basePos[0],basePos[1],tileSize,tileSize))

        identifier = (fg_color,bg_color)
        texture = sword_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path+"Sword.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            sword_texture[identifier] = texture
            print("rebuilding","Sword.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

    def degrade(self,multiplier=1,character=None):
        if self.baseDamage <= 10:
            return

        if random.random()*self.baseDamage*multiplier > 200:
            self.baseDamage -= 1
            if character:
                character.addMessage(f"your weapon degrades and now has {self.baseDamage} damage")

    def getLongInfo(self, character=None):
        """
        return a longer than normal description text

        Returns:
            the description text
        """

        text = super().getLongInfo(character)
        text += f"""
baseDamage:
{self.baseDamage}

"""
        return text

    # bad code: very hacky way of equiping things
    def apply(self, character):
        """
        handle a character trying to use this item
        by equiping itself on the player

        Parameters:
            character: the character trying to use the iten
        """

        character.addMessage(f"you equip the sword and wield a {self.baseDamage} weapon now")
        charSequence = []
        for i in range(2,self.baseDamage+1):
            char = str(i)
            if i < 10:
                char = " "+char
            charSequence.append(char)
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "wt")})
        character.container.addAnimation(character.getPosition(),"charsequence",len(charSequence)-1,{"chars":charSequence})
        character.container.addAnimation(character.getPosition(),"showchar",5,{"char":charSequence[-1]})
        character.container.addAnimation(character.getPosition(),"showchar",2,{"char":(src.interaction.urwid.AttrSpec("#fff", "black"), "wt")})

        oldWeapon = None
        if character.weapon:
            oldWeapon = character.weapon
            character.weapon = None

        character.weapon = self
        character.changed("equipedItem",(character,self))
        if self.container:
            self.container.removeItem(self)
        else:
            if self in character.inventory:
                character.removeItemFromInventory(self)

        if oldWeapon:
            if character.getFreeInventorySpace():
                character.addToInventory(oldWeapon)
            else:
                character.container.addItem(oldWeapon,character.getPosition())

    def upgrade(self):
        self.baseDamage += 1
        super().upgrade()

    def downgrade(self):
        self.baseDamage -= 1
        super().downgrade()

src.items.addType(Sword)

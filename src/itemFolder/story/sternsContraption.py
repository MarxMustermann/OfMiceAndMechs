import src

import random
import numpy as np

mainContraption_texture = {}

class MainContraption(src.items.Item):
    """
    """

    type = "MainContraption"
    description = "very weird machinery. It looks important"
    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "main contraption"

        self.walkable = False
        self.bolted = True
        self.meltdownLevel = 0

    def drawSDL(self, renderer, basePos, fg_color=(255,255,255,255), bg_color=(0,0,0,255), tileSize=None):

        if tileSize is None:
            tileSize = src.interaction.tileHeight

        border_width = tileSize//10+1

        identifier = (fg_color,bg_color)
        texture = mainContraption_texture.get(identifier)
        if not texture:
            base_path = "config/tiles/"
            path = base_path+"MainContraption.png"
            circle = src.interaction.tcod.image.Image.from_file(path)
            for x_index in range(0,circle.width):
                for y_index in range(0,circle.height):
                    color = circle.get_pixel(x_index,y_index)
                    if color == (255, 255, 255):
                        circle.put_pixel(x_index,y_index,fg_color[:3])
                    if color == (0, 0, 0):
                        circle.put_pixel(x_index,y_index,bg_color[:3])
            texture = renderer.upload_texture(np.asarray(circle))
            mainContraption_texture[identifier] = texture
            print("rebuilding","MainContraption.png",identifier)
        renderer.copy(texture, (0,0,texture.width,texture.height),(basePos[0],basePos[1],tileSize,tileSize),)

        renderer.draw_color = fg_color

        if self.bolted:
            items = self.container.getItemByPosition(self.getPosition(offset=(0,-1,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(-1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))

            items = self.container.getItemByPosition(self.getPosition(offset=(0,1,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))

            items = self.container.getItemByPosition(self.getPosition(offset=(1,0,0)))
            if not (len(items) == 1 and items[0].type in ("Contraption","Scrap","MainContraption",)):
                renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))
        else:
            renderer.fill_rect((basePos[0],basePos[1],tileSize,border_width))
            renderer.fill_rect((basePos[0],basePos[1],border_width,tileSize))
            renderer.fill_rect((basePos[0],basePos[1]+tileSize-border_width,tileSize,border_width))
            renderer.fill_rect((basePos[0]+tileSize-border_width,basePos[1],border_width,tileSize))

    def startMeltdown(self):
        self.handleTick()

    def handleTick(self):

        tick = src.gamestate.gamestate.tick%(15*15*15)

        if not self.meltdownLevel:
            if tick == 1:
                for i in range(1,20):
                    pos = (random.randint(1,13),random.randint(1,13),0)
                    self.container.addAnimation(pos,"smoke",6,{})
                    self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                    self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                    self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                contraptions = self.container.getItemsByType("Contraption")
                for i in range(1,3):
                    random.choice(contraptions).startMeltdown()

                self.container.addAnimation(self.getPosition(),"smoke",2,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            if tick == 2:
                for character in self.container.characters[:]:
                    character.addMessage("something explodes and sends shrapnel into the room")
                    character.hurt(character.health//2,reason="hit by shrapnel")
                    if character == src.gamestate.gamestate.mainChar:
                        src.interaction.send_tracking_ping("shrapnel_1")

            if tick > 6:
                self.container.addAnimation(self.getPosition(),"smoke",2,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick == 6:
                for character in self.container.characters[:]:
                    character.addMessage("something explodes into shrapnel")
                    character.hurt(25,reason="hit by shrapnel")
                    if character == src.gamestate.gamestate.mainChar:
                        src.interaction.send_tracking_ping("shrapnel_2")
                for i in range(1,2):
                    pos = (random.randint(1,13),random.randint(1,13),0)
                    self.container.addAnimation(pos,"smoke",6,{})
                    self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                contraptions = self.container.getItemsByType("Contraption")
                for i in range(1,3):
                    random.choice(contraptions).startMeltdown()

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick == 10:
                for character in self.container.characters[:]:
                    character.addMessage("your implant urges:\nleave the room!\nDo this by follow the suggested action\nIt is on the left side of the screen.")
                    if character == src.gamestate.gamestate.mainChar:
                        src.interaction.send_tracking_ping("room_message_1")
            if tick > 10:
                self.container.addAnimation(self.getPosition(),"smoke",4,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick == 15:
                for character in self.container.characters[:]:
                    character.addMessage("you hear a *BOOM* and *klink**klink**klink*")
                    character.hurt(30,reason="hit by shrapnel")
                    character.addMessage("your implant screams:\nleave NOW!\nDo this by follow the suggested action\nIt is shown on the left side of the screen.")
                    if character == src.gamestate.gamestate.mainChar:
                        src.interaction.send_tracking_ping("shrapnel_3")
                for i in range(1,3):
                    pos = (random.randint(1,13),random.randint(1,13),0)
                    self.container.addAnimation(pos,"smoke",6,{})
                    self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
                
                contraptions = self.container.getItemsByType("Contraption")
                for i in range(1,3):
                    random.choice(contraptions).startMeltdown()

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick > 15:
                self.container.addAnimation(self.getPosition(),"smoke",6,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            if tick == 18:
                for character in self.container.characters[:]:
                    character.addMessage("something big explodes and\nit sounds like something even bigger broke")
                    character.hurt(10,reason="hit by shrapnel")
                    text = []
                    text.append("\n"*5)
                    text.append(" "*5)
                    text.append("You need to leave the room NOW.")
                    text.append(" "*5)
                    text.append("\n"*3)
                    text.append(" "*5)
                    text.append("This room will explode and you will die.")
                    text.append(" "*5)
                    text.append("\n"*3)
                    text.append(" "*5)
                    text.append((src.interaction.urwid.AttrSpec("#f00", "#000"),"Follow the instruction on the left side of the screen."))
                    text.append(" "*5)
                    text.append("\n"*5)
                    character.showTextMenu(text,do_not_scale=True)
                    if character == src.gamestate.gamestate.mainChar:
                        src.interaction.send_tracking_ping("shrapnel_4")
                for i in range(1,5):
                    pos = (random.randint(1,13),random.randint(1,13),0)
                    self.container.addAnimation(pos,"smoke",6,{})
                    self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                contraptions = self.container.getItemsByType("Contraption")
                for i in range(1,3):
                    random.choice(contraptions).startMeltdown()

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick > 20:
                self.container.addAnimation(self.getPosition(),"smoke",10,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            self.container.addAnimation(self.getPosition(),"showchar",1+tick%10,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            if tick == 22:
                contraptions = self.container.getItemsByType("Contraption")
                for contraption in contraptions:
                    if not contraption.meltdownLevel:
                        contraption.startMeltdown()

            if tick == 33:
                self.meltdownLevel = 1
            if not self.container.characters:
                contraptions = self.container.getItemsByType("Contraption")
                intact_contraptions = []
                for contraption in contraptions:
                    if contraption.meltdownLevel:
                        continue
                    intact_contraptions.append(contraption)
                if len(intact_contraptions) < 7:
                    self.meltdownLevel = 1
                else:
                    for i in range(1,5):
                        random.choice(intact_contraptions).startMeltdown()
        else:
            contraptions = self.container.getItemsByType("Contraption")
            for contraption in contraptions:
                if not contraption.meltdownLevel:
                    contraption.startMeltdown()

            if self.meltdownLevel == 6:
                bigX = self.container.xPosition
                bigY = self.container.yPosition
                terrain = self.getTerrain()

                fg_colors = ["#faa","#c8a","#ca8","#c88"]
                bg_colors = ["#f00","#c00","#a11","#d11"]
                chars = ["#%","%$","%#"]
                for x in range(1,14):
                    for y in range(1,14):
                        terrain.addAnimation((bigX*15+x,bigY*15+y,0),"showchar",random.randint(3,5),{"char":[(src.interaction.urwid.AttrSpec(random.choice(fg_colors), random.choice(bg_colors)), "%%")]})
                        terrain.addAnimation((bigX*15+x,bigY*15+y,0),"showchar",random.randint(1,3),{"char":[(src.interaction.urwid.AttrSpec(random.choice(fg_colors), random.choice(bg_colors)), random.choice(chars))]})
                        terrain.addAnimation((bigX*15+x,bigY*15+y,0),"showchar",random.randint(1,2),{"char":[(src.interaction.urwid.AttrSpec(random.choice(fg_colors), random.choice(bg_colors)), random.choice(chars))]})
                        terrain.addAnimation((bigX*15+x,bigY*15+y,0),"showchar",2,{"char":[(src.interaction.urwid.AttrSpec("#c88", "#d11"), "~~")]})

                        amount = random.randint(1,10)
                        if x in (1,13,) or y in (1,13,):
                            amount = random.randint(8,15)
                        scrap = src.items.itemMap["Scrap"](amount=amount)
                        terrain.addItem(scrap,(bigX*15+x,bigY*15+y,0))
                terrain.scrapFields.append((bigX,bigY,0))

                """
                enemySpawns = [(4,6,0),(4,8,0),(3,10,0),(3,7,0),(5,8,0),(7,9,0)]
                if src.gamestate.gamestate.difficulty == "easy":
                    enemySpawns.remove((4,8,0))
                for bigPos in enemySpawns:
                    numEnemies = random.randint(1,5)
                    if bigPos == (5,8,0):
                        numEnemies = 5
                    for i in range(0,numEnemies):
                        enemy = src.characters.characterMap["Spider"]()
                        enemy.faction = "insects"

                        terrain.addCharacter(enemy,bigPos[0]*15+random.randint(3,12),bigPos[1]*15+random.randint(3,12))

                hunterSpawns = [(9,10,0),(10,9,0),(12,12,0)]
                for bigPos in hunterSpawns:
                    enemy = src.characters.characterMap["Hunter"]()
                    enemy.faction = "insects"
                    terrain.addCharacter(enemy,bigPos[0]*15+random.randint(3,12),bigPos[1]*15+random.randint(3,12))
                """

                for room_pos in ((6,6,0),(6,7,0),(6,8,0),(8,6,0),(8,7,0),(8,8,0),):
                    room = self.getTerrain().getRoomByPosition(room_pos)[0]

                    # add scrap
                    scrap_amount = 20
                    if room_pos == (8,6,0):
                        scrap_amount = 100
                    for _i in range(0,scrap_amount):
                        pos = (random.randint(1,11),random.randint(1,11),0)
                        if pos == (1,1,0) and room_pos == (6,6,0):
                            continue
                        if pos == (11,1,0) and room_pos == (8,6,0):
                            continue
                        if pos[1] == 1 and room_pos == (6,6,0):
                            continue
                        if pos in ((10,6,0),(6,11,0),(6,1,0),(1,6,0),):
                            continue

                        for item in room.getItemByPosition(pos)[:]:
                            item.destroy()

                        scrap = src.items.itemMap["Scrap"](amount=random.randint(1,10))
                        room.addItem(scrap,pos)

                    # add enemies
                    for _i in range(0,5):
                        crawler = src.characters.characterMap["Mechanical_Crawler"]()

                        quest = src.quests.questMap["SecureTile"](toSecure=room.getPosition())
                        quest.autoSolve = True
                        quest.assignToCharacter(crawler)
                        quest.activate()
                        crawler.quests.append(quest)

                        pos = (random.randint(3,9),random.randint(3,9),0)
                        room.addCharacter(crawler,pos[0],pos[1])

                self.container.destroy()
                return

            if self.meltdownLevel == 1:
                contraptions = self.container.getItemsByType("Contraption")
                for contraption in contraptions:
                    if random.random() < 0.5:
                        contraption.startMeltdown()

            if self.meltdownLevel > 4:
                src.interaction.send_tracking_ping("explosion_start_room")
                for character in self.container.characters[:]:
                    if not character.dead:
                        character.addMessage("you feel the floor shake\nand the walls move\nand everything explodes")
                        character.addMessage("you die")
                        character.die(reason="you died from explosion")
                        if character == src.gamestate.gamestate.mainChar:
                            src.interaction.send_tracking_ping("explosion_death")

            self.container.addAnimation(self.getPosition(),"smoke",2,{})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            for i in range(1*(self.meltdownLevel-3)*10):
                pos = (random.randint(1,13),random.randint(1,13),0)
                self.container.addAnimation(pos,"smoke",6,{})
                self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            self.container.addAnimation(self.getPosition(),"showchar",1+tick%10,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            self.meltdownLevel += 1

        event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+1)
        event.setCallback({"container": self, "method": "handleTick"})
        currentTerrain = self.getTerrain()
        currentTerrain.addEvent(event)

    def render(self):
        if self.meltdownLevel > 3:
            return (src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")
        
        color = "#888"
        tick = src.gamestate.gamestate.tick%(15*15*15)
        if tick > 10:
            color = "#f88"
        displaychars = "*]"

        display = [
                (src.interaction.urwid.AttrSpec(color, "black"), displaychars),
            ]
        return display

src.items.addType(MainContraption)

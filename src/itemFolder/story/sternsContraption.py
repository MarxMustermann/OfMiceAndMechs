import src
import random

class SternsContraption(src.items.Item):
    """
    """

    type = "SternsContraption"

    def __init__(self,epoch=0):
        """
        configure the superclass
        """

        super().__init__(display="!!")
        self.name = "sterns contraption"

        self.walkable = False
        self.bolted = True
        self.meltdownLevel = 0

    def getLongInfo(self):
        return f"{self.itemID}"

    def startMeltdown(self):
        self.handleTick()

    def handleTick(self):

        tick = src.gamestate.gamestate.tick%(15*15*15)

        if not self.meltdownLevel:
            if tick == 1:
                for character in self.container.characters[:]:
                    character.hurt(20,reason="shrapnel")
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

            if tick > 5:
                self.container.addAnimation(self.getPosition(),"smoke",2,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick == 5:
                for character in self.container.characters[:]:
                    character.hurt(25,reason="shrapnel")
                for i in range(1,2):
                    pos = (random.randint(1,13),random.randint(1,13),0)
                    self.container.addAnimation(pos,"smoke",6,{})
                    self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                contraptions = self.container.getItemsByType("Contraption")
                for i in range(1,3):
                    random.choice(contraptions).startMeltdown()

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick > 10:
                self.container.addAnimation(self.getPosition(),"smoke",4,{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})
            if tick == 15:
                for character in self.container.characters[:]:
                    character.hurt(30,reason="shrapnel")
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

            if tick == 20:
                for character in self.container.characters[:]:
                    character.hurt(10,reason="shrapnel")
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

            if tick == 25:
                self.meltdownLevel = 1
            if not self.container.characters:
                self.meltdownLevel = 1
        else:
            if self.meltdownLevel == 1:
                contraptions = self.container.getItemsByType("Contraption")
                for contraption in contraptions:
                    if random.random() < 0.5:
                        contraption.startMeltdown()

            if self.meltdownLevel > 4:
                for character in self.container.characters[:]:
                    character.die(reason="explosion")

            self.container.addAnimation(self.getPosition(),"smoke",2,{})
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            for i in range(1*(self.meltdownLevel-3)*10):
                pos = (random.randint(1,13),random.randint(1,13),0)
                self.container.addAnimation(pos,"smoke",6,{})
                self.container.addAnimation(pos,"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

                self.container.addAnimation(self.getPosition(),"smoke",random.randint(1,6),{})
                self.container.addAnimation(self.getPosition(),"showchar",1,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            self.container.addAnimation(self.getPosition(),"showchar",1+tick%10,{"char":[(src.interaction.urwid.AttrSpec("#faa", "#f00"), "%%")]})

            if self.meltdownLevel == 8:
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

                enemySpawns = [(4,6,0),(4,8,0),(3,9,0),(3,7,0),(5,9,0),(6,9,0)]
                for bigPos in enemySpawns:
                    for i in range(1,4):
                        enemy = src.characters.Statue()

                        quest = src.quests.questMap["SecureTile"](toSecure=bigPos)
                        quest.autoSolve = True
                        quest.assignToCharacter(enemy)
                        quest.activate()
                        enemy.quests.append(quest)

                        terrain.addCharacter(enemy,bigPos[0]*15+random.randint(2,13),bigPos[1]*15+random.randint(2,13))

                self.container.destroy()
                return
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

src.items.addType(SternsContraption)

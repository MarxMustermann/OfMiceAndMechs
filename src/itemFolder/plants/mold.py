import src
import random

class Mold(src.items.Item):
    type = "Mold"

    def __init__(self,xPosition=0,yPosition=0,creator=None,noId=False):
        super().__init__(src.canvas.displayChars.moss,xPosition,yPosition,creator=creator,name="mold")
        self.charges = 2
        self.walkable = True
        self.attributesToStore.extend([
               "charges"])

    def apply(self,character):
        character.satiation += 2
        if character.satiation > 1000:
            character.satiation = 1000
        self.destroy(generateSrcap=False)
        character.addMessage("you eat the mold and gain 2 satiation")

    def startSpawn(self):
        if self.charges and self.container:
            if not (self.xPosition and self.yPosition and self.terrain):
                return
            event = src.events.RunCallbackEvent(src.gamestate.gamestate.tick+(2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%1000,creator=self)
            event.setCallback({"container":self,"method":"spawn"})
            self.terrain.addEvent(event)

    def spawn(self):
        if self.charges and self.container:
            if not (self.xPosition and self.yPosition):
                return
            direction = (2*self.xPosition+3*self.yPosition+src.gamestate.gamestate.tick)%4
            direction = random.choice([0,1,2,3])
            if direction == 0:
                newPos = (self.xPosition,self.yPosition+1,self.zPosition)
            if direction == 1:
                newPos = (self.xPosition+1,self.yPosition,self.zPosition)
            if direction == 2:
                newPos = (self.xPosition,self.yPosition-1,self.zPosition)
            if direction == 3:
                newPos = (self.xPosition-1,self.yPosition,self.zPosition)

            #if (((newPos[0]%15 == 0 or newPos[0]%15 == 14) and not (newPos[1]%15 in (8,))) or
            #    ((newPos[1]%15 == 0 or newPos[1]%15 == 14) and not (newPos[0]%15 in (8,)))):
            #    return

            itemList = self.container.getItemByPosition(newPos)
            if not len(itemList):
                new = src.items.itemMap["Mold"](creator=self)
                new.xPosition = newPos[0]
                new.yPosition = newPos[1]
                self.container.addItems([new])
                new.startSpawn()
            elif len(itemList) > 0:
                if itemList[-1].type == "Mold":
                    self.charges += itemList[-1].charges//2
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["Sprout"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Sprout":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["Sprout2"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                elif itemList[-1].type == "Sprout2":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    if (newPos[0]%15,newPos[1]%15) in ((7,7,0),):
                        new = itemMap["CommandBloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                    elif (newPos[0]%15,newPos[1]%15) in ((1,7,0),(7,1,0),(13,7,0),(7,13,0)) and self.container.getItemByPosition((newPos[0]-newPos[0]%15+7,newPos[1]-newPos[1]%15+7,0)) and self.container.getItemByPosition((newPos[0]-newPos[0]%15+7,newPos[1]-newPos[1]%15+7,0))[-1].type == "CommandBloom":
                        new = itemMap["CommandBloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                    else:
                        new = src.items.itemMap["Bloom"](creator=self)
                        new.xPosition = newPos[0]
                        new.yPosition = newPos[1]
                        self.container.addItems([new])
                        new.startSpawn()
                elif itemList[-1].type == "Bloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["SickBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])
                    new.startSpawn()
                elif itemList[-1].type == "Corpse":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["PoisonBloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "SickBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "PoisonBloom":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["PoisonBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type == "Bush":
                    item = itemList[-1]
                    item.container.removeItem(item)
                    item.xPosition = None
                    item.yPosition = None

                    new = src.items.itemMap["EncrustedBush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                    new = src.items.itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type == "EncrustedBush":
                    new = src.items.itemMap["Bush"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                    itemList[-1].tryToGrowRoom(new)

                elif itemList[-1].type in ["PoisonBush","EncrustedPoisonBush"]:
                    new = src.items.itemMap["PoisonBloom"](creator=self)
                    new.xPosition = self.xPosition
                    new.yPosition = self.yPosition
                    self.container.addItems([new])
                    self.container.removeItem(self)

                elif itemList[-1].type in ["Coal"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = src.items.itemMap["Bush"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type in ["MoldFeed"]:
                    itemList[-1].destroy(generateSrcap=False)

                    new = src.items.itemMap["Bloom"](creator=self)
                    new.xPosition = newPos[0]
                    new.yPosition = newPos[1]
                    self.container.addItems([new])

                elif itemList[-1].type in ["CommandBloom"]:
                    itemList[-1].charges += 1

        self.charges -= 1
        if self.charges:
            self.startSpawn()

    def getLongInfo(self):
        return """
item: Mold

description:
This is a patch of mold

you can eat it to gain 2 satiation.
"""

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

src.items.addType(Mold)

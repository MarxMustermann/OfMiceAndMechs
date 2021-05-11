import src

class Mortar(src.items.Item):
    type = "Mortar"
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="mortar",creator=None,noId=False):

        super().__init__(src.canvas.displayChars.mortar,xPosition,yPosition,creator=creator,name=name)
        
        self.bolted = False
        self.loaded = False
        self.loadedWith = None
        self.precision = 5

        self.attributesToStore.extend([
               "loaded","precision"])

    def apply(self,character):
        if not self.loaded:
            itemFound = None
            for item in character.inventory:
                if item.type == "Bomb":
                    itemFound = item
                    continue

            if not itemFound:
                character.addMessage("could not load mortar. no bomb in inventory")
                return

            character.addMessage("you load the mortar")

            character.inventory.remove(itemFound)
            self.loadedWith = itemFound
            self.loaded = True
        else:
            if not self.loadedWith:
                self.loaded = False
                return
            character.addMessage("you fire the mortar")
            bomb = self.loadedWith
            self.loadedWith = None
            self.loaded = False

            bomb.yPosition = self.yPosition
            bomb.xPosition = self.xPosition
            bomb.bolted = False

            distance = 10
            if (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision == 0:
                character.addMessage("you missfire (0)")
                self.precision += 10
                distance -= src.gamestate.gamestate.tick%10-10//2
                character.addMessage((distance,src.gamestate.gamestate.tick%10,10//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision == 1:
                character.addMessage("you missfire (1)")
                self.precision += 5
                distance -= src.gamestate.gamestate.tick%7-7//2
                character.addMessage((distance,src.gamestate.gamestate.tick%7,7//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision < 10:
                character.addMessage("you missfire (10)")
                self.precision += 2
                distance -= src.gamestate.gamestate.tick%3-3//2
                character.addMessage((distance,src.gamestate.gamestate.tick%3,3//2))
            elif (src.gamestate.gamestate.tick+self.yPosition+self.xPosition)%self.precision < 100:
                character.addMessage("you missfire (100)")
                self.precision += 1
                distance -= src.gamestate.gamestate.tick%2-2//2
                character.addMessage((distance,src.gamestate.gamestate.tick%2,2//2))

            bomb.yPosition += distance

            self.container.addItems([bomb])

            bomb.destroy()

    def getLongInfo(self):

        text = """

A mortar. Load it with bombs and activate it to fire.

It fires 10 steps to the south. Its current precision is """+str(self.precision)+""".

"""
        return text

src.items.addType(Mortar)

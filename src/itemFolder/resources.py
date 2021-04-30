import src

'''
crushed something, basically raw metal
'''
class Scrap(src.items.ItemNew):
    type = "Scrap"
        
    '''
    almost straightforward state initialization
    '''
    def __init__(self,xPosition=0,yPosition=0,amount=1,name="scrap",creator=None,noId=False):

        self.amount = 1

        super().__init__(src.canvas.displayChars.scrap_light,xPosition,yPosition,creator=creator,name=name)
        
        # set up metadata for saveing
        self.attributesToStore.extend([
               "amount"])
        
        self.bolted = False

        self.amount = amount

        self.setWalkable()

    '''
    move the item and leave residue
    '''
    def moveDirection(self,direction,force=1,initialMovement=True):
        self.dropStuff()
        super().moveDirection(direction,force,initialMovement)

    '''
    leave a trail of pieces
    bad code: only works on terrain
    '''
    def dropStuff(self):
        self.setWalkable()

        # only drop something if there is something left to drop
        if self.amount <= 1:
            return

        # determine how much should fall off
        fallOffAmount = 1
        if self.amount > 2:
            fallOffAmount = 2

        # remove scrap from self
        self.amount -= fallOffAmount

        # generate the fallen off scrap
        newItem = Scrap(self.xPosition,self.yPosition,fallOffAmount,creator=self)
        newItem.room = self.room
        newItem.terrain = self.terrain

        # place the fallen off parts on map
        # bad code: should be handled by terrain
        self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)].append(newItem)
        self.terrain.itemsOnFloor.append(newItem)

    '''
    recalculate the walkable attribute
    '''
    def setWalkable(self):
        if self.amount < 5:
            self.walkable = True
        else:
            self.walkable = False
      
    '''
    recalculate the display char
    '''
    @property
    def display(self):
        if self.amount < 5:
            return src.canvas.displayChars.scrap_light
        elif self.amount < 15:
            return src.canvas.displayChars.scrap_medium
        else:
            return src.canvas.displayChars.scrap_heavy
                
    '''
    get resistance to beeing moved depending on size
    '''
    def getResistance(self):
        return self.amount*2

    '''
    destroying scrap means to merge the scrap 
    '''
    def destroy(self, generateSrcap=True):
        # get list of scrap on same location
        # bad code: should be handled in the container
        foundScraps = []
        for item in self.container.itemByCoordinates[(self.xPosition,self.yPosition)]:
            if type(item) == Scrap:
                foundScraps.append(item)
        
        # merge existing and new scrap
        if len(foundScraps) > 1:
            for item in foundScraps:
                if item == self:
                    continue
                self.amount += item.amount
                # bad code: direct manipulation of terrain state
                self.container.itemByCoordinates[(self.xPosition,self.yPosition)].remove(item)

    def getLongInfo(self):
        text = """
item: Scrap

description:
Scrap is a raw material. Its main use is to be converted to metal bars in a scrap compactor.

There is %s in this pile
"""%(self.amount,)

        return text

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.amount <= 1:
            super().pickUp(character)
            return

        if self.xPosition == None or self.yPosition == None:
            return

        foundBig = False
        for item in character.inventory:
            if item.walkable == False:
                foundBig = True
                break
        self.amount -= 1

        character.addMessage("you pick up a piece of scrap, there is %s left"%(self.amount,))

        # add item to characters inventory
        character.inventory.append(Scrap(amount=1,creator=self))

    '''
    get picked up by the supplied character
    '''
    def apply(self,character):
        scrapFound = []
        for item in character.inventory:
            if item.type == "Scrap":
                scrapFound.append(item)
                break

        for item in scrapFound:
            if self.amount < 20:
                self.amount += item.amount
                character.addMessage("you add a piece of scrap there pile contains %s scrap now."%(self.amount,))
                character.inventory.remove(item)

        self.setWalkable()

'''
basically refined scrap and the default resource
'''
class MetalBars(src.items.ItemNew):
    type = "MetalBars"

    def __init__(self,xPosition=0,yPosition=0,name="metal bar",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.metalBars,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False 

    def getLongInfo(self):
        text = """ 
item: MetalBars

description:
A metal bar is a raw resource. It is used by most machines and produced by a scrap compactor.

"""
        return text

'''
'''
class Case(src.items.ItemNew):
    type = "Case"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="case",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.case,xPosition,yPosition,name=name,creator=creator)

    def getLongInfo(self):
        text = """

A case. Is complex building item. It is used to build bigger things.

"""
        return text

'''
'''
class PocketFrame(src.items.ItemNew):
    type = "PocketFrame"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="pocket frame",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.pocketFrame,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True

    def getLongInfo(self):
        text = """

A pocket frame. Is complex building item. It is used to build smaller things.

"""
        return text

'''
basic item with different appearance
'''
class Coal(src.items.Item):
    type = "Coal"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Coal",creator=None,noId=False):
        self.canBurn = True
        super().__init__(src.canvas.displayChars.coal,xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = False

    def getLongInfo(self):
        text = """
item: Coal

description:
Coal is used as an energy source. It can be used to fire furnaces.

"""
        return text

    def destroy(self, generateSrcap=True):
        super().destroy(generateSrcap=False)

    def apply(self,character):
        if not self.xPosition:
            return

        if isinstance(character,src.characters.Monster) and character.phase == 1 and ((gamestate.tick+self.xPosition)%10 == 5):
            newChar = characters.Exploder(creator=self)
            import copy
            newChar.macroState = character.macroState
            character.macroState = {}
            newChar.satiation = character.satiation
            newChar.explode = False

            newChar.solvers = [
                      "NaiveActivateQuest",
                      "ActivateQuestMeta",
                      "NaiveExamineQuest",
                      "ExamineQuestMeta",
                      "NaivePickupQuest",
                      "NaiveMurderQuest",
                      "DrinkQuest",
                      "NaiveDropQuest",
                    ]

            self.container.addCharacter(newChar,self.xPosition,self.yPosition)
            character.die()
            self.destroy(generateSrcap=False)
        else:
            super().apply(character)

import src

'''
a pile of stuff to take things from
this doesn't hold objects but spawns them
'''
class Pile(src.items.Item):
    type = "Pile"

    '''
    call superclass constructor with modified paramters and set some state
    '''
    def __init__(self,xPosition=0,yPosition=0,name="pile",itemType="Coal",creator=None,noId=False):
        self.contains_canBurn = True # bad code: should be abstracted
        self.itemType = itemType
        self.numContained = 100
        super().__init__(src.canvas.displayChars.pile,xPosition,yPosition,name=name,creator=creator)

        # set metadata for saving
        self.attributesToStore.extend([
               "numContained"])

    '''
    take from the pile
    '''
    def apply(self,character):
        # write log on impossible state
        if self.numContained < 1:
            debugMessages.append("something went seriously wrong. I should have morphed by now")
            return

        # check characters inventory
        if len(character.inventory) > 10:
            character.addMessage("you cannot carry more items")
            return

        # spawn item to inventory
        character.inventory.append(self.itemType(creator=self))
        character.changed()
        character.addMessage("you take a piece of "+str(self.itemType.type))

        # reduce item count
        self.numContained -= 1

        # morph into a single item
        if self.numContained == 1:
            self.room.removeItem(self)
            new = self.itemType(creator=self)
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition
            self.room.addItems([new])

        super().apply(character,silent=True)

    '''
    print info with item counter
    '''
    def getDetailedInfo(self):
        return super().getDetailedInfo()+" of "+str(self.itemType.type)+" containing "+str(self.numContained)

    def getLongInfo(self):
        text = """
item: Pile

description:
A Pile. Use it to take coal from it

"""
        return text

import src

'''
a vending machine basically
bad code: currently only dispenses goo flasks
'''
class ObjectDispenser(src.items.Item):
    type = "ObjectDispenser"

    '''
    '''
    def __init__(self,xPosition=None,yPosition=None, name="object dispenser",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.objectDispenser,xPosition,yPosition,name=name,creator=creator)

        self.storage = []
        counter = 0
        while counter < 5:
            self.storage.append(GooFlask(creator=self))
            counter += 1

    '''
    drop goo flask
    '''
    def dispenseObject(self):
        if len(self.storage):
            new = self.storage.pop()
            new.xPosition = self.xPosition
            new.yPosition = self.yPosition+1
            self.room.addItems([new])
        else:
            src.logger.debugMessages.append("the object dispenser is empty")

    def getLongInfo(self):
        text = """
item: ObjectDispenser

description:
A object dispenser holds and returns objects.

You can use it to retrieve an object from the object dispenser.

"""
        return text

src.items.addType(ObjectDispenser)

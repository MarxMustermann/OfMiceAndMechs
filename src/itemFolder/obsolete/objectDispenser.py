import logging

import src

"""
a vending machine basically
bad code: currently only dispenses goo flasks
"""

logger = logging.getLogger(__name__)

class ObjectDispenser(src.items.Item):
    type = "ObjectDispenser"

    """
    """

    def __init__(self):
        super().__init__(display=src.canvas.displayChars.objectDispenser)
        self.name = "object dispenser"

        self.storage = []
        counter = 0
        while counter < 5:
            self.storage.append(src.items.itemMap["GooFlask"]())
            counter += 1

    """
    drop goo flask
    """

    def dispenseObject(self):
        if len(self.storage):
            new = self.storage.pop()
            self.container.addItem(new,(self.xPosition,self.yPosition+1,self.zPosition))
        else:
            logger.debug("the object dispenser is empty")

    def getLongInfo(self):
        text = """
item: ObjectDispenser

description:
A object dispenser holds and returns objects.

You can use it to retrieve an object from the object dispenser.

"""
        return text


src.items.addType(ObjectDispenser)

import src

class SparcRewardLock(src.items.Item):
    type = "SparcRewardLock"

    def __init__(self,xPosition=0,yPosition=0,name="SaccrificialCircle",creator=None,noId=False):
        super().__init__("%°",xPosition,yPosition,name=name,creator=creator)
        self.walkable = True
        self.bolted = True

    def apply(self,character):
        foundItem = None
        for item in character.inventory:
            if item.type == "StaticCrystal":
                foundItem = item
                break

        if not foundItem:
            character.addMessage("no static crystal in inventory - insert to claim reward")
            return

        character.inventory.append(foundItem)
        character.addMessage("well done")

src.items.addType(SparcRewardLock)

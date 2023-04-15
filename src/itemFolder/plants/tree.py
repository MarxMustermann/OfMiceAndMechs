import src
import random

class Tree(src.items.Item):
    """
    ingame item serving as an infinite food source
    """

    type = "Tree"
    bolted = True
    walkable = False
    numMaggots = 0
    name = "tree"

    def __init__(self):
        """
        initialise internal state
        """

        super().__init__(display=src.canvas.displayChars.tree)

        self.maxMaggot = random.randint(75, 150)

        try:
            self.lastUse = src.gamestate.gamestate.tick
        except:
            self.lastUse = -100000

        self.attributesToStore.extend(["maggot", "maxMaggot", "lastUse"])

    def regenerateMaggots(self):
        """
        regenerate maggots to account for passed time
        """

        self.numMaggots += (src.gamestate.gamestate.tick - self.lastUse) // 10
        self.numMaggots = min(self.numMaggots, self.maxMaggot)

    def apply(self, character):
        """
        handle a character trying to use this item
        by dropping some food

        Parameters:
            character: the character 
        """

        if not self.container:
            character.addMessage("The tree has to be on the outside to be used")
            return

        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        character.addMessage("you harvest a vat maggot")
        character.frustration += 1

        targetFull = False
        targetPos = (self.xPosition + 1, self.yPosition, self.zPosition)
        items = self.container.getItemByPosition(targetPos)
        if len(items) > 15:
            targetFull = True
        for item in items:
            if item.walkable == False:
                targetFull = True

        if targetFull:
            character.addMessage("the target area is full, you harvest no moaggots")
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"XX")})
            self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#740", "black"),"[]")})
            return

        if not self.numMaggots:
            self.container.addAnimation(self.getPosition(),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
            character.addMessage("The tree has no maggots left")
            return

        # spawn new item
        self.numMaggots -= 1
        new = src.items.itemMap["VatMaggot"]()
        new.bolted = False
        self.container.addItem(new,(self.xPosition+1,self.yPosition,self.zPosition))

        self.container.addAnimation(self.getPosition(),"showchar",1,{"char":"~-"})
        self.container.addAnimation(self.getPosition(offset=(1,0,0)),"showchar",1,{"char":"~-"})

    def getLongInfo(self):
        """
        returns a longer than normal description text
        this recalculates the internal state and has side effects

        Returns:
            the decription text
        """

        self.regenerateMaggots()
        self.lastUse = src.gamestate.gamestate.tick

        text = super().getLongInfo()
        text += """
numMaggots: %s

description:
A tree can be used as a source for vat maggots.

Activate the tree to harvest a vat maggot.

""" % (
            self.numMaggots,
        )
        return text

src.items.addType(Tree)

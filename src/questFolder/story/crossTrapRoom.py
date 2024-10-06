import src


class CrossTrapRoom(src.quests.MetaQuestSequence):
    type = "CrossTrapRoom"

    def __init__(self, description="cross trap room", creator=None, lifetime=None, targetPosition=None, paranoid=False, showCoordinates=True,direction=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason


    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        baseCommand = "d"
        nextPos = (character.xPosition+1,character.yPosition,0)
        if character.yPosition < 6:
            baseCommand = "s"
            nextPos = (character.xPosition,character.yPosition+1,0)
        elif character.yPosition > 6:
            baseCommand = "w"
            nextPos = (character.xPosition,character.yPosition-1,0)

        items = character.container.getItemByPosition(nextPos)
        
        # save to move
        if (not items) or (items[0].type != "TriggerPlate"):
            return (None,(baseCommand,"move"))

        # block trigger plates
        if character.inventory and character.inventory[-1].walkable:
            return (None,("L"+baseCommand,"block TrickerPlate"))

        # check of traps are in cooldown
        foundActiveTrap = False
        for offset in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0)):
            checkPos = (nextPos[0]+offset[0],nextPos[1]+offset[1],nextPos[2]+offset[2])

            for item in character.container.getItemByPosition(checkPos):
                if item.type != "RodTower":
                    continue
                if item.isInCoolDown():
                    continue
                foundActiveTrap = True
                break

        if not foundActiveTrap:
            return (None,(baseCommand,"step on disabled trap"))
        
        return (None,("J"+baseCommand,"trigger trap"))


    def generateTextDescription(self):
        triggerPlate = src.items.itemMap["TriggerPlate"]()
        rodTower = src.items.itemMap["RodTower"]()

        return ["""
The bases defence seems to be working,
but they seem to register us as threat.
We need to circumvent the defenses.

The design is pretty old:
The TriggerPlates """,triggerPlate.render(),""" are cennected to the RodTowers """,rodTower.render(),""".
So if you step on the TriggerPlate the RodTower whacks you.

There are two ways you can bypass those traps:

1. Put items on top of the TriggerPlates. 
That prevents them from triggering and you can savely step on them.

2. Activate the TriggerPlates from the sides.
That makes the RodTowers hit the air and they will not work for some time.
During that time you can step onto the TriggerPlate without getting harmed.
"""]

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.wrapedTriggerCompletionCheck, "moved")
        super().assignToCharacter(character)

    def wrapedTriggerCompletionCheck(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        self.triggerCompletionCheck(extraInfo[0])

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if character.getBigPosition() == (5,7,0):
            return False

        self.postHandler()

src.quests.addType(CrossTrapRoom)

import src


class ActivateRegenerator(src.quests.MetaQuestSequence):
    type = "ActivateRegenerator"

    def __init__(self, description="activate the regenerator", creator=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description

    def handleRegeneratorActivated(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleRegeneratorActivated, "regenerator activated")

        return super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        # check if the regenerator was activated
        regenerator = None
        terrain = character.getTerrain()
        for room in terrain.rooms:
            regenerator = room.getItemByType("Regenerator",needsBolted=True)
            if regenerator:
                break
        if regenerator and regenerator.activated:
            if not dryRun:
                self.postHandler()
            return True
        
        return False

    def getNextStep(self,character,ignoreCommands=False,dryRun=True):

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        
        # handle most menus
        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))
        
        # enter rooms properly
        if character.xPosition%15 == 7 and character.yPosition%15 == 14:
            return (None,("w","enter the tile"))
        if character.xPosition%15 == 7 and character.yPosition%15 == 0:
            return (None,("s","enter the tile"))
        if character.xPosition%15 == 14 and character.yPosition%15 == 7:
            return (None,("a","enter the tile"))
        if character.xPosition%15 == 0 and character.yPosition%15 == 7:
            return (None,("d","enter the tile"))

        # activate correct item when marked
        action = self.generate_confirm_interaction_command(allowedItems=("Regenerator","CoalBurner"))
        if action:
            return action

        # find regenerator
        regenerator = None
        terrain = character.getTerrain()
        for room in terrain.rooms:
            regenerator = room.getItemByType("Regenerator",needsBolted=True)
            if regenerator:
                break

        # go to regenerator
        if character.getBigPosition() != regenerator.container.getPosition():
            quest = src.quests.questMap["GoToTile"](targetPosition=regenerator.container.getPosition(),description="go to the temple",reason="to reach the regenerator")
            return ([quest],None)
        if character.getDistance(regenerator.getPosition()) > 1:
            quest = src.quests.questMap["GoToPosition"](targetPosition=regenerator.getPosition(),ignoreEndBlocked=True,description="go to the Regenerator",reason="to activate the regenerator")
            return ([quest],None)
        
        # use regenerator
        t_pos = regenerator.getPosition()
        pos = character.getPosition()
        direction = "."
        if (pos[0]-1,pos[1],pos[2]) == t_pos:
            direction = "a"
        if (pos[0]+1,pos[1],pos[2]) == t_pos:
            direction = "d"
        if (pos[0],pos[1]-1,pos[2]) == t_pos:
            direction = "w"
        if (pos[0],pos[1]+1,pos[2]) == t_pos:
            direction = "s"
        interactionCommand = "J"
        if submenue:
            if submenue.tag == "advancedInteractionSelection":
                interactionCommand = ""
            else:
                return (None,(["esc"],"close menu"))
        return (None,(interactionCommand+direction,"activate the Regenerator"))

    def generateTextDescription(self):
        text = ["""
You reach out to your implant and it answers:

The base has some clones now and there are many enemies to be slain.
There will be fights and somebody will get hurt
Time will heal wounds, but that can be sped up.

The base has a Regenerator. It is located in the temple.
It will heal all nearby creatures faster.
Activate it so you and the other clones heal while waiting in the temple.
"""]
        return text

    def getQuestMarkersSmall(self,character,renderForTile=False):
        '''
        return the quest markers for the normal map
        '''
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if not renderForTile:
            if isinstance(character.container,src.rooms.Room):
                for item in character.container.itemsOnFloor:
                    if not item.type == "Regenerator":
                        continue
                    if not item.bolted:
                        continue
                    result.append((item.getPosition(),"target"))
        return result

src.quests.addType(ActivateRegenerator)

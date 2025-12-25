import src


class BrewPotion(src.quests.MetaQuestSequence):
    type = "BrewPotion"

    def __init__(self, description="brew potion", creator=None, lifetime=None, potionType=None, amount=1):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = description

        self.shortCode = "e"
        self.potionType = potionType
        self.amount = amount

    def handleBrewedPotions(self,extraInfo=None):
        try:
            self.amount
        except:
            self.amount = 1
        if self.amount and self.amount > 1:
            self.amount -= 1
            return
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleBrewedPotions, "brewed potion")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False
        return False

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        if not character.container.isRoom:
            pos = character.getSpacePosition()
            if pos == (14,7,0):
                return (None,("a","enter room"))
            if pos == (0,7,0):
                return (None,("d","enter room"))
            if pos == (7,14,0):
                return (None,("w","enter room"))
            if pos == (7,0,0):
                return (None,("s","enter room"))

        # activate production item when marked
        if character.macroState.get("itemMarkedLast"):
            item = character.macroState["itemMarkedLast"]
            if item.type == "AlchemyTable":
                return (None,("j","activate AlchemyTable"))
            else:
                return (None,(".","undo selection"))

        # ensure inventory space
        if not character.getFreeInventorySpace():
            quest = src.quests.questMap["ClearInventory"]()
            return ([quest],None)

        submenue = character.macroState["submenue"]
        if submenue and not ignoreCommands:
            if isinstance(submenue,src.menuFolder.selectionMenu.SelectionMenu):
                if submenue.tag == "alchemyTableProductSelection":
                    selectionCommand = "j"
                    amount = self.amount
                    if amount is None:
                        amount = submenue.extraInfo["item"].get_amount_producable(self.potionType,character)
                    if amount > 1:
                        selectionCommand = "J"
                    action = submenue.get_command_to_select_option(self.potionType,selectionCommand=selectionCommand)
                    if action:
                        return (None,(action,"produce item"))

                    action = submenue.get_command_to_select_option("byName")
                    if action:
                        return action

                    return (None,(["esc"],"close menu"))
                else:
                    return (None,(submenue.get_command_to_select_option("produce potion"),"start brewing"))

            if submenue.tag == "metalWorkingAmountInput":
                amount = self.amount
                if amount is None:
                    amount = submenue.extraInfo["item"].get_amount_producable(self.potionType,character)
                return (None,(submenue.get_command_to_input(str(amount)),"enter amount to produce"))

            if submenue.tag not in ("advancedInteractionSelection",):
                return (None,(["esc"],"close menu"))

        terrain = character.getTerrain()

        if not character.searchInventory("Flask"):
            quest = src.quests.questMap["FetchItems"](toCollect="Flask",amount=1)
            return ([quest],None)

        if not character.searchInventory("ManaCrystal"):
            quest = src.quests.questMap["FetchItems"](toCollect="ManaCrystal",amount=1)
            return ([quest],None)

        if not character.searchInventory("Bloom"):
            quest = src.quests.questMap["FetchItems"](toCollect="Bloom",amount=1)
            return ([quest],None)

        if character.container.isRoom:
            offsets = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
            for offset in offsets:
                pos = character.getPosition(offset=offset)
                items = character.container.getItemByPosition(pos)
                if not items:
                    continue

                if not items[0].type == "AlchemyTable":
                    continue
                
                message = "start brewing a potion"
                if offset == (0,0,0):
                    return (None,(list("j"),message))

                interactionCommand = "J"
                if submenue:
                    if submenue.tag == "advancedInteractionSelection":
                        interactionCommand = ""
                    else:
                        return (None,(["esc"],"close menu"))
                if offset == (1,0,0):
                    return (None,(list(interactionCommand+"d"),message))
                if offset == (-1,0,0):
                    return (None,(list(interactionCommand+"a"),message))
                if offset == (0,1,0):
                    return (None,(list(interactionCommand+"s"),message))
                if offset == (0,-1,0):
                    return (None,(list(interactionCommand+"w"),message))


            for item in character.container.itemsOnFloor:
                if not item.type == "AlchemyTable":
                    continue
                if not item.bolted:
                    continue

                if character.getDistance(item.getPosition()) > 1:
                    quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),description="go to AlchemyTable",ignoreEndBlocked=True)
                    return ([quest],None)

        for room in terrain.rooms:
            for item in room.itemsOnFloor:
                if not item.type == "AlchemyTable":
                    continue
                if not item.bolted:
                    continue

                quest = src.quests.questMap["GoToTile"](targetPosition=room.getPosition(),description="go to a room having a AlchemyTable")
                return ([quest],None)

        return (None,(".","stand around confused"))

    def generateTextDescription(self):
        text = [f"""
Brew a potion of the type {self.potionType}
"""]
        amount = self.amount
        if amount is None:
            amount = "some amount of"
        text.append(f"produce {self.amount} potions")
        return text

    def handleQuestFailure(self,extraParam):
        self.fail(extraParam["reason"])

src.quests.addType(BrewPotion)

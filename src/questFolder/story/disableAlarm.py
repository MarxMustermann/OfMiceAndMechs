import src


class DisableAlarm(src.quests.MetaQuestSequence):
    type = "DisableAlarm"

    def __init__(self, description="disable alarm", creator=None, lifetime=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description

    def getTargetRoom(self):
        terrain = self.character.getTerrain()
        for room in terrain.rooms:
            if room.getItemByType("SiegeManager"):
                return room
        return None

    def getNextStep(self,character=None,ignoreCommands=False,dryRun=True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        # set up helper variables
        terrain = character.getTerrain()

        # heal
        if character.health < character.adjustedMaxHealth - 20 and character.canHeal():
            interaction_command = "J"
            if submenue:
                if submenue.tag == "advancedInteractionSelection":
                    interaction_command = ""
                else:
                    return (None,(["esc"],"close menu"))
            return (None,(interaction_command+"H","heal"))
        if character.health < character.adjustedMaxHealth//5:
            return self._solver_trigger_fail(dryRun,"low health")

        # get the target room
        room = self.getTargetRoom()
        if not room:
            return self._solver_trigger_fail(dryRun,"no siege manager found")
        targetposition = room.getPosition()

        # clear the target
        if terrain.getEnemiesOnTile(character,targetposition):
            quest = src.quests.questMap["SecureTile"](toSecure=targetposition,endWhenCleared=True)
            return ([quest],None)

        # disable the alarm
        quest = src.quests.questMap["LiftOutsideRestrictions"]()
        return ([quest],None)

    def generateTextDescription(self):
        room = self.getTargetRoom()
        if room:
            targetPosition = room.getPosition()
            character_position = self.character.getBigPosition()
            direction_string = self.character.getTerrain().getDistanceDescription(character_position,targetPosition)
            direction_string = f"The room with the SiegeManager is {direction_string}.\n"
            if character_position == targetPosition:
                direction_string = "You are in the room with the SiegeManager"
        else:
            direction_string = "The target room is missing."

        sample_siegeManager = src.items.itemMap["SiegeManager"]()
        text = ["""
The groundskeeper is not willing to leave its room as long as the alarm is running.
""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Disable the alarm."),f"""
Use the SiegeManager (""",sample_siegeManager.metaRender(),f""") to unrestrict the outside movement.

{direction_string}
"""]
        return text

    def triggerCompletionCheck(self,character=None,dryRun=True):
        if not character:
            return False

        if not character.getTerrain().alarm:
            if not dryRun:
                self.postHandler()
            return True
        return False

src.quests.addType(DisableAlarm)

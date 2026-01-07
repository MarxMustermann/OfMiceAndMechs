import random

import src

class SearchForRuins(src.quests.MetaQuestSequence):
    '''
    quest to adventure and collect cool stuff
    '''
    type = "SearchForRuins"
    def __init__(self, description="search for ruins", creator=None, lifetime=None, reason=None):
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        self.track = []

    def getNextStep(self,character=None,ignoreCommands=False, dryRun = True):
        '''
        generate the next step towards solving this quest
        Parameters:
            character:       the character doing the quest
            ignoreCommands:  whether to generate commands or not
            dryRun:          flag to be stateless or not
        Returns:
            the activity to run as next step
        '''

        # handle weird edge cases
        if self.subQuests:
            return (None,None)
        if not character:
            return (None,None)

        # get all reasonable candidates to move to with desirability
        candidates = []
        extraWeight = {}
        for x in range(1,14):
            for y in range(1,14):
                coordinate = (x, y, 0)
                extraWeight[coordinate] = 1
                if coordinate in character.terrainInfo:
                    info = character.terrainInfo[coordinate]
                    if not info.get("tag") == "ruin":
                        extraWeight[coordinate] = 30000
                        continue
                    if info.get("looted"):
                        extraWeight[coordinate] = 30000
                        continue
                    extraWeight[coordinate] = 0
                if coordinate == (7,7,0): # avoid endgame dungeon
                    extraWeight[coordinate] = 32000
                candidates.append(coordinate)

        # fail on weird state
        if not len(candidates):
            self._solver_trigger_fail(dryRun,"no candidates")

        # sort nearest target candidate skewed by desirebility with slight random
        best_candidate = None
        best_distance = None
        current_pos = character.getTerrainPosition()
        for candidate in candidates:
            distance = src.helpers.distance_between_points(current_pos, candidate)
            distance += extraWeight[candidate]
            distance += random.random()
            if best_candidate is None or distance < best_distance:
                best_distance = distance
                best_candidate = candidate
        targetTerrain = best_candidate

        # move to the actual target terrain
        reason = "check for ruin"
        if targetTerrain in character.terrainInfo:
            reason = "go to ruin"
        quest = src.quests.questMap["GoToTerrain"](targetTerrain=targetTerrain,reason=reason)
        return ([quest], None)

    def generateTextDescription(self):
        '''
        generate a textual description to be shown on the UI
        '''
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        
        text = [f"""
Find an unexplored ruin{reason}.
"""]
        return text

    def handleChangedTerrain(self,extraInfo):
        '''
        check if ruin was walked into
        '''
        self.triggerCompletionCheck(self.character)

    def assignToCharacter(self, character):
        '''
        listen to the character changing the terrain
        '''
        if self.character:
            return

        self.startWatching(character,self.handleChangedTerrain, "changedTerrain")
        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None,dryRun=True):
        '''
        check and end quest if completed
        '''
        if not character:
            return False

        currentTerrain = character.getTerrain()
        if not currentTerrain.tag == "ruin":
            return False

        info = character.terrainInfo[currentTerrain.getPosition()]
        if info.get("looted"):
            return False

        if not dryRun:
            self.postHandler()
        return True

# register the quest type
src.quests.addType(SearchForRuins)

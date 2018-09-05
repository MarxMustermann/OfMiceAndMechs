import json
import src.characters as characters

class Void():
    id = "void**#"
    creationCounter = 0

    def getCreationCounter(self):
        self.creationCounter += 1
        return self.creationCounter

'''
the container for the gamestate that is not contained elsewhere
'''
class GameState():
    '''
    basic state setting with some initialization
    bad code: initialization should happen in story or from loading
    '''
    def __init__(self,phase=None):
        self.gameWon = False
        self.tick = 0

        # set the phase
        self.currentPhase = phasesByName["BrainTesting"]
        if phase:
            self.currentPhase = phasesByName[phase]

        # add the main char
        self.mainChar = characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)],creator=void)
        self.mainChar.watched = True
        mainChar = self.mainChar

    '''
    save the gamestate to disc
    bad pattern: loading and saving one massive json will break on the long run. load function should be delegated down to be able to scale json size
    '''
    def save(self):
        saveFile = open("gamestate/gamestate.json","w")
        state = self.getState()
        if not state["gameWon"]:
            saveFile.write(json.dumps(state,indent=4, sort_keys=True))
        else:
            # destroy the savefile
            saveFile.write(json.dumps("Winning is no fun at all"))
        saveFile.close()

    '''
    load the gamestate from disc
    bad pattern: loading and saving one massive json will break on the long run. load function should be delegated down to be able to scale json size
    '''
    def load(self):
        saveFile = open("gamestate/gamestate.json")
        rawstate = saveFile.read()
        state = json.loads(rawstate)
        saveFile.close()

        self.setState(state)

    '''
    rebuild gamestate from half serialized form
    '''
    def setState(self,state):
        # the object itself
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]["name"]]
        self.tick = state["tick"]

        # the terrain
        terrain.setState(state["terrain"],self.tick)

        self.currentPhase().start()

        xPosition = self.mainChar.xPosition
        if "xPosition" in state["mainChar"]:
            xPosition = state["mainChar"]["xPosition"]
        yPosition = self.mainChar.yPosition
        if "yPosition" in state["mainChar"]:
            yPosition = state["mainChar"]["yPosition"]

        """
        if "room" in state["mainChar"]:
            for room in terrain.rooms:
                if room.id == state["mainChar"]["room"]:
                    room.addCharacter(self.mainChar,xPosition,yPosition)
                    break
        else:
            terrain.addCharacter(self.mainChar,xPosition,yPosition)
        """
        self.mainChar.setState(state["mainChar"])

    '''
    get gamestate in half serialized form
    '''
    def getState(self):
        return {  
              "currentPhase":self.currentPhase.getState(),
              "mainChar":self.mainChar.getDiffState(),
              "terrain":terrain.getDiffState(),
              "tick":self.tick,
              "gameWon":self.gameWon
               }

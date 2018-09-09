import json
import src.characters as characters

'''
the creator that should be used if there is no valid creator object
basically supply ids for unique ids
'''
class Void():
    id = "void**#"
    creationCounter = 0

    '''
    supply a counter to allow unique id creation
    '''
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
    bad pattern: loading and saving one massive json will break on the long run. save function should be delegated down to be able to scale json size
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
        # load state from disc
        saveFile = open("gamestate/gamestate.json")
        rawstate = saveFile.read()
        state = json.loads(rawstate)
        saveFile.close()

        # set state
        self.setState(state)

    '''
    rebuild gamestate from half serialized form
    '''
    def setState(self,state):
        # the object itself
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]["name"]]()
        self.tick = state["tick"]

        # update void
        void.creationCounter = state["creationCounter"]

        # load the terrain
        terrain.setState(state["terrain"],self.tick)

        # load the main character
        xPosition = self.mainChar.xPosition
        if "xPosition" in state["mainChar"]:
            xPosition = state["mainChar"]["xPosition"]
        yPosition = self.mainChar.yPosition
        if "yPosition" in state["mainChar"]:
            yPosition = state["mainChar"]["yPosition"]
        if "room" in state["mainChar"]:
            for room in terrain.rooms:
                if room.id == state["mainChar"]["room"]:
                    room.addCharacter(self.mainChar,xPosition,yPosition)
                    break
        else:
            terrain.addCharacter(self.mainChar,xPosition,yPosition)
        self.mainChar.setState(state["mainChar"])

        # load cinematics
        for cinematicId in state["cinematics"]["ids"]:
            cinematic = cinematics.getCinematicFromState(state["cinematics"]["states"][cinematicId])
            cinematics.cinematicQueue.append(cinematic)

    '''
    get gamestate in half serialized form
    '''
    def getState(self):
        # load the main characters state
        mainCharState = self.mainChar.getDiffState()
        mainCharState["room"] = self.mainChar.room.id
        mainCharState["xPosition"] = self.mainChar.xPosition
        mainCharState["yPosition"] = self.mainChar.yPosition

        # load the cinematics
        cinematicStorage = {}
        cinematicStorage["ids"] = []
        cinematicStorage["states"] = {}
        for cinematic in cinematics.cinematicQueue:
            cinematicStorage["ids"].append(cinematic.id)
            cinematicStorage["states"][cinematic.id] = cinematic.getState()

        # generate state dict
        return {  
              "currentPhase":self.currentPhase.getState(),
              "mainChar":mainCharState,
              "terrain":terrain.getDiffState(),
              "tick":self.tick,
              "gameWon":self.gameWon,
              "cinematics":cinematicStorage,
              "creationCounter":void.creationCounter,
               }

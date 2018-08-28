import json
import src.characters as characters

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
        self.mainChar = characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)])
        self.mainChar.watched = True
        mainChar = self.mainChar

    '''
	save the gamestate to disc
	'''
    def save(self):
        saveFile = open("gamestate/gamestate.json","w")
        state = self.getState()
        if not state["gameWon"]:
            saveFile.write(json.dumps(state))
        else:
		    # destroy the savefile
            saveFile.write(json.dumps("Winning is no fun at all"))
        saveFile.close()

    '''
	load the gamestate from disc
	'''
    def load(self):
        saveFile = open("gamestate/gamestate.json")
        rawstate = saveFile.read()
        state = json.loads(rawstate)
        saveFile.close()

        self.setState(state)
        self.mainChar.setState(state["mainChar"])

    '''
	rebuild gamestate from half serialized form
	'''
    def setState(self,state):
	    # the object itself
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]]
        self.tick = state["tick"]

	    # the rooms
        for room in terrain.rooms:
            room.setState(state["roomStates"][room.id])
        for room in terrain.rooms:
            room.timeIndex = self.tick

    '''
	get gamestate in half serialized form
	'''
    def getState(self):
	    # the rooms
        roomStates = {}
        roomList = []
        for room in terrain.rooms:
            roomList.append(room.id)
            roomStates[room.id] = room.getState()
        
        return {  "gameWon":self.gameWon,
              "currentPhase":self.currentPhase.name,
              "tick":self.tick,
              "mainChar":self.mainChar.getState(),
                  "rooms":roomList,
                  "roomStates":roomStates,
               }

import json
import src.characters as characters

class GameState():
    def __init__(self):
        self.gameWon = False
        self.currentPhase = phasesByName["FirstTutorialPhase"]
        self.currentPhase = phasesByName["WakeUpPhase"]
        self.tick = 0

        self.mainChar = characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)])
        self.mainChar.watched = True
        #terrain.tutorialMachineRoom.addCharacter(self.mainChar,3,3)
        mainChar = self.mainChar

    def save(self):
        saveFile = open("gamestate/gamestate.json","w")
        state = self.getState()
        if not state["gameWon"]:
            saveFile.write(json.dumps(state))
        else:
            saveFile.write(json.dumps("Winning is no fun at all"))
        saveFile.close()

    def load(self):
        saveFile = open("gamestate/gamestate.json")
        rawstate = saveFile.read()
        state = json.loads(rawstate)
        saveFile.close()

        self.setState(state)
        self.mainChar.setState(state["mainChar"])

    def setState(self,state):
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]]
        self.tick = state["tick"]

        for room in terrain.rooms:
            room.setState(state["roomStates"][room.id])

        for room in terrain.rooms:
            room.timeIndex = self.tick

    def getState(self):
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

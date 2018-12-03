############################################################################################################
###
##     the state of the game should 
#
############################################################################################################

# include basic libs
import json

# include basic internal libs
import src.characters

'''
the container for the gamestate
bad code: all game state should be reachable from here
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
        if phase:
            self.currentPhase = phasesByName[phase]()
        else:
            self.currentPhase = phasesByName["BrainTesting"]()

        # add the main char
        self.mainChar = src.characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)],creator=void)
        self.mainChar.watched = True
        self.mainChar.terrain = None
        mainChar = self.mainChar
        self.openingCinematic = None

    '''
    save the gamestate to disc
    bad pattern: loading and saving one massive json will break on the long run. save function should be delegated down to be able to scale json size
    '''
    def save(self):
        # get state as dictionary
        state = self.getState()

        # prepare the savefile
        saveFile = open("gamestate/gamestate.json","w")

        # write the gamestate
        if not state["gameWon"]:
            saveFile.write(json.dumps(state,indent=4, sort_keys=True))
        # destroy the savefile
        else:
            saveFile.write(json.dumps("Winning is no fun at all"))

        # close the savefile
        # bad code: should use with 
        saveFile.close()

    '''
    load the gamestate from disc
    bad pattern: loading and saving one massive json will break on the long run. load function should be delegated down to be able to scale json size
    '''
    def load(self):
        # handle missing savefile
        import os
        if not os.path.isfile("gamestate/gamestate.json"):
            # bad code: should log
            return False

        # load state from disc
        # bad code: exception should not be hidden
        try:
            saveFile = open("gamestate/gamestate.json")
        except:
            # bad code: should log
            return False

        rawstate = saveFile.read()

        # handle special gamestates
        if rawstate in ["you lost","reset","Winning is no fun at all"]:
            # bad code: should log
            return False

        # get state
        state = json.loads(rawstate)

        # close filehandle
        # bad code: should use with 
        saveFile.close()

        # set state
        self.setState(state)
        return True

    '''
    rebuild gamestate from half serialized form
    '''
    def setState(self,state):
        # the object itself
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]["name"]]()
        self.currentPhase.setState(state["currentPhase"])
        self.tick = state["tick"]

        # update void
        void.setState(state["void"])

        # load the terrain
        terrain.setState(state["terrain"],self.tick)

        # load the main character
        # bad code: should be simplified
        xPosition = self.mainChar.xPosition
        if "xPosition" in state["mainChar"]:
            xPosition = state["mainChar"]["xPosition"]
        yPosition = self.mainChar.yPosition
        if "yPosition" in state["mainChar"]:
            yPosition = state["mainChar"]["yPosition"]
        if "room" in state["mainChar"]:
            if state["mainChar"]["room"]:
                for room in terrain.rooms:
                    if room.id == state["mainChar"]["room"]:
                        room.addCharacter(self.mainChar,xPosition,yPosition)
                        break
            else:
                if state["terrain"]:
                    terrain.addCharacter(self.mainChar,xPosition,yPosition)
        else:
            if state["terrain"]:
                terrain.addCharacter(self.mainChar,xPosition,yPosition)
        self.mainChar.setState(state["mainChar"])

        # load cinematics
        for cinematicId in state["cinematics"]["ids"]:
            cinematic = cinematics.getCinematicFromState(state["cinematics"]["states"][cinematicId])
            cinematics.cinematicQueue.append(cinematic)

        # load submenu
        import src.interaction
        if "submenu" in state:
            if state["submenu"]:
                src.interaction.submenue = src.interaction.getSubmenuFromState(state["submenu"])
            else:
                src.interaction.submenue = None

    '''
    get gamestate in half serialized form
    '''
    def getState(self):
        # generate the main characters state
        mainCharState = self.mainChar.getDiffState()
        if self.mainChar.room:
            mainCharState["room"] = self.mainChar.room.id
        else:
            mainCharState["room"] = None
        if self.mainChar.terrain:
            mainCharState["terrain"] = self.mainChar.terrain.id
        else:
            mainCharState["terrain"] = None
        mainCharState["xPosition"] = self.mainChar.xPosition
        mainCharState["yPosition"] = self.mainChar.yPosition

        # generate the cinematics
        cinematicStorage = {}
        cinematicStorage["ids"] = []
        cinematicStorage["states"] = {}
        for cinematic in cinematics.cinematicQueue:
            if cinematic == self.openingCinematic:
                continue
            if cinematic.aborted:
                continue
            cinematicStorage["ids"].append(cinematic.id)
            cinematicStorage["states"][cinematic.id] = cinematic.getState()

        # generate state dict
        import src.interaction
        submenueState = None
        if src.interaction.submenue:
            submenueState = src.interaction.submenue.getState()

        # generate the state
        # bad code: result should be generated earlier
        return {  
              "currentPhase":self.currentPhase.getState(),
              "mainChar":mainCharState,
              "terrain":terrain.getDiffState(),
              "tick":self.tick,
              "gameWon":self.gameWon,
              "cinematics":cinematicStorage,
              "void":void.getState(),
              "submenu":submenueState
               }

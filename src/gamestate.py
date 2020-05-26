############################################################################################################
###
##     the state of the game should 
#
############################################################################################################

# include basic libs
import json

# include basic internal libs
import src.characters
import src.terrains
import src.saveing

'''
the container for the gamestate
bad code: all game state should be reachable from here
'''
class GameState(src.saveing.Saveable):
    '''
    basic state setting with some initialization
    bad code: initialization should happen in story or from loading
    '''
    def __init__(self,phase=None, seed=0):
        super().__init__()
        self.id = "gamestate"
        self.mainChar = None
        self.successSeed = 0
        pass

    def setup(self,phase=None, seed=0):
        self.initialSeed = seed

        self.gameWon = False
        self.tick = 0

        self.macros = {}

        try:
            with open("gamestate/successSeed.json","r") as successSeedFile:
                rawState = json.loads(successSeedFile.read())
                self.successSeed = int(rawState["successSeed"])
        except:
            self.successSeed = 0

        # set the phase
        if phase:
            self.currentPhase = phasesByName[phase](seed=seed)
        else:
            self.currentPhase = phasesByName["BuildBase"](seed=seed)

        # add the main char
        self.mainChar = src.characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)],creator=void)
        self.mainChar.watched = True
        self.mainChar.terrain = None
        mainChar = self.mainChar
        self.openingCinematic = None

        self.terrainMap = []
        for y in range(0,30):
            line = []
            for x in range(0,30):
                if x == 15 and y == 15: 
                    thisTerrain = self.terrainType(creator=self,seed=seed)
                    self.terrain = thisTerrain
                else:
                    thisTerrain = src.terrains.Nothingness(creator=self)
                thisTerrain.xPosition = x
                thisTerrain.yPosition = y
                line.append(thisTerrain)
            self.terrainMap.append(line)

    '''
    save the gamestate to disc
    bad pattern: loading and saving one massive json will break on the long run. save function should be delegated down to be able to scale json size
    '''
    def save(self):
        # get state as dictionary
        state = self.getState()

        with open("gamestate/successSeed.json","w") as successSeedFile:
            successSeedFile.write(json.dumps({"successSeed":self.successSeed}))

        from shutil import copyfile
        try:
            copyfile("gamestate/gamestate.json", "gamestate/gamestate_backup.json")
        except:
            pass

        if not state["gameWon"]:
            gamedump = json.dumps(state,indent=4, sort_keys=True)
        else:
            gamedump = json.dumps("Winning is no fun at all")

        # write the savefile
        with open("gamestate/gamestate.json","w") as saveFile:
            saveFile.write(gamedump)

    '''
    load the gamestate from disc
    bad pattern: loading and saving one massive json will break on the long run. load function should be delegated down to be able to scale json size
    '''
    def load(self):
        # handle missing savefile
        import os
        if not os.path.isfile("gamestate/gamestate.json"):
            debugMessages.append("no gamestate found - NOT LOADING")
            print("no gamestate found")
            return False

        # load state from disc
        with open("gamestate/gamestate.json") as saveFile:
            rawstate = saveFile.read()

            # handle special gamestates
            if rawstate in ["you lost","reset","Winning is no fun at all","\"Winning is no fun at all\""]:
                debugMessages.append("special gamestate "+str(rawstate)+" found - NOT LOADING")
                print("final gamestate found - resetting")
                return False

            # get state
            state = json.loads(rawstate)

        # set state
        self.setState(state)
        print(src.saveing.loadingRegistry.delayedCalls)
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
        self.initialSeed = state["initialSeed"]

        self.macros = state["macros"]

        # update void
        void.setState(state["void"])

        import src.terrains
        self.terrainMap = []
        y = 0
        for line in state["terrainMap"]:
            newLine = []
            x = 0
            for item in line:
                thisTerrain = src.terrains.getTerrainFromState(item,creator=self)
                thisTerrain.xPosition = x
                thisTerrain.yPosition = y
                newLine.append(thisTerrain)
                x += 1
            self.terrainMap.append(newLine)
            y += 1

        # load the terrain
        global terrain
        self.terrain = self.terrainMap[15][15]
        terrain = self.terrain

        if state["mainChar"]["terrain"]:
            for terrainLine in self.terrainMap:
                for iterTerrain in terrainLine:
                    if iterTerrain.id == state["mainChar"]["terrain"]:
                        terrain = iterTerrain
                        self.terrain = iterTerrain

        # load the main character
        # bad code: should be simplified
        if not self.mainChar:
            self.mainChar = src.characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)],creator=void)
        xPosition = self.mainChar.xPosition
        if "xPosition" in state["mainChar"]:
            xPosition = state["mainChar"]["xPosition"]
        yPosition = self.mainChar.yPosition
        if "yPosition" in state["mainChar"]:
            yPosition = state["mainChar"]["yPosition"]
        if "room" in state["mainChar"] and state["mainChar"]["room"]:
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
        # generate simple state
        state = {}
        state["currentPhase"] = self.currentPhase.getState()
        state["tick"] = self.tick
        state["gameWon"] = self.gameWon
        state["void"] = void.getState()
        state["initialSeed"] = self.initialSeed
        state["macros"] = self.macros

        state["terrainMap"] = []
        for line in self.terrainMap:
            newLine = []
            for item in line:
                newLine.append(item.getState())
            state["terrainMap"].append(newLine)

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
        mainCharState["id"] = self.mainChar.id
        state["mainChar"] = mainCharState

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
        state["cinematics"] = cinematicStorage

        # generate state dict
        import src.interaction
        submenueState = None
        if src.interaction.submenue:
            submenueState = src.interaction.submenue.getState()
        state["submenu"] = submenueState

        return state

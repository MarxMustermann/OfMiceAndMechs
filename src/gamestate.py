# include basic libs
import json
import os

# include basic internal libs
import src.characters
import src.terrains
import src.saveing
import src.terrains
import src.canvas
import src.logger
import src.cinematics
import config

gamestate = None
phasesByName = {}


class GameState(src.saveing.Saveable):
    """
    the container for all of the gamestate
    """

    def __init__(self,gameIndex):
        """
        basic state setting with some initialization
        """

        super().__init__()
        self.id = "gamestate"
        self.mainChar = None
        self.successSeed = 0
        self.tick = 0
        self.gameHalted = False
        self.stopGameInTicks = None
        self.extraRoots = []
        self.dragState = None
        self.gameIndex = gameIndex
        self.initialSeed = None
        self.timedAutoAdvance = None
        self.gameOver = False
        self.gameOverText = ""

        self.multi_chars = set()
        self.header = None
        self.main = None
        self.footer = None

        """
        self.uiElements = [
                {"type":"gameMap","offset":(20,2)},
                {"type":"miniMap","offset":(2,2)},
                {"type":"healthInfo","offset":(40,45),"width":82},
                {"type":"indicators","offset":(40,46),"width":82},
                {"type":"text","offset":(74,47), "text":"press ? for help"},
                ]
        """

        self.uiElements = [
                        {"type":"gameMap","offset":(19,6)},
                        {"type":"miniMap","offset":(2,2)},
                        {"type":"healthInfo","offset":(40,2),"width":82},
                        {"type":"indicators","offset":(40,3),"width":82},
                        {"type":"text","offset":(74,4), "text":[src.interaction.ActionMeta(content="press z for help",payload="z")]},
                        {"type":"guiButtons","offset":(40,4),"width":82},
                        {"type":"rememberedMenu","offset":(2,18),"size":(36,80)},
                        {"type":"rememberedMenu2","offset":(133,2),"size":(62,80)},
                        ]

        self.clickMap = {}

    # bad code: initialization should happen in story or from loading
    def setup(self, phase=None, seed=0):
        """
        sets up the game world

        Parameters:
            phase: the phase to start with
            seed: the rng seed
        """

        self.initialSeed = seed

        self.gameWon = False
        self.tick = 0

        self.macros = {}

        try:
            with open("gamestate/successSeed.json", "r") as successSeedFile:
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
        self.mainChar = src.characters.Character(
            src.canvas.displayChars.main_char,
            3,
            3,
            automated=False,
            name=config.names.characterFirstNames[
                self.tick % len(config.names.characterFirstNames)
            ]
            + " "
            + config.names.characterLastNames[
                self.tick % len(config.names.characterLastNames)
            ],
        )
        self.mainChar.watched = True
        self.mainChar.terrain = None
        mainChar = self.mainChar
        self.openingCinematic = None

        self.terrainMap = []
        for y in range(0, 15):
            line = []
            for x in range(0, 15):
                if x == 15 and y == 15:
                    thisTerrain = self.terrainType(seed=seed)
                    self.terrain = thisTerrain
                else:
                    thisTerrain = src.terrains.Nothingness()
                thisTerrain.xPosition = x
                thisTerrain.yPosition = y
                line.append(thisTerrain)
            self.terrainMap.append(line)

    def setTerrain(self,terrain,pos):
        self.terrainMap[pos[1]][pos[0]] = terrain
        terrain.xPosition = pos[0]
        terrain.yPosition = pos[1]

    # bad pattern: loading and saving one massive json will break on the long run. save function should be delegated down to be able to scale json size
    def save(self):
        """
        save the game state to disc
        """

        import pickle
        import shutil
        import os

        if not os.path.exists("gamestate/"):
            os.makedirs("gamestate/")

        try:
            shutil.copyfile("gamestate/gamestate_%s"%(self.gameIndex,), "gamestate/gamestate_%s_backup"%(self.gameIndex,))
        except:
            pass

        try:
            file = open("gamestate/gamestate_%s"%(self.gameIndex,), 'wb')

            # dump information to that file
            print(src.gamestate.gamestate.mainChar.specialRender)
            pickle.dump(self, file)

            # close the file
            file.close()
        except:
            try:
                shutil.copyfile("gamestate/gamestate_%s_backup"%(self.gameIndex,), "gamestate/gamestate_%s"%(self.gameIndex,))
            except:
                pass

        try:
            # register the save
            with open("gamestate/globalInfo.json", "r") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[]}

        saves = rawState["saves"]
        saves[self.gameIndex] =  {"difficulty":10,"scenario":"test"}
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

        return

    def saveOld(self):
        # get state as dictionary
        state = self.getState()

        from shutil import copyfile

        try:
            copyfile("gamestate/gamestate_%s.json"%(self.gameIndex,), "gamestate/gamestate_%s_backup.json"%(self.gameIndex,))
        except:
            pass

        try:
            gamedump = json.dumps(state, indent=4, sort_keys=True)
        except:
            print(gamedump)

        # write the savefile
        with open("gamestate/gamestate_%s.json"%(self.gameIndex,), "w") as saveFile:
            saveFile.write(gamedump)

        try:
            # register the save
            with open("gamestate/globalInfo.json", "r") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[]}

        saves = rawState["saves"]
        saves[self.gameIndex] = "taken"
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

    # bad pattern: loading and saving one massive json will break on the long run. load function should be delegated down to be able to scale json size
    def loadP(self,gameIndex):
        """
        load the gamestate from disc

        Returns:
            bool: success indicator
        """

        import pickle
        file = open("gamestate/gamestate_%s"%(gameIndex,), 'rb')
        # dump information to that file
        newSelf = pickle.load(file)

        # close the file
        file.close()

        print(newSelf)

        return newSelf

        # handle missing savefile
        if not os.path.isfile("gamestate/gamestate_%s.json"%(self.gameIndex,)):
            src.logger.debugMessages.append("no gamestate found - NOT LOADING")
            print("no gamestate found")
            return False

        # load state from disc
        with open("gamestate/gamestate_%s.json"%(self.gameIndex,)) as saveFile:
            rawstate = saveFile.read()

            # handle special gamestates
            if rawstate in [
                "you lost",
                "reset",
                "Winning is no fun at all",
                '"Winning is no fun at all"',
            ]:
                src.logger.debugMessages.append(
                    "special gamestate " + str(rawstate) + " found - NOT LOADING"
                )
                print("final gamestate found - resetting")
                return False

            # get state
            state = json.loads(rawstate)

        # set state
        self.setState(state)
        if src.saveing.loadingRegistry.delayedCalls:
            print("unresolved delayed calls")
            print(src.saveing.loadingRegistry.delayedCalls)
        return True

    def setState(self, state):
        """
        rebuild gamestate from half serialized form

        Parameters:
            state: the gamestate to load
        """

        # the object itself
        self.gameWon = state["gameWon"]
        self.currentPhase = phasesByName[state["currentPhase"]["name"]]()
        self.currentPhase.setState(state["currentPhase"])
        src.saveing.loadingRegistry.register(self.currentPhase)
        self.tick = state["tick"]
        self.initialSeed = state["initialSeed"]

        self.extraRoots = []
        for item in state["extraRoots"]:
            self.extraRoots.append(src.rooms.getRoomFromState(item))

        self.macros = state["macros"]

        self.terrainMap = []
        y = 0
        for line in state["terrainMap"]:
            newLine = []
            x = 0
            for item in line:
                thisTerrain = src.terrains.getTerrainFromState(item)
                thisTerrain.xPosition = x
                thisTerrain.yPosition = y
                newLine.append(thisTerrain)
                x += 1
            self.terrainMap.append(newLine)
            y += 1

        # load the terrain
        global terrain
        self.terrain = self.terrainMap[7][7]
        terrain = self.terrain

        print("checking for terrain")
        if state["mainChar"]["terrain"]:
            for terrainLine in self.terrainMap:
                for iterTerrain in terrainLine:
                    if iterTerrain.id == state["mainChar"]["terrain"]:
                        terrain = iterTerrain
                        self.terrain = iterTerrain
                        print("found terrain")

        # load the main character
        # bad code: should be simplified
        if not self.mainChar:
            self.mainChar = src.characters.Character(
                src.canvas.displayChars.main_char,
                3,
                3,
                automated=False,
                name=config.names.characterFirstNames[
                    self.tick % len(config.names.characterFirstNames)
                ]
                + " "
                + config.names.characterLastNames[
                    self.tick % len(config.names.characterLastNames)
                ],
                characterId=state["mainChar"]["id"],
            )
            src.saveing.loadingRegistry.register(self.mainChar)
        xPosition = self.mainChar.xPosition
        if "xPosition" in state["mainChar"]:
            xPosition = state["mainChar"]["xPosition"]
        yPosition = self.mainChar.yPosition
        if "yPosition" in state["mainChar"]:
            yPosition = state["mainChar"]["yPosition"]
        if "room" in state["mainChar"] and state["mainChar"]["room"]:
            for line in self.terrainMap:
                for terrain in line:
                    for room in terrain.rooms:
                        if room.id == state["mainChar"]["room"]:
                            room.addCharacter(self.mainChar, xPosition, yPosition)
                            break
        else:
            terrain.addCharacter(self.mainChar, xPosition, yPosition)
        self.mainChar.setState(state["mainChar"])

        # load cinematics
        for cinematicId in state["cinematics"]["ids"]:
            cinematic = src.cinematics.getCinematicFromState(
                state["cinematics"]["states"][cinematicId]
            )
            src.cinematics.cinematicQueue.append(cinematic)

        # load submenu
        if "submenu" in state:
            if state["submenu"]:
                src.interaction.submenue = src.interaction.getSubmenuFromState(
                    state["submenu"]
                )
            else:
                src.interaction.submenue = None

    def getState(self):
        """
        get game state in half serialized form

        Returns:
            the game state
        """

        # generate simple state
        state = {
            "currentPhase": self.currentPhase.getState(),
            "tick": self.tick,
            "gameWon": self.gameWon,
            "initialSeed": self.initialSeed,
            "macros": self.macros,
            "terrainMap": [],
            "extraRoots": [],
        }

        for item in self.extraRoots:
            state["extraRoots"].append(("Room",item.getState()))

        for line in self.terrainMap:
            newLine = []
            for item in line:
                newLine.append(item.getState())
            state["terrainMap"].append(newLine)

        # generate the main characters state
        mainCharState = self.mainChar.getState()
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
        cinematicStorage = {"ids": [], "states": {}}
        for cinematic in src.cinematics.cinematicQueue:
            if cinematic == self.openingCinematic:
                continue
            if cinematic.aborted:
                continue
            cinematicStorage["ids"].append(cinematic.id)
            cinematicStorage["states"][cinematic.id] = cinematic.getState()
        state["cinematics"] = cinematicStorage

        # generate state dict
        submenueState = None
        if src.interaction.submenue:
            submenueState = src.interaction.submenue.getState()
        state["submenu"] = submenueState

        return state

def setup(gameIndex):
    """
    initialises the game state 
    """

    global gamestate
    gamestate = GameState(gameIndex)

# include basic libs
import json
import os

# include basic internal libs
import src.characters
import src.terrains
import src.terrains
import src.canvas
import src.logger
import src.cinematics
import config

gamestate = None
phasesByName = {}


class GameState:
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
        self.savedThisTurn = False
        self.waitedForInputThisTurn = False
        self.gods = {
                        1:{"name":"god1"},
                        2:{"name":"god2"},
                        3:{"name":"god3"},
                        4:{"name":"god4"},
                        5:{"name":"god5"},
                        6:{"name":"god6"},
                        7:{"name":"god7"},
                    }

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
                        {"type":"rememberedMenu","offset":(2,18),"size":(35,80)},
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
            with open("gamestate/successSeed.json") as successSeedFile:
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
            automated=False
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

    def save(self):
        self.savedThisTurn = True
        tcodConsole = src.interaction.tcodConsole
        tcodContext = src.interaction.tcodContext
        printUrwidToTcod = src.interaction.printUrwidToTcod

        offsetX = 51
        offsetY = 10

        tcodConsole.clear()
        printUrwidToTcod("+-------------+",(offsetX+3+16,offsetY+13))
        printUrwidToTcod("| saving game |",(offsetX+3+16,offsetY+14))
        printUrwidToTcod("+-------------+",(offsetX+3+16,offsetY+15))
        tcodContext.present(tcodConsole)

        """
        save the game state to disc
        """

        import pickle
        import shutil
        import os

        if not os.path.exists("gamestate/"):
            os.makedirs("gamestate/")

        try:
            shutil.copyfile(f"gamestate/gamestate_{self.gameIndex}", f"gamestate/gamestate_{self.gameIndex}_backup")
        except:
            pass

        file = open(f"gamestate/gamestate_{self.gameIndex}", 'wb')

        # dump information to that file
        pickle.dump(self, file)

        # close the file
        file.close()

        try:
            # register the save
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[],"lastGameIndex":0}

        saves = rawState["saves"]
        saves[self.gameIndex] =  {"difficulty":10,"scenario":"test"}
        rawState["lastGameIndex"] = self.gameIndex
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

        return

    def loadP(self,gameIndex):
        """
        load the gamestate from disc

        Returns:
            bool: success indicator
        """

        try:
            # register the save
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[],"lastGameIndex":0}

        rawState["lastGameIndex"] = gameIndex
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)


        import pickle
        file = open(f"gamestate/gamestate_{gameIndex}", 'rb')
        # dump information to that file
        newSelf = pickle.load(file)

        # close the file
        file.close()

        return newSelf

def setup(gameIndex):
    """
    initialise the game state 
    """

    global gamestate
    gamestate = GameState(gameIndex)

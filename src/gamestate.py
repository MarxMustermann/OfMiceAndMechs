
import json
import zlib
import tcod

import src.canvas
import src.characters
import src.terrains

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
        self.saveAtTheTurnEnd = False
        self.waitedForInputThisTurn = False
        self.stern = {"first_reachout_done":False,"first_silenced":False,"reached_base":False,"examined_trap":False,"last_implant_interaction":-100}
        self.gods = {}
        self.theOldOne = {
                "throneTaken":False
                    }
        self.difficulty = None
        self.difficultyMap = None
        self.mainLoop = {"counter":0,"character_queue":[]}

        self.multi_chars = set()
        self.header = None
        self.main = None
        self.footer = None
        self.world_infos = None

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
                        {"type":"miniMap","offset":(2,1)},
                        {"type":"healthInfo","offset":(40,2),"width":82},
                        {"type":"indicators","offset":(40,3),"width":82},
                        {"type":"text","offset":(74,4), "text":[src.interaction.ActionMeta(content="press ? for help",payload="z")]},
                        {"type":"time","offset":(74,5),},
                        {"type":"guiButtons","offset":(40,4),"width":82},
                        {"type":"rememberedMenu","offset":(2,18),"size":(35,80)},
                        {"type":"rememberedMenu2","offset":(132,18),"size":(50,80)},
                        {"type":"zoneMap","offset":(66,1)},
                        ]

        self.clickMap = {}
        self.story = None
        self.teleporterGroups = {}
        self.itemToUpdatePerTick = []

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
        for y in range(15):
            line = []
            for x in range(15):
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
        '''
        save the game state to disc
        '''

        src.interaction.send_tracking_ping("saving_"+str(self.gameIndex))

        # note that the game was saved (obsolete?)
        self.savedThisTurn = True

        src.interaction.renderGameDisplay(showSaving=True)

        # import stuff. (should not be within a function -_-)
        import os
        import pickle
        import shutil

        # draw an info that saving is in progress
        if not os.path.exists("gamestate/"):
            os.makedirs("gamestate/")

        savestateId = self.world_infos["savestateId"]

        # store a backup of the savegame
        try:
            shutil.copyfile(f"gamestate/gamestate_{savestateId}", f"gamestate/gamestate_{savestateId}_backup")
        except:
            pass

        # create the actual save file
        with open(f"gamestate/gamestate_{savestateId}", 'wb') as file:
            compressed = zlib.compress(pickle.dumps(self),9)
            file.write(compressed)

        # register the save
        try:
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"worlds": [],"customPrefabs":[],"lastGameIndex":0,"wordCounter":0,}
        saves = rawState["worlds"]
        rawState["lastGameIndex"] = self.gameIndex
        rawState["worlds"][self.gameIndex]["hasSave"] = True
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

    def loadP(self,gameIndex):
        '''
        load the gamestate from disc

        Parameters:
            gameIndex: the index of the gameslot to load

        Returns:
            bool: success indicator
        '''

        src.interaction.send_tracking_ping("loading_"+str(gameIndex))

        # update the metadata
        try:
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"worlds": [],"customPrefabs":[],"lastGameIndex":0,"wordCounter":0}

        savestateId = rawState["worlds"][gameIndex]["savestateId"]

        rawState["lastGameIndex"] = gameIndex
        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
            json.dump(rawState,globalInfoFile)

        # load the actual gamefile
        import pickle
        with open(f"gamestate/gamestate_{savestateId}", 'rb') as file:
            try:
                newSelf = pickle.loads(zlib.decompress(file.read()))
            except:
                with open(f"gamestate/gamestate_{savestateId}_backup", 'rb') as file:
                    newSelf = pickle.loads(zlib.decompress(file.read()))

        return newSelf

def setup(gameIndex):
    """
    initialise the game state
    """

    global gamestate
    gamestate = GameState(gameIndex)

import sys
import json
import time

import src.items as items
import src.quests as quests
import src.rooms as rooms
import src.characters as characters
import src.terrains as terrains
import src.cinematics as cinematics
import src.story as story
import src.gameMath as gameMath
import src.interaction as interaction
import src.gamestate as gamestate
import src.events as events
import config.commandChars as commandChars
import config.names as names

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--phase", type=str, help="the phase to start in")
parser.add_argument("--unicode", action="store_true", help="force fallback encoding")
parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
parser.add_argument("-m", "--music", action="store_true", help="enable music (downloads stuff and runs mplayer!)")
parser.add_argument("-t", "--tiles", action="store_true", help="spawn a tile based view of the map (requires pygame)")
parser.add_argument("-ts", "--tileSize", type=int, help="the base size of tiles")
parser.add_argument("-T", "--terrain", type=str, help="select the terrain")
args = parser.parse_args()

import src.canvas as canvas

if args.unicode:
    displayChars = canvas.DisplayMapping("unicode")
else:
    displayChars = canvas.DisplayMapping("pureASCII")

##################################################################################################################################
###
##        background music
#
#################################################################################################################################

if args.music :
    def playMusic():
        import threading
        thread = threading.currentThread()
        import subprocess
        import os.path
        # I didn't ask the people at freemusicarchive about the position on traffic leeching. If you know they don't like it please create an issue

        if not os.path.isfile("music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/ece1b96c8f23874bda6ffdda2dd6cf9cd2fcb582","-O","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        if not os.path.isfile("music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/c1a7a0cd0e262469607e26935e69ed1e5bfed538","-O","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        mplayer = subprocess.Popen(["mplayer","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        while mplayer.stdout.read1(100):
           if thread.stop:
               mplayer.terminate()
               mplayer.kill()
               return
        
    from threading import Thread
    musicThread = Thread(target=playMusic)
    musicThread.stop = False
    musicThread.start()
else:
    musicThread = None

##################################################################################################################################
###
##        some stuff that is somehow needed but slated for removal
#
#################################################################################################################################

# HACK: common variables with modules
phasesByName = {}
story.phasesByName = phasesByName
story.registerPhases()
gamestate.phasesByName = phasesByName

# HACK: common variables with modules
cinematics.quests = quests
story.quests = quests
terrains.quests = quests

# HACK: common variables with modules
story.rooms = rooms

# HACK: common variables with modules
items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars
story.displayChars = displayChars
gamestate.displayChars = displayChars
interaction.displayChars = displayChars
cinematics.displayChars = displayChars

# HACK: common variables with modules
story.cinematics = cinematics
interaction.cinematics = cinematics
events.cinematics = cinematics

# HACK: common variables with modules
items.commandChars = commandChars
story.commandChars = commandChars
interaction.commandChars = commandChars
interaction.setFooter()

# HACK: common variables with modules
story.names = names
gamestate.names = names

# HACK: common variables with modules
story.items = items

# HACK: common variables with modules
items.characters = characters
rooms.characters = characters
story.characters = characters

# HACK: common variables with modules
cinematics.main = interaction.main
cinematics.header = interaction.header

# HACK: common variables with modules
cinematics.loop = interaction.loop
quests.loop = interaction.loop
story.loop = interaction.loop
events.loop = interaction.loop

# HACK: common variables with modules
story.events = events

# HACK: common variables with modules
cinematics.callShow_or_exit = interaction.callShow_or_exit
quests.callShow_or_exit = interaction.callShow_or_exit
story.callShow_or_exit = interaction.callShow_or_exit
events.callShow_or_exit = interaction.callShow_or_exit

# HACK: common variables with modules
rooms.calculatePath        = gameMath.calculatePath
quests.calculatePath        = gameMath.calculatePath
characters.calculatePath    = gameMath.calculatePath
terrains.calculatePath         = gameMath.calculatePath

# HACK: common variables with modules
rooms.Character = characters.Character
        
# HACK: common variables with modules
messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages
story.messages = messages
interaction.messages = messages
events.messages = messages

cinematics.interaction = interaction
characters.interaction = interaction
story.interaction = interaction
rooms.interaction = interaction
items.interaction = interaction
quests.interaction = interaction

if args.debug:
    class debugToFile(object):
        def __init__(self):
            logfile = open("debug.log","w")
            logfile.close()
        def append(self,message):
            logfile = open("debug.log","a")
            logfile.write(str(message)+"\n")
            logfile.close()
    debugMessages = debugToFile()
    interaction.debug = True
else:
    class FakeLogger(object):
        def append(self,message):
            pass

    debugMessages = FakeLogger()
    interaction.debug = False

items.debugMessages = debugMessages
quests.debugMessages = debugMessages
rooms.debugMessages = debugMessages
characters.debugMessages = debugMessages
terrains.debugMessages = debugMessages
cinematics.debugMessages = debugMessages
story.debugMessages = debugMessages
interaction.debugMessages = debugMessages
events.debugMessages = debugMessages

# HACK: common variables with modules
quests.showCinematic = cinematics.showCinematic

##########################################
###
## set up the trainingsterrain. A container will be made later
#
##########################################
if args.terrain and args.terrain == "scrapField":
    terrain = terrains.TutorialTerrain2()
else:
    terrain = terrains.TutorialTerrain()

# HACK: common variables with modules
items.terrain = terrain
story.terrain = terrain
interaction.terrain = terrain
gamestate.terrain = terrain
quests.terrain = terrain

cinematics.interaction = interaction

# HACK: common variables with modules
characters.roomsOnMap = terrain.rooms

# state that should be contained in the gamestate
mapHidden = True
mainChar = None

# the available Phases
phasesByName["FirstTutorialPhase"] = story.FirstTutorialPhase
phasesByName["SecondTutorialPhase"] = story.SecondTutorialPhase
phasesByName["ThirdTutorialPhase"] = story.ThirdTutorialPhase
phasesByName["VatPhase"] = story.VatPhase
phasesByName["MachineRoomPhase"] = story.MachineRoomPhase
phasesByName["OpenWorld"] = story.OpenWorld
phasesByName["ScreenSaver"] = story.ScreenSaver

##################################################################################################################################
###
##        setup the game
#
#################################################################################################################################

# create and load the gamestate
gameStateObj = gamestate.GameState(phase=args.phase)
try:
    gameStateObj.load()
except:
    pass

# HACK: common variables with modules
story.gamestate = gameStateObj
interaction.gamestate = gameStateObj

# HACK: common variables with modules
rooms.mainChar = gameStateObj.mainChar
terrains.mainChar = gameStateObj.mainChar
story.mainChar = gameStateObj.mainChar
interaction.mainChar = gameStateObj.mainChar
cinematics.mainChar = gameStateObj.mainChar
quests.mainChar = gameStateObj.mainChar

# set up the splash screen
cinematics.showCinematic("""

OOO FFF          AAA N N DD
O O FF   mice    AAA NNN D D
OOO F            A A N N DD




MMM   MMM  EEEEEE  CCCCCC  HH   HH  SSSSSSS
MMMM MMMM  EE      CC      HH   HH  SS
MM MMM MM  EEEE    CC      HHHHHHH  SSSSSSS
MM  M  MM  EEEE    CC      HHHHHHH  SSSSSSS
MM     MM  EE      CC      HH   HH        S
MM     MM  EEEEEE  CCCCCC  HH   HH  SSSSSSS



   a pipedream 

""",rusty=True)

# set up the current phase
gameStateObj.currentPhase().start()

##################################################################################################################################
###
##        the main loop
#
#################################################################################################################################

# the game loop
def advanceGame():
    global movestate
    for character in terrain.characters:
        character.advance()

    for room in terrain.rooms:
        room.advance()

    gameStateObj.tick += 1

# HACK: common variables with modules
cinematics.advanceGame = advanceGame
interaction.advanceGame = advanceGame

if args.tiles:
    import pygame
    pygame.init()
    if args.tileSize:
        interaction.tileSize = args.tileSize
    else:
        interaction.tileSize = 10
    pydisplay = pygame.display.set_mode((41*(interaction.tileSize+1), 41*(interaction.tileSize+1)))
    pygame.display.set_caption('Of Mice and Mechs')
    pygame.display.update()
    interaction.pygame = pygame
    interaction.pydisplay = pydisplay
    interaction.useTiles = True
else:
    interaction.useTiles = False

# start the interactio loop of the underlying library
try:
    interaction.loop.run()
except:
    if musicThread:
        musicThread.stop = True
    raise

if musicThread:
    musicThread.stop = True

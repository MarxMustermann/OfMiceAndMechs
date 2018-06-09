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
args = parser.parse_args()

import src.canvas as canvas

if args.unicode:
    displayChars = canvas.DisplayMapping("unicode")
else:
    displayChars = canvas.DisplayMapping("pureASCII")


##################################################################################################################################
###
##        some stuff that is somehow needed but slated for removal
#
#################################################################################################################################

#import sys, pygame
#pygame.init()
#pygame.mixer.music.load("music/chutulu.mp3")
#pygame.mixer.music.play()

# HACK: common variables with modules
phasesByName = {}
story.phasesByName = phasesByName
story.registerPhases()
gamestate.phasesByName = phasesByName

# HACK: common variables with modules
cinematics.quests = quests
story.quests = quests

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

if args.debug:
    class debugToFile(object):
        def __init__(self):
            logfile = open("debug.log","w")
            logfile.close()
        def append(message):
            logfile = open("debug.log","a")
            logfile.write(message)
            logfile.close()
    debugMessages = messages
else:
    debugMessages = []

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

# start the interactio loop of the underlying library
interaction.loop.run()

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

if len(sys.argv) > 1:
    import config.displayChars_fallback as displayChars
else:
    import config.displayChars as displayChars

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
items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars
story.displayChars = displayChars
gamestate.displayChars = displayChars

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

# HACK: common variables with modules
cinematics.loop = interaction.loop
quests.loop = interaction.loop
story.loop = interaction.loop

# HACK: common variables with modules
story.events = events

# HACK: common variables with modules
cinematics.callShow_or_exit = interaction.callShow_or_exit
quests.callShow_or_exit = interaction.callShow_or_exit
story.callShow_or_exit = interaction.callShow_or_exit

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

##################################################################################################################################
###
##        setup the game
#
#################################################################################################################################

# create and load the gamestate
gameStateObj = gamestate.GameState()
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
""")

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

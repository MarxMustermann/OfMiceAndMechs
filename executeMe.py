#####################################################################################################################
###
##      load environment and start the games main loop
#       basically nothing to see here
#       if you are a first time visitor, interaction.py, story.py and gamestate.py are probably better files to start with
#
#####################################################################################################################

# import basic libs
import sys
import json
import time

# import basic internal libs
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
import src.chats as chats
import src.saveing as saveing

# import configs
import config.commandChars as commandChars
import config.names as names

# parse arguments
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

# set rendering mode
if args.unicode:
    displayChars = canvas.DisplayMapping("unicode")
else:
    displayChars = canvas.DisplayMapping("pureASCII")

##################################################################################################################################
###
##        background music
#
#################################################################################################################################

# play music
if args.music :
    def playMusic():
        import threading
        thread = threading.currentThread()
        import subprocess
        import os.path

        # download music
        # bad pattern: I didn't ask the people at freemusicarchive about the position on traffic leeching. If you know they don't like it please create an issue
        # bad code: it obviously is an issue, since they knowingly broke this mechanism
        if not os.path.isfile("music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/ece1b96c8f23874bda6ffdda2dd6cf9cd2fcb582","-O","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        if not os.path.isfile("music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"):
            subprocess.call(["wget","-q","https://freemusicarchive.org/music/download/c1a7a0cd0e262469607e26935e69ed1e5bfed538","-O","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        mplayer = subprocess.Popen(["mplayer","music/Diezel_Tea_-_01_-_Kilikia_Original_Mix.mp3","music/Diezel_Tea_-_01_-_Arzni_Part_1_ft_Sam_Khachatourian.mp3"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # play music
        while mplayer.stdout.read1(100):
           if thread.stop:
               mplayer.terminate()
               mplayer.kill()
               return
        
    # start music as subprocess
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

# bad code: common variables with modules
void = saveing.Void()
characters.void = void
rooms.void = void
items.void = void
terrains.void = void
gamestate.void = void
story.void = void
interaction.void = void
quests.void = void
cinematics.void = void
events.void = void

# bad code: common variables with modules
rooms.story = story

# bad code: common variables with modules
story.chats = chats
characters.chats = chats

# bad code: common variables with modules
loadingRegistry = saveing.LoadingRegistry()
characters.loadingRegistry = loadingRegistry
quests.loadingRegistry = loadingRegistry
rooms.loadingRegistry = loadingRegistry
cinematics.loadingRegistry = loadingRegistry
items.loadingRegistry = loadingRegistry
story.loadingRegistry = loadingRegistry
events.loadingRegistry = loadingRegistry
terrains.loadingRegistry = loadingRegistry
saveing.loadingRegistry = loadingRegistry

# bad code: common variables with modules
phasesByName = {}
story.phasesByName = phasesByName
story.registerPhases()
gamestate.phasesByName = phasesByName

# bad code: common variables with modules
cinematics.quests = quests
story.quests = quests
terrains.quests = quests
characters.quests = quests
items.quests = quests
chats.quests = quests

# bad code: common variables with modules
story.rooms = rooms

# bad code: common variables with modules
items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars
story.displayChars = displayChars
gamestate.displayChars = displayChars
interaction.displayChars = displayChars
cinematics.displayChars = displayChars
characters.displayChars = displayChars
events.displayChars = displayChars
chats.displayChars = displayChars

# bad code: common variables with modules
story.cinematics = cinematics
interaction.cinematics = cinematics
events.cinematics = cinematics
rooms.cinematics = cinematics
gamestate.cinematics = cinematics

# bad code: common variables with modules
items.commandChars = commandChars
story.commandChars = commandChars
characters.commandChars = commandChars
interaction.commandChars = commandChars
chats.commandChars = commandChars

interaction.setFooter()

# bad code: common variables with modules
story.names = names
gamestate.names = names
items.names = names
rooms.names = names

# bad code: common variables with modules
story.items = items

# bad code: common variables with modules
items.characters = characters
rooms.characters = characters
story.characters = characters
terrains.characters = characters

# bad code: common variables with modules
cinematics.main = interaction.main
cinematics.header = interaction.header

# bad code: common variables with modules
cinematics.loop = interaction.loop
quests.loop = interaction.loop
story.loop = interaction.loop
events.loop = interaction.loop

# bad code: common variables with modules
story.events = events
items.events = events
rooms.events = events
quests.events = events
characters.events = events
terrains.events = events

# bad code: common variables with modules
cinematics.callShow_or_exit = interaction.callShow_or_exit
quests.callShow_or_exit = interaction.callShow_or_exit
story.callShow_or_exit = interaction.callShow_or_exit
events.callShow_or_exit = interaction.callShow_or_exit
chats.callShow_or_exit = interaction.callShow_or_exit

# bad code: common variables with modules
rooms.calculatePath        = gameMath.calculatePath
quests.calculatePath        = gameMath.calculatePath
characters.calculatePath    = gameMath.calculatePath
terrains.calculatePath         = gameMath.calculatePath

# bad code: common variables with modules
rooms.Character = characters.Character
        
# bad code: common variables with modules
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
chats.messages = messages

cinematics.interaction = interaction
characters.interaction = interaction
story.interaction = interaction
rooms.interaction = interaction
items.interaction = interaction
quests.interaction = interaction
chats.interaction = interaction

if args.debug:
    '''
    logger object for logging to file
    '''
    class debugToFile(object):
        '''
        clear file
        '''
        def __init__(self):
            logfile = open("debug.log","w")
            logfile.close()
        '''
        add log message to file
        '''
        def append(self,message):
            logfile = open("debug.log","a")
            logfile.write(str(message)+"\n")
            logfile.close()
    
    # set debug mode
    debugMessages = debugToFile()
    interaction.debug = True
    characters.debug = True
    quests.debug = True
else:
    '''
    dummy logger
    '''
    class FakeLogger(object):
        '''
        discard input
        '''
        def append(self,message):
            pass

    # set debug mode
    debugMessages = FakeLogger()
    interaction.debug = False
    characters.debug = False
    quests.debug = False

# bad code: common variables with modules
items.debugMessages = debugMessages
quests.debugMessages = debugMessages
rooms.debugMessages = debugMessages
characters.debugMessages = debugMessages
terrains.debugMessages = debugMessages
cinematics.debugMessages = debugMessages
story.debugMessages = debugMessages
interaction.debugMessages = debugMessages
events.debugMessages = debugMessages

# bad code: common variables with modules
quests.showCinematic = cinematics.showCinematic

##########################################
###
## set up the terrain
#
##########################################

# spawn selected terrain
if args.terrain and args.terrain == "scrapField":
    terrain = terrains.TutorialTerrain2(creator=void)
elif args.terrain and args.terrain == "nothingness":
    terrain = terrains.Nothingness(creator=void)
else:
    terrain = terrains.TutorialTerrain(creator=void)

# bad code: common variables with modules
items.terrain = terrain
story.terrain = terrain
interaction.terrain = terrain
gamestate.terrain = terrain
terrains.terrain = terrain
quests.terrain = terrain
chats.terrain = terrain

# bad code: common variables with modules
cinematics.interaction = interaction

# bad code: common variables with modules
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

# bad code: common variables with modules
story.gamestate = gameStateObj
interaction.gamestate = gameStateObj
quests.gamestate = gameStateObj
characters.gamestate = gameStateObj
items.gamestate = gameStateObj
terrains.gamestate = gameStateObj
rooms.gamestate = gameStateObj

# bad code: common variables with modules
rooms.mainChar = gameStateObj.mainChar
terrains.mainChar = gameStateObj.mainChar
story.mainChar = gameStateObj.mainChar
interaction.mainChar = gameStateObj.mainChar
cinematics.mainChar = gameStateObj.mainChar
quests.mainChar = gameStateObj.mainChar
chats.mainChar = gameStateObj.mainChar

# set up the splash screen
if not args.debug:
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


        - a pipedream 

""",rusty=True,scrolling=True)

##################################################################################################################################
###
##        the main loop
#
#################################################################################################################################

# the game loop
# bad code: either unused or should be contained in terrain
def advanceGame():
    for character in terrain.characters:
        character.advance()

    for room in terrain.rooms:
        room.advance()

    gameStateObj.tick += 1

# bad code: common variables with modules
cinematics.advanceGame = advanceGame
interaction.advanceGame = advanceGame

try:
    # load the game
    gameStateObj.load()
except Exception as e:
    ignore = input("could not load gamestate. abort (y/n)?")
    if ignore == "y":
        raise e

    # set up the current phase
    gameStateObj.currentPhase.start()

# bad code: loading registry should be cleared

if args.tiles:
    # spawn tile based rendered window
    import pygame
    pygame.init()
    pygame.key.set_repeat(200,20)
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

######################################################################################################
###
##    main loop is started here
#
######################################################################################################

# start the interaction loop of the underlying library
try:
    interaction.loop.run()
except:
    if musicThread:
        musicThread.stop = True
    raise

# stop the music
if musicThread:
    musicThread.stop = True

# print death messages
if gameStateObj.mainChar.dead:
    print("you died.")
    if gameStateObj.mainChar.deathReason:
        print("Cause of death:\n"+gameStateObj.mainChar.deathReason)

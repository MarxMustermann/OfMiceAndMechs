#!/usr/bin/env python3

"""
load environment and start the games main loop
basically nothing to see here
if you are a first time visitor, interaction.py, story.py and gamestate.py are probably better files to start with
"""

# import basic libs
import sys
import json
import time

# import basic internal libs
import src.items as items

import src.itemFolder
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
import src.canvas as canvas
import src.logger as logger


# import configs
import config.commandChars as commandChars
import config.names as names

# parse arguments
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--phase", type=str, help="the phase to start in")
parser.add_argument("--unicode", action="store_true", help="force fallback encoding")
parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
parser.add_argument(
    "-t",
    "--tiles",
    action="store_true",
    help="spawn a tile based view of the map (requires pygame)",
)
parser.add_argument("--urwid", action="store_true", help="do shell based")
parser.add_argument("-ts", "--tileSize", type=int, help="the base size of tiles")
parser.add_argument("-T", "--terrain", type=str, help="select the terrain")
parser.add_argument("-s", "--seed", type=str, help="select the seed of a new game")
parser.add_argument("--multiplayer", action="store_true", help="activate multiplayer")
parser.add_argument("--load", action="store_true", help="load")
parser.add_argument("--noload", action="store_true", help="do not load saves")
parser.add_argument(
    "-S", "--speed", type=int, help="set the speed of the game to a fixed speed"
)
parser.add_argument("-sc", "--scenario", type=str, help="set the scenario to run")
parser.add_argument("-notcod", "--notcod", action="store_true", help="do not use tcod renderer")
args = parser.parse_args()

################################################################################
#
#         switch scenarios
#
################################################################################

if not args.notcod:
    import tcod

    screen_width = 100
    screen_height = 25

    tileset = tcod.tileset.load_tilesheet(
        "Acorntileset2.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    context = tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="OfMiceAndMechs",
        vsync=True,
            )
    root_console = tcod.Console(screen_width, screen_height, order="F")

gameIndex = None

# load the gamestate
loaded = False
if args.load:
    shouldLoad = True
elif args.noload:
    shouldLoad = False
else:
    if args.notcod:
        load = input("load saved game? (Y/n)")
        if load.lower() == "n":
            shouldLoad = False
        else:
            shouldLoad = True
    else:
        try:
            with open("gamestate/globalInfo.json", "r") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
                saves = rawState["saves"]
        except:
            saves = [0,0,0,0,0,0,0,0,0,0]

        y = 2
        for i in range(0,10):
            if not saves[i]:
                root_console.print(x=3,y=2+i,string="%s: new game"%(i,))
            else:
                root_console.print(x=3,y=2+i,string="%s: load game"%(i,))

        context.present(root_console)

        index = None
        while index == None:
            foundEvent = False
            events = tcod.event.get()
            for event in events:
                context.convert_event(event)
                if isinstance(event, tcod.event.MouseButtonUp):
                    index = event.tile.y-2
                    if index > 9 or index < 0:
                        index = None
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    translatedKey = None
                    if key == tcod.event.KeySym.N1:
                        index = 1
                    if key == tcod.event.KeySym.N2:
                        index = 2
                    if key == tcod.event.KeySym.N3:
                        index = 3
                    if key == tcod.event.KeySym.N4:
                        index = 4
                    if key == tcod.event.KeySym.N5:
                        index = 5
                    if key == tcod.event.KeySym.N6:
                        index = 6
                    if key == tcod.event.KeySym.N7:
                        index = 7
                    if key == tcod.event.KeySym.N8:
                        index = 8
                    if key == tcod.event.KeySym.N9:
                        index = 9
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
            context.present(root_console)

        if saves[index]:
            shouldLoad = True
            gameIndex = index
        else:
            shouldLoad = False
            gameIndex = index

if not shouldLoad:
    if not args.scenario:
        scenarios = [
            (
                "BackToTheRoots",
                "main game",
                "m",
            ),
            (
                "Tutorials",
                "tutorials",
                "t",
            ),
            (
                "PrefabDesign",
                "PrefabDesign",
                "p",
            ),
            (
                "basebuilding",
                "basebuilding",
                "b",
            ),
            (
                "RoguelikeStart",
                "RoguelikeStart",
                "r",
            ),
            (
                "survival",
                "survival",
                "s",
            ),
            (
                "creative",
                "creative mode",
                "c",
            ),
            (
                "dungeon",
                "dungeon",
                "d",
            ),
            (
                "siege2",
                "siege2",
                "S",
            ),
            (
                "Tour",
                "(Tour)",
                "T",
            ),
            (
                "siege",
                "(siege)",
                "x",
            ),
        ]

        text = "\n"
        for scenario in scenarios:
            text += "%s: %s\n" % (
                scenario[2],
                scenario[1],
            )

        if args.notcod:
            scenarioNum = input("select scenario (type number)\n\n%s\n\n" % (text,))
            scenario = scenarios[int(scenarioNum)][0]
        else:

            #print("offer the player the option to start playing now or do something more specific") 
            root_console.clear()
            root_console.print(x=3,y=2,string="warning: The main game might be somewhat wild and confusing to new players.\nIt is recommended to try at least some tutorials first.\n\np: play now\nt: do tutorials\ns: start specific scenario")

            while 1:
                foundEvent = False
                events = tcod.event.get()
                for event in events:
                    if isinstance(event,tcod.event.MouseButtonUp):
                        context.convert_event(event)
                        mainSelection = event.tile.y-5
                        if mainSelection in (0,1,2):
                            foundEvent = True

                    if isinstance(event,tcod.event.KeyDown):
                        key = event.sym
                        if key == tcod.event.KeySym.p:
                            mainSelection = 0
                            foundEvent = True
                        if key == tcod.event.KeySym.t:
                            mainSelection = 1
                            foundEvent = True
                        if key == tcod.event.KeySym.s:
                            mainSelection = 2
                            foundEvent = True
                            

                context.present(root_console)
                if foundEvent:
                    break

            if mainSelection == 0:
                #print("loading main game")
                scenario = "BackToTheRoots"

            elif mainSelection == 1:
                #print("loading tutorial")
                scenario = "Tutorials"

            elif mainSelection == 2:
                print("offering the player to start a specific scenario")
                root_console.clear()
                root_console.print(x=3,y=2,string=text)
                while 1:
                    foundEvent = False
                    events = tcod.event.get()
                    for event in events:
                        if isinstance(event,tcod.event.MouseButtonUp):
                            context.convert_event(event)
                            index = event.tile.y-3
                            foundEvent = True
                            scenario = scenarios[index][0]

                        if isinstance(event,tcod.event.KeyDown):
                            translatedKey = None
                            if event.sym == tcod.event.KeySym.m:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "M"
                                else:
                                    translatedKey = "m"
                            if event.sym == tcod.event.KeySym.t:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "T"
                                else:
                                    translatedKey = "t"
                            if event.sym == tcod.event.KeySym.p:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "P"
                                else:
                                    translatedKey = "p"
                            if event.sym == tcod.event.KeySym.b:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "B"
                                else:
                                    translatedKey = "b"
                            if event.sym == tcod.event.KeySym.r:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "R"
                                else:
                                    translatedKey = "r"
                            if event.sym == tcod.event.KeySym.s:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "S"
                                else:
                                    translatedKey = "s"
                            if event.sym == tcod.event.KeySym.c:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "C"
                                else:
                                    translatedKey = "c"
                            if event.sym == tcod.event.KeySym.d:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "D"
                                else:
                                    translatedKey = "d"
                            if event.sym == tcod.event.KeySym.x:
                                if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                                    translatedKey = "X"
                                else:
                                    translatedKey = "x"

                            for checkScenario in scenarios:
                                if checkScenario[2] == translatedKey:
                                    print(checkScenario)
                                    scenario = checkScenario[0]
                                    foundEvent = True
                                    print(scenario)
                                    break

                        if isinstance(event, tcod.event.Quit):
                            raise SystemExit()
                            
                        if foundEvent:
                            break

                    context.present(root_console)
                    if foundEvent:
                        break
                print("scenario")
                print(scenario)
    else:
        scenario = args.scenario

    if not args.notcod:
        #context.close()
        pass

    if scenario == "siege":
        args.terrain = "test"
        args.phase = "Siege"
    elif scenario == "siege2":
        args.terrain = "test"
        args.phase = "Siege2"
    elif scenario == "basebuilding":
        args.terrain = "nothingness"
        args.phase = "BaseBuilding"
    elif scenario == "survival":
        args.terrain = "desert"
        args.phase = "DesertSurvival"
    elif scenario == "creative":
        args.terrain = "nothingness"
        args.phase = "CreativeMode"
    elif scenario == "dungeon":
        args.terrain = "nothingness"
        args.phase = "Dungeon"
    elif scenario == "WorldBuildingPhase":
        args.terrain = "nothingness"
        args.phase = "WorldBuildingPhase"
    elif scenario == "RoguelikeStart":
        args.terrain = "nothingness"
        args.phase = "RoguelikeStart"
    elif scenario == "Tour":
        args.terrain = "nothingness"
        args.phase = "Tour"
    elif scenario == "BackToTheRoots":
        args.terrain = "nothingness"
        args.phase = "BackToTheRoots"
    elif scenario == "PrefabDesign":
        args.terrain = "nothingness"
        args.phase = "PrefabDesign"
    elif scenario == "Tutorials":
        args.terrain = "nothingness"
        args.phase = "Tutorials"
    print("game parameters set to %s %s"%(args.terrain, args.phase,))

if not args.notcod:
    pass

# set rendering mode
if args.urwid:
    if args.unicode:
        displayChars = canvas.DisplayMapping("unicode")
    else:
        displayChars = canvas.DisplayMapping("pureASCII")
elif not args.notcod:
    if args.unicode:
        displayChars = canvas.DisplayMapping("unicode")
    else:
        displayChars = canvas.DisplayMapping("pureASCII")
else:
    displayChars = canvas.TileMapping("testTiles")

# bad code: common variables with modules
canvas.displayChars = displayChars

if args.speed:
    interaction.speed = args.speed

if args.seed:
    seed = int(args.seed)
else:
    import random

    seed = random.randint(1, 100000)

if not args.urwid:
    interaction.nourwid = True

    import src.pseudoUrwid

    interaction.urwid = src.pseudoUrwid
    characters.urwid = src.pseudoUrwid
    interaction.setUpNoUrwid()
else:
    interaction.nourwid = False
    import urwid

    interaction.urwid = urwid
    characters.urwid = urwid
    interaction.setUpUrwid()

if not args.notcod:
    interaction.setUpTcod()

story.registerPhases()

# create and load the gamestate
gamestate.setup(gameIndex)

interaction.debug = args.debug
logger.setup(interaction.debug)

if shouldLoad:
    try:
        # load the game
        loaded = gamestate.gamestate.load()
        seed = gamestate.gamestate.initialSeed
    except Exception as e:
        ignore = input(
            "error in gamestate, could not load gamestate completely. Abort and show error message? (Y/n)"
        )
        if not ignore.lower() == "n":
            raise e
mainChar = gamestate.gamestate.mainChar

################################################################################
#
#         some stuff that is somehow needed but slated for removal
#
################################################################################

interaction.setFooter()

##########################################
#
#  set up the terrain
#
##########################################

if not loaded:
    # spawn selected terrain
    if args.terrain and args.terrain == "scrapField":
        gamestate.gamestate.terrainType = terrains.ScrapField
    elif args.terrain and args.terrain == "nothingness":
        gamestate.gamestate.terrainType = terrains.Nothingness
    elif args.terrain and args.terrain == "test":
        gamestate.gamestate.terrainType = terrains.GameplayTest
    elif args.terrain and args.terrain == "tutorial":
        gamestate.gamestate.terrainType = terrains.TutorialTerrain
    elif args.terrain and args.terrain == "desert":
        gamestate.gamestate.terrainType = terrains.Desert
    else:
        gamestate.gamestate.terrainType = terrains.GameplayTest
else:
    terrain = gamestate.gamestate.terrain
    interaction.lastTerrain = terrain

# state that should be contained in the gamestate
mapHidden = True
mainChar = None

if not loaded:
    gamestate.gamestate.setup(phase=args.phase, seed=seed)
    terrain = gamestate.gamestate.terrainMap[7][7]
    interaction.lastTerrain = terrain

# set up the splash screen
if not args.debug and not interaction.submenue and not loaded:
    text = """

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


    press space to continue

"""
    #openingCinematic = cinematics.TextCinematic(text, rusty=True, scrolling=True)
    #cinematics.cinematicQueue.insert(0, openingCinematic)
    #gamestate.gamestate.openingCinematic = openingCinematic
    #gamestate.gamestate.mainChar.macroState["commandKeyQueue"].insert(
    #    0, (".", ["norecord"])
    #)
    #gamestate.gamestate.mainChar.macroState["commandKeyQueue"].insert(
    #    0, (".", ["norecord"])
    #)
    #gamestate.gamestate.mainChar.macroState["commandKeyQueue"].insert(
    #    0, (".", ["norecord"])
    #)
    #gamestate.gamestate.mainChar.macroState["commandKeyQueue"].insert(
    #    0, (".", ["norecord"])
    #)
else:
    gamestate.gamestate.openingCinematic = None

# set up the current phase
if not loaded:
    gamestate.gamestate.currentPhase.start(seed=seed)

# bad code: loading registry should be cleared

# bad code: common variables with modules

# set up tile based mode
if args.tiles:
    # spawn tile based rendered window
    import pygame

    pygame.init()
    pygame.key.set_repeat(200, 20)
    if args.tileSize:
        interaction.tileSize = args.tileSize
    else:
        interaction.tileSize = 10
    pydisplay = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
    pygame.display.set_caption("Of Mice and Mechs")
    pygame.display.update()
    interaction.pygame = pygame
    interaction.pydisplay = pydisplay
    interaction.useTiles = True
    interaction.tileMapping = canvas.TileMapping("testTiles")
else:
    interaction.useTiles = False
    interaction.tileMapping = None

if args.multiplayer:
    interaction.multiplayer = True
    interaction.fixedTicks = 0.1
else:
    interaction.multiplayer = False
    interaction.fixesTicks = False


################################################################################
#
#     main loop is started here
#
################################################################################

# start the interaction loop of the underlying library
if args.urwid:
    input("game ready. press enter to start")
    interaction.loop.run()

if not args.urwid:
    while 1:
        interaction.gameLoop(None, None)

# print death messages
if gamestate.gamestate.mainChar.dead:
    print("you died.")
    if gamestate.gamestate.mainChar.deathReason:
        print("Cause of death:\n" + gamestate.gamestate.mainChar.deathReason)

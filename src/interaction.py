"""
code for user interaction belongs here
bad pattern: logic should be moved somewhere else
"""
import collections
import json
import logging
import os
import random
import time
import gzip


import src.canvas
import src.chats
import src.gamestate
import src.quests
import src.rooms
import src.terrains
from config import commandChars
from src import cinematics
from multiprocessing import Process

################################################################################
#
#        setting up the basic user interaction library
#         bad code: urwid specific code should be somewhere else
#
################################################################################

logger = logging.getLogger(__name__)
continousOperation = 0
main = None
frame = None
urwid = None
fixedTicks = False
speed = None
libtcodpy = None
noFlicker = False



class EndGame(Exception):
    pass

def advanceGame():
    """
    advance the game
    """
    global multi_chars

    mainCharTerrain = src.gamestate.gamestate.mainChar.getTerrain()
    multi_chars = set()
    for row in src.gamestate.gamestate.terrainMap:
        for specificTerrain in row:
            for character in specificTerrain.characters:
                multi_chars.add(character)
            for room in specificTerrain.rooms:
                for character in room.characters:
                    multi_chars.add(character)
            specificTerrain.advance()
            if specificTerrain != mainCharTerrain:
                specificTerrain.animations = []
                for room in specificTerrain.rooms:
                    room.animations = []

    for extraRoot in src.gamestate.gamestate.extraRoots:
        for character in extraRoot.characters:
            multi_chars.add(character)

    src.gamestate.gamestate.multi_chars = multi_chars
    src.gamestate.gamestate.tick += 1
    logger.info("Tick %d", src.gamestate.gamestate.tick)

    for character in multi_chars:
        character.timeTaken -= 1

    for character in multi_chars:
        advanceChar(character)


    if src.gamestate.gamestate.tick%(15*15*15) == 0:
        for god in src.gamestate.gamestate.gods.values():
            if "mana" not in god:
                god["mana"] = 0
            god["mana"] += 10

        for (godId,god) in src.gamestate.gamestate.gods.items():
            terrain = src.gamestate.gamestate.terrainMap[god["lastHeartPos"][1]][god["lastHeartPos"][0]]
            foundEmptyGlassStatue = None
            hasItem = False
            for room in terrain.rooms:
                glassStatues = room.getItemsByType("GlassStatue")
                for glassStatue in glassStatues:
                    if glassStatue.itemID != godId:
                        continue

                    if glassStatue.hasItem:
                        hasItem = True
                    else:
                        foundEmptyGlassStatue = glassStatue

            if not hasItem and foundEmptyGlassStatue:
                foundEmptyGlassStatue.hasItem = True

        for god in src.gamestate.gamestate.gods.values():
            terrain = src.gamestate.gamestate.terrainMap[god["lastHeartPos"][1]][god["lastHeartPos"][0]]
            increaseAmount = min(1,terrain.maxMana-terrain.mana)
            terrain.mana += increaseAmount

        if not src.gamestate.gamestate.difficulty == "tutorial":
            src.magic.spawnWaves()
    if settings.get("auto save"):
        if src.gamestate.gamestate.tick % 150 == 0:
            src.gamestate.gamestate.save()
            src.gamestate.gamestate.mainChar.addMessage("auto saved")

def advanceGame_disabled():
    """
    advance the game
    """
    global multi_chars

    multi_chars = set()
    for row in src.gamestate.gamestate.terrainMap:
        for specificTerrain in row:
            for character in specificTerrain.characters:
                multi_chars.add(character)
            for room in specificTerrain.rooms:
                for character in room.characters:
                    multi_chars.add(character)
            specificTerrain.advance()

    for extraRoot in src.gamestate.gamestate.extraRoots:
        for character in extraRoot.characters:
            multi_chars.add(character)

    src.gamestate.gamestate.multi_chars = multi_chars
    src.gamestate.gamestate.tick += 1

    #if src.gamestate.gamestate.tick%100 == 15:
    #    src.gamestate.gamestate.save()

class AbstractedDisplay:
    """
    an abstraction that allows to not only use urwid for texts
    """

    def __init__(self, urwidInstance):
        self.urwidInstance = urwidInstance
        self.text = ""

    def set_text(self, text):
        if self.urwidInstance:
            self.urwidInstance.set_text(text)
        self.text = text

    def get_text(self):
        return self.text

    def renderSDL2(self):
        pass

tcodConsole = None
tcodContext = None
tcod = None
soundloader = None
tcodAudio = None
tcodAudioDevice = None
tcodMixer = None
sounds = {}
settings = None

def playSound(soundName,channelName,loop=False):
    if settings["sound"] != 0:
        channel = src.interaction.tcodMixer.get_channel(channelName)
        if not channel.busy:
            channel.play(sounds[soundName], volume = settings["sound"]/32)

def checkResetWindowSize(width,height):
    tileHeight = height//51//2*2
    if tileHeight < 6:
        tileHeight = 6
    if tileHeight > 20:
        tileHeight = 20

    newHeight = height//tileHeight
    newWidth  = (width//tileHeight)*2
    tileset = tcod.tileset.load_tilesheet(
        f"scaled_{tileHeight//2}x{tileHeight}.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    tcodContext.change_tileset(tileset)

    global tcodConsole
    root_console = tcod.console.Console(newWidth, newHeight, order="F")
    tcodConsole = root_console

def setUpTcod():
    global settings
    if os.path.isfile("config/globalSettings.json"):
                with open("config/globalSettings.json") as f:
                    settings = json.loads(f.read())
    else:
        settings = {"auto save": False, "sound": 32, "fullscreen": True} #Default Settings
    
    import tcod as internalTcod
    global tcod
    tcod = internalTcod

    """
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    tileset = tcod.tileset.load_tilesheet(
        "terminal.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    tileset = tcod.tileset.load_tilesheet(
        "ownFont2.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    """
    """
    tileset = tcod.tileset.load_tilesheet(
        "OfMiceAndMechs_7x15.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    """
    tileset = tcod.tileset.load_tilesheet(
        "scaled_7x14.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    """
    tileset =  tcod.tileset.load_truetype_font("./config/font/dejavu-sans-mono-fonts-ttf-2.35/ttf/DejaVuSansMono.ttf",48,24)
    """

    context = tcod.context.new_terminal(
            None,
            None,
            tileset=tileset,
            title="OfMiceAndMechs",
            vsync=True,
            sdl_window_flags=tcod.lib.SDL_WINDOW_RESIZABLE | tcod.lib.SDL_WINDOW_MAXIMIZED,
                )
    size = context.recommended_console_size()

    root_console = tcod.console.Console(size[0], size[1], order="F")
    global tcodConsole
    global tcodContext
    tcodConsole = root_console
    tcodContext = context


    root_console.print(x=1,y=1,string="loading game")

    context.present(root_console,integer_scaling=True,keep_aspect=True)

    tcod.lib.SDL_SetWindowFullscreen(
        tcodContext.sdl_window_p,
        tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP if settings["fullscreen"] else 0,
    )
    
    import soundfile as sf
    import tcod.sdl.audio as audio

    global soundloader
    soundloader = sf

    global sounds
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/step.ogg',dtype='float32')
    sounds["step"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/scrapcompactorUsed.ogg',dtype='float32')
    sounds["scrapcompactorUsed"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/machineUsed.ogg',dtype='float32')
    sounds["machineUsed"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/workshopRoom.ogg',dtype='float32')
    sounds["workshopRoom"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/electroRoom.ogg',dtype='float32')
    sounds["electroRoom"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/playerDeath.ogg',dtype='float32')
    sounds["playerDeath"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/died.wav',dtype='float32')
    sounds["enemyDied"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/hurt.wav',dtype='float32')
    sounds["hurt"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/shot.wav',dtype='float32')
    sounds["shot"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/explosion.wav',dtype='float32')
    sounds["explosion"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/itemDropped.ogg',dtype='float32')
    sounds["itemDropped"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/itemPickedUp.ogg',dtype='float32')
    sounds["itemPickedUp"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/machineUsed.ogg',dtype='float32')
    sounds["machineUsed"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/loop1.wav',dtype='float32')
    sounds["loop1"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/loop2.wav',dtype='float32')
    sounds["loop2"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read("sounds/loop1_start.wav", dtype="float32")
    sounds["loop1_start"] = sound_clip
    global tcodAudio
    tcodAudio = audio

    """
    tcod.lib.SDL_SetWindowFullscreen(
        context.sdl_window_p,
        tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
    )
    """

    global tcodMixer
    global tcodAudioDevice
    device = src.interaction.tcodAudio.open(samples = 12000)
    tcodAudioDevice = device
    mixer = src.interaction.tcodAudio.BasicMixer(device)
    tcodMixer = mixer

    """
    if not context.sdl_window_p:
        return
    fullscreen = tcod.lib.SDL_GetWindowFlags(context.sdl_window_p) & (
        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
    )
    tcod.lib.SDL_SetWindowFullscreen(
        context.sdl_window_p,
        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
    )
    """
    tcodMixer.get_channel("background").play(sound = sounds["loop1_start"],volume = settings["sound"]/ 32.0,on_end = sound_loop)

def sound_loop(ch):
    if random.random() < 0.5:
        ch.play(sound = sounds["loop1"],volume = settings["sound"]/32.0,on_end = sound_loop)
    else:
        ch.play(sound = sounds["loop2"],volume = settings["sound"]/32.0,on_end = sound_loop)

def changeVolume():
    channel = tcodMixer.get_channel("background")
    channel.volume = settings["sound"]/ 32.0
    
footer = None
main = None
header = None

def setUpUrwid():
    """
    initialise console based rendering
    """

    import urwid

    # the containers for the shown text
    urwidHeader = urwid.Text("")
    urwidMain = urwid.Text("")
    urwidFooter = urwid.Text("", align="right")

    global footer
    global main
    global header

    global frame
    global loop

    if not src.gamestate.gamestate.header:
        src.gamestate.gamestate.header = AbstractedDisplay(urwidHeader)
    if not src.gamestate.gamestate.main:
        src.gamestate.gamestate.main = AbstractedDisplay(urwidMain)
    if not src.gamestate.gamestate.footer:
        src.gamestate.gamestate.footer = AbstractedDisplay(urwidFooter)

    header = src.gamestate.gamestate.header
    main = src.gamestate.gamestate.main
    footer = src.gamestate.gamestate.footer

    urwidMain.set_layout("left", "clip")
    frame = urwid.Frame(
        urwid.Filler(urwidMain, "top"), header=urwidHeader, footer=urwidFooter
    )

    # get the interaction loop from the library
    loop = urwid.MainLoop(frame, unhandled_input=keyboardListener)

    loop.set_alarm_in(0.1, gameLoop)

    loop.set_alarm_in(0.1, handleMultiplayerClients)


def setUpNoUrwid():
    """
    initialise rendering without a console
    """

    global footer
    global main
    global header

    if not src.gamestate.gamestate.header:
        src.gamestate.gamestate.header = AbstractedDisplay(None)
    if not src.gamestate.gamestate.main:
        src.gamestate.gamestate.main = AbstractedDisplay(None)
    if not src.gamestate.gamestate.footer:
        src.gamestate.gamestate.footer = AbstractedDisplay(None)

    header = src.gamestate.gamestate.header
    main = src.gamestate.gamestate.main
    footer = src.gamestate.gamestate.footer

# timestamps for detecting periods in inactivity etc
lastLagDetection = time.time()
lastRedraw = time.time()

# states for stateful interaction
fullAutoMode = False
idleCounter = 0
submenue = None
ticksSinceDeath = None
levelAutomated = 0

# the state for the footer
# bad code: this should be contained in an object
footerInfo = []
footerText = ""
doubleFooterText = footerText + footerText
footerPosition = 0
footerLength = len(footerText)
footerSkipCounter = 20

macros = {}

# obsolete: redo or delete
def setFooter():
    """
    calculate and set footer text
    """

    # bad code: global variables
    global footerInfo
    global footerText
    global doubleFooterText
    global footerPosition
    global footerLength
    global footerSkipCounter

    # calculate the text
    # bad pattern: footer should be dynamically generated
    footerInfo = [
        "@  = you",
        "XX = Wall",
        ":: = floor",
        "[] = door",
        "** = pipe",
        "is = scrap",
        "is = scrap",
        "oo / öö = furnace",
        "OO / 00 = growth tank",
        "|| / // = lever",
        "@a / @b ... @z = npcs",
        "xX = quest marker (your current target)",
        "press " + commandChars.show_help + " for help",
        "press " + commandChars.move_north + " to move north",
        "press " + commandChars.move_south + " to move south",
        "press " + commandChars.show_quests + " for quests",
        "press " + commandChars.show_quests_detailed + " for advanced quests",
        "press " + commandChars.show_inventory + " for inventory",
        "press " + commandChars.move_west + " to move west",
        "press " + commandChars.move_east + " to move east",
        "press " + commandChars.activate + " to activate",
        "press " + commandChars.pickUp + " to pick up",
        "press " + commandChars.hail + " to talk",
        "press " + commandChars.drop + " to drop",
    ]
    footerText = ", ".join(footerInfo) + ", "

    # calculate meta information for footer
    doubleFooterText = footerText + footerText
    doubleFooterText = "- press " + commandChars.show_help + " for an help text -"
    doubleFooterText = doubleFooterText * 20
    footerPosition = 0
    footerLength = len(footerText)
    footerSkipCounter = 20

# bad code: keystrokes should not be injected in the first place
def callShow_or_exit(loop, key):
    """
    helper function around urwids key handling
    is used to inject keystrokes

    Parameters:
        loop: the urwid main loop
        key: the key pressed
    """

    show_or_exit(key)

def show_or_exit(key,targetCharacter=None):
    """
    add keystrokes from urwid to the players command queue

    Parameters:
        key: the key pressed
        charState: the state of the char to add the keystroke to
    """

    if not targetCharacter:
        char = src.gamestate.gamestate.mainChar
    else:
        char = targetCharacter

    char.runCommandString((key,),nativeKey=True,addBack=True)

shownStarvationWarning = False

def moveCharacter(direction,char,noAdvanceGame,header,urwid,dash=False):

    # do inner room movement
    if char.room:
        item = char.room.moveCharacterDirection(char, direction, dash=dash)

        # remember items bumped into for possible interaction
        if item:
            char.addMessage("You cannot walk there " + str(direction))
            char.addMessage("press " + commandChars.activate + " to apply")
            if not noAdvanceGame:
                header.set_text(
                    (
                        urwid.AttrSpec("default", "default"),
                        renderHeader(char),
                    )
                )
            return item
        else:
            char.changed("moved", (char, direction))
            return None

    # do movement on terrain
    # bad code: these calculation should be done elsewhere
    else:
        if not char.terrain:
            return None

        return char.terrain.moveCharacterDirection(char, direction, dash=dash)

def handleCollision(char,charState):
    if charState["itemMarkedLast"] and char.personality["moveItemsOnCollision"]:
        char.runCommandString("kl")
        return
    if charState["itemMarkedLast"] and char.personality["avoidItems"]:
        char.runCommandString(random.choice(("a","w","s","d",)))
        return
    char.changed("itemCollision")
    if not char.container:
        return
    char.container.addAnimation(charState["itemMarkedLast"].getPosition(),"showchar",4,{"char":(urwid.AttrSpec("#fff", "#000"), "XX")})


def handleActivityKeypress(char, header, main, footer, flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

press key to select action

* w/s/a/d = move one tile north/south/west/east
* m = move to tile
* M = move to terrain
* g = run guard mode for 10 ticks
* h = get emergency heatlh
"""
        header.set_text(
            (urwid.AttrSpec("default", "default"), "action menu")
        )
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    char.interactionState["runaction"] = {}

def handleActivitySelection(key,char):
    if key in ("w","a","s","d"):
        if isinstance(char.container,src.rooms.Room):
            charPos = char.container.getPosition()
        else:
            charPos = (char.xPosition//15,char.yPosition//15,0)

        if key in ("w",):
            newPos = (charPos[0],charPos[1]-1,charPos[2])
        if key in ("s",):
            newPos = (charPos[0],charPos[1]+1,charPos[2])
        if key in ("a",):
            newPos = (charPos[0]-1,charPos[1],charPos[2])
        if key in ("d",):
            newPos = (charPos[0]+1,charPos[1],charPos[2])

        quest = src.quests.questMap["GoToTile"](targetPosition=newPos,paranoid=True)
        quest.autoSolve = True
        quest.assignToCharacter(char)
        quest.activate()

        char.quests.insert(0,quest)

    if key == "g":
        char.startGuarding(1)
    if key == "h":
        char.getEmergencyHealth()
    if key == "M":
        terrain = char.getTerrain()

        # render empty map
        mapContent = char.renderZoneInfo()
        functionMap = {}
        extraText = "test"

        submenue = src.menuFolder.mapMenu.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=char.getTerrain().getPosition())
        char.macroState["submenue"] = submenue
        char.runCommandString("~",nativeKey=True)

        for x in range(1,14):
            for y in range(1,14):
                functionMap[(x,y)] = {}
                functionMap[(x,y)]["j"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveToTerrain",
                        "params":{},
                    },
                    "description":"move to tile",
                }

    if key == "m":
        terrain = char.getTerrain()

        # render empty map
        mapContent = []
        for x in range(15):
            mapContent.append([])
            for y in range(15):
                if x not in (0, 14) and y not in (0, 14):
                    displayChar = "  "
                elif x != 7 and y != 7:
                    displayChar = "##"
                else:
                    displayChar = "  "
                mapContent[x].append(displayChar)

        functionMap = {}

        for x in range(1,14):
            for y in range(1,14):
                functionMap[(x,y)] = {}
                functionMap[(x,y)]["j"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveToTile",
                        "params":{},
                    },
                    "description":"move to tile",
                }
                functionMap[(x,y)]["c"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveFixedTileTarget",
                        "params":{"targetCoordinate":(7,7,0)},
                    },
                    "description":"move to center",
                }
                functionMap[(x,y)]["W"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveFixedTileTarget",
                        "params":{"targetCoordinate":(7,1,0)},
                    },
                    "description":"move to north crossing",
                }
                functionMap[(x,y)]["A"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveFixedTileTarget",
                        "params":{"targetCoordinate":(1,7,0)},
                    },
                    "description":"move to west crossing",
                }
                functionMap[(x,y)]["S"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveFixedTileTarget",
                        "params":{"targetCoordinate":(7,13,0)},
                    },
                    "description":"move to south crossing",
                }
                functionMap[(x,y)]["D"] = {
                    "function": {
                        "container":char,
                        "method":"triggerAutoMoveFixedTileTarget",
                        "params":{"targetCoordinate":(13,7,0)},
                    },
                    "description":"move to east crossing",
                }

        for scrapField in terrain.scrapFields:
            mapContent[scrapField[1]][scrapField[0]] = "ss"

        for forest in terrain.forests:
            mapContent[forest[1]][forest[0]] = "ff"

        for room in terrain.rooms:
            if not (len(room.itemsOnFloor) > 13+13+11+11 or room.floorPlan or room.storageSlots or len(room.walkingSpace) > 4 or room.inputSlots):
                mapContent[room.yPosition][room.xPosition] = "EE"
            else:
                mapContent[room.yPosition][room.xPosition] = room.displayChar

        extraText = "\n\n"

        submenue = src.menuFolder.mapMenu.MapMenu(mapContent=mapContent,functionMap=functionMap, extraText=extraText, cursor=char.getBigPosition())
        char.macroState["submenue"] = submenue
        char.runCommandString("~",nativeKey=True)
    del char.interactionState["runaction"]

def handleStartMacroReplayChar(key,char,charState,main,header,footer,urwid,flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

press key for macro to replay

current macros:

"""
        for key, value in charState["macros"].items():
            compressedMacro = ""
            for keystroke in value:
                if len(keystroke) == 1:
                    compressedMacro += keystroke
                else:
                    compressedMacro += "/" + keystroke + "/"

            text += f"""
{key} - {compressedMacro}"""

        header.set_text((urwid.AttrSpec("default", "default"), "record macro"))
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    charState["replay"].append("")

def handleMacroReplayChar(key,char,charState,main,header,footer,urwid,flags):
    if charState["replay"] and (
        charState["replay"][-1] == ""
        or charState["replay"][-1][-1].isupper()
        or charState["replay"][-1][-1] == " "
    ):
        if not charState["number"]:

            charState["replay"][-1] += key

            if (
                charState["replay"][-1][-1].isupper()
                or charState["replay"][-1][-1] == " "
            ):

                if "norecord" in flags:
                    return

                if src.gamestate.gamestate.mainChar == char and 1==0:
                    text = """

    press key for macro to replay

    %s

    current macros:

    """ % (
                        charState["replay"][-1]
                    )

                    for macroName, value in charState["macros"].items():
                        if not macroName.startswith(charState["replay"][-1]):
                            continue

                        compressedMacro = ""
                        for keystroke in value:
                            if len(keystroke) == 1:
                                compressedMacro += keystroke
                            else:
                                compressedMacro += "/" + keystroke + "/"

                        text += f"""
    {macroName} - {compressedMacro}"""

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "record macro")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                return

            if charState["replay"][-1] in charState["macros"]:
                char.addMessage(
                    "replaying {}: {}".format(
                        charState["replay"][-1],
                        "".join(charState["macros"][charState["replay"][-1]]),
                    )
                )
            else:
                char.addMessage(
                    "no macro recorded to %s" % (charState["replay"][-1])
                )

            stitchCommands(charState)

            charState["replay"].pop()
        else:
            num = int(charState["number"])
            charState["number"] = None

            charState["doNumber"] = True

            command = ""
            counter = 0
            while counter < num:
                command += "_"+key
                counter += 1
            charState["replay"].pop()

            char.runCommandString(command)

            charState["doNumber"] = False

def stitchCommands(charState):
    """
    commands = []
    for keyPress in charState["macros"][charState["replay"][-1]]:
        commands.append((keyPress, ["norecord"]))
    charState["commandKeyQueue"] = (
        commands + charState["commandKeyQueue"]
    )
    """
    if charState["replay"][-1] not in charState["macros"]:
        return
    stitchCommands2(charState,reversed(charState["macros"][charState["replay"][-1]]))

def stitchCommands2(charState,inCommands):
    commands = []
    flags = ["norecord"]
    for keyPress in inCommands:
        commands.append(stitchCommands4(keyPress, flags))
    stitchCommands3(charState,commands)

def stitchCommands4(keyPress,flags):
    return (keyPress, flags)

def stitchCommands3(charState,commands):
    charState["commandKeyQueue"].extend(commands)
    #commands = [('g', ['norecord']), ('g', ['norecord']), ('_', ['norecord']), ('g', ['norecord'])]

def handleRecordingChar(key,char,charState,main,header,footer,urwid,flags):
    if (
        key not in ("lagdetection", "lagdetection_", "-")
        or char.interactionState.get("varActions")
    ):
        if (
            charState["recordingTo"] is None
            or charState["recordingTo"][-1].isupper()
            or charState["recordingTo"][-1] == " "
        ):
            if charState["recordingTo"] is None:
                charState["recordingTo"] = key
            else:
                charState["recordingTo"] += key

            if not (key.isupper() or key == " "):
                charState["macros"][charState["recordingTo"]] = []
                char.addMessage(
                    "start recording to: %s" % (charState["recordingTo"])
                )
            else:
                if (
                    src.gamestate.gamestate.mainChar == char
                    and "norecord" not in flags
                ):
                    text = """

type the macro name you want to record to

%s

""" % (
                        charState["recordingTo"]
                    )

                    for key, value in charState["macros"].items():

                        if not key.startswith(charState["recordingTo"]):
                            continue

                        compressedMacro = ""
                        for keystroke in value:
                            if len(keystroke) == 1:
                                compressedMacro += keystroke
                            else:
                                compressedMacro += "/" + keystroke + "/"

                        text += f"""
{key} - {compressedMacro}"""

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "record macro")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True

            return None
        else:
            if "norecord" not in flags:
                charState["macros"][charState["recordingTo"]].append(key)
    return (1,key)

def checkRecording(key,char,charState,main,header,footer,urwid,flags):
    return handleRecordingChar(key,char,charState,main,header,footer,urwid,flags)

def doAdvancedInteraction(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    if not char.container:
        del char.interactionState["advancedInteraction"]
        return
    if key == "w":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition - 1, char.zPosition)
        )
        if items:
            items[0].apply(char)
            char.timeTaken += char.movementSpeed
    elif key == "s":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition + 1, char.zPosition)
        )
        if items:
            items[0].apply(char)
            char.timeTaken += char.movementSpeed
    elif key == "d":
        items = char.container.getItemByPosition(
            (char.xPosition + 1, char.yPosition, char.zPosition)
        )
        if items:
            items[0].apply(char)
            char.timeTaken += char.movementSpeed
    elif key == "a":
        items = char.container.getItemByPosition(
            (char.xPosition - 1, char.yPosition, char.zPosition)
        )
        if items:
            items[0].apply(char)
            char.timeTaken += char.movementSpeed
    elif key == ".":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition, char.zPosition)
        )
        if items:
            items[0].apply(char)
            char.timeTaken += char.movementSpeed
    elif key == "i":
        if char.inventory:
            char.inventory[-1].apply(char)
    elif key == "j":
        character = char
        if not character.jobOrders:
            char.addMessage("no job Order")
            return

        if not character.jobOrders[-1].getTask():
            character.jobOrders.pop()
            del char.interactionState["advancedInteraction"]
            return

        if character.jobOrders:
            character.jobOrders[-1].apply(character)
        else:
            for item in reversed(character.inventory):
                if isinstance(item, src.items.itemMap["JobOrder"]):
                    item.apply(char)
                    char.addMessage("ran job Order")
                    break
    elif key == "f":
        character = char
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["GooFlask"]) and item.uses > 0:
                item.apply(character)
                break
            if (
                isinstance(item, src.items.itemMap["BioMass"]) or isinstance(item,src.items.itemMap["Bloom"]) or isinstance(item,src.items.itemMap["PressCake"]) or isinstance(item,src.items.itemMap["SickBloom"])
            ):
                item.apply(character)
                character.inventory.remove(item)
                break
            if isinstance(item, src.items.itemMap["Corpse"]):
                item.apply(character)
                break
    elif key in {"h","H"}:
        character = char
        for item in character.inventory:
            if isinstance(item, src.items.itemMap["Vial"]) and item.uses > 0:
                if key == "h":
                    item.apply(character)
                    break

                while item.uses and character.health < character.maxHealth:
                    item.apply(character)
    del char.interactionState["advancedInteraction"]

def doAdvancedConfiguration(key,char,charState,main,header,footer,urwid,flags):
    if not char.container:
        del char.interactionState["advancedConfigure"]
        return
    if key == "w":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition - 1, char.zPosition)
        )
        if items:
            items[0].configure(char)
            char.runCommandString("~",nativeKey=True)
            char.timeTaken += char.movementSpeed
    elif key == "s":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition + 1, char.zPosition)
        )
        if items:
            items[0].configure(char)
            char.runCommandString("~",nativeKey=True)
            char.timeTaken += char.movementSpeed
    elif key == "d":
        items = char.container.getItemByPosition(
            (char.xPosition + 1, char.yPosition, char.zPosition)
        )
        if items:
            items[0].configure(char)
            char.runCommandString("~",nativeKey=True)
            char.timeTaken += char.movementSpeed
    elif key == "a":
        items = char.container.getItemByPosition(
            (char.xPosition - 1, char.yPosition, char.zPosition)
        )
        if items:
            items[0].configure(char)
            char.runCommandString("~",nativeKey=True)
            char.timeTaken += char.movementSpeed
    elif key == ".":
        items = char.container.getItemByPosition(
            (char.xPosition, char.yPosition, char.zPosition)
        )
        if items:
            items[0].configure(char)
            char.runCommandString("~",nativeKey=True)
            char.timeTaken += char.movementSpeed
    elif key == "i" and char.inventory:
        char.inventory[-1].configure(char)
    del char.interactionState["advancedConfigure"]

def doAdvancedPickup(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    if char.container is None:
        del char.interactionState["advancedPickup"]
        return

    char.timeTaken += char.movementSpeed
    if len(char.inventory) >= 10:
        if key == "w":
            char.container.addAnimation(char.getPosition(offset=(0,-1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        if key == "s":
            char.container.addAnimation(char.getPosition(offset=(0,1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        if key == "d":
            char.container.addAnimation(char.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        if key == "a":
            char.container.addAnimation(char.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        char.container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"[]")})
        char.addMessage("you cannot carry more items")
    elif not char.container:
        pass
    else:
        container = char.container
        if key == "w":
            items = container.getItemByPosition(
                (char.xPosition, char.yPosition - 1, char.zPosition)
            )
            if items:
                item = items[0]
                item.pickUp(char)
                container.addAnimation(char.getPosition(offset=(0,-1,0)),"charsequence",1,{"chars":["--",item.render()]})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":[item.render(),"++"]})
            else:
                char.addMessage("no item to pick up")
                container.addAnimation(char.getPosition(offset=(0,-1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        elif key == "s":
            items = char.container.getItemByPosition(
                (char.xPosition, char.yPosition + 1, char.zPosition)
            )
            if items:
                item = items[0]
                item.pickUp(char)
                container.addAnimation(char.getPosition(offset=(0,1,0)),"charsequence",1,{"chars":["--",item.render()]})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":[item.render(),"++"]})
            else:
                char.addMessage("no item to pick up")
                container.addAnimation(char.getPosition(offset=(0,1,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        elif key == "d":
            items = char.container.getItemByPosition(
                (char.xPosition + 1, char.yPosition, char.zPosition)
            )
            if items:
                item = items[0]
                item.pickUp(char)
                container.addAnimation(char.getPosition(offset=(1,0,0)),"charsequence",1,{"chars":["--",item.render()]})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":[item.render(),"++"]})
            else:
                char.addMessage("no item to pick up")
                container.addAnimation(char.getPosition(offset=(1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        elif key == "a":
            items = char.container.getItemByPosition(
                (char.xPosition - 1, char.yPosition, char.zPosition)
            )
            if items:
                item = items[0]
                item.pickUp(char)
                container.addAnimation(char.getPosition(offset=(-1,0,0)),"charsequence",1,{"chars":["--",item.render()]})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"charsequence",1,{"chars":[item.render(),"++"]})
            else:
                char.addMessage("no item to pick up")
                container.addAnimation(char.getPosition(offset=(-1,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
                container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
        elif key == ".":
            items = char.container.getItemByPosition(
                (char.xPosition, char.yPosition, char.zPosition)
            )
            if items:
                item = items[0]
                item.pickUp(char)
            else:
                char.addMessage("no item to pick up")
                container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
    del char.interactionState["advancedPickup"]

def doAdvancedDrop(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    char.timeTaken += char.movementSpeed
    if key == "w":
        pos = (char.xPosition, char.yPosition - 1, char.zPosition)
    elif key == "s":
        pos = (char.xPosition, char.yPosition + 1, char.zPosition)
    elif key == "d":
        pos = (char.xPosition + 1, char.yPosition + 0, char.zPosition)
    elif key == "a":
        pos = (char.xPosition - 1, char.yPosition + 0, char.zPosition)
    else:
        pos = (char.xPosition, char.yPosition, char.zPosition)

    char.drop(
        None,
        pos
    )
    del char.interactionState["advancedDrop"]

def doStateChange(key,char,charState,main,header,footer,urwid,flags):
    if key in (">",):
        # do stateSave
        char.interactionState["replay"] = charState["replay"]
        char.interactionState["submenue"] = charState["submenue"]
        char.interactionState["number"] = charState["number"]
        char.interactionState["itemMarkedLast"] = charState["itemMarkedLast"]
        char.interactionState["macrostate"] = charState
        char.interactionStateBackup.append(char.interactionState)
        char.interactionState = {}
        charState["replay"] = []
        charState["submenue"] = None
        charState["number"] = None
        charState["itemMarkedLast"] = None
    elif key in ("<",):
        if len(char.interactionStateBackup):
            char.interactionState = char.interactionStateBackup.pop()
            charState["replay"] = char.interactionState["replay"]
            charState["submenue"] = char.interactionState["submenue"]
            charState["number"] = char.interactionState["number"]
            charState["itemMarkedLast"] = char.interactionState["itemMarkedLast"]
        else:
            char.addMessage("nothing to restore")
        del char.interactionState["stateChange"]

def doHandleMenu(key,char,charState,main,header,footer,urwid,flags):
    # let the submenu handle the keystroke
    lastSubmenu = charState["submenue"]
    noRender = True
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        noRender = False
    done = charState["submenue"].handleKey(key, noRender=noRender, character=char)

    if lastSubmenu != charState["submenue"]:
        charState["submenue"].handleKey("~", noRender=noRender, character=char)
        done = False

    # reset rendering flags
    if done:
        charState["submenue"] = None
        char.specialRender = False

def doStackPop(key,char,charState,main,header,footer,urwid,flags):
    if key in char.registers:
        char.registers[key].pop()
        if not len(char.registers[key]):
            del char.registers[key]
    char.doStackPop = False

def doStackPush(key,char,charState,main,header,footer,urwid,flags):
    if key not in char.registers:
        char.registers[key] = []
    char.registers[key].append(0)
    char.doStackPush = False

def doRangedAttack(key,char):
    char.doRangedAttack(direction=key)
    del char.interactionState["fireDirection"]

def doFunctionCall(key,char,charState,main,header,footer,urwid,flags):
    if key not in (" ", "backspace", "enter"):
        char.interactionState["functionCall"] += key

        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            header.set_text((urwid.AttrSpec("default", "default"), "call function"))
            main.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    """

call function %s
"""
                    % (char.interactionState["functionCall"]),
                )
            )
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True
    else:
        char.addMessage(char.interactionState["functionCall"])
        if char.interactionState["functionCall"] == "clear":
            char.registers = {}
            #char.jobOrders = []
        if char.interactionState["functionCall"] == "clear registers":
            char.registers = {}
        if char.interactionState["functionCall"] == "clearJobOrders":
            char.jobOrders = []
        if char.interactionState["functionCall"] == "huntkill":
            char.huntkill()
        del char.interactionState["functionCall"]

def doEnumerateState(key,char,charState,main,header,footer,urwid,flags):
    if char.interactionState["enumerateState"][-1]["type"] is None:
        char.interactionState["enumerateState"][-1]["type"] = key
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            header.set_text((urwid.AttrSpec("default", "default"), "observe"))
            main.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    """

get position for what thing

* d - drill
* s - scrap
* f - food
* c - character
* m - marker bean
* C - coal
* M - corpse
* e - enemy
* x - tilecenter
* k - command
* n - machinery
* j - jobOrder
* J - jobBoard
* t - transport in
* T - transport out
* R - room tile

""",
                )
            )
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True
        return

    if char.interactionState["enumerateState"][-1]["type"] == "p":
        char.addMessage("type:" + key)

        if key == "d":
            char.interactionState["enumerateState"][-1]["target"] = ["Drill"]
        elif key == "s":
            char.interactionState["enumerateState"][-1]["target"] = ["Scrap"]
        elif key == "f":
            char.interactionState["enumerateState"][-1]["target"] = [
                "Corpse",
                "GooFlask",
                "Bloom",
                "SickBloom",
                "BioMass",
                "PressCake",
            ]
        elif key == "c":
            char.interactionState["enumerateState"][-1]["target"] = ["character"]
        elif key == "m":
            char.interactionState["enumerateState"][-1]["target"] = ["MarkerBean"]
        elif key == "C":
            char.interactionState["enumerateState"][-1]["target"] = ["Coal"]
        elif key == "k":
            char.interactionState["enumerateState"][-1]["target"] = ["Command"]
        elif key == "M":
            char.interactionState["enumerateState"][-1]["target"] = ["Corpse"]
        elif key == "n":
            char.interactionState["enumerateState"][-1]["target"] = [
                "Machine",
                "ScrapCompactor",
            ]
        elif key == "e":
            char.interactionState["enumerateState"][-1]["target"] = ["enemy"]
        elif key == "r":
            char.interactionState["enumerateState"][-1]["target"] = ["roomEntry"]
        elif key == "R":
            char.interactionState["enumerateState"][-1]["target"] = ["roomTile"]
        elif key == "x":
            if "d" not in char.registers:
                char.registers["d"] = [0]
            if "s" not in char.registers:
                char.registers["s"] = [0]
            if "a" not in char.registers:
                char.registers["a"] = [0]
            if "w" not in char.registers:
                char.registers["w"] = [0]
            if char.xPosition:
                char.registers["d"][-1] = 7 - char.xPosition % 15
                char.registers["s"][-1] = 7 - char.yPosition % 15
            char.registers["a"][-1] = -char.registers["d"][-1]
            char.registers["w"][-1] = -char.registers["s"][-1]
            char.addMessage(
                "found in direction {}a {}s {}d {}w".format(
                    char.registers["a"][-1],
                    char.registers["s"][-1],
                    char.registers["d"][-1],
                    char.registers["w"][-1],
                )
            )
            char.interactionState["enumerateState"].pop()
            return
        elif key == "j":
            char.interactionState["enumerateState"][-1]["target"] = ["JobOrder"]
        elif key == "s":
            char.interactionState["enumerateState"][-1]["target"] = ["JobBoard"]
        elif key == "t":
            char.interactionState["enumerateState"][-1]["target"] = [
                "TransportInNode"
            ]
        elif key == "T":
            char.interactionState["enumerateState"][-1]["target"] = [
                "TransportOutNode"
            ]
        else:
            char.addMessage("not a valid target")
            char.interactionState["enumerateState"].pop()
            return

        if "a" not in char.registers:
            char.registers["a"] = [0]
        char.registers["a"][-1] = 0
        if "w" not in char.registers:
            char.registers["w"] = [0]
        char.registers["w"][-1] = 0
        if "s" not in char.registers:
            char.registers["s"] = [0]
        char.registers["s"][-1] = 0
        if "d" not in char.registers:
            char.registers["d"] = [0]
        char.registers["d"][-1] = 0

        if not char.container:
            char.addMessage("character is nowhere")
            char.interactionState["enumerateState"].pop()
            return

        foundItems = []
        foundItemQuery = False
        for query in char.interactionState["enumerateState"][-1]["target"]:
            if query not in ("character", "enemy", "roomEntry", "roomTile"):
                foundItemQuery = True
                break
        if foundItemQuery:
            listFound = []
            if char.room:
                itemDict = char.container.itemByCoordinates
            else:
                itemDict = char.container.itemsByCoordinate
            for (pos, value) in itemDict.items():  # <= really really bad and horribly slow. iterate like 10000 items
                if (
                    pos[0] - (char.xPosition - char.xPosition % 15) > 13
                    or pos[0] - (char.xPosition - char.xPosition % 15) < 1
                ):
                    continue
                if (
                    pos[1] - (char.yPosition - char.yPosition % 15) > 13
                    or pos[1] - (char.yPosition - char.yPosition % 15) < 1
                ):
                    continue
                if value:
                    listFound.append(value[-1])

            for item in listFound:
                if (
                    item.type not in char.interactionState["enumerateState"][-1]["target"]
                ):
                    continue
                foundItems.append(item)

        if "roomTile" in char.interactionState["enumerateState"][-1]["target"] and char.terrain:
            for room in char.terrain.rooms:
                foundItems.append(room)

        if "character" in char.interactionState["enumerateState"][-1]["target"]:
            for otherChar in char.container.characters:
                if otherChar == char:
                    continue
                if not (
                    otherChar.xPosition
                    and otherChar.yPosition
                    and char.xPosition
                    and char.yPosition
                ):
                    continue
                if (
                    otherChar.xPosition - (char.xPosition - char.xPosition % 15)
                    > 13
                    or otherChar.xPosition - (char.xPosition - char.xPosition % 15)
                    < 1
                ):
                    continue
                if (
                    otherChar.yPosition - (char.yPosition - char.yPosition % 15)
                    > 13
                    or otherChar.yPosition - (char.yPosition - char.yPosition % 15)
                    < 1
                ):
                    continue
                foundItems.append(otherChar)

        if "enemy" in char.interactionState["enumerateState"][-1]["target"]:
            for otherChar in char.container.characters:
                if otherChar == char:
                    continue
                if not (
                    otherChar.xPosition
                    and otherChar.yPosition
                    and char.xPosition
                    and char.yPosition
                ):
                    continue
                if otherChar.faction == char.faction:
                    continue
                if (
                    otherChar.xPosition - (char.xPosition - char.xPosition % 15)
                    > 13
                    or otherChar.xPosition - (char.xPosition - char.xPosition % 15)
                    < 1
                ):
                    continue
                if (
                    otherChar.yPosition - (char.yPosition - char.yPosition % 15)
                    > 13
                    or otherChar.yPosition - (char.yPosition - char.yPosition % 15)
                    < 1
                ):
                    continue
                foundItems.append(otherChar)

        found = None
        if len(foundItems):
            found = foundItems[src.gamestate.gamestate.tick % len(foundItems)]

        if not found:
            char.addMessage(
                "no "
                + ",".join(char.interactionState["enumerateState"][-1]["target"])
                + " found"
            )
            char.interactionState["enumerateState"].pop()
            return

        if isinstance(found, src.rooms.Room):
            char.registers["d"][-1] = found.xPosition - char.xPosition // 15
            char.registers["s"][-1] = found.yPosition - char.yPosition // 15
            char.registers["a"][-1] = -char.registers["d"][-1]
            char.registers["w"][-1] = -char.registers["s"][-1]
        else:
            char.registers["d"][-1] = found.xPosition - char.xPosition
            char.registers["s"][-1] = found.yPosition - char.yPosition
            char.registers["a"][-1] = -char.registers["d"][-1]
            char.registers["w"][-1] = -char.registers["s"][-1]

        char.addMessage(
            ",".join(char.interactionState["enumerateState"][-1]["target"])
            + " found in direction {}a {}s {}d {}w".format(
                char.registers["a"][-1],
                char.registers["s"][-1],
                char.registers["d"][-1],
                char.registers["w"][-1],
            )
        )
        char.interactionState["enumerateState"].pop()
        return

    char.interactionState["enumerateState"].pop()

def doRegisterAccess(key,char,charState,main,header,footer,urwid,flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

press key for register to modify or press = to load value from a register

current registers:

"""
        for itemKey, value in char.registers.items():
            convertedValues = []
            for item in reversed(value):
                convertedValues.append(str(item))
            text += f"""\n{itemKey} - {",".join(convertedValues)}"""

        header.set_text((urwid.AttrSpec("default", "default"), "registers"))
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    char.interactionState["varActions"].append({"outOperator": None})

def doVariableAction(key,char,charState,main,header,footer,urwid,flags):

    lastVarAction = char.interactionState["varActions"][-1]
    if lastVarAction["outOperator"] is None:
        if key in ("esc", "enter"):
            char.interactionState["varActions"].pop()
            return
        elif key == "=":
            lastVarAction["outOperator"] = True
            lastVarAction["register"] = None
        else:
            lastVarAction["outOperator"] = False
            lastVarAction["register"] = ""
            lastVarAction["action"] = None
            lastVarAction["number"] = ""

    register = lastVarAction["register"]

    if lastVarAction["outOperator"] is True:
        if register is None or (
            (register == "" or register[-1].isupper() or register.endswith(" "))
            and (key.isupper() or key == " ")
        ):
            if register is None:
                lastVarAction["register"] = ""
            else:
                lastVarAction["register"] += key
            register = lastVarAction["register"]

            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for register to load value from

current registers (%s):

""" % (
                    register
                )
                for key, value in char.registers.items():
                    if not key.startswith(register):
                        continue
                    convertedValues = []
                    for item in reversed(value):
                        convertedValues.append(str(item))
                    text += f"""\n{key} - {",".join(convertedValues)}"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "reading registers")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True
            return

        else:
            if register:
                key = register + key

            def getValue():
                if key not in char.registers:
                    char.addMessage(f"no value in register using {key}")
                    return 0

                if isinstance(char.registers[key][-1], str):
                    return char.registers[key][-1]

                if char.registers[key][-1] < 0:
                    # char.addMessage("negative value in register using %s"%(key,))
                    return 0

                # char.addMessage("found value %s for register using %s"%(char.registers[key][-1],key,))
                return char.registers[key][-1]

            value = getValue()
            char.runCommandString(str(value))
            return
    else:
        if register == "" or register[-1].isupper() or register[-1] == " ":
            if key.isupper() or key == " ":
                lastVarAction["register"] += key
                register = lastVarAction["register"]

                if (
                    src.gamestate.gamestate.mainChar == char
                    and "norecord" not in flags
                ):
                    text = """

press key for register manipulate

current registers (%s):

""" % (
                        register
                    )
                    for key, value in char.registers.items():
                        if not key.startswith(register):
                            continue
                        convertedValues = []
                        for item in reversed(value):
                            convertedValues.append(str(item))
                        text += f"""\n{key} - {",".join(convertedValues)}"""

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "registers")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                return

            else:
                lastVarAction["register"] += key

                if (
                    src.gamestate.gamestate.mainChar == char
                    and "norecord" not in flags
                ):
                    text = """

press key for the action you want to do on the register

* = - assign value to register
* + - add to register
* - - subtract from register
* / - divide register
* * - multiply register
* % - apply modulo to register

"""
                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "reading registers")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                return
        action = lastVarAction["action"]
        if action is None:
            lastVarAction["action"] = key

            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = f"""

input value for this operation (${register}{action})

type number or load value from register

"""
                header.set_text(
                    (urwid.AttrSpec("default", "default"), "reading registers")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True
            return
        if char.key in "0123456789":
            lastVarAction["number"] += key

            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = f"""

input value for this operation (${register}{action}{lastVarAction["number"]})

type number

press any other key to finish

"""
                header.set_text(
                    (urwid.AttrSpec("default", "default"), "reading registers")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True
            return

        if action == "=":
            if register not in char.registers:
                char.registers[register] = [0]

            char.registers[register][-1] = int(lastVarAction["number"])
        if action == "+":
            char.registers[register][-1] += int(lastVarAction["number"])
        if action == "-":
            char.registers[register][-1] -= int(lastVarAction["number"])
        if action == "/":
            char.registers[register][-1] //= int(lastVarAction["number"])
        if action == "%":
            char.registers[register][-1] %= int(lastVarAction["number"])
        if action == "*":
            char.registers[register][-1] *= int(lastVarAction["number"])

        char.runCommandString(key, extraFlags=flags)
        char.interactionState["varActions"].pop()
        return

def doStartCondition(key,char,charState,main,header,footer,urwid,flags):
    char.interactionState["ifCondition"].append(None)
    char.interactionState["ifParam1"].append([])
    char.interactionState["ifParam2"].append([])

    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

press key for the condition you want to check against.

* i = inventory empty
* b = latest move was blocked by item
* I = inventory full
* > = register c is bigger than 0
* < = register c is lower than 0
* = = register c is exactly 0
* f = floor empty
* t = satiation below 300
* e = food source in inventory
* E = enemy nearby
* c = corpse nearby
* F = food nearby

"""

        header.set_text(
            (urwid.AttrSpec("default", "default"), "conditional action")
        )
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

def doCondition(key,char,charState,main,header,footer,urwid,flags):
    if char.interactionState["ifCondition"][-1] is None:
        char.interactionState["ifCondition"][-1] = key

        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            text = """

press key for the action to run in case the condition is true or
press _ to run a macro in case the condition is true

"""

            header.set_text(
                (urwid.AttrSpec("default", "default"), "conditional action")
            )
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

    elif char.interactionState["ifParam1"][-1] in ([], [("_", ["norecord"])]) or (
        (
            char.interactionState["ifParam1"][-1][-1][0].isupper()
            or char.interactionState["ifParam1"][-1][-1][0] == " "
        )
        and char.interactionState["ifParam1"][-1][0][0] == "_"
    ):
        char.interactionState["ifParam1"][-1].append((key, ["norecord"]))

        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            if (
                (
                    char.interactionState["ifParam1"][-1][-1][0].isupper()
                    or char.interactionState["ifParam1"][-1][-1][0] == " "
                )
                and char.interactionState["ifParam1"][-1][0][0] == "_"
            ) or char.interactionState["ifParam1"][-1][-1][0] == "_":
                inputString = ""
                for item in char.interactionState["ifParam1"][-1]:
                    inputString += item[0]
                inputString = inputString[1:]

                text = """

type the macro that should be run in case the condition is true

%s

""" % (
                    inputString
                )

                for key, value in charState["macros"].items():

                    if not key.startswith(inputString):
                        continue
                    compressedMacro = ""
                    for keystroke in value:
                        if len(keystroke) == 1:
                            compressedMacro += keystroke
                        else:
                            compressedMacro += "/" + keystroke + "/"

                        text += f"""
{key} - {compressedMacro}"""

            else:
                text = """

press key for the action to run in case the condition is false
press _ to run a macro in case the condition is false

"""

            header.set_text(
                (urwid.AttrSpec("default", "default"), "conditional action")
            )
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

    elif char.interactionState["ifParam2"][-1] in ([], [("_", ["norecord"])]) or (
        (
            char.interactionState["ifParam2"][-1][-1][0].isupper()
            or char.interactionState["ifParam2"][-1][-1][0] == " "
        )
        and char.interactionState["ifParam2"][-1][0][0] == "_"
    ):
        char.interactionState["ifParam2"][-1].append((key, ["norecord"]))

        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            inputString = ""
            for item in char.interactionState["ifParam2"][-1]:
                inputString += item[0]
            inputString = inputString[1:]

            text = """

type the macro that should be run in case the condition is false

%s

""" % (
                inputString
            )

            for key, value in charState["macros"].items():

                if not key.startswith(inputString):
                    continue
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/" + keystroke + "/"

                    text += f"""
{key} - {compressedMacro}"""

            header.set_text(
                (urwid.AttrSpec("default", "default"), "conditional action")
            )
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

        if not (
            char.interactionState["ifParam2"][-1] in ([], [("_", ["norecord"])])
            or char.interactionState["ifParam2"][-1][-1][0].isupper()
            or char.interactionState["ifParam2"][-1][-1][0] == " "
        ):
            conditionTrue = True

            if char.interactionState["ifCondition"][-1] == "i":
                if len(char.inventory) == 0:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "b":
                if charState["itemMarkedLast"]:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "I":
                if len(char.inventory) >= 10:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == ">":
                if "c" in char.registers and char.registers["c"][-1] > 0:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "<":
                if "c" in char.registers and char.registers["c"][-1] < 0:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "=":
                if (
                    "c" in char.registers
                    and "v" in char.registers
                    and char.registers["c"][-1] == char.registers["v"][-1]
                ):
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "f":
                pos = (char.xPosition, char.yPosition)
                if (
                    char.container
                    and pos in char.container.itemByCoordinates
                    and len(char.container.itemByCoordinates[pos]) > 0
                ):
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "t":
                if char.satiation < 300:
                    conditionTrue = True
                else:
                    conditionTrue = False
            if char.interactionState["ifCondition"][-1] == "e":
                conditionTrue = False
                for item in char.inventory:
                    if isinstance(item, src.items.GooFlask) and item.uses > 1:
                        conditionTrue = True
                        break
            if char.interactionState["ifCondition"][-1] == "E":
                conditionTrue = False
                if char.container:
                    for character in char.container.characters:
                        if (
                            (
                                not (
                                    character.xPosition // 15
                                    == char.xPosition // 15
                                    and character.yPosition // 15
                                    == char.yPosition // 15
                                )
                            )
                            or character.xPosition % 15 in [0, 14]
                            or character.yPosition % 15 in [0, 14]
                        ):
                            continue
                        if (
                            abs(character.xPosition - char.xPosition) < 20
                            and abs(character.yPosition - char.yPosition) < 20
                            and character.faction != char.faction
                        ):
                            conditionTrue = True
                            break
            """
            if char.interactionState["ifCondition"][-1] == "c":
                conditionTrue = False
                if char.container:
                    for (item, value) in char.container.itemByCoordinates.items():
                        if (
                            (
                                not (
                                    item[0] // 15 == char.xPosition // 15
                                    and item[1] // 15 == char.yPosition // 15
                                )
                            )
                            or item[0] % 15 in [0, 14]
                            or item[1] % 15 in [0, 14]
                        ):
                            continue
                        if not value:
                            continue

                        if value[-1].type == "Corpse":
                            conditionTrue = True
                            break
            if char.interactionState["ifCondition"][-1] == "F":
                conditionTrue = False
                if char.container:
                    for (item, value) in char.container.itemByCoordinates.items():
                        if not (
                            item[0] // 15 == char.xPosition // 15
                            and item[1] // 15 == char.yPosition // 15
                        ):
                            continue
                        if not value:
                            continue

                        if value[-1].type in [
                            "Corpse",
                            "GooFlask",
                            "Bloom",
                            "SickBloom",
                            "BioMass",
                            "PressCake",
                        ]:
                            conditionTrue = True
                            break
            """
            if conditionTrue:
                char.runCommandString(char.interactionState["ifParam1"][-1])
            else:
                char.runCommandString(char.interactionState["ifParam2"][-1])

            char.interactionState["ifCondition"].pop()
            char.interactionState["ifParam1"].pop()
            char.interactionState["ifParam2"].pop()

def doBuildNumber(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    if charState["number"] is None:
        charState["number"] = ""
    charState["number"] += key
    key = commandChars.ignore

def doStartLooping(key,char,charState,main,header,footer,urwid,flags):
    charState["loop"].append(2)

def doLoop(key,char,charState,main,header,footer,urwid,flags):
    if not charState["replay"]:
        char.runCommandString("§"+key)
        charState["loop"].pop()
    else:
        char.runCommandString("§_"+key)
        charState["loop"].pop()

def doRepeat(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    num = int(charState["number"])
    charState["number"] = None

    charState["doNumber"] = True

    convertedKeystroke = [(key, ["norecord"])]*num
    char.runCommandString(convertedKeystroke,preconverted=True)

    charState["doNumber"] = False

def startStopRecording(key,char,charState,main,header,footer,urwid,flags):
    if not charState["recording"]:
        char.addMessage("press key to record to")
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            header.set_text((urwid.AttrSpec("default", "default"), "observe"))
            text = """

press key to record to.

current macros:

"""
            for key, value in charState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/" + keystroke + "/"

                text += f"""
{key} - {compressedMacro}"""

            header.set_text((urwid.AttrSpec("default", "default"), "record macro"))
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

        charState["recording"] = True
        return
    else:
        charState["recording"] = False
        if charState["recordingTo"] and charState["recordingTo"] in charState["macros"]:
            if charState["macros"][charState["recordingTo"]]:
                char.addMessage(
                    "recorded: {} to {}".format(
                        "".join(charState["macros"][charState["recordingTo"]]),
                        charState["recordingTo"],
                    )
                )
            else:
                del charState["macros"][charState["recordingTo"]]
                char.addMessage(
                    "deleted: %s because of empty recording"
                    % (charState["recordingTo"])
                )
        charState["recordingTo"] = None

def doStartStackPop(key,char,charState,main,header,footer,urwid,flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

type key for the register to pop.

current registers

"""
        for key, value in char.registers.items():
            convertedValues = []
            for item in reversed(value):
                convertedValues.append(str(item))
            text += f"""\n{key} - {",".join(convertedValues)}"""

        header.set_text((urwid.AttrSpec("default", "default"), "popping registers"))
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    char.doStackPop = True

def doStartStackPush(key,char,charState,main,header,footer,urwid,flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" in flags:
        text = """

type key for the register to push.

current registers

"""
        for key, value in char.registers.items():
            convertedValues = []
            for item in reversed(value):
                convertedValues.append(str(item))
            text += f"""\n{key} - {",".join(convertedValues)}"""

        header.set_text((urwid.AttrSpec("default", "default"), "pushing registers"))
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    char.doStackPush = True

runactionStr = "runaction"
advancedInteractionStr = "advancedInteraction"
advancedConfigureStr = "advancedConfigure"
advancedPickupStr = "advancedPickup"
advancedDropStr = "advancedDrop"
submenueStr = "submenue"
varActionsStr = "varActions"
recordingStr = "recording"
replayStr = "replay"
numberStr = "number"
numKeysConst = ("0","1","2","3","4","5","6","7","8","9",)
recordKeyConst = "-"
replayKeyConst = "_"

#def handlePriorityActions_old(char,charState,flags,key,main,header,footer,urwid):
def handlePriorityActions(params):
    char = params[0]
    charState = params[1]
    flags = params[2]
    key = params[3]
    main = params[4]
    header = params[5]
    footer = params[6]
    urwid = params[7]

    params[0].specialRender = False

    if params[1][recordingStr]:
        result = checkRecording(key,char,charState,main,header,footer,urwid,flags)
        if not (result and result[0]):
            return None
        key = result[1]

    if (
        charState[submenueStr]
        and charState[submenueStr].stealAllKeys
        and (key not in ("|", ">", "<") and not charState[submenueStr].escape)
    ):
        doHandleMenu(key,char,charState,main,header,footer,urwid,flags)
        key = commandChars.ignore

    if runactionStr in char.interactionState:
        handleActivitySelection(key,char)
        return None

    if "fireDirection" in char.interactionState:
        doRangedAttack(key,char)
        return None

    if advancedInteractionStr in char.interactionState:
        doAdvancedInteraction(params)
        return None

    if runactionStr in char.interactionState:
        handleActivitySelection(key,char)
        return None

    if advancedConfigureStr in char.interactionState:
        doAdvancedConfiguration(key,char,charState,main,header,footer,urwid,flags)
        return None

    if advancedPickupStr in char.interactionState:
        doAdvancedPickup(params)
        return None

    if advancedDropStr in char.interactionState:
        doAdvancedDrop(params)
        return None

    if not charState[submenueStr] and key in numKeysConst:
        doBuildNumber(params)
        return None

    if key == recordKeyConst and not char.interactionState.get(varActionsStr):
        startStopRecording(key,char,charState,main,header,footer,urwid,flags)
        return None

    if charState[replayStr] and key not in (
        "lagdetection",
        "lagdetection_",
        "~",
    ):
        handleMacroReplayChar(key,char,charState,main,header,footer,urwid,flags)
        return None

    if key == replayKeyConst:
        handleStartMacroReplayChar(key,char,charState,main,header,footer,urwid,flags)
        return None

    if charState[numberStr] and key not in (
        commandChars.ignore,
        "lagdetection",
        "lagdetection_",
    ):
        doRepeat(params)
        return None

    # save and quit
    if key in (commandChars.quit_normal, commandChars.quit_instant):
        if hasattr(urwid,"ExitMainLoop"):
            raise urwid.ExitMainLoop()
        src.interaction.tcodMixer.close()
        raise SystemExit()

    return (1,key)

def doSetInterrupt(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    char.setInterrupt = True

def doDockLeft(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    if char.rememberedMenu:
        menu = char.rememberedMenu.pop()
        menu.sidebared = False
        char.macroState["submenue"] = menu
        char.macroState["submenue"].handleKey("~", noRender=False, character=char)
        char.specialRender = True

def doDockRight(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    if char.rememberedMenu2:
        menu = char.rememberedMenu2.pop()
        menu.sidebared = False
        char.macroState["submenue"] = menu
        char.macroState["submenue"].handleKey("~", noRender=False, character=char)
        char.specialRender = True

def doShowMenu(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    options = [("save", "save"), ("main menu","save and back to main menu"),("quit", "save and quit"),("help","help"),
               ("toggleQuestExpanding", "toggleQuestExpanding"),
               ("toggleQuestExpanding2", "toggleQuestExpanding2"),
               ("toggleExpandQ", "toggleExpandQ"),
               ("toggleCommandOnPlus", "toggleCommandOnPlus"),
               ("change personality settings", "change personality settings"),
               ("change setting", "change setting")]
    submenu = src.menuFolder.selectionMenu.SelectionMenu("What do you want to do?", options)
    char.macroState["submenue"] = submenu

    def trigger():
        selection = submenu.getSelection()
        if selection == "change personality settings":

            def getValue():
                settingName = char.macroState["submenue"].selection

                def setValue():
                    value = char.macroState["submenue"].text
                    if settingName in (
                        "autoCounterAttack",
                        "autoFlee",
                        "abortMacrosOnAttack",
                        "attacksEnemiesOnContact",
                    ):
                        if value == "True":
                            value = True
                        else:
                            value = False
                    else:
                        value = int(value)
                    char.personality[settingName] = value

                if settingName is None:
                    return
                submenu3 = src.menuFolder.inputMenu.InputMenu("input value")
                char.macroState["submenue"] = submenu3
                char.macroState["submenue"].followUp = setValue
                return

            options = []
            for (key, value) in char.personality.items():
                options.append((key, f"{key}: {value}"))
            submenu2 = src.menuFolder.selectionMenu.SelectionMenu("select personality setting", options)
            char.macroState["submenue"] = submenu2
            char.macroState["submenue"].followUp = getValue
            return
        if selection == "save":
            tmp = char.macroState["submenue"]
            char.macroState["submenue"] = None
            src.gamestate.gamestate.save()
            char.macroState["submenue"] = tmp
        elif selection == "quit":
            char.macroState["submenue"] = None
            char.specialRender = False
            src.gamestate.gamestate.save()
            # src.interaction.tcodMixer.close()
            raise SystemExit() #HACK: workaround for bug that causes memory leak
        elif selection == "actions":
            pass
        elif selection == "macros":
            pass
        elif selection == "toggleQuestExpanding":
            char.autoExpandQuests = not char.autoExpandQuests
        elif selection == "toggleQuestExpanding2":
            char.autoExpandQuests2 = not char.autoExpandQuests2
        elif selection == "toggleExpandQ":
            char.autoExpandQ = not char.autoExpandQ
        elif selection == "toggleCommandOnPlus":
            char.disableCommandsOnPlus = not char.disableCommandsOnPlus
        elif selection == "changeFaction":
            if char.faction == "player":
                char.faction = "monster"
            else:
                char.faction = "player"
            pass
        elif selection == "help":
            charState["submenue"] = src.menuFolder.helpMenu.HelpMenu()
        elif selection == "keybinding":
            pass
        elif selection == "change setting":
            charState["submenue"] = src.menuFolder.settingMenu.SettingMenu() 
        elif selection == "main menu":
            char.macroState["submenue"] = None
            char.specialRender = False
            src.gamestate.gamestate.save()
            src.gamestate.gamestate = None
            raise EndGame("the game was ended manually")

    char.macroState["submenue"].followUp = trigger
    char.runCommandString(".",nativeKey=True)

def doSpecialAction(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        header.set_text((urwid.AttrSpec("default", "default"), "observe"))
        main.set_text(
            (
                urwid.AttrSpec("default", "default"),
                """

select what you want to do

* c - clear macros

""",
            )
        )
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True
    char.interactionState["functionCall"] = ""

def doStartObserve(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        header.set_text((urwid.AttrSpec("default", "default"), "observe"))
        main.set_text(
            (
                urwid.AttrSpec("default", "default"),
                """

select what you want to observe

* p - get position of something

""",
            )
        )
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True
    char.interactionState["enumerateState"].append({"type": None})

def doResetQuit(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    with open("gamestate/gamestate.json", "w") as saveFile:
        saveFile.write("reset")
    raise urwid.ExitMainLoop()

def handleNoContextKeystroke(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    # do automated movement for the main character
    if key in ("u",):
        doSetInterrupt(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return None

    if key in ("ESC","lESC",):
        doDockLeft(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return None
    if key in ("rESC",):
        doDockRight(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return None
    if key in ("esc",):
        doShowMenu(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return None
    if key in ("y",):
        doSpecialAction(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return None
    """
    if key in ("o",):
        doStartObserve(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        return
    """

    # call callback if key was overwritten
    if "stealKey" in charState and key in charState["stealKey"]:
        charState["stealKey"][key]()

    # handle the keystroke for a char on the map
    else:
        # open the debug menue
        if key in ("\'",):
            charState["submenue"] = src.menuFolder.debugMenu.DebugMenu()

        # destroy save and quit
        if key in (commandChars.quit_delete,):
            doResetQuit(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)

        """
        move the player into a direction
        """
        # move the player
        if key in (commandChars.wait):
            char.timeTaken += 1
            if char.exhaustion > 1:
                char.exhaustion = max(1,char.exhaustion-10)
            else:
                char.exhaustion = 0
            charState["itemMarkedLast"] = None
            char.lastMoveSkipped = True
            return None
        if key in (commandChars.move_north, "up"):
            charState["itemMarkedLast"] = moveCharacter("north",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
            return None
        if key in (commandChars.move_south, "down"):
            charState["itemMarkedLast"] = moveCharacter("south",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
            return None
        if key in (commandChars.move_east, "right"):
            charState["itemMarkedLast"] = moveCharacter("east",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
            return None
        if key in (commandChars.move_west, "left"):
            charState["itemMarkedLast"] = moveCharacter("west",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
            return None

        # move the player
        if key in (
            "W",
            "S",
            "D",
            "A",
        ):
            offset = {"W":(0,1,0),"S":(0,-1,0),"A":(1,0,0),"D":(-1,0,0)}[key]
            charPos = char.getPosition()
            for enemy in char.getNearbyEnemies():
                if enemy.getPosition(offset=offset) == charPos:
                    char.selectSpecialAttack(enemy)
                    return None

            if char.tool:
                char.tool.apply(char)
                if key in ("W",):
                    charState["itemMarkedLast"] = moveCharacter("north",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                    return None
                if key in ("S",):
                    charState["itemMarkedLast"] = moveCharacter("south",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                    return None
                if key in ("D",):
                    charState["itemMarkedLast"] = moveCharacter("east",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                    return None
                if key in ("A",):
                    charState["itemMarkedLast"] = moveCharacter("west",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                    return None

            if key in ("W",):
                charState["itemMarkedLast"] = moveCharacter("north",char,noAdvanceGame,header,urwid,dash=True)
                if charState["itemMarkedLast"]:
                    handleCollision(char,charState)
                if char.exhaustion < 10:
                    charState["itemMarkedLast"] = moveCharacter("north",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                return None
            if key in ("S",):
                charState["itemMarkedLast"] = moveCharacter("south",char,noAdvanceGame,header,urwid,dash=True)
                if charState["itemMarkedLast"]:
                    handleCollision(char,charState)
                if char.exhaustion < 10:
                    charState["itemMarkedLast"] = moveCharacter("south",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                return None
            if key in ("D",):
                charState["itemMarkedLast"] = moveCharacter("east",char,noAdvanceGame,header,urwid,dash=True)
                if charState["itemMarkedLast"]:
                    handleCollision(char,charState)
                if char.exhaustion < 10:
                    charState["itemMarkedLast"] = moveCharacter("east",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                return None
            if key in ("A",):
                charState["itemMarkedLast"] = moveCharacter("west",char,noAdvanceGame,header,urwid,dash=True)
                if charState["itemMarkedLast"]:
                    handleCollision(char,charState)
                if char.exhaustion < 10:
                    charState["itemMarkedLast"] = moveCharacter("west",char,noAdvanceGame,header,urwid,dash=True)
                    if charState["itemMarkedLast"]:
                        handleCollision(char,charState)
                return None

        """
        if key in ("M",):
            if char.combatMode is None:
                char.combatMode = "agressive"
            elif char.combatMode == "agressive":
                char.combatMode = "defensive"
            else:
                char.combatMode = None
            char.addMessage("switched combatMode to: %s" % (char.combatMode,))
        """
        if key in (commandChars.attack,"M"):
            # bad code: should be part of a position object
            adjascentFields = [
                (char.xPosition, char.yPosition),
                (char.xPosition - 1, char.yPosition),
                (char.xPosition + 1, char.yPosition),
                (char.xPosition, char.yPosition - 1),
                (char.xPosition, char.yPosition + 1),
            ]
            for enemy in char.container.characters:
                if enemy == char:
                    continue
                if (
                    key != "M"
                    and enemy.faction == char.faction
                ):
                    continue
                if (enemy.xPosition, enemy.yPosition) not in adjascentFields:
                    continue
                if isinstance(char, src.characters.characterMap["Monster"]) and char.phase == 4:
                    char.addMessage("entered stage 5")
                    char.enterPhase5()
                char.attack(enemy)
                break

        # activate an item
        if key in ("c",):
            # activate the marked item
            if charState["itemMarkedLast"]:
                charState["itemMarkedLast"].configure(char)

            # activate an item on floor
            else:
                # for item in char.container.itemsOnFloor:
                #    if item.xPosition == char.xPosition and item.yPosition == char.yPosition:
                #        item.apply(char)
                #        break
                if not char.container:
                    return None
                entry = char.container.getItemByPosition(
                    (char.xPosition, char.yPosition, char.zPosition)
                )
                if len(entry):
                    entry[0].configure(char)

        # activate an item
        if key in (commandChars.activate,):
            # activate the marked item
            if charState["itemMarkedLast"]:
                if not charState["itemMarkedLast"].container:
                    return None

                charState["itemMarkedLast"].apply(char)
                char.timeTaken += char.movementSpeed

            # activate an item on floor
            else:
                # for item in char.container.itemsOnFloor:
                #    if item.xPosition == char.xPosition and item.yPosition == char.yPosition:
                #        item.apply(char)
                #        break
                if not (
                    char.xPosition is None
                    or char.yPosition is None
                    or char.zPosition is None
                    or char.container is None
                ):
                    entry = char.container.getItemByPosition(
                        (char.xPosition, char.yPosition, char.zPosition)
                    )

                    if entry:
                        entry[0].apply(char)
                        char.timeTaken += char.movementSpeed

        # examine an item
        if key in (commandChars.examine,):
            # examine the marked item
            if charState["itemMarkedLast"]:
                char.examinePosition(charState["itemMarkedLast"].getPosition())

            # examine an item on floor
            else:
                char.examinePosition(char.getPosition())

        # drop first item from inventory
        # bad pattern: the user has to have the choice for what item to drop
        if key in (commandChars.drop,):
            char.timeTaken += char.movementSpeed
            if "NaiveDropQuest" not in char.solvers and not char.godMode:
                char.addMessage("you do not have the nessecary solver yet (drop)")
            else:
                if len(char.inventory):
                    item = char.inventory[-1]
                    char.drop(item)
                    char.container.addAnimation(char.getPosition(),"charsequence",1,{"chars":["++",item.render()]})
                else:
                    char.addMessage("no item to drop")
                    char.container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})

        # drink from the first available item in inventory
        # bad pattern: the user has to have the choice from what item to drink from
        # bad code: drinking should happen in character
        if key in ("J",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for the advanced interaction

* w = activate north
* a = activate west
* s = activate south
* d = activate east
* . = activate item on floor
* i = activate last item in inventory
* f = eat food
* h = heal
* H = heal fully
* j = activate job order

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced activate")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedInteraction"] = {}
            return None

        if key in ("C",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for the configuration interaction

* w = configure north
* a = configure west
* s = configure south
* d = configure east
* . = configure item on floor
* i = configure last item in inventory

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced config")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedConfigure"] = {}
            return None

        if key in ("g",):
            handleActivityKeypress(char, header, main, footer, flags)
            return None

        if key in ("f",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key to set fire direction

* w = fire north
* a = fire west
* s = fire south
* d = fire east

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "fire menu")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["fireDirection"] = {}
            return None

        if key in ("K",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for advanced pickup

* w = pick up north
* a = pick up west
* s = pick up south
* d = pick up east
* . = pick item on floor

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced pick up")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedPickup"] = {}
            return None

        if key in ("L",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for advanced drop

* w = drop north
* a = drop west
* s = drop south
* d = drop east
* . = drop on floor

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced drop")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedDrop"] = {}
            return None

        if key in ("#",):
            activeQuest = char.getActiveQuest()
            if activeQuest:
                activeQuest.reroll()
            return None


        # pick up items
        # bad code: picking up should happen in character
        if key in (commandChars.pickUp,):
            char.timeTaken += char.movementSpeed
            if len(char.inventory) >= 10:
                char.container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"XX")})
                char.addMessage("you cannot carry more items")
            else:
                item = charState["itemMarkedLast"]

                if not item:
                    if not char.container:
                        return None
                    itemList = char.container.getItemByPosition(
                        (char.xPosition, char.yPosition, char.zPosition)
                    )

                    if len(itemList):
                        item = itemList[0]

                if not item:
                    char.addMessage("no item to pick up found")
                    char.container.addAnimation(char.getPosition(offset=(0,0,0)),"showchar",1,{"char":(src.interaction.urwid.AttrSpec("#f00", "black"),"][")})
                    return None

                item.pickUp(char)

                char.container.addAnimation(char.getPosition(),"charsequence",1,{"chars":["--",item.render()]})

        # open chat partner selection
        if key in (commandChars.hail,):
            charState["submenue"] = src.menuFolder.chatPartnerselection.ChatPartnerselection()

        if key in ("H",):
            charState["submenue"] = src.menuFolder.instructSubordinatesMenu.InstructSubordinatesMenu()

        if key in ("r",) and char.room:
            charState["submenue"] = src.menuFolder.roomMenu.RoomMenu(char.room)

        """
        # recalculate the questmarker since it could be tainted
        elif key not in (commandChars.pause,):
            charState["lastMoveAutomated"] = False
            if char.quests:
                char.setPathToQuest(char.quests[0])
        """

    # drop the marker for interacting with an item after bumping into it
    # bad code: ignore autoadvance opens up an unintended exploit
    if key not in (
        "lagdetection",
        "lagdetection_",
        commandChars.wait,
        commandChars.autoAdvance,
    ):
        charState["itemMarkedLast"] = None

    char.specialRender = False

    # doesn't open the dev menu and toggles rendering mode instead
    # bad code: code should act as advertised
    if key in (commandChars.devMenu,):
        if src.canvas.displayChars.mode == "unicode":
            src.canvas.displayChars.setRenderingMode("pureASCII")
        else:
            src.canvas.displayChars.setRenderingMode("unicode")

    # open quest menu
    if key in (commandChars.show_quests,):
        charState["submenue"] = src.menuFolder.questMenu.QuestMenu()
        char.changed("opened quest menu",(char,))

    # open help menu
    if key in (commandChars.show_help,"z"):
        charState["submenue"] = src.menuFolder.helpMenu.HelpMenu()
        char.changed("openedHelp")

    # open inventory
    if key in (commandChars.show_inventory,):
        charState["submenue"] = src.menuFolder.inventoryMenu.InventoryMenu(char)

    # open the menu for giving quests
    if key in (commandChars.show_quests_detailed,):
        charState["submenue"] = src.menuFolder.advancedQuestMenu.AdvancedQuestMenu(char)

    # open the character information
    if key in (commandChars.show_characterInfo,"v",):
        charState["submenue"] = src.menuFolder.characterInfoMenu.CharacterInfoMenu(char=char)

    # open the character information
    if key in ("o",):
        charState["submenue"] = src.menuFolder.combatInfoMenu.CombatInfoMenu(char=char)

    # open the character information
    if key in ("t",):
        charState["submenue"] = src.menuFolder.changeViewsMenu.ChangeViewsMenu()

    # open the character information
    if key in ("x",):
        charState["submenue"] = src.menuFolder.messagesMenu.MessagesMenu(char=char)

    # open the help screen
    if key in (commandChars.show_help,):
        char.specialRender = True

    return (1,key)


# bad code: there are way too much lines of code in this function
# bad code: probably only one parameter needed
def processInput(key, charState=None, noAdvanceGame=False, char=None):
    """
    handle a keystroke

    Parameters:
        charState: the state of the character the input belongs to
                   this can probably be deduced from char
        noAdvanceGame: flag indication whether the game should be advanced
                       always True in practice
        char: the character the input belongs to
    """
    char.implantLoad += 1

    if char.implantLoad > 100:
        char.timeTaken += 1
        char.implantLoad = 0

    if char.dead:
        return

    if charState is None:
        charState = src.gamestate.gamestate.mainChar.macroState

    if char is None:
        char = src.gamestate.gamestate.mainChar

    if char.room:
        terrain = char.room.terrain
    else:
        terrain = char.terrain

    if terrain is None:
        if char.lastRoom:
            terrain = char.lastRoom.terrain
        else:
            terrain = char.lastTerrain

    flags = key[1]
    key = key[0]

    # ignore mouse interaction
    # bad pattern: mouse input should be used
    if type(key) == tuple:
        return

    params = (char,charState,flags,key,main,header,footer,urwid)
    priorityActionResult = handlePriorityActions(params)
    if not (priorityActionResult and priorityActionResult[0] == 1):
        return
    key = priorityActionResult[1]

    # bad code: global variables
    global lastLagDetection
    global idleCounter
    global ticksSinceDeath

    # show the scrolling footer
    # bad code: this should be contained in an object
    if key in ("lagdetection", "lagdetection_"):
        # show the scrolling footer
        if (not charState["submenue"]) and (
            not len(cinematics.cinematicQueue)
            or not cinematics.cinematicQueue[0].overwriteFooter
        ):
            # bad code: global variables
            global footerPosition
            global footerLength
            global footerSkipCounter

            # scroll footer every 20 lagdetection events (about 2 seconds)
            # bad code: using the lagdetection as timer is abuse
            if footerSkipCounter == 20:
                footerSkipCounter = 0
                if not (charState["replay"] or charState["doNumber"]):
                    screensize = loop.screen.get_cols_rows()
                    footer.set_text(
                        doubleFooterText[
                        footerPosition: screensize[0] - 1 + footerPosition
                        ]
                    )
                    if footerPosition == footerLength:
                        footerPosition = 0
                    else:
                        footerPosition += 1
                footerSkipCounter += 1

        # set the cinematic specific footer
        else:
            footerSkipCounter = 20
            if not charState["submenue"]:
                footer.set_text(" " + cinematics.cinematicQueue[0].footerText)
                if (
                    isinstance(
                        cinematics.cinematicQueue[0], src.cinematics.TextCinematic
                    )
                    and cinematics.cinematicQueue[0].firstRun
                ):
                    cinematics.cinematicQueue[0].advance()
            else:
                footer.set_text(" " + charState["submenue"].footerText)

    # discard key strokes, if they were not processed for too long
    ignoreList = (
        commandChars.autoAdvance,
        commandChars.quit_instant,
        commandChars.ignore,
        commandChars.quit_delete,
        commandChars.pause,
        commandChars.show_quests,
        commandChars.show_quests_detailed,
        commandChars.show_inventory,
        commandChars.show_inventory_detailed,
        commandChars.show_characterInfo,
    )
    if key not in ignoreList and lastLagDetection < time.time() - 0.4:
        pass
            # return

    # repeat autoadvance keystrokes
    # bad code: keystrokes are abused here, a timer would be more appropriate
    if key in (commandChars.autoAdvance,):
        if not charState["ignoreNextAutomated"]:
            char.runCommandString(commandChars.autoAdvance)
            char.runCommandString(commandChars.advance)
            return
        else:
            charState["ignoreNextAutomated"] = False

    if key in (commandChars.advance, commandChars.autoAdvance):
        char.showThinking = True
        if len(char.quests):
            charState["lastMoveAutomated"] = True
            char.applysolver()
            if not char.automated:
                char.runCommandString("~")
        else:
            char.generateQuests()

    # handle a keystroke while on map or in cinematic
    if not charState["submenue"]:
        result = handleNoContextKeystroke(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        if not (result and result[0] == 1):
            return
        key = result[1]

    # render submenus
    if charState["submenue"]:

        # set flag to not render the game
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            char.specialRender = True

        noRender = True
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            noRender = False

        # let the submenu handle the keystroke
        lastSubmenu = charState["submenue"]
        done = charState["submenue"].handleKey(key, noRender=noRender, character=char)

        if lastSubmenu != charState["submenue"] and charState["submenue"]:
            charState["submenue"].handleKey("~", noRender=noRender, character=char)
            done = False

        # reset rendering flags
        if done:
            charState["submenue"] = None
            char.specialRender = False

    if charState["replay"] or charState["doNumber"]:
        text = ""
        for cmd in reversed(charState["commandKeyQueue"]):
            item = cmd[0]
            if (
                isinstance(item, list | tuple)
                or item in ("lagdetection", "lagdetection_")
            ):
                continue
            text += str(cmd[0])
        footer.set_text((urwid.AttrSpec("default", "default"), text))


# bad pattern: should be configurable
def renderHeader(character):
    """
    render the information section on top of the screen

    Parameters:
        character: the character to use to get the information from
    """

    return ""

    # render the sections to display
    questSection = src.menuFolder.questMenu.QuestMenu.renderQuests(maxQuests=2)
    messagesSection = renderMessages(character)

    # calculate the size of the elements
    if loop:
        screensize = loop.screen.get_cols_rows()
    else:
        screensize = (400, 400)
    questWidth = (screensize[0] // 3) - 2
    messagesWidth = screensize[0] - questWidth - 3

    # prepare for rendering the header
    txt = ""
    counter = 0
    splitedQuests = questSection.split("\n")
    splitedMessages = messagesSection.split("\n")
    rowCounter = 0

    # add lines for the header
    continueLooping = True
    questLine = ""
    messagesLine = ""
    while True:

        # get the next line for each element
        if questLine == "" and len(splitedQuests):
            questLine = splitedQuests.pop(0)
        if messagesLine == "" and len(splitedMessages):
            messagesLine = splitedMessages.pop(0)

        # stop adding lines after some rounds
        rowCounter += 1
        if rowCounter > 5:
            break

        # cut off left line
        if len(questLine) > questWidth:
            txt += questLine[:questWidth] + "┃ "
            questLine = questLine[questWidth:]

        # pad left line
        else:
            txt += questLine + " " * (questWidth - len(questLine)) + "┃ "
            # bug?: doesn't this pop twice?
            if splitedQuests:
                questLine = splitedQuests.pop(0)
            else:
                questLine = ""

        if len(messagesLine) > messagesWidth:
            # cut off right line
            txt += messagesLine[:messagesWidth]
            messagesLine = messagesLine[messagesWidth:]
        else:
            txt += messagesLine
            # bug?: doesn't this pop twice?
            if splitedMessages:
                messagesLine = splitedMessages.pop(0)
            else:
                messagesLine = ""
        txt += "\n"

    # add the lower decoration
    txt += "━" * +questWidth + "┻" + "━" * (screensize[0] - questWidth - 1) + "\n"

    return txt

# bad code: global function
def renderMessages(character, maxMessages=5):
    """
    render the last x messages into a string

    Parameters:
        character: the character to render the messages from
        maxMessages: the maximum amount of messages rendered

    Returns:
        the rendered messages
    """

    txt = ""
    messages = character.messages
    if len(messages) > maxMessages:
        for message in messages[-maxMessages + 1:]:
            txt += str(message) + "\n"
    else:
        for message in messages:
            txt += str(message) + "\n"

    return txt

lastTerrain = None

lastCenterX = None
lastCenterY = None

# bad code: should be contained somewhere
def render(char):
    """
    render the map

    Parameters:
        char: the character to center the map on
    Returns:
        rendered map
    """

    if char.room:
        thisTerrain = char.room.terrain
    else:
        thisTerrain = char.terrain

    global lastTerrain
    if thisTerrain:
        lastTerrain = thisTerrain
    else:
        thisTerrain = lastTerrain

    # center on player
    # bad code: should focus on arbitrary positions
    if (
        char.room
        and char.room.xPosition
    ):
        centerX = (
            char.room.xPosition * 15
            + char.room.offsetX
            + char.xPosition
        )
        centerY = (
            char.room.yPosition * 15
            + char.room.offsetY
            + char.yPosition
        )
    else:
        centerX = char.xPosition
        centerY = char.yPosition

    global lastCenterX
    global lastCenterY
    if not centerX:
        centerX = lastCenterX
        centerY = lastCenterY
    else:
        lastCenterX = centerX
        lastCenterY = centerY

    # set size of the window into the world
    viewsize = 44
    halfviewsite = (viewsize - 1) // 2

    # calculate the windows position
    if loop:
        screensize = loop.screen.get_cols_rows()
        decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(), True)
        screensize = (
            screensize[0] - decorationSize[0][0],
            screensize[1] - decorationSize[0][1],
        )
    else:
        screensize = (400, 400)
    shift = (
        screensize[1] // 2 - (viewsize - 1) // 2,
        screensize[0] // 4 - (viewsize - 1) // 2,
    )

    # render the map
    if (
        char.room
        and not char.room.xPosition
    ):
        chars = char.room.render()
    else:
        chars = thisTerrain.render(size=(viewsize, viewsize),coordinateOffset=(centerY - halfviewsite -1, centerX - halfviewsite-1))
        miniMapChars = []

        '''
        if hasattr(src.gamestate.gamestate.mainChar,"rank") and src.gamestate.gamestate.mainChar.rank and src.gamestate.gamestate.mainChar.rank < 5 or 1==1:
            if isinstance(src.gamestate.gamestate.mainChar.container,src.rooms.Room):
                text.append(src.gamestate.gamestate.mainChar.container.name)
                if hasattr(src.gamestate.gamestate.mainChar.container,"electricalCharges"):
                    text.append("echarge: %s"%(src.gamestate.gamestate.mainChar.container.electricalCharges,))
                if hasattr(src.gamestate.gamestate.mainChar.container,"maxElectricalCharges"):
                    text.append("maxecharge: %s"%(src.gamestate.gamestate.mainChar.container.maxElectricalCharges,))
                """
                if hasattr(src.gamestate.gamestate.mainChar.container,"sources"):
                    text.append("sources: ")
                    for source in src.gamestate.gamestate.mainChar.container.sources:
                        text.append("    %s"%(source,))
                """
                if hasattr(src.gamestate.gamestate.mainChar.container,"floorPlan"):
                    text.append("floorPlan: ")
                    text.append("    %s"%(src.gamestate.gamestate.mainChar.container.floorPlan,))

        chars = []
        y = 0
        roomCounter = 0
        for line in mapChars:
            if y < len(miniMapChars):
                chars.append(miniMapChars[y]+["  "]*5)
            else:
                if roomCounter < len(text):
                    counter = 0
                    localChars = ""
                    localLine = []
                    for char in text[roomCounter]:
                        if len(localChars) > 0:
                            localLine.append(localChars+char)
                            counter += 1
                            localChars = ""
                        else:
                            localChars = char
                    if localChars:
                        counter += 1
                        localLine.append(localChars+" ")

                    chars.append(localLine+["  "]*(20-counter))
                else:
                    chars.append(["  "]*20)
                roomCounter += 1

            chars[y].extend(mapChars[y])

            y += 1
        '''

    # place rendering in screen
    canvas = src.canvas.Canvas(
        size=(viewsize+1, viewsize+20),
        chars=chars,
        coordinateOffset=(0,0),
        shift=shift,
        displayChars=src.canvas.displayChars,
        tileMapping=tileMapping,
    )

    return canvas

multi_currentChar = None
new_chars = set()
charindex = 0


def keyboardListener(key, targetCharacter=None):
    """
    handles true key presses from the player

    Parameters:
        key: the key pressed
    """

    if not targetCharacter:
        char = src.gamestate.gamestate.mainChar
    else:
        char = targetCharacter

    if char.macroState["commandKeyQueue"] and "ctrl" not in key:
        return

    global multi_currentChar
    multi_chars = src.gamestate.gamestate.multi_chars
    global charindex

    global continousOperation
    continousOperation = -1

    if not multi_currentChar:
        multi_currentChar = char
    state = char.macroState

    if key == "ctrl d":
        char.clearCommandString()
        state["loop"] = []
        state["replay"].clear()
        char.huntkilling = False
        if "ifCondition" in char.interactionState:
            char.interactionState["ifCondition"].clear()
            char.interactionState["ifParam1"].clear()
            char.interactionState["ifParam2"].clear()
        for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
            if not quest.autoSolve:
                continue
            quest.autoSolve = False

        for quest in src.gamestate.gamestate.mainChar.quests:
            if not quest.autoSolve:
                continue
            quest.autoSolve = False

        char.guarding = 0
        char.hasOwnAction = False
        char.runCommandString("~")

    elif key == "ctrl t":
        if src.gamestate.gamestate.gameHalted:
            src.gamestate.gamestate.gameHalted = False
        else:
            src.gamestate.gamestate.gameHalted = True

    elif key == "ctrl p":
        if not char.macroStateBackup:
            char.macroStateBackup = (
                char.macroState
            )
            char.setDefaultMacroState()
            char.macroState[
                "macros"
            ] = char.macroStateBackup["macros"]

            state = char.macroState
        else:
            char.macroState = (
                char.macroStateBackup
            )
            char.macroState[
                "macros"
            ] = char.macroStateBackup["macros"]
            char.macroStateBackup = None

    elif key == "ctrl x":
        src.gamestate.gamestate.save()
        raise urwid.ExitMainLoop()

    elif key == "ctrl o":
        with open("macros.json") as macroFile:
            import json

            rawMacros = json.loads(macroFile.read())
            parsedMacros = {}

            state = "normal"
            for key, value in rawMacros.items():
                parsedMacro = []
                for macroPart in value:
                    if state == "normal":
                        if macroPart == "/":
                            state = "multi"
                            combinedKey = ""
                            continue
                        parsedMacro.append(macroPart)
                    if state == "multi":
                        if macroPart == "/":
                            state = "normal"
                            parsedMacro.append(combinedKey)
                        else:
                            combinedKey += macroPart
                parsedMacros[key] = parsedMacro

            char.macroState["macros"] = parsedMacros

    elif key == "ctrl k":
        with open("macros.json", "w") as macroFile:
            import json

            compressedMacros = {}
            for key, value in char.macroState[
                "macros"
            ].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/" + keystroke + "/"
                compressedMacros[key] = compressedMacro
            macroFile.write(json.dumps(compressedMacros, indent=10, sort_keys=True))

    elif key == "ctrl a":

        toRemove = []
        for character in multi_chars:
            if character.dead:
                toRemove.append(character)
        for character in toRemove:
            multi_chars.remove(character)

        newChar = None


        charindex += 1
        if charindex >= len(multi_chars):
            charindex = 0
        if charindex < 0:
            charindex = 0
        newChar = list(multi_chars)[charindex]

        if not newChar:
            messages.append("charindex %s" % charindex)
            return

        if not targetCharacter:
            src.gamestate.gamestate.mainChar = newChar
        else:
            global shadowCharacter
            shadowCharacter = newChar
        char = newChar
        state = char.macroState

    elif key == "ctrl i":
        foundChar = None
        for character in char.container.characters:
            if character == char:
                continue
            if character.xPosition == char.xPosition and character.yPosition == char.yPosition:
                foundChar = character
                break

        if not foundChar:
            for character in char.container.characters:
                if character == char:
                    continue
                if character.getBigPosition() == char.getBigPosition():
                    foundChar = character
                    break

        if not foundChar:
            for character in char.container.characters:
                if character == char:
                    continue
                foundChar = character
                break

        if foundChar:
            src.gamestate.gamestate.mainChar = foundChar
    elif src.gamestate.gamestate.gameHalted:
        if key == "M":
            # 1000 moves and then stop
            src.gamestate.gamestate.stopGameInTicks = 1000
        if key == "D":
            src.gamestate.gamestate.stopGameInTicks = 100
        if key == "X":
            src.gamestate.gamestate.stopGameInTicks = 10
        if key == "I":
            src.gamestate.gamestate.stopGameInTicks = 1
        if key == "s":
            global speed
            speed = 0.1
        src.gamestate.gamestate.gameHalted = False
    else:
        show_or_exit(key,targetCharacter)


lastAdvance = 0
lastAutosave = 0

lastcheck = time.time()
def getTcodEvents():
    src.gamestate.gamestate.waitedForInputThisTurn = True
    global lastcheck

    foundEvent = False

    if lastcheck < time.time()-0.01:
        events = tcod.event.get()
        for event in events:
            foundEvent = True
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent):
                if event.type == "WINDOWCLOSE":
                    src.interaction.tcodMixer.close()
                    raise SystemExit()
                if event.type == "WINDOWEXPOSED":
                    renderGameDisplay()
            if isinstance(event,tcod.event.MouseButtonDown):# or isinstance(event,tcod.event.MouseButtonUp):
                tcodContext.convert_event(event)
                clickPos = (event.tile.x,event.tile.y)
                if src.gamestate.gamestate.clickMap:
                    if clickPos not in src.gamestate.gamestate.clickMap:
                        continue

                    value = src.gamestate.gamestate.clickMap[clickPos]
                    if isinstance(value, list | str):
                        src.gamestate.gamestate.mainChar.runCommandString(value,nativeKey=True)
                    elif isinstance(value,dict):
                        if "params" not in value:
                            value["params"] = {}
                        value["params"]["event"] = event
                        src.saveing.Saveable.callIndirect(None,value)
                    else:
                        value()

                if isinstance(event,tcod.event.MouseButtonUp):
                    src.gamestate.gamestate.dragState = None

            if isinstance(event,tcod.event.KeyDown):
                key = event.sym
                translatedKey = None
                if key in (tcod.event.KeySym.LSHIFT,4097):
                    continue
                if key == tcod.event.KeySym.RETURN:
                    translatedKey = "enter"
                if key == tcod.event.KeySym.BACKSPACE:
                    translatedKey = "backspace"
                """
                if key == tcod.event.KeySym.SPACE:
                    translatedKey = " "
                if key == tcod.event.KeySym.PERIOD:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = ":"
                    else:
                        translatedKey = "."
                if key == tcod.event.KeySym.HASH:
                    translatedKey = "#"
                """
                if key == tcod.event.KeySym.ESCAPE:
                    if event.mod & tcod.event.Modifier.RSHIFT:
                        translatedKey = "rESC"
                    elif event.mod & tcod.event.Modifier.LSHIFT:
                        translatedKey = "lESC"
                    elif event.mod & tcod.event.Modifier.SHIFT:
                        translatedKey = "ESC"
                    else:
                        translatedKey = "esc"
                """
                if key == tcod.event.KeySym.N1:
                    translatedKey = "1"
                if key == tcod.event.KeySym.N2:
                    translatedKey = "2"
                if key == tcod.event.KeySym.N3:
                    translatedKey = "3"
                if key == tcod.event.KeySym.N4:
                    translatedKey = "4"
                if key == tcod.event.KeySym.N5:
                    translatedKey = "5"
                if key == tcod.event.KeySym.N6:
                    translatedKey = "6"
                if key == tcod.event.KeySym.N7:
                    translatedKey = "7"
                if key == tcod.event.KeySym.N8:
                    translatedKey = "8"
                if key == tcod.event.KeySym.N9:
                    translatedKey = "9"
                if key == tcod.event.KeySym.N0:
                    translatedKey = "0"
                if key == tcod.event.KeySym.COMMA:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = ";"
                    else:
                        translatedKey = ","
                if key == tcod.event.KeySym.MINUS:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "_"
                    else:
                        translatedKey = "-"
                if key == tcod.event.KeySym.PLUS or key == tcod.event.KeySym.KP_PLUS:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "*"
                    else:
                        translatedKey = "+"
                if key == tcod.event.KeySym.a:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,4161,4224,):
                        translatedKey = "ctrl a"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "A"
                    else:
                        translatedKey = "a"
                if key == tcod.event.KeySym.b:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "B"
                    else:
                        translatedKey = "b"
                """
                if key == tcod.event.KeySym.c:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl c"
                """
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "C"
                    else:
                        translatedKey = "c"
                """
                if key == tcod.event.KeySym.d:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl d"
                """
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "D"
                    else:
                        translatedKey = "d"
                if key == tcod.event.KeySym.e:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "E"
                    else:
                        translatedKey = "e"
                if key == tcod.event.KeySym.f:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "F"
                    else:
                        translatedKey = "f"
                if key == tcod.event.KeySym.g:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "G"
                    else:
                        translatedKey = "g"
                if key == tcod.event.KeySym.h:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "H"
                    else:
                        translatedKey = "h"
                """
                if key == tcod.event.KeySym.i:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl i"
                """
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "I"
                    else:
                        translatedKey = "i"
                if key == tcod.event.KeySym.j:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "J"
                    else:
                        translatedKey = "j"
                if key == tcod.event.KeySym.k:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "K"
                    else:
                        translatedKey = "k"
                if key == tcod.event.KeySym.l:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "L"
                    else:
                        translatedKey = "l"
                if key == tcod.event.KeySym.m:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "M"
                    else:
                        translatedKey = "m"
                if key == tcod.event.KeySym.n:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "N"
                    else:
                        translatedKey = "n"
                if key == tcod.event.KeySym.o:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "O"
                    else:
                        translatedKey = "o"
                if key == tcod.event.KeySym.p:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "P"
                    else:
                        translatedKey = "p"
                if key == tcod.event.KeySym.q:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "Q"
                    else:
                        translatedKey = "q"
                if key == tcod.event.KeySym.r:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "R"
                    else:
                        translatedKey = "r"
                if key == tcod.event.KeySym.s:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "S"
                    else:
                        translatedKey = "s"
                """
                if key == tcod.event.KeySym.t:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl t"
                """
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "T"
                    else:
                        translatedKey = "t"
                if key == tcod.event.KeySym.u:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "U"
                    else:
                        translatedKey = "u"
                """
                if key == tcod.event.KeySym.v:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl v"
                    else:
                        translatedKey = "v"

                if key == tcod.event.KeySym.w:
                    if event.mod & tcod.event.Modifier.CTRL:
                        translatedKey = "ctrl w"
                """
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "W"
                    else:
                        translatedKey = "w"
                if key == tcod.event.KeySym.x:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "X"
                    else:
                        translatedKey = "x"
                if key == tcod.event.KeySym.y:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "Y"
                    else:
                        translatedKey = "y"
                if key == tcod.event.KeySym.z:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,4097,4098):
                        translatedKey = "Z"
                    else:
                        translatedKey = "z"
                """
                if key == tcod.event.KeySym.F11:
                    fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                    )
                    tcod.lib.SDL_SetWindowFullscreen(
                        tcodContext.sdl_window_p,
                        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                    )
                if key == tcod.event.KeySym.RIGHT:
                    if not (event.mod & tcod.event.Modifier.CTRL or event.mod & tcod.event.Modifier.SHIFT):
                         translatedKey = "right"
                if key == tcod.event.KeySym.LEFT:
                    if not (event.mod & tcod.event.Modifier.CTRL or event.mod & tcod.event.Modifier.SHIFT):
                        translatedKey = "left"
                if key == tcod.event.KeySym.UP:
                    if not (event.mod & tcod.event.Modifier.CTRL or event.mod & tcod.event.Modifier.SHIFT):
                        translatedKey = "up"
                if key == tcod.event.KeySym.DOWN:
                    if not (event.mod & tcod.event.Modifier.CTRL or event.mod & tcod.event.Modifier.SHIFT):
                        translatedKey = "down"
                if translatedKey is None:
                    continue

                keyboardListener(translatedKey)

            if isinstance(event,tcod.event.TextInput):
                translatedKey = event.text

                if translatedKey is None:
                    continue

                keyboardListener(translatedKey)

        lastcheck = time.time()
        return foundEvent
    return None

class UiAnchor:
    def __init__(self,tag=""):
        pass

class ActionMeta:
    def __init__(self, payload=None,content=None):
        self.payload = payload
        self.content = content

def printUrwidToTcod(inData,offset,color=None,internalOffset=None,size=None, actionMeta=None, explecitConsole=None):
    if explecitConsole:
        tcodConsole_local = explecitConsole
    else:
        tcodConsole_local = tcodConsole

    if not internalOffset:
        internalOffset = [0,0]

    if not color:
        color = ((255,255,255),(0,0,0))
    if color[0] == (None,None,None):
        color = ((255,255,255),color[1])
    if color[1] == (None,None,None):
        color = (color[0],(0,0,0))

    if isinstance(inData,str):
        counter = 0
        for line in inData.split("\n"):
            if counter > 0:
                internalOffset[0] = 0
                internalOffset[1] += 1

            skipPrint = False
            toPrint = line
            if size:
                if internalOffset[0] > size[0]:
                    skipPrint = True
                if internalOffset[1] > size[1]:
                    skipPrint = True

                if not skipPrint:
                    toPrint = line[:size[0]-internalOffset[0]]

            if not skipPrint:
                x = offset[0]+internalOffset[0]
                y = offset[1]+internalOffset[1]
                if actionMeta:
                    for i in range(len(toPrint)):
                        src.gamestate.gamestate.clickMap[(x+i,y)] = actionMeta
                tcodConsole_local.print(x=x,y=y,string=toPrint,fg=color[0],bg=color[1])

            internalOffset[0] += len(line)
            counter += 1


    if isinstance(inData,tuple):
        printUrwidToTcod(inData[1],offset,(inData[0].get_rgb_values()[:3],inData[0].get_rgb_values()[3:]),internalOffset,size,actionMeta,explecitConsole = tcodConsole_local)

    if isinstance(inData,int):
        printUrwidToTcod(src.canvas.displayChars.indexedMapping[inData],offset,color,internalOffset,size,actionMeta,explecitConsole = tcodConsole_local)

    if isinstance(inData,list):
        for item in inData:
            printUrwidToTcod(item,offset,color,internalOffset,size,actionMeta,explecitConsole = tcodConsole_local)

    if isinstance(inData, ActionMeta):
        printUrwidToTcod(inData.content,offset,color,internalOffset,size,inData.payload,explecitConsole = tcodConsole_local)

    #footertext = stringifyUrwid(inData)

def printUrwidToDummy(dummy,inData,offset,color=None,internalOffset=None,size=None, actionMeta=None):
    if not internalOffset:
        internalOffset = [0,0]

    if not color:
        color = ((255,255,255),(0,0,0))
    if color[0] == (None,None,None):
        color = ((255,255,255),color[1])
    if color[1] == (None,None,None):
        color = (color[0],(0,0,0))

    if isinstance(inData,str):
        counter = 0
        for line in inData.split("\n"):
            if counter > 0:
                internalOffset[0] = 0
                internalOffset[1] += 1

            skipPrint = False
            toPrint = line
            if size:
                if internalOffset[0] > size[0]:
                    skipPrint = True
                if internalOffset[1] > size[1]:
                    skipPrint = True

                if not skipPrint:
                    toPrint = line[:size[0]-internalOffset[0]]

            if not skipPrint:
                x = offset[0]+internalOffset[0]
                y = offset[1]+internalOffset[1]
                #if actionMeta:
                #    for i in range(0,len(toPrint)):
                #        src.gamestate.gamestate.clickMap[(x+i,y)] = actionMeta
                #tcodConsole.print(x=x,y=y,string=toPrint,fg=color[0],bg=color[1])

                extraX = 0
                for char in toPrint:
                    try:
                        dummy[y][x+extraX] = [[list(color[0]),list(color[1])],char]
                    except:
                        pass
                    extraX += 1

            internalOffset[0] += len(line)
            counter += 1


    if isinstance(inData,tuple):
        printUrwidToDummy(dummy,inData[1],offset,(inData[0].get_rgb_values()[:3],inData[0].get_rgb_values()[3:]),internalOffset,size,actionMeta)

    if isinstance(inData,int):
        printUrwidToDummy(dummy,src.canvas.displayChars.indexedMapping[inData],offset,color,internalOffset,size,actionMeta)

    if isinstance(inData,list):
        for item in inData:
            printUrwidToDummy(dummy,item,offset,color,internalOffset,size,actionMeta)

    if isinstance(inData, ActionMeta):
        printUrwidToDummy(dummy,inData.content,offset,color,internalOffset,size,inData.payload)

    #footertext = stringifyUrwid(inData)

def renderGameDisplay(renderChar=None):
    pseudoDisplay = []

    src.gamestate.gamestate.clickMap = {}

    text = ""

    if not renderChar:
        char = src.gamestate.gamestate.mainChar
    else:
        char = renderChar

    if char.room:
        thisTerrain = char.room.terrain
    else:
        thisTerrain = char.terrain

    submenue = char.macroState.get("submenue")
    if submenue:
        submenue.rerender()

    global lastTerrain
    if thisTerrain:
        lastTerrain = thisTerrain
    else:
        thisTerrain = lastTerrain

    #bug: this fucks up performance
    def stringifyUrwid(inData):
        outData = ""
        for item in inData:
            if isinstance(item, tuple):
                outData += stringifyUrwid(item[1])
            if isinstance(item, list):
                outData += stringifyUrwid(item)
            if isinstance(item, str):
                outData += item
            if isinstance(item, ActionMeta):
                outData += item.content
        return outData

    # render the game
    if not char.specialRender or tcodConsole:

        skipRender = True

        """
        thresholds = [
            10,
            50,
            100,
            500,
            1000,
            5000,
            10000,
            50000,
            100000,
            500000,
            1000000,
        ]
        skipper = 0
        for threshold in thresholds:
            if continousOperation > threshold:
                skipper += 1
        if skipper == 0 or src.gamestate.gamestate.tick % skipper == 0:
            skipRender = False

        if (
            len(src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"])
            == 0
        ):
            skipRender = False
        """
        skipRender = False

        if (not skipRender) or fixedTicks:

            # render map
            # bad code: display mode specific code
            if not char.godMode and (
                char.satiation < 300
                or char.health < 30
            ):
                warning = True
            else:
                warning = False
            #header.set_text(
            #    (
            #        urwid.AttrSpec("default", "default"),
            #        renderHeader(char),
            #    )
            #)
            if useTiles:
                canvas = render(char)
                canvas.setPygameDisplay(pydisplay, pygame, tileSize)

                w, h = pydisplay.get_size()

                font = pygame.font.Font("config/DejaVuSansMono.ttf", 14)
                plainText = stringifyUrwid(header.get_text())
                counter = 0
                for line in plainText.split("\n"):
                    text = font.render(line, True, (200, 200, 200))
                    pydisplay.blit(text, (0, 0 + 15 * counter))
                    counter += 1
                pygame.display.update()

                plainText = stringifyUrwid(footer.get_text())
                text = font.render(plainText, True, (200, 200, 200))
                tw, th = font.size(plainText)
                pydisplay.blit(text, (w - tw - 8, h - th - 8))
                pygame.display.update()
            if tcodConsole:
                if not renderChar:
                    tcodConsole.clear()

                for y in range(55):
                    pseudoDisplay.append([])
                    for _x in range(210):
                        pseudoDisplay[y].append("")

                def addToPseudeDisplay(chars,offsetX,offsetY):
                    extraY = 0
                    extraX = 0
                    for char in chars:
                        if char == "\n":
                            extraX = 0
                            extraY += 1
                            continue
                        if isinstance(char,str):
                            pseudoDisplay[offsetY+extraY][offsetX+extraX] = char
                            extraX += len(char)
                        elif isinstance(char,tuple):
                            pseudoDisplay[offsetY+extraY][offsetX+extraX] = char[1]
                            extraX += len(char[1])
                        else:
                            pseudoDisplay[offsetY+extraY][offsetX+extraX] = "XX"
                    extraY += 1

                for uiElement in src.gamestate.gamestate.uiElements:
                    if uiElement["type"] == "gameMap":
                        canvas = render(char)
                        if not renderChar:
                            canvas.printTcod(tcodConsole,uiElement["offset"][0],uiElement["offset"][1],warning=warning)
                        else:
                            canvas.getAsDummy(pseudoDisplay,uiElement["offset"][0],uiElement["offset"][1],warning=warning)

                    if uiElement["type"] == "miniMap":
                        miniMapChars = thisTerrain.renderTiles()
                        canvas = src.canvas.Canvas(
                            size=(15, 15),
                            chars=miniMapChars,
                            coordinateOffset=(0,0),
                            shift=(0,0),
                            displayChars=src.canvas.displayChars,
                            tileMapping=None,
                        )
                        canvas.getAsDummy(pseudoDisplay,uiElement["offset"][0],uiElement["offset"][1]+1,warning=warning)
                        canvas.printTcod(tcodConsole,uiElement["offset"][0],uiElement["offset"][1]+1,warning=warning)
                        if not src.gamestate.gamestate.mainChar.dead:
                            position_string = str(src.gamestate.gamestate.mainChar.getBigPosition())
                            if src.gamestate.gamestate.mainChar.container and src.gamestate.gamestate.mainChar.container.isRoom:
                                position_string += " "+str(src.gamestate.gamestate.mainChar.container.tag)
                            printUrwidToTcod(position_string,(2*uiElement["offset"][0]+2,uiElement["offset"][1]))

                    if uiElement["type"] == "zoneMap":
                        miniMapChars = src.gamestate.gamestate.mainChar.renderZoneInfo()
                        canvas = src.canvas.Canvas(
                            size=(15, 15),
                            chars=miniMapChars,
                            coordinateOffset=(0,0),
                            shift=(0,0),
                            displayChars=src.canvas.displayChars,
                            tileMapping=None,
                        )
                        canvas.getAsDummy(pseudoDisplay,uiElement["offset"][0],uiElement["offset"][1]+1,warning=warning)
                        canvas.printTcod(tcodConsole,uiElement["offset"][0],uiElement["offset"][1]+1,warning=warning)
                        if not src.gamestate.gamestate.mainChar.dead:
                            position_string = str(src.gamestate.gamestate.mainChar.getTerrainPosition())
                            position_string += " "+str(src.gamestate.gamestate.mainChar.getTerrain().tag)
                            printUrwidToTcod(position_string,(2*uiElement["offset"][0]+2,uiElement["offset"][1]))

                    if uiElement["type"] == "healthInfo":
                        if src.gamestate.gamestate.dragState:
                            continue
                        if not footer:
                            continue

                        stepSize = char.maxHealth/15
                        if stepSize == 0:
                            stepSize = 1
                        healthRate = int(char.health/stepSize)

                        if char.health == 0:
                            healthDisplay = "---------------"
                        else:
                            healthDisplay = [(urwid.AttrSpec("#f00", "default"),"x"*healthRate),(urwid.AttrSpec("#444", "default"),"."*(15-healthRate))]

                        flaskInfo = "-"
                        if char.flask:
                            flaskInfo = str(char.flask.uses)

                        statusEffectDisplay = ""
                        status = {}
                        for statusEffect in char.statusEffects:
                            if statusEffect.getShortCode() in status:
                                status[statusEffect.getShortCode()] += 1
                            else:
                                status[statusEffect.getShortCode()] = 1
                        for k in status:
                            if status[k] > 1:
                                statusEffectDisplay += k + "x" + str(status[k]) + " "
                            else:
                                statusEffectDisplay += k + " "

                        text = [
                            "health: " , healthDisplay ,
                            "  effects: " , statusEffectDisplay
                        ]

                        x = max(uiElement["offset"][0]+uiElement["width"]//2-len(stringifyUrwid(text))//2,0)
                        y = uiElement["offset"][1]

                        printUrwidToTcod(text,(x,y),size=(uiElement["width"],1))
                        printUrwidToDummy(pseudoDisplay,text,(x,y),size=(uiElement["width"],1))

                        """
                        offset = (uiElement["offset"][0]+44-len(stringifyUrwid(footer.get_text()))//2,uiElement["offset"][1])
                        width = uiElement["width"]
                        printUrwidToTcod(footer.get_text(),offset,size=(width,100))
                        printUrwidToDummy(pseudoDisplay,footer.get_text(),offset,size=(width,100))
                        """
                    if uiElement["type"] == "indicators":
                        autoIndicator = ActionMeta(content="*",payload="*")
                        if char.macroState["commandKeyQueue"] or (char.getActiveQuest() and char.getActiveQuest().autoSolve):
                            """
                            def test():
                                char.clearCommandString()
                                char.macroState["loop"] = []
                                char.macroState["replay"].clear()
                                char.huntkilling = False
                                if "ifCondition" in char.interactionState:
                                    char.interactionState["ifCondition"].clear()
                                    char.interactionState["ifParam1"].clear()
                                    char.interactionState["ifParam2"].clear()
                                activeQuest = char.getActiveQuest()
                                if activeQuest and activeQuest.autoSolve:
                                    activeQuest.autoSolve = False
                                char.runCommandString("~")

                            autoIndicator = ActionMeta(content=(urwid.AttrSpec("#f00", "default"),"*"),payload=test)
                            """
                        indicators = [ActionMeta(content="x",payload="x~")," ",ActionMeta(content="q",payload="q~")," ",ActionMeta(content="v",payload="v~")," ",autoIndicator," ",ActionMeta(content="t",payload="t~")]

                        x = max(uiElement["offset"][0]+uiElement["width"]//2-len(indicators)//2,0)
                        y = uiElement["offset"][1]

                        printUrwidToTcod(indicators,(x,y),size=(uiElement["width"],1))
                        printUrwidToDummy(pseudoDisplay,indicators,(x,y),size=(uiElement["width"],1))

                    if uiElement["type"] == "text":
                        printUrwidToTcod(uiElement["text"],uiElement["offset"])
                        printUrwidToDummy(pseudoDisplay,uiElement["text"],uiElement["offset"])
                    if uiElement["type"] == "time":
                        text = f"epoch: {src.gamestate.gamestate.tick//(15*15*15)} tick: {src.gamestate.gamestate.tick%(15*15*15)}"
                        printUrwidToTcod(text,uiElement["offset"],((255, 68, 51),(0,0,0)) if src.gamestate.gamestate.mainChar.timeTaken > 1 else None)
                        printUrwidToDummy(pseudoDisplay,text,uiElement["offset"])
                    if uiElement["type"] == "rememberedMenu" and char.rememberedMenu:
                        chars = []
                        counter = 0
                        for menu in reversed(char.rememberedMenu):
                            chars.extend(["------------- ",ActionMeta(content=">",payload=["lESC"]),"\n\n"])
                            chars.extend(menu.render(char))
                            counter += 1
                        size = uiElement["size"]
                        offset = uiElement["offset"]
                        printUrwidToTcod(chars,offset,size=size)
                        printUrwidToDummy(pseudoDisplay,chars,offset,size=size)

                    if uiElement["type"] == "rememberedMenu2" and char.rememberedMenu2:
                        chars = []
                        for menu in reversed(char.rememberedMenu2):
                            chars.extend(["------------- ",ActionMeta(content="<",payload=["rESC"]),"\n\n"])
                            chars.extend(menu.render(char))
                        size = uiElement["size"]
                        offset = uiElement["offset"]
                        printUrwidToTcod(chars,offset,size=size)
                        printUrwidToDummy(pseudoDisplay,chars,offset,size=size)

                if not char.specialRender:
                    tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if not useTiles and not tcodConsole:
                main.set_text(
                    (
                        urwid.AttrSpec("#999", "black"),
                        canvas.getUrwirdCompatible(warning=warning),
                    )
                )

                canvas = render(char)
    if char.specialRender:
        if useTiles:
            pydisplay.fill((0, 0, 0))
            font = pygame.font.Font("config/DejaVuSansMono.ttf", 14)

            plainText = stringifyUrwid(main.get_text())
            counter = 0
            for line in plainText.split("\n"):
                text = font.render(line, True, (200, 200, 200))
                pydisplay.blit(text, (30, 110 + 15 * counter))
                counter += 1

            pygame.display.update()
        if tcodConsole:
            plainText = stringifyUrwid(main.get_text())
            height = 0
            width = 0
            for line in plainText.split("\n"):
                height += 1
                width = max(width,len(line))

            screen_width = 200
            screen_width = 150
            screen_height = 51
            offsetLeft = max(screen_width//2-width//2,1)
            offsetTop = max(screen_height//2-height//2,1)

            try:
                counter = offsetTop
                tcodConsole.print(x=offsetLeft, y=counter-1, string="|",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter-1][offsetLeft] = "|"
                tcodConsole.print(x=offsetLeft+width+3, y=counter-1, string="|",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter-1][offsetLeft+width+3] = "|"
                tcodConsole.print(x=offsetLeft+width+0, y=counter-1, string="<",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter-1][offsetLeft+width+0] = "<"
                src.gamestate.gamestate.clickMap[(offsetLeft+width+0,counter-1)] = ["lESC"]
                tcodConsole.print(x=offsetLeft+width+1, y=counter-1, string="X",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter-1][offsetLeft+width+1] = "X"
                src.gamestate.gamestate.clickMap[(offsetLeft+width+1,counter-1)] = ["esc"]
                tcodConsole.print(x=offsetLeft+width+2, y=counter-1, string=">",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter-1][offsetLeft+width+2] = ">"
                src.gamestate.gamestate.clickMap[(offsetLeft+width+2,counter-1)] = ["rESC"]

                #tcodConsole.print(x=offsetLeft+width+5, y=counter-1, string=stringifyUrwid(header.get_text()),fg=(255,255,255),bg=(0,0,0))
                #pseudoDisplay[counter-1][offsetLeft+width+5] = stringifyUrwid(header.get_text())
                tcodConsole.print(x=offsetLeft-2, y=counter, string="--+-"+"-"*width+"-+--",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter][offsetLeft-2] = "--+-"+"-"*width+"-+--"
                extraX = 0
                for char in "--+-"+"-"*width+"-+--":
                    pseudoDisplay[counter][offsetLeft-2+extraX] = char
                    extraX += 1
                counter += 1
                tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
                extraX = 0
                for char in "| "+" "*width+" |":
                    pseudoDisplay[counter][offsetLeft+extraX] = char
                    extraX += 1
                counter += 1
                for _line in plainText.split("\n"):
                    tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
                    extraX = 0
                    for char in "| "+" "*width+" |":
                        pseudoDisplay[counter][offsetLeft+extraX] = char
                        extraX += 1
                    counter += 1
                tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
                extraX = 0
                for char in "| "+" "*width+" |":
                    pseudoDisplay[counter][offsetLeft+extraX] = char
                    extraX += 1
                counter += 1
                tcodConsole.print(x=offsetLeft-2, y=counter, string="--+-"+"-"*width+"-+--",fg=(255,255,255),bg=(0,0,0))
                extraX = 0
                for char in "--+-"+"-"*width+"-+--":
                    pseudoDisplay[counter][offsetLeft-2+extraX] = char
                    extraX += 1
                tcodConsole.print(x=offsetLeft, y=counter+1, string="|",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter+1][offsetLeft] = "|"
                tcodConsole.print(x=offsetLeft+width+3, y=counter+1, string="|",fg=(255,255,255),bg=(0,0,0))
                pseudoDisplay[counter+1][offsetLeft+width+3] = "|"
            except:
                pass

            #printUrwidToTcod(main.get_text(),(offsetLeft+2,offsetTop+2),size=(width,height))
            if not renderChar:
                printUrwidToTcod(main.get_text(),(offsetLeft+2,offsetTop+2))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            else:
                printUrwidToDummy(pseudoDisplay, main.get_text(),(offsetLeft+2,offsetTop+2))

    if renderChar:
        sendNetworkDraw(pseudoDisplay)
    else:
        if shadowCharacter:
            renderGameDisplay(shadowCharacter)

def showMainMenu(args=None):
    from pathlib import Path
    Path("gamestate").mkdir(parents=True, exist_ok=True)

    try:
        with open("gamestate/globalInfo.json") as globalInfoFile:
            rawState = json.loads(globalInfoFile.read())
            saves = rawState["saves"]
            gameIndex = rawState["lastGameIndex"]
    except:
        saves = [0,0,0,0,0,0,0,0,0,0]
        gameIndex = 0

    scenarios = [
        (
        "mainGame",
        "main game",
        "m",
        ),
        (
        "mainGameRoguelike",
        "main game (sieged/roguelike)",
        "r",
        ),
        (
        "mainGameProduction",
        "main game (production/base management)",
        "b",
        ),
    ]

    selectedScenario = "mainGame"
    difficulty = "easy"

    def fixRoomRender(render):
        for row in render:
            row.append("\n")
        return render

    src.gamestate.setup(None)
    src.gamestate.gamestate.terrainType = src.terrains.Nothingness
    src.gamestate.gamestate.mainChar = src.characters.Character()

    terrain = src.terrains.Nothingness()
    mainChar = src.gamestate.gamestate.mainChar

    item = src.items.itemMap["ArchitectArtwork"]()
    architect = item
    item.bolted = False
    item.godMode = True
    terrain.addItem(item,(1,1,0))

    src.gamestate.gamestate.mainChar.macroState["macros"]["j"] = ["J", "f"]
    src.gamestate.gamestate.mainChar.godMode = True
    src.gamestate.gamestate.mainChar.faction = "city test"

    mainRoom = architect.doAddRoom(
                        {
                            "coordinate": (7,7),
                            "roomType": "EmptyRoom",
                            "doors": "0,6 6,0 12,6 6,12",
                            "offset": [1,1],
                            "size": [13, 13],
                        },
                        None,
                  )
    mainRoom.storageRooms = []

    cityBuilder = src.items.itemMap["CityBuilder2"]()
    cityBuilder.architect = architect
    mainRoom.addItem(cityBuilder,(7,1,0))
    cityBuilder.registerRoom(mainRoom)

    mainRoom.addCharacter(
            src.gamestate.gamestate.mainChar, 6, 6
        )

    cityBuilder.spawnCity(src.gamestate.gamestate.mainChar)

    staffArtwork = src.items.itemMap["StaffArtwork"]()
    mainRoom.addItem(staffArtwork,(1,1,0))

    dutyArtwork = src.items.itemMap["DutyArtwork"]()
    mainRoom.addItem(dutyArtwork,(5,1,0))

    orderArtwork = src.items.itemMap["OrderArtwork"]()
    mainRoom.addItem(orderArtwork,(3,1,0))

    produtionArtwork = src.items.itemMap["ProductionArtwork"]()
    mainRoom.addItem(produtionArtwork,(3,11,0))

    mainRoom.removeCharacter(src.gamestate.gamestate.mainChar)

    startGame = False
    logoText = """

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

"""

    for x in range(1,14):
        for y in range(1,14):
            if (x,y) == (8,5):
                continue

            if terrain.getRoomByPosition((x,y)):
                continue

            for _i in range(1,8):
                mold = src.items.itemMap["Mold"]()
                mold.dead = True
                terrain.addItem(mold,(15*x+random.randint(1,13),15*y+random.randint(1,13),0))

            placedMines = False

            if random.random() > 0.5:
                placedMines = True
                for _i in range(1,2+random.randint(1,5)):
                    offsetX = random.randint(1,13)
                    offsetY = random.randint(1,13)

                    xPos = 15*x+offsetX
                    yPos = 15*y+offsetY

                    if terrain.getItemByPosition((xPos,yPos,0)):
                        continue

                    landmine = src.items.itemMap["LandMine"]()
                    terrain.addItem(landmine,(xPos,yPos,0))

            for _i in range(1,5+random.randint(1,20)):
                offsetX = random.randint(1,13)
                offsetY = random.randint(1,13)

                xPos = 15*x+offsetX
                yPos = 15*y+offsetY

                if terrain.getItemByPosition((xPos,yPos,0)):
                    continue

                if placedMines:
                    landmine = src.items.itemMap["LandMine"]()
                    terrain.addItem(landmine,(xPos,yPos,0))

                scrap = src.items.itemMap["Scrap"](amount=random.randint(1,13))
                terrain.addItem(scrap,(xPos,yPos,0))

    lastStep = time.time()
    submenu = None

    while 1:
        tcodConsole.clear()
        time.sleep(0.1)

        try:
            # register the save
            with open("gamestate/globalInfo.json") as globalInfoFile:
                rawState = json.loads(globalInfoFile.read())
        except:
            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[],"lastGameIndex":0}

        canLoad = False
        if rawState["saves"][gameIndex]:
            canLoad = True
        saves = rawState["saves"]

        if startGame:
            global new_chars
            new_chars = set()

            loadingControl = {}
            loadingControl["done"] = False
            loadingControl["needsStart"] = False
            def showLoading():
                tcodConsole.clear()
                printUrwidToTcod("+--------------+",(offsetX+3+16,offsetY+13))
                printUrwidToTcod("| loading game |",(offsetX+3+16,offsetY+14))
                printUrwidToTcod("+--------------+",(offsetX+3+16,offsetY+15))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            def doLoad():
                if canLoad:
                    src.gamestate.gamestate = src.gamestate.gamestate.loadP(gameIndex)
                    setUpNoUrwid()
                    src.gamestate.gamestate.mainChar.runCommandString("~")
                else:
                    seed = 0
                    src.gamestate.setup(gameIndex)
                    setUpNoUrwid()

                    if selectedScenario == "siege":
                        terrain = "test"
                        phase = "Siege"
                    elif selectedScenario == "mainGame":
                        terrain = "test"
                        phase = "MainGame"
                    elif selectedScenario == "mainGameRoguelike":
                        terrain = "test"
                        phase = "MainGameRoguelike"
                    elif selectedScenario == "mainGameProduction":
                        terrain = "test"
                        phase = "MainGameProduction"
                    elif selectedScenario == "mainGameRaid":
                        terrain = "test"
                        phase = "MainGameRaid"
                    elif selectedScenario == "mainGameArena":
                        terrain = "test"
                        phase = "MainGameArena"
                    elif selectedScenario == "mainGameArena2":
                        terrain = "test"
                        phase = "MainGameArena2"
                    elif selectedScenario == "Siege":
                        terrain = "test"
                        phase = "MainGame"
                    elif selectedScenario == "basebuilding":
                        terrain = "nothingness"
                        phase = "BaseBuilding"
                    elif selectedScenario == "survival":
                        terrain = "desert"
                        phase = "DesertSurvival"
                    elif selectedScenario == "creative":
                        terrain = "nothingness"
                        phase = "CreativeMode"
                    elif selectedScenario == "dungeon":
                        terrain = "nothingness"
                        phase = "Dungeon"
                    elif selectedScenario == "WorldBuildingPhase":
                        terrain = "nothingness"
                        phase = "WorldBuildingPhase"
                    elif selectedScenario == "RoguelikeStart":
                        terrain = "nothingness"
                        phase = "RoguelikeStart"
                    elif selectedScenario == "Tour":
                        terrain = "nothingness"
                        phase = "Tour"
                    elif selectedScenario == "BackToTheRoots":
                        terrain = "nothingness"
                        phase = "BackToTheRoots"
                    elif selectedScenario == "PrefabDesign":
                        terrain = "nothingness"
                        phase = "PrefabDesign"
                    elif selectedScenario == "Tutorials":
                        terrain = "nothingness"
                        phase = "Tutorials"

                    if terrain and terrain == "scrapField":
                        src.gamestate.gamestate.terrainType = src.terrains.ScrapField
                    elif terrain and terrain == "nothingness":
                        src.gamestate.gamestate.terrainType = src.terrains.Nothingness
                    elif terrain and terrain == "test":
                        src.gamestate.gamestate.terrainType = src.terrains.GameplayTest
                    elif terrain and terrain == "tutorial":
                        src.gamestate.gamestate.terrainType = src.terrains.TutorialTerrain
                    elif terrain and terrain == "desert":
                        src.gamestate.gamestate.terrainType = src.terrains.Desert
                    else:
                        src.gamestate.gamestate.terrainType = src.terrains.GameplayTest

                    src.gamestate.gamestate.mainChar = src.characters.Character()
                    src.gamestate.gamestate.setup(phase=phase, seed=seed)

                    loadingControl["needsStart"] = True

            """
            def loader():
                doLoad()
                loadingControl["done"] = True

            async def redrawer():
                while not loadingControl["done"]:
                    showLoading()

            async def asyncTask():
                loop = asyncio.get_running_loop()
                await asyncio.gather(
                    loop.run_in_executor(None,loader),
                    redrawer()
                )
            asyncio.run(asyncTask())
            """
            doLoad()

            if loadingControl["needsStart"] is True:
                src.gamestate.gamestate.currentPhase.start(seed=None,difficulty=difficulty)
                terrain = src.gamestate.gamestate.terrainMap[7][7]

                src.gamestate.gamestate.mainChar.runCommandString("~")

                global lastTerrain
                lastTerrain = terrain

            break

        if time.time() - lastStep > 1:
            lastStep = time.time()
            terrain.advance()
            src.gamestate.gamestate.tick += 1

            charList = []
            charList.extend(terrain.characters)
            for room in terrain.rooms:
                charList.extend(room.characters)

            removeList = []
            for character in charList:
                advanceChar(character)

        height = 10
        width = 46

        printUrwidToTcod(fixRoomRender(terrain.render(coordinateOffset=(15*5,15*5),size=(50,126))),(0,0))

        offsetX = 51
        offsetY = 10

        printUrwidToTcod("|",(offsetX,offsetY))
        printUrwidToTcod("|",(offsetX+width,offsetY))
        printUrwidToTcod("--+"+45*"-"+"+--",(offsetX-2,offsetY+1))
        for y in range(offsetY+2,offsetY+21+height):
            printUrwidToTcod("|"+45*" "+"|",(offsetX,y))
        printUrwidToTcod("--+"+45*"-"+"+--",(offsetX-2,offsetY+18))
        printUrwidToTcod("--+"+45*"-"+"+--",(offsetX-2,offsetY+21+height))
        printUrwidToTcod("|",(offsetX,offsetY+22+height))
        printUrwidToTcod("|",(offsetX+width,offsetY+22+height))
        printUrwidToTcod(src.urwidSpecials.makeRusty(logoText),(offsetX+2,offsetY+1))

        printUrwidToTcod("press p to (p)lay",(offsetX+3,offsetY+20))

        printUrwidToTcod("press p to (p)lay",(offsetX+3,offsetY+27))
        printUrwidToTcod("press g to select (g)ameslot",(offsetX+3,offsetY+28))
        if canLoad:
            printUrwidToTcod("press D to delete gamestate",(offsetX+3,offsetY+29))
        else:
            printUrwidToTcod("press d/s to edit game settings",(offsetX+3,offsetY+29))

        color = "#fff"
        if saves[gameIndex]:
            color = "#333"
        printUrwidToTcod((src.interaction.urwid.AttrSpec(color, "black"),f"(d)ifficulty - {difficulty}"),(offsetX+3,offsetY+23))
        color = "#fff"
        if saves[gameIndex]:
            color = "#333"
        printUrwidToTcod((src.interaction.urwid.AttrSpec(color, "black"),f"(s)cenario   - {selectedScenario}"),(offsetX+3,offsetY+24))
        printUrwidToTcod(f"(g)ameslot   - {gameIndex}",(offsetX+3,offsetY+25))

        if submenu == "gameslot":
            printUrwidToTcod("+----------------------+",(offsetX+3+16,offsetY+23))
            printUrwidToTcod("| choose the gameslot: |",(offsetX+3+16,offsetY+24))
            for i in range(10):
                if saves[i]:
                    printUrwidToTcod(f"| {i}: load game         |",(offsetX+3+16,offsetY+25+i))
                else:
                    printUrwidToTcod(f"| {i}: new game          |",(offsetX+3+16,offsetY+25+i))
            printUrwidToTcod("+----------------------+",(offsetX+3+16,offsetY+35))

        if submenu == "scenario":
            maxLength = 0
            for scenario in scenarios:
                maxLength = max(maxLength,len(scenario[1]))

            printUrwidToTcod("+"+"-"*(maxLength+5)+"+",(offsetX+3+16,offsetY+22))
            i = 0
            for scenario in scenarios:
                printUrwidToTcod(("| %s: %s "+" "*(maxLength-len(scenario[1]))+"|")%(scenario[2],scenario[1],),(offsetX+3+16,offsetY+23+i))
                i += 1
            printUrwidToTcod("+"+"-"*(maxLength+5)+"+",(offsetX+3+16,offsetY+23+i))


        if submenu == "difficulty":
            printUrwidToTcod("+-------------------------------------------------------------------+",(offsetX+3+16,offsetY+21))
            printUrwidToTcod("| (e)asy                                                            |",(offsetX+3+16,offsetY+22))
            printUrwidToTcod("| easy is easy. Recommended to start with.                          |",(offsetX+3+16,offsetY+23))
            printUrwidToTcod("| This mode should teach you how the game works.                    |",(offsetX+3+16,offsetY+24))
            printUrwidToTcod("|                                                                   |",(offsetX+3+16,offsetY+25))
            printUrwidToTcod("| (m)edium                                                          |",(offsetX+3+16,offsetY+26))
            printUrwidToTcod("| medium is pretty hard. Recommended after winning an easy run.     |",(offsetX+3+16,offsetY+27))
            printUrwidToTcod("| Balanced to be challenging after mastering one game mechanic      |",(offsetX+3+16,offsetY+28))
            printUrwidToTcod("|                                                                   |",(offsetX+3+16,offsetY+29))
            printUrwidToTcod("| (d)ifficult                                                       |",(offsetX+3+16,offsetY+30))
            printUrwidToTcod("| difficult is really hard. not recomended                          |",(offsetX+3+16,offsetY+31))
            printUrwidToTcod("| Should be a challenging with full meta knowledge                  |",(offsetX+3+16,offsetY+32))
            printUrwidToTcod("+-------------------------------------------------------------------+",(offsetX+3+16,offsetY+33))

        if submenu == "delete":
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#f00", "black"),"+---------------------------------------+"),(offsetX+2,offsetY+21))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#f00", "black"),"| this will delete your game state      |"),(offsetX+2,offsetY+22))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#f00", "black"),"| press y to confirm                    |"),(offsetX+2,offsetY+23))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#f00", "black"),"+---------------------------------------+"),(offsetX+2,offsetY+24))

        if submenu == "confirmQuit":
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#fff", "black"),"+-----------------------------+"),(offsetX+2,offsetY+21))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#fff", "black"),"| Do you really want to quit? |"),(offsetX+2,offsetY+22))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#fff", "black"),"| press y/enter to confirm    |"),(offsetX+2,offsetY+23))
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#fff", "black"),"+-----------------------------+"),(offsetX+2,offsetY+24))

        tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

        events = tcod.event.get()
        for event in events:
            if submenu == "gameslot":
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    if key == tcod.event.KeySym.ESCAPE:
                        submenu = None
                    if key == tcod.event.KeySym.F11:
                        fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                            tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                        )
                        tcod.lib.SDL_SetWindowFullscreen(
                            tcodContext.sdl_window_p,
                            0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                        )
                    if key == tcod.event.KeySym.N0:
                        gameIndex = 0
                        submenu = None
                    if key == tcod.event.KeySym.N1:
                        gameIndex = 1
                        submenu = None
                    if key == tcod.event.KeySym.N2:
                        gameIndex = 2
                        submenu = None
                    if key == tcod.event.KeySym.N3:
                        gameIndex = 3
                        submenu = None
                    if key == tcod.event.KeySym.N4:
                        gameIndex = 4
                        submenu = None
                    if key == tcod.event.KeySym.N5:
                        gameIndex = 5
                        submenu = None
                    if key == tcod.event.KeySym.N6:
                        gameIndex = 6
                        submenu = None
                    if key == tcod.event.KeySym.N7:
                        gameIndex = 7
                        submenu = None
                    if key == tcod.event.KeySym.N8:
                        gameIndex = 8
                        submenu = None
                    if key == tcod.event.KeySym.N9:
                        gameIndex = 9
                        submenu = None
            elif submenu == "scenario":
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    convertedKey = None
                    if key == tcod.event.KeySym.F11:
                        fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                            tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                        )
                        tcod.lib.SDL_SetWindowFullscreen(
                            tcodContext.sdl_window_p,
                            0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                        )
                    if key == tcod.event.KeySym.ESCAPE:
                        submenu = None
                    if key == tcod.event.KeySym.m:
                        convertedKey = "m"
                    if key == tcod.event.KeySym.h:
                        if event.mod & tcod.event.Modifier.SHIFT:
                            convertedKey = "H"
                        else:
                            convertedKey = "h"
                    if key == tcod.event.KeySym.t:
                        if event.mod & tcod.event.Modifier.SHIFT:
                            convertedKey = "T"
                        else:
                            convertedKey = "t"
                    if key == tcod.event.KeySym.p:
                        convertedKey = "p"
                    if key == tcod.event.KeySym.b:
                        convertedKey = "b"
                    if key == tcod.event.KeySym.r:
                        convertedKey = "r"
                    if key == tcod.event.KeySym.s:
                        if event.mod & tcod.event.Modifier.SHIFT:
                            convertedKey = "S"
                        else:
                            convertedKey = "s"
                    if key == tcod.event.KeySym.c:
                        convertedKey = "c"
                    if key == tcod.event.KeySym.d:
                        convertedKey = "d"
                    if key == tcod.event.KeySym.x:
                        if event.mod & tcod.event.Modifier.SHIFT:
                            convertedKey = "X"
                        else:
                            convertedKey = "x"

                    for scenario in scenarios:
                        if scenario[2] == convertedKey:
                            selectedScenario = scenario[0]
                            submenu = None

            elif submenu == "difficulty":
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    if key == tcod.event.KeySym.F11:
                        fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                            tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                        )
                        tcod.lib.SDL_SetWindowFullscreen(
                            tcodContext.sdl_window_p,
                            0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                        )
                    if key == tcod.event.KeySym.ESCAPE:
                        submenu = None
                    if key == tcod.event.KeySym.e:
                        difficulty = "easy"
                        submenu = None
                    if key == tcod.event.KeySym.m:
                        difficulty = "medium"
                        submenu = None
                    if key == tcod.event.KeySym.d:
                        difficulty = "difficult"
                        submenu = None
            elif submenu == "delete":
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym

                    if key == tcod.event.KeySym.F11:
                        fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                            tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                        )
                        tcod.lib.SDL_SetWindowFullscreen(
                            tcodContext.sdl_window_p,
                            0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                        )
                    if key == tcod.event.KeySym.y:
                        try:
                            # register the save
                            with open("gamestate/globalInfo.json") as globalInfoFile:
                                rawState = json.loads(globalInfoFile.read())
                        except:
                            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[],"lastGameIndex":0}

                        rawState["saves"][gameIndex] = 0
                        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
                            json.dump(rawState,globalInfoFile)

                    submenu = None
            elif submenu == "confirmQuit":
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    if key in (tcod.event.KeySym.RETURN,tcod.event.KeySym.y):
                        src.interaction.tcodMixer.close()
                        raise SystemExit()
                    submenu = None
            else:
                if isinstance(event, tcod.event.Quit):
                    src.interaction.tcodMixer.close()
                    raise SystemExit()
                if isinstance(event, tcod.event.WindowResized):
                    checkResetWindowSize(event.width,event.height)
                if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                    src.interaction.tcodMixer.close()
                    raise SystemExit()
                if isinstance(event,tcod.event.KeyDown):
                    key = event.sym
                    if key == tcod.event.KeySym.F11:
                        fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                            tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                        )
                        tcod.lib.SDL_SetWindowFullscreen(
                            tcodContext.sdl_window_p,
                            0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                        )
                    if key == tcod.event.KeySym.ESCAPE:
                        submenu = "confirmQuit"
                    if key == tcod.event.KeySym.p:
                        try:
                            # register the save
                            with open("gamestate/globalInfo.json") as globalInfoFile:
                                rawState = json.loads(globalInfoFile.read())
                        except:
                            rawState = {"saves": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],"customPrefabs":[],"lastGameIndex":0}

                        rawState["lastGameIndex"] = gameIndex
                        with open("gamestate/globalInfo.json", "w") as globalInfoFile:
                            json.dump(rawState,globalInfoFile)
                        startGame = True
                    if key == tcod.event.KeySym.g:
                        submenu = "gameslot"
                    if key == tcod.event.KeySym.s:
                        if not canLoad:
                            submenu = "scenario"
                    if key == tcod.event.KeySym.d:
                        if event.mod & tcod.event.Modifier.SHIFT:
                            submenu = "delete"
                        else:
                            if not canLoad:
                                submenu = "difficulty"

def showInterruptChoice(text,options):
    tcod.event.get()

    while 1:
        tcodConsole.clear()
        printUrwidToTcod(text,(0,0))
        tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

        events = tcod.event.get()
        for event in events:
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                src.interaction.tcodMixer.close()
                raise SystemExit()

            if isinstance(event,tcod.event.TextInput):
                translatedKey = event.text

                if translatedKey is None:
                    continue

                if translatedKey in options:
                    return translatedKey
    return None

def showInterruptText(text):
    tcod.event.get()

    while 1:
        tcodConsole.clear()
        printUrwidToTcod(text,(0,0))
        tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

        events = tcod.event.get()
        for event in events:
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event,tcod.event.KeyDown):
                key = event.sym
                if key in (tcod.event.KeySym.ESCAPE,tcod.event.KeySym.RETURN,tcod.event.KeySym.SPACE):
                    return

def showIntro():
    def fixRoomRender(render):
        for row in render:
            row.append("\n")
        return render

    src.gamestate.setup(None)
    src.gamestate.gamestate.terrainType = src.terrains.GameplayTest
    src.gamestate.gamestate.mainChar = src.characters.Character()
    src.gamestate.gamestate.mainChar.registers["HOMEx"] = 7
    src.gamestate.gamestate.mainChar.registers["HOMEy"] = 7
    src.gamestate.gamestate.mainChar.registers["HOMETx"] = 7
    src.gamestate.gamestate.mainChar.registers["HOMETy"] = 7
    src.gamestate.gamestate.mainChar.faction = "city demo"

    stage = 0
    stageState = None
    room = None
    skip = False
    while 1:
        if not skip:
            tcodConsole.clear()

        if stage == 0:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}

            if not skip:
                text = """
You """+"."*stageState["substep"]+"""


"""
                printUrwidToTcod(text,(60,24))
                printUrwidToTcod((src.interaction.urwid.AttrSpec("#ff2", "black"), "@ "),(63,27))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if time.time()-stageState["lastChange"] > 1 or skip:
                stageState["substep"] += 1
                stageState["lastChange"] = time.time()
                if stageState["substep"] == 4:
                    stageState = None
                    skip = False

            if not skip:
                time.sleep(0.01)

        if stage == 1:
            if stageState is None:
                stageState = {"lastChange":time.time(),"substep":0,"animationStep":0}

                scrapTakenMap = {}
                blockedMap = set()
                stageState["scrapToAdd"] = []
                for tile in [(6,7),(6,8),(7,8),(8,8)]:
                    for _i in range(1,150):
                        pos = (tile[0]*15+random.randint(1,13),tile[1]*15+random.randint(1,13),0)
                        if pos in blockedMap:
                            continue
                        stageState["scrapToAdd"].append(((pos),random.choice([1,1,1,1,5,5,15])))
                        blockedMap.add(pos)

                stageState["MoldToAdd"] = []
                for tile in [(6,6),(7,6),(8,6),(8,7)]:
                    for _i in range(1,10):
                        stageState["MoldToAdd"].append(((tile[0]*15+random.randint(1,13),tile[1]*15+random.randint(1,13),0),))

            if not skip:
                text = ["""You are born into a world of metal"""]
                if stageState["substep"] > 4:
                    text.append(""", rust""")
                if stageState["substep"] > 6:
                    text.append(""" and mold.""")

            if not room:
                terrain = src.terrains.Nothingness()
                terrain.yPosition = 7
                terrain.xPosition = 7
                src.gamestate.gamestate.tick = 0
                room = src.rooms.EmptyRoom()
                room.reconfigure(sizeX=13,sizeY=13,doorPos=[(0,6),(12,6)])
                room.hidden = False
                room.xPosition = 7
                room.yPosition = 7
                room.offsetX = 1
                room.offsetY = 1
                terrain.addRoom(room)
                terrain.hidden = False

            terrain.lastRender = None

            if stageState["substep"] == 6:
                terrain.hidden = False

                if (time.time()-stageState["lastChange"] > 0.001 or skip) and stageState["scrapToAdd"]:
                    stageState["lastChange"] = time.time()

                    for _i in range(6):
                        if not stageState["scrapToAdd"]:
                            continue
                        scrapItem = stageState["scrapToAdd"].pop()
                        terrain.addItem(src.items.itemMap["Scrap"](amount=scrapItem[1]),scrapItem[0])

            if stageState["substep"] == 7:
                terrain.hidden = False

                while stageState["MoldToAdd"]:
                    moldItem = stageState["MoldToAdd"].pop()
                    item = src.items.itemMap["MoldSpore"]()
                    terrain.addItem(item,moldItem[0])
                    item.startSpawn()

            if stageState["substep"] == 8:
                if (time.time()-stageState["lastChange"] > 0.1 or skip) and src.gamestate.gamestate.tick < 10000:
                    stageState["lastChange"] = time.time()

                    for _i in range(1,400):
                        terrain.advance()
                        src.gamestate.gamestate.tick += 1

            if not skip:
                roomRender = room.render()
                roomRender = fixRoomRender(roomRender)
                roomRender[6][6] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                mapStep = min(stageState["animationStep"],16)
                terrainRender = terrain.render(coordinateOffset=(15*7+1-mapStep,15*7+1-mapStep),size=(12+2*mapStep,12+2*mapStep))
                terrainRender = fixRoomRender(terrainRender)
                terrainRender[6+mapStep][6+mapStep] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                if stageState["substep"] < 4:
                    printUrwidToTcod(roomRender,(51,21))
                else:
                    printUrwidToTcod(terrainRender,(51-2*mapStep,21-mapStep))
                if stageState["substep"] < 5:
                    printUrwidToTcod(text,(47-min(9,stageState["animationStep"]//2),19-min(stageState["animationStep"],17)))
                else:
                    printUrwidToTcod(text,(38,2))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if stageState["substep"] == 4 and (time.time()-stageState["lastChange"] > 0.2 or skip) and stageState["animationStep"] < 17:
                stageState["animationStep"] += 1
                stageState["lastChange"] = time.time()

            if (time.time()-stageState["lastChange"] > 1 or
                     (skip and stageState["substep"] == 6 and not stageState["scrapToAdd"]) or
                     (skip and stageState["substep"] == 8 and not src.gamestate.gamestate.tick < 10000) or
                     (skip and stageState["substep"] not in [6,8])):
                stageState["substep"] += 1
                stageState["lastChange"] = time.time()
                if stageState["substep"] == 11:
                    stageState = None
                    skip = False

            if not skip:
                time.sleep(0.01)

        if stage == 2:
            text = """Strange mechanations fill the world with ancient logic"""

            terrain.lastRender = None

            if stageState is None:
                stageState = {"lastChange":time.time(), "items":[],"terrainItems":[],"outputslots":[],"walkingSpaces":[],"inputslots":[],"fastSpawn":set(),"subStep":0,"didRemove":False}

                machine = src.items.itemMap["Machine"]()
                machine.setToProduce("Sheet")
                stageState["items"].extend([
                    (src.items.itemMap["Scrap"](amount=5),(1,7,0)),
                    (src.items.itemMap["ScrapCompactor"](),(2,7,0)),
                    (machine,(4,7,0)),
                ])

                machine = src.items.itemMap["Machine"]()
                machine.setToProduce("Rod")
                machine2 = src.items.itemMap["Machine"]()
                machine2.setToProduce("Tank")
                machine3 = src.items.itemMap["Machine"]()
                machine3.setToProduce("Sword")
                machine4 = src.items.itemMap["Machine"]()
                machine4.setToProduce("Armor")
                stageState["items"].extend([
                    (src.items.itemMap["ScrapCompactor"](),(2,9,0)),
                    (machine,(4,9,0)),
                    (machine2,(8,5,0)),
                    (machine3,(4,3,0)),
                    (machine4,(4,5,0)),
                ])

                command1 = src.items.itemMap["Command"]()
                command1.command =  "ddKdaj"
                command1.bolted = True

                command2 = src.items.itemMap["Command"]()
                command2.command =  "waajjddsdjaj"
                command2.bolted = True

                command3 = src.items.itemMap["Command"]()
                command3.command =  "wd2w4aJsJwddJsJwddssaas"
                command3.bolted = True

                command4 = src.items.itemMap["Command"]()
                command4.command =  "wjwjwjwjdkalsdkalsdkalsdkalsj"
                command4.bolted = True

                command5 = src.items.itemMap["Command"]()
                command5.command =  "kdldj"

                command6 = src.items.itemMap["Command"]()
                command6.command =  "5a4w14ajjj13sjjj13djjj13djjj13w13a.2s6a"+10*"Lw"+10*"Ls"+"5d2s5d"+50*"Js"+"j"
                command6.bolted = True

                command7 = src.items.itemMap["Command"]()
                command7.command =  "kdldj"

                command8 = src.items.itemMap["Command"]()
                command8.command =  "5a3w14dj13wj13aj13aj13s13d.4w2dj2a4s"+".3s5das"+50*"Js"+"wdj"
                command8.bolted = True

                command9 = src.items.itemMap["Command"]()
                command9.command =  "kdldj"

                command10 = src.items.itemMap["Command"]()
                command10.command =  "5a2w"+"4aJw4d"+"2waaJwJsdd2w4asJsw4d"+"dd2sJsww"+"dddKwaJw3aJwa6s5d2s"+10*"Js"+"aaajj20.ddd2wj"
                command10.bolted = True

                scratchPlate = src.items.itemMap["ScratchPlate"]()
                scratchPlate.bolted = True
                scratchPlate.commands["noscratch"] = "jjaKsdJsJs20."
                scratchPlate.settings["scratchThreashold"] = 300
                scratchPlate.lastActivation = -2000

                scratchPlate2 = src.items.itemMap["ScratchPlate"]()
                scratchPlate2.bolted = True
                scratchPlate2.commands["noscratch"] = "jjaKsdJsJs20.aKsdJsJs20.aKsdJsJs20."
                scratchPlate2.settings["scratchThreashold"] = 300
                scratchPlate2.lastActivation = -2000


                stageState["items"].extend([
                    (src.items.itemMap["Corpse"](),(1,11,0)),
                    (scratchPlate,(2,10,0)),
                    (src.items.itemMap["CorpseAnimator"](),(2,11,0)),
                    (command1,(3,11,0)),
                    (command2,(4,11,0)),
                    (command3,(5,11,0)),
                    (src.items.itemMap["Corpse"](),(6,11,0)),
                    (src.items.itemMap["Corpse"](),(7,11,0)),
                    (src.items.itemMap["Corpse"](),(7,11,0)),
                    (src.items.itemMap["Corpse"](),(7,11,0)),
                    (src.items.itemMap["Corpse"](),(7,11,0)),
                    (src.items.itemMap["Corpse"](),(7,11,0)),
                    (scratchPlate2,(8,10,0)),
                    (src.items.itemMap["CorpseAnimator"](),(8,11,0)),
                    (command4,(9,11,0)),
                    (command5,(9,10,0)),
                    (command6,(11,10,0)),
                    (command7,(9,9,0)),
                    (command8,(11,9,0)),
                    (command9,(9,8,0)),
                    (command10,(11,8,0)),
                    (src.items.itemMap["Corpse"](),(11,11,0)),
                    (src.items.itemMap["Corpse"](),(11,11,0)),
                    (src.items.itemMap["Corpse"](),(11,11,0)),
                    (src.items.itemMap["Corpse"](),(11,11,0)),
                    (src.items.itemMap["Corpse"](),(11,11,0)),
                    (src.items.itemMap["Corpse"](),(10,11,0)),
                    (src.items.itemMap["Corpse"](),(10,11,0)),
                    (src.items.itemMap["Corpse"](),(10,11,0)),
                    (src.items.itemMap["Corpse"](),(10,11,0)),
                    (src.items.itemMap["Corpse"](),(10,11,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(7,4,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(10,5,0)),
                    (src.items.itemMap["Corpse"](),(11,4,0)),
                    (src.items.itemMap["Corpse"](),(11,4,0)),
                    (src.items.itemMap["Corpse"](),(11,4,0)),
                    (src.items.itemMap["Corpse"](),(11,4,0)),
                    (src.items.itemMap["Corpse"](),(11,4,0)),
                ])

                commandGooProduction = src.items.itemMap["Command"]()
                commandGooProduction.command = "d"+10*"Ls"+"d"+10*"10.Js"+"aassd"+10*"Kd"+"aww"+"7a"+10*"Lw"+"d"+10*"Jw"+"ddJwddJwdd"
                commandGooProduction.bolted = True

                bloom = src.items.itemMap["Bloom"]()
                bloom.dead = True
                bloom.bolted = True

                gooFlask = src.items.itemMap["GooFlask"]()
                gooFlask.uses = 100

                machine = src.items.itemMap["Machine"]()
                machine.setToProduce("GooFlask")

                gooDispenser = src.items.itemMap["GooDispenser"]()
                gooDispenser.charges = 1
                gooDispenser.commands["filled"] = "dLwa"
                stageState["items"].extend([
                    (src.items.itemMap["BloomShredder"](),(2,1,0)),
                    (src.items.itemMap["BioPress"](),(4,1,0)),
                    (src.items.itemMap["GooProducer"](),(6,1,0)),
                    (gooDispenser,(7,1,0)),
                    (gooFlask,(8,1,0)),
                    (commandGooProduction,(8,2,0)),
                    (machine,(10,1,0)),
                    (bloom,(10,2,0)),
                    (src.items.itemMap["Bolt"](),(11,2,0)),
                    (src.items.itemMap["Bolt"](),(11,3,0)),
                    (src.items.itemMap["Sorter"](),(10,3,0)),
                    (src.items.itemMap["Scraper"](),(2,4,0)),
                    (src.items.itemMap["ScrapCompactor"](),(2,5,0)),
                ])

                def generatePaving():
                    item = src.items.itemMap["Paving"]()
                    item.bolted = True
                    return item

                for y in reversed(range(8,14)):
                    stageState["terrainItems"].append((generatePaving(),(6*15+7,6*15+y,0)))
                for x in range(8,14):
                    stageState["terrainItems"].append((generatePaving(),(6*15+x,6*15+7,0)))
                for x in range(8,14):
                    stageState["terrainItems"].append((generatePaving(),(6*15+x,6*15+7,0)))
                for x in range(1,7):
                    stageState["terrainItems"].append((generatePaving(),(7*15+x,6*15+7,0)))
                for x in range(8,14):
                    stageState["terrainItems"].append((generatePaving(),(7*15+x,6*15+7,0)))
                for x in range(1,7):
                    stageState["terrainItems"].append((generatePaving(),(8*15+x,6*15+7,0)))
                for y in range(8,14):
                    stageState["terrainItems"].append((generatePaving(),(8*15+7,6*15+y,0)))
                for y in range(1,7):
                    stageState["terrainItems"].append((generatePaving(),(8*15+7,7*15+y,0)))
                for y in range(8,14):
                    stageState["terrainItems"].append((generatePaving(),(8*15+7,7*15+y,0)))
                for x in range(1,7):
                    stageState["terrainItems"].append((generatePaving(),(8*15+x,7*15+7,0)))

                stageState["terrainItems"].append((src.items.itemMap["AutoFarmer"](),(6*15+7,6*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["AutoFarmer"](),(7*15+7,6*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["AutoFarmer"](),(8*15+7,6*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["AutoFarmer"](),(8*15+7,7*15+7,0)))

                stageState["terrainItems"].append((src.items.itemMap["ItemCollector"](),(6*15+7,7*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["ItemCollector"](),(6*15+7,8*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["ItemCollector"](),(7*15+7,8*15+7,0)))
                stageState["terrainItems"].append((src.items.itemMap["ItemCollector"](),(8*15+7,8*15+7,0)))

                for x in reversed(range(1,12)):
                    stageState["walkingSpaces"].append((x,6,0))
                    stageState["walkingSpaces"].append((x,2,0))
                for x in reversed(range(1,9)):
                    stageState["walkingSpaces"].append((x,10,0))
                for x in reversed(range(1,7)):
                    stageState["walkingSpaces"].append((x,8,0))
                for y in reversed(range(2,11)):
                    stageState["walkingSpaces"].append((6,y,0))

                stageState["walkingSpaces"].append((8,3,0))
                stageState["walkingSpaces"].append((8,4,0))
                stageState["walkingSpaces"].append((9,4,0))
                stageState["walkingSpaces"].append((1,3,0))
                stageState["walkingSpaces"].append((2,3,0))
                stageState["walkingSpaces"].append((4,4,0))
                stageState["walkingSpaces"].append((5,4,0))
                stageState["walkingSpaces"].append((11,5,0))
                stageState["walkingSpaces"].append((11,3,0))
                stageState["walkingSpaces"].append((3,4,0))

                stageState["outputslots"].append(("Sword",(5,3,0)))
                stageState["outputslots"].append(("Armor",(5,5,0)))
                stageState["outputslots"].append(("Sheet",(5,7,0)))
                stageState["outputslots"].append(("Rod",(5,9,0)))
                stageState["outputslots"].append(("MetalBars",(3,7,0)))
                stageState["outputslots"].append(("MetalBars",(3,9,0)))
                stageState["outputslots"].append(("Corpse",(7,3,0)))
                stageState["outputslots"].append(("GooFlask",(8,1,0)))
                stageState["outputslots"].append(("Tank",(9,5,0)))
                stageState["outputslots"].append(("Corpse",(7,4,0)))
                stageState["outputslots"].append(("Corpse",(10,5,0)))
                stageState["outputslots"].append(("Corpse",(11,4,0)))

                stageState["inputslots"].append(("Tank",(9,1,0)))
                stageState["inputslots"].append(("Scrap",(1,5,0)))
                stageState["inputslots"].append(("MetalBars",(3,5,0)))
                stageState["inputslots"].append(("Rod",(3,3,0)))
                stageState["inputslots"].append(("Sheet",(7,5,0)))
                stageState["inputslots"].append(("Scrap",(1,7,0)))
                stageState["inputslots"].append(("Scrap",(1,9,0)))
                stageState["inputslots"].append((None,(1,4,0)))
                stageState["inputslots"].append(("Corpse",(1,11,0)))
                stageState["inputslots"].append(("Corpse",(6,11,0)))
                stageState["inputslots"].append(("Corpse",(7,11,0)))
                stageState["inputslots"].append(("Corpse",(10,11,0)))
                stageState["inputslots"].append(("Corpse",(11,11,0)))
                stageState["inputslots"].append(("Scrap",(1,9,0)))
                stageState["inputslots"].append(("Scrap",(1,9,0)))

            if not skip:
                roomRender = room.render()
                roomRender = fixRoomRender(roomRender)
                roomRender[6][6] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")

                terrainRender = terrain.render(coordinateOffset=(15*6,15*6),size=(44,44))
                terrainRender = fixRoomRender(terrainRender)
                terrainRender[22][22] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                printUrwidToTcod(text,(38,2))
                printUrwidToTcod(terrainRender,(19,5))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if stageState["walkingSpaces"] and stageState["subStep"] > 1:
                stageState["lastChange"] = time.time()
                for pos in stageState["walkingSpaces"]:
                    if pos not in room.walkingSpace:
                        room.walkingSpace.add(pos)
                stageState["walkingSpaces"] = []
            elif stageState["outputslots"] and stageState["subStep"] > 1:
                stageState["lastChange"] = time.time()
                for (itemType,pos) in stageState["outputslots"]:
                    room.addOutputSlot(pos,itemType)
                stageState["outputslots"] = []
            elif stageState["inputslots"] and stageState["subStep"] > 1:
                stageState["lastChange"] = time.time()
                for (itemType,pos) in stageState["inputslots"]:
                    if itemType == "Corpse":
                        room.addInputSlot(pos,itemType,{"maxAmount":3})
                    else:
                        room.addInputSlot(pos,itemType)
                stageState["inputslots"] = []
            elif stageState["items"] and stageState["subStep"] > 2:
                if time.time()-stageState["lastChange"] > 0.1 or skip:
                    stageState["lastChange"] = time.time()
                    numItems = 2
                    i = 0
                    while i < numItems:
                        if not stageState["items"]:
                            i += 1
                            continue
                        item = stageState["items"].pop()
                        room.addItem(item[0],item[1])
                        if item[1] in stageState["fastSpawn"]:
                            i -= 1
                        else:
                            stageState["fastSpawn"].add(item[1])
                        i += 1
            elif not stageState["didRemove"] and stageState["subStep"] > 2:
                for x in range(15*6+7,15*8+7+1):
                    items = terrain.getItemByPosition((x,15*6+7,0))
                    if items:
                        terrain.removeItems(items)
                    items = terrain.getItemByPosition((x,15*7+7,0))
                    if items:
                        terrain.removeItems(items)
                    items = terrain.getItemByPosition((x,15*8+7,0))
                    if items:
                        terrain.removeItems(items)

                for y in range(15*6+7,15*8+7+1):
                    items = terrain.getItemByPosition((15*6+7,y,0))
                    if items:
                        terrain.removeItems(items)
                    items = terrain.getItemByPosition((15*8+7,y,0))
                    if items:
                        terrain.removeItems(items)

                stageState["didRemove"] = True

            elif stageState["terrainItems"] and stageState["subStep"] > 2:
                if time.time()-stageState["lastChange"] > 0.01 or skip:
                    stageState["lastChange"] = time.time()
                    for _i in range(4):
                        if not stageState["terrainItems"]:
                            continue
                        item = stageState["terrainItems"].pop()
                        terrain.addItem(item[0],item[1])
            else:
                if time.time()-stageState["lastChange"] > 1 or skip:
                    stageState["lastChange"] = time.time()
                    stageState["subStep"] += 1
                    if stageState["subStep"] == 4:
                        stageState = None
                        skip = False

            if not skip:
                time.sleep(0.01)

        if stage == 3:
            text1 = """Strange machinations fill the world with ancient logic"""
            text2 = """and you work on tasks with unknown purposes."""

            terrain.lastRender = None

            if stageState is None:
                stageState = {"lastChange":time.time()}

            if not skip:
                terrainRender = terrain.render(coordinateOffset=(15*6,15*6),size=(44,44))
                terrainRender = fixRoomRender(terrainRender)
                terrainRender[22][22] = (src.interaction.urwid.AttrSpec("#ff2", "black"), "@ ")
                printUrwidToTcod(text1,(38,2))
                printUrwidToTcod(text2,(42,3))
                printUrwidToTcod(terrainRender,(19,5))

                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if time.time()-stageState["lastChange"] > 2 or skip:
                stageState = None
                skip = False

        if stage == 4:
            text1 = """Strange machinations fill the world with ancient logic"""
            text2 = """and you work on tasks with unknown purposes."""

            terrain.lastRender = None

            if stageState is None:
                stageState = {"lastChange":time.time(),"substep":0,"endless":False}

                npc = src.characters.Character()
                npc.faction = "city demo"
                npc.registers["HOMETx"] = 7
                npc.registers["HOMETy"] = 7
                npc.registers["HOMEx"] = 7
                npc.registers["HOMEy"] = 7
                npc.runCommandString("4w2dKw")
                room.addCharacter(npc,6,6)

                npc.solvers = [
                    "SurviveQuest",
                    "Serve",
                    "NaiveMoveQuest",
                    "MoveQuestMeta",
                    "NaiveActivateQuest",
                    "ActivateQuestMeta",
                    "NaivePickupQuest",
                    "PickupQuestMeta",
                    "DrinkQuest",
                    "ExamineQuest",
                    "FireFurnaceMeta",
                    "CollectQuestMeta",
                    "WaitQuest",
                    "NaiveDropQuest",
                    "NaiveMurderQuest",
                    "DropQuestMeta",
                    "DeliverSpecialItem",
                ]


                quest = src.quests.questMap["BeUsefull"](targetPosition=(7,7,0))
                quest.autoSolve = True
                quest.assignToCharacter(npc)
                quest.activate()
                npc.quests.insert(0,quest)

                npc.duties = ["clearing","hauling"]
                npc.duties = ["scratch checking"]
                npc.duties = ["clearing","hauling","scratch checking"]

                src.gamestate.gamestate.mainChar = npc

            terrainRender = terrain.render(coordinateOffset=(15*6,15*6),size=(44,44))
            terrainRender = fixRoomRender(terrainRender)
            printUrwidToTcod(text1,(38,2))
            printUrwidToTcod(text2,(42,3))
            printUrwidToTcod(terrainRender,(19,5))

            if src.gamestate.gamestate.tick > 10400:
                if stageState["endless"]:
                    printUrwidToTcod("press space to stop watching",(47,4))
                else:
                    printUrwidToTcod("press space to continue watching",(46,4))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if stageState["substep"] < 1 and time.time()-stageState["lastChange"] > 0:
                stageState["lastChange"] = time.time()
                stageState["substep"] += 1

            if stageState["substep"] > 0:
                if time.time()-stageState["lastChange"] > 0.15:
                    stageState["lastChange"] = time.time()
                    terrain.advance()
                    src.gamestate.gamestate.tick += 1

                    removeList = []
                    for character in room.characters+terrain.characters:
                        character.timeTaken -= 1
                        advanceChar(character,render=False, pull_events = False)

                if src.gamestate.gamestate.tick > 10470 and not stageState["endless"]:
                    stageState = None
                    skip = False

            if skip:
                stageState = None
                skip = False

        if stage == 5:
            text1 = """Strange machinations fill the world with ancient logic"""
            text2 = """and you work on tasks with unknown purposes."""

            terrain.lastRender = None

            if stageState is None:
                stageState = {"lastChange":time.time(),"substep":0}

            if not skip:
                offset = min(stageState["substep"],16)
                if not stageState["substep"] > 16:
                    terrainRender = terrain.render(coordinateOffset=(15*6+offset,15*6+offset),size=(44-2*offset,44-2*offset))
                    terrainRender = fixRoomRender(terrainRender)
                    printUrwidToTcod(terrainRender,(19+2*offset,5+offset))
                printUrwidToTcod(text1,(38,2+offset))
                printUrwidToTcod(text2,(42,3+offset))
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if time.time()-stageState["lastChange"] > 0.3:
                stageState["lastChange"] = time.time()
                stageState["substep"] += 1

            if stageState["substep"] > 30 or skip:
                stageState = None
                skip = False

        if stage == 6:
            if stageState is None:
                stageState = {"lastChange":time.time(),"substep":0,"animationStep":0}

            text1 = """
But despite all the unknowns, you have that voice in your head. It tells you:"""

            text2 = """
"You will rule the world someday, but first

"""
            text3 = """

FOLLOW YOUR ORDERS
"""

            if stageState["substep"] > 0 and stageState["substep"] < 5:
                printUrwidToTcod(text1,(27,19))
            if stageState["substep"] > 2 and stageState["substep"] < 5:
                printUrwidToTcod(text2,(44,23))
            if stageState["substep"] > 3:
                printUrwidToTcod(src.urwidSpecials.makeRusty(text3)[:stageState["animationStep"]],(55,25))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)

            if stageState["substep"] == 4 and stageState["animationStep"] < len(text3):
                if time.time()-stageState["lastChange"] > 0.1:
                    stageState["animationStep"] += 1
                    stageState["lastChange"] = time.time()
            if time.time()-stageState["lastChange"] > 3:
                stageState["substep"] += 1
                stageState["lastChange"] = time.time()
                if stageState["substep"] > 5:
                    stageState = None
                    skip = False

            if not skip:
                time.sleep(0.01)

            if skip:
                stageState = None
                skip = False

        if stage > 6:
            break

        events = tcod.event.get()
        for event in events:
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event,tcod.event.KeyDown):
                key = event.sym
                if key == tcod.event.KeySym.F11:
                    fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                    )
                    tcod.lib.SDL_SetWindowFullscreen(
                        tcodContext.sdl_window_p,
                        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                    )
                if key == tcod.event.KeySym.RETURN:
                    skip = True
                if key == tcod.event.KeySym.SPACE and stage == 4:
                    if not stageState["endless"]:
                        stageState["endless"] = True
                    else:
                        stageState = None
                if key == tcod.event.KeySym.ESCAPE:
                    stage = 7

        if not stageState:
            stage += 1

def showRunOutro():

    def fixRoomRender(render):
        for row in render:
            row.append("\n")
        return render

    stage = 0
    stageState = None
    room = None
    subStep = 0
    subStep2 = 1
    addedText = False
    sleepAmountGrow = 0.125
    painPositions = []
    while 1:
        tcodConsole.clear()

        if stage == 0:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}
            text = """
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |

"""
            printUrwidToTcod(text,(40,14))
            textBase = ["""
You take the crown and put it on your head.      """+"""
It latches on firmly and you grid your teeth.       """+"""
The crowns connectors bite through your skull and reach your implant.
                        """+"""
It connects and is ready to merge with you.
                                           """+""""""]
            text = "".join(textBase[0:subStep])
            if not subStep < len(textBase)-1:
                text += textBase[-1][0:subStep2]
            printUrwidToTcod(text,(45,17))

            if not subStep2 < len(textBase[-1]):
                printUrwidToTcod("press enter to merge with the throne",(45,27))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if subStep < len(textBase)-1:
                time.sleep(0.5)
                subStep += 1
            elif subStep2 < len(textBase[-1]):
                subStep2 += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        elif stage == 1:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}
            text = """
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |

"""
            printUrwidToTcod(text,(40,14))
            textBase = ["""
You merge with the Throne.
The gods bow and

        you rule the world now."""]
            text = "".join(textBase[0:subStep])
            if not subStep < len(textBase)-1:
                text += textBase[-1][0:subStep2]
            printUrwidToTcod(text,(45,17))

            if not subStep2 < len(textBase[-1]):
                printUrwidToTcod("press enter to reach out to implant",(45,27))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if subStep < len(textBase)-1:
                time.sleep(0.5)
                subStep += 1
            elif subStep2 < len(textBase[-1]):
                subStep2 += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        elif stage == 2:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}
            text = """
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |

"""
            printUrwidToTcod(text,(40,14))
            textBase = ["""
You reach out to your implant and it answers:

No advice can be rendered to a true leader.
You rule this world now and your responsibility.





press enter to run credits"""]
            text = "".join(textBase[0:subStep])
            if not subStep < len(textBase)-1:
                text += textBase[-1][0:subStep2]
            printUrwidToTcod(text,(45,17))

            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if subStep < len(textBase)-1:
                time.sleep(0.5)
                subStep += 1
            elif subStep2 < len(textBase[-1]):
                subStep2 += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        elif stage == 3:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}
            text = """
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |

"""
            printUrwidToTcod(text,(40,14))
            textBase = ["""
credits:

MarxMustermann






press enter"""]
            text = "".join(textBase[0:subStep])
            if not subStep < len(textBase)-1:
                text += textBase[-1][0:subStep2]
            printUrwidToTcod(text,(45,17))

            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if subStep < len(textBase)-1:
                time.sleep(0.5)
                subStep += 1
            elif subStep2 < len(textBase[-1]):
                subStep2 += 1
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        else:
            break

        events = tcod.event.get()
        for event in events:
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event,tcod.event.KeyDown):
                key = event.sym
                if key == tcod.event.KeySym.F11:
                    fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                    )
                    tcod.lib.SDL_SetWindowFullscreen(
                        tcodContext.sdl_window_p,
                        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                    )
                if key == tcod.event.KeySym.ESCAPE:
                    stage = 7
                if key == tcod.event.KeySym.RETURN:
                    stage += 1
                    subStep = 0

def showRunIntro():

    def fixRoomRender(render):
        for row in render:
            row.append("\n")
        return render

    stage = 0
    stageState = None
    room = None
    subStep = 0
    subStep2 = 1
    addedText = False
    sleepAmountGrow = 0.125
    painPositions = []
    while 1:
        tcodConsole.clear()

        if stage == 0:
            if stageState is None:
                stageState = {"substep":1,"lastChange":time.time()}
            text = """
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
  |                                                                         |
--+-------------------------------------------------------------------------+--
  |                                                                         |

"""
            printUrwidToTcod(text,(40,14))
            textBase = ["""
You see """,".",".",".",""" nothing
""","You hear ",".",".",".",""" nothing
""","You know ",".",".",".",""" nothing
""","You remember ",".",".",".",""" nothing
""","You feel ",".",".",".",""" A sharp pain burrowing through you mind.     \n\
You remember how tendrils of pain grew from from your implant.     \n\
You know that something is wrong within your implant.     \n\

It eats your mind and           \n\
starts to burn your flesh.                                                \n\
"""]
            if not noFlicker and not subStep < len(textBase)-1:
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
                time.sleep(0.01)
            text = "".join(textBase[0:subStep])
            if not subStep < len(textBase)-1:
                text += textBase[-1][0:subStep2]
            printUrwidToTcod(text,(45,17))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            if subStep < len(textBase)-1:
                time.sleep(0.5)
                subStep += 1
            elif subStep2 < len(textBase[-1]):
                subStep2 += 1
                time.sleep(0.03)
            else:
                stage += 2 # skip one stage
                subStep = 0
                subStep2 = 0
        elif stage == 1:
            tcodConsole.clear()
            painChars = ["#","%","&","*","+","`"]
            painColors = ["#fff","#55f","#f5f","#aaf","#a9f","#9af"]
            for painPos in painPositions:
                painChar = random.choice(painChars)
                painColor = random.choice(painColors)
                printUrwidToTcod((src.interaction.urwid.AttrSpec(painColor, "black"), painChar),painPos)

            if not noFlicker:
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            time.sleep(0.01)
            text = """
                                                                                   \n\
    |                                                                         |    \n\
  --+-------------------------------------------------------------------------+--  \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
    |                                                                         |    \n\
  --+-------------------------------------------------------------------------+--  \n\
    |                                                                         |    \n\
                                                                                   \n\
"""
            printUrwidToTcod(text,(38,13))
            if not noFlicker:
                tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            time.sleep(0.02)
            textBase = """
The pain grows and grows and grows and grows and grows and grows and
grows and grows and grows and grows and grows and grows and grows and
grows and grows and grows and grows and grows and grows and grows and
grows and grows and grows and grows and grows and grows and grows and
grows and grows and grows and grows
""".split(" ")
            text = " ".join(textBase[0:subStep])
            printUrwidToTcod(text,(45,17))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            for _i in range(100):
                pos = (random.randint(1,199),random.randint(1,50))
                if pos[0] > 37 and pos[0] < 121 and pos[1] > 13 and pos[1] < 34:
                    continue
                if pos not in painPositions:
                    painPositions.append(pos)

            if subStep < len(textBase)-1:
                time.sleep(sleepAmountGrow)
                sleepAmountGrow -= 0.00075
                subStep += 1
            else:
                stage += 1
                subStep = 0
                subStep2 = 0
        elif stage == 2:
            backgroundText = "You will rule the world some day, but first follow your orders.   "

            numChars=len(backgroundText)-14
            #if subStep < numChars*1:
            #    color = "#000"
            #    color2 = "#000"
            #    color3 = "#000"
            if subStep < numChars*1:
                color = "#000"
                color2 = "#000"
                color3 = "#111"
            elif subStep < numChars*2:
                color = "#000"
                color2 = "#111"
                color3 = "#222"
            elif subStep < numChars*3:
                color = "#111"
                color2 = "#222"
                color3 = "#332"
            elif subStep < numChars*4:
                color = "#222"
                color2 = "#333"
                color3 = "#442"
            else:
                color = "#333"
                color2 = "#333"
                color3 = "#442"
            """
            else:
                color = "#442"
                color2 = "#442"
                color3 = "#552"
            elif subStep < l*7:
                color = "#552"
                color2 = "#662"
                color3 = "#772"
            elif subStep < l*8:
                color = "#662"
                color2 = "#772"
                color3 = "#882"
            elif subStep < l*9:
                color = "#772"
                color2 = "#882"
                color3 = "#992"
            elif subStep < l*10:
                color = "#882"
                color2 = "#992"
                color3 = "#aa2"
            elif subStep < l*11:
                color = "#992"
                color2 = "#aa2"
                color3 = "#bb2"
            else:
                color = "#aa2"
                color2 = "#aa2"
                color3 = "#ff2"
            elif subStep < l*12:
                color = "#bb2"
                color2 = "#cc2"
            elif subStep < l*13:
                color = "#cc2"
                color2 = "#dd2"
            elif subStep < l*14:
                color = "#dd2"
                color2 = "#ee2"
            elif subStep < l*15:
                color = "#ee2"
                color2 = "#ff2"
            else:
                color = "#ff2"
                color2 = "#ff2"
            """

            """
            convertedBackgroundText = []
            counter = 0
            for char in backgroundText:
                if counter <
                    convertedBackgroundText.append((src.interaction.urwid.AttrSpec(color2, "black"), char))
                else:
                    convertedBackgroundText.append((src.interaction.urwid.AttrSpec(color, "black"), char))
                counter += 1
            backgroundText = convertedBackgroundText
            """

            attrSpec = src.interaction.urwid.AttrSpec(color2, "black")
            attrSpec2 = src.interaction.urwid.AttrSpec(color, "black")
            attrSpec3 = src.interaction.urwid.AttrSpec(color3, "black")
            line = backgroundText*4
            offset = 0
            width = len(backgroundText)

            index = subStep%numChars
            backgroundText = "You will rule the world some day, but first follow your orders.   "
            if index > 2:
                index += 1
            if index > 7:
                index += 1
            if index > 12:
                index += 1
            if index > 16:
                index += 1
            if index > 22:
                index += 1
            if index > 27:
                index += 1
            if index > 32:
                index += 1
            if index > 36:
                index += 1
            if index > 42:
                index += 1
            if index > 49:
                index += 1
            if index > 54:
                index += 1
            part1 = backgroundText[0:index]
            part1len = len(part1)
            part2 = backgroundText[index]
            part3 = backgroundText[index+1:]

            x = 0
            y = 0
            for _i in range(150):
                printUrwidToTcod((attrSpec,part1),(x,y))
                printUrwidToTcod((attrSpec3,part2),(x+part1len,y))
                printUrwidToTcod((attrSpec2,part3),(x+part1len+1,y))
                offset = 200 - x
                x += width
                if x > 200:
                    y += 2
                    x = -offset
            text = """
                                                                                       \n\
      |                                                                         |      \n\
    --+-------------------------------------------------------------------------+--    \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
      |                                                                         |      \n\
    --+-------------------------------------------------------------------------+--    \n\
      |                                                                         |      \n\
                                                                                       \n\
"""
            printUrwidToTcod(text,(36,13))
            text = ""
            text += """
until something breaks."""
            if subStep > 15:
                baseText = """

Your implant stops emitting pain
and for a moment you hear terrible silence."""
                #text += " ".join(baseText.split(" ")[:(subStep-15)])
                text += "".join(list(baseText)[:(subStep*3-15*3)])
            if subStep > 55:
                baseText = """

But it slowly comes back
and you hear that familiar voice again."""
                #text += " ".join(baseText.split(" ")[:(subStep-35)])
                text += "".join(list(baseText)[:(subStep*3-55*3)])
            if subStep > 100:
                text += """


suggested action:
press enter to continue
"""
            printUrwidToTcod(text,(45,17))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            time.sleep(0.2)
            subStep += 1
        elif stage ==  3:
            text = """
You."""
            if subStep > 0:
                text += """
You see walls made out of solid steel"""
            if subStep > 1:
                text += """
and feel the touch of the cold hard floor."""
            if subStep > 2:
                text += """
The room is filled with various items."""
            if subStep > 3:
                text += """
You recognise your hostile suroundings and
try to remember how you got here ..."""
                if not addedText:
                    src.gamestate.gamestate.mainChar.addMessage("----------\n\n"+text)
                    addedText = True

            printUrwidToTcod(text,(133,6))
            if subStep == 0:
                text = """
suggested action:
press enter
to open your eyes"""
            elif subStep == 1:
                text = """
suggested action:
press enter
to feel around"""
            elif subStep == 2:
                text = """
suggested action:
press enter
to look around"""
            elif subStep == 3:
                text = """
suggested action:
press enter
to orient yourself"""

            else:
                text = """
suggested action:
press enter
to remember"""

            printUrwidToTcod(text,(2,19))
            if subStep == 1:
                wall = src.items.itemMap["Wall"]()
                totalOffsetX = 56+26-offset[0]*2
                totalOffsetY = 15+13-offset[1]
                for i in range(13):
                    if i == 6:
                        continue
                    printUrwidToTcod(wall.render(),(totalOffsetX+2*i,totalOffsetY))
                    printUrwidToTcod(wall.render(),(totalOffsetX,totalOffsetY+i))
                    printUrwidToTcod(wall.render(),(totalOffsetX+2*i,totalOffsetY+12))
                    printUrwidToTcod(wall.render(),(totalOffsetX+12*2,totalOffsetY+i))
            if subStep == 2:
                room = src.rooms.EmptyRoom(None,None,None,None)
                room.reconfigure(13, 13, doorPos=[(12,6),(6,12),(0,6),(6,0)])
                room.hidden = False
                printUrwidToTcod(fixRoomRender(room.render()),(56+26-offset[0]*2,15+13-offset[1]))
            if subStep == 3:
                offset = src.gamestate.gamestate.mainChar.getPosition()
                printUrwidToTcod(fixRoomRender(src.gamestate.gamestate.mainChar.container.render()),(56+26-offset[0]*2,15+13-offset[1]))
            if subStep == 4:
                offset = src.gamestate.gamestate.mainChar.getPosition()
                roomPos = src.gamestate.gamestate.mainChar.container.getPosition()
                terrainRender = src.gamestate.gamestate.mainChar.getTerrain().render(coordinateOffset=(15*(roomPos[1]-1)-6+offset[1],15*(roomPos[0]-1)-6+offset[0]),size=(44,44))
                terrainRender = fixRoomRender(terrainRender)
                printUrwidToTcod(terrainRender,(38,6))

                miniMapChars = src.gamestate.gamestate.mainChar.getTerrain().renderTiles()
                miniMapChars = fixRoomRender(miniMapChars)
                printUrwidToTcod(miniMapChars,(4,2))

            offset = src.gamestate.gamestate.mainChar.getPosition()
            printUrwidToTcod((src.interaction.urwid.AttrSpec("#ff2", "black"), "@ "),(76+6,22+6))
            tcodContext.present(tcodConsole,integer_scaling=True,keep_aspect=True)
            time.sleep(0.1)
        else:
            break

        events = tcod.event.get()
        for event in events:
            if isinstance(event, tcod.event.Quit):
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event, tcod.event.WindowResized):
                checkResetWindowSize(event.width,event.height)
            if isinstance(event, tcod.event.WindowEvent) and event.type == "WINDOWCLOSE":
                src.interaction.tcodMixer.close()
                raise SystemExit()
            if isinstance(event,tcod.event.KeyDown):
                key = event.sym
                if key == tcod.event.KeySym.F11:
                    fullscreen = tcod.lib.SDL_GetWindowFlags(tcodContext.sdl_window_p) & (
                        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
                    )
                    tcod.lib.SDL_SetWindowFullscreen(
                        tcodContext.sdl_window_p,
                        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
                    )
                if key == tcod.event.KeySym.ESCAPE:
                    stage = 7
                if key == tcod.event.KeySym.RETURN:
                    if stage != 3:
                        # move to next stage
                        stage += 1
                        subStep = 0

                        # skip stage 2
                        if stage == 1:
                            stage += 1
                    else:
                        subStep += 1

                        if subStep > 4:
                            bombs = []
                            numExplosions = 0
                            for item in src.gamestate.gamestate.mainChar.container.itemsOnFloor:
                                if item.type == "Bomb":
                                    numExplosions += 1
                                    item.destroy()
                                if numExplosions > 2:
                                    break
                            stage += 1
                            subStep = 0

def gameLoop(loop=None, user_data=None):
    while 1:
        advanceGame()
        #renderGameDisplay()

def gameLoop_disabled(loop, user_data=None):
    """
    run the game for one tick

    Parameters:
        loop: the main loop (urwids main loop)
        user_data: parameter have to handle but is ignored
    """

    slowestTick = None
    slowestTickSpeed = None
    totalTickSpeed = 0
    numTrackedTicks = 0
    if not os.path.exists("perfDebug"):
        os.makedirs("perfDebug")

    if src.gamestate.gamestate.stopGameInTicks is not None:
        if src.gamestate.gamestate.stopGameInTicks == 0:
            src.gamestate.gamestate.gameHalted = True
            src.gamestate.gamestate.stopGameInTicks = None
        else:
            src.gamestate.gamestate.stopGameInTicks -= 1

    if src.gamestate.gamestate.gameHalted:
        loop.set_alarm_in(0.001, gameLoop)
        return

    global lastAdvance
    global fixedTicks
    global lastAutosave

    runFixedTick = False
    if speed:
        fixedTicks = speed
    if fixedTicks and time.time() - lastAdvance > fixedTicks:
        runFixedTick = True

    global multi_currentChar
    global new_chars

    firstRun = True
    lastcheck = time.time()
    lastRender = time.time()

    while not loop or firstRun:
        if lastAutosave == 0:
            lastAutosave = src.gamestate.gamestate.tick
        if src.gamestate.gamestate.tick - lastAutosave > 1000:
            # src.gamestate.gamestate.save()
            lastAutosave = src.gamestate.gamestate.tick

        firstRun = False

        # transform and store the keystrokes that accumulated in pygame
        if useTiles:
            import pygame

            for item in pygame.event.get():
                if item.type == pygame.QUIT:
                    src.gamestate.gamestate.save()
                    pygame.quit()
                if not hasattr(item, "unicode"):
                    continue
                key = item.unicode
                if key == "":
                    continue
                if key == "\x10":
                    key = "ctrl p"
                if key == "\x18":
                    key = "ctrl x"
                if key == "\x0f":
                    key = "ctrl o"
                if key == "\x04":
                    key = "ctrl d"
                if key == "\x0b":
                    key = "ctrl k"
                if key == "\x01":
                    key = "ctrl a"
                if key == "\x17":
                    key = "ctrl w"
                if key == "\x1b":
                    key = "esc"
                if key == "\r":
                    key = "enter"
                keyboardListener(key)

        if not src.gamestate.gamestate.mainChar.timeTaken > 1 and tcod:
            getTcodEvents()
            #    #getNetworkedEvents()

        src.gamestate.gamestate.savedThisTurn = False
        src.gamestate.gamestate.waitedForInputThisTurn = False

        """
        profiler = cProfile.Profile()
        profiler.enable()
        """

        startTime = time.time()
        origTick = src.gamestate.gamestate.tick

        hasAutosolveQuest = False
        for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
            if not quest.autoSolve:
                continue
            hasAutosolveQuest = True

        if shadowCharacter:
            while shadowCharacter.macroState["commandKeyQueue"] and shadowCharacter.macroState["commandKeyQueue"][-1][0] == "~":
                renderGameDisplay()
                shadowCharacter.macroState["commandKeyQueue"].pop()

        global continousOperation
        if (
            src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"] and not speed
        ) or runFixedTick or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest or (shadowCharacter and shadowCharacter.macroState["commandKeyQueue"]):
            continousOperation += 1

            if not len(cinematics.cinematicQueue):
                lastAdvance = time.time()
                advanceGame()
                multi_chars = src.gamestate.gamestate.multi_chars

            """
            for char in multi_chars:
                if char.dead:
                    continue
                if not char.container:
                    continue
                # 5/0
                advanceChar(char)
                pass
            """

        if src.gamestate.gamestate.mainChar.timeTaken > 1:
            lastAdvance = time.time()
            advanceGame()
            multi_chars = src.gamestate.gamestate.multi_chars

            for char in multi_chars:
                if char.dead:
                    continue
                if not char.container:
                    continue
                # 5/0
                advanceChar(char)
                pass

        """
        if src.gamestate.gamestate.tick > origTick and not src.gamestate.gamestate.savedThisTurn and not src.gamestate.gamestate.waitedForInputThisTurn and not origTick == 0:
            endTime = time.time()
            tickSpeed = endTime-startTime
            totalTickSpeed += tickSpeed
            numTrackedTicks += 1
            if tickSpeed > 0.01:
                profiler.dump_stats("perfDebug/tick%s"%(origTick,))
                if slowestTickSpeed == None or slowestTickSpeed < tickSpeed:
                    print("new slowest tick")
                    slowestTickSpeed = tickSpeed
                    slowestTick = origTick
                print("tick time %s for %s"%(tickSpeed,origTick,))
                print("slowest tick %s for %s"%(slowestTickSpeed,slowestTick,))
            else:
                print("yay, a fast tick!!")
                print("tick time %s for %s"%(tickSpeed,origTick,))
            print("average tick length on %s ticks: %s"%(numTrackedTicks,(totalTickSpeed/numTrackedTicks),))
        """

        """ HACK
        if not src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"]:
            renderGameDisplay()
        """
        #renderGameDisplay()

        """
        endTime = time.time()
        if endTime-startTime < 0.009999:
            time.sleep(0.01-(endTime-startTime))
        """

    loop.set_alarm_in(0.001, gameLoop)

def clearMessages(char):
    while len(char.messages) > 100:
        char.messages = char.messages[-100:]

skipNextRender = False
lastRender = None
def advanceChar(char,render=True, pull_events = True):
    global skipNextRender

    state = char.macroState

    rerender = True

    global lastRender

    lastLoop = time.time()
    if (char == src.gamestate.gamestate.mainChar) and char.timeTaken > 1 and render:
        renderGameDisplay()
        lastRender = time.time()
    while char.timeTaken < 1:
        if (char == src.gamestate.gamestate.mainChar) and rerender and char.getTerrain():
            #char.getTerrain().animations = []
            #for room in char.getTerrain().rooms:
            #    room.animations = []
            if render:
                """ HACK
                if not src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"]:
                    skipedRenders = 0
                    renderGameDisplay()
                """
                if src.gamestate.gamestate.tick%3 == 0:
                    renderGameDisplay()
            lastRender = time.time()
            rerender = False
        if (char == src.gamestate.gamestate.mainChar):
            if char.dead:
                return
            newInputs = getTcodEvents() if pull_events else None

            if (time.time()-lastRender) > 0.1 and render and not skipNextRender:
                skipNextRender = True

                terrain = char.getTerrain()
                if terrain.animations:
                    skipNextRender = False
                for room in terrain.rooms:
                    if room.animations:
                        skipNextRender = False

                renderGameDisplay()
                lastRender = time.time()

            if newInputs:
                skipNextRender = False

            desiredTime = 0.01
            timeDiff = time.time()-lastLoop
            if timeDiff < desiredTime:
                time.sleep(desiredTime-timeDiff)
            lastLoop = time.time()

        hasAutosolveQuest = False
        for quest in char.getActiveQuests():
            if not quest.autoSolve:
                continue
            hasAutosolveQuest = True

        if char.huntkilling:
            processInput(
                (char.doHuntKill(),["norecord"]),
                 charState=state, noAdvanceGame=True, char=char)
            rerender = True
            skipNextRender = False
        elif char.hasOwnAction > 0:
            for commandChar in char.getOwnAction():
                processInput(
                    (commandChar,["norecord"]),
                     charState=state, noAdvanceGame=True, char=char)
            rerender = True
            skipNextRender = False
        elif state["commandKeyQueue"]:
            if (char == src.gamestate.gamestate.mainChar):
                char.getTerrain().animations = []
                for room in char.getTerrain().rooms:
                    room.animations = []
            key = state["commandKeyQueue"].pop()
            processInput(
                key, charState=state, noAdvanceGame=True, char=char
            )
            rerender = True
            skipNextRender = False
        elif char.autoAdvance:
            char.runCommandString("+")
            char.timeTaken += 1
        elif hasAutosolveQuest:
            rerender = True
            char.runCommandString("+")
            skipNextRender = False
        elif char.autoExpandQuests2 and char.getActiveQuest() and not (char.getActiveQuest().getSolvingCommandString(char)):
            char.getActiveQuest().generateSubquests(char,dryRun=False)
        elif char.autoExpandQuests and char.getActiveQuest() and not (char.getActiveQuest().getSolvingCommandString(char)):
            char.runCommandString("+",nativeKey=True)
        else:
            if (char == src.gamestate.gamestate.mainChar):
                if pull_events and getTcodEvents():
                    skipNextRender = False
            else:
                char.timeTaken = 1

def advanceChar_disabled(char):
    if char.stasis:
        return
    if char.disabled:
        return

    if (
        len(cinematics.cinematicQueue)
        and char != src.gamestate.gamestate.mainChar
    ):
        return

    state = char.macroState

    while char.quests and char.quests[0].completed:
        char.quests.remove(char.quests[0])

    hasAutosolveQuest = False
    for quest in char.getActiveQuests():
        if not quest.autoSolve:
            continue
        hasAutosolveQuest = True

    # do random action
    if not (state["commandKeyQueue"] or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest):
        #char.die(reason="idle")
        #char.startIdling()
        char.runCommandString("100.")

    clearMessages(char)

    if state["commandKeyQueue"] or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest:
        if state["commandKeyQueue"]:
            key = state["commandKeyQueue"][-1]
            while (
                isinstance(key[0], list | tuple)
                or key[0] in ("lagdetection", "lagdetection_")
            ):
                if state["commandKeyQueue"]:
                    key = state["commandKeyQueue"].pop()
                else:
                    key = ("~", [])

        while (state["commandKeyQueue"] or char.huntkilling or char.hasOwnAction or (char == src.gamestate.gamestate.mainChar and not char.dead) or hasAutosolveQuest) and char.timeTaken < 1:

            if char.huntkilling:
                processInput(
                        (char.doHuntKill(),["norecord"]),
                        charState=state, noAdvanceGame=True, char=char)
            elif char.hasOwnAction > 0:
                for commandChar in char.getOwnAction():
                    processInput(
                            (commandChar,["norecord"]),
                            charState=state, noAdvanceGame=True, char=char)
            elif state["commandKeyQueue"]:
                key = state["commandKeyQueue"].pop()
                processInput(
                    key, charState=state, noAdvanceGame=True, char=char
                )
            elif hasAutosolveQuest:
                char.runCommandString("+")
            else:
                if tcod:
                    startTime = time.time()

                    while (not state["commandKeyQueue"]) and char.timeTaken < 1:
                        hasAutosolveQuest = False
                        for quest in char.getActiveQuests():
                            if not quest.autoSolve:
                                continue
                            hasAutosolveQuest = True

                        if (char == src.gamestate.gamestate.mainChar):
                            getTcodEvents()

                            renderGameDisplay()
                            if char.getTerrain():
                                char.getTerrain().lastRender = None

                        else:
                            char.timeTaken = 1
                        #getNetworkedEvents()

                        #if shadowCharacter:
                        #    while shadowCharacter.macroState["commandKeyQueue"] and shadowCharacter.macroState["commandKeyQueue"][-1][0] == "~":
                        #        renderGameDisplay()
                        #        shadowCharacter.macroState["commandKeyQueue"].pop()

                        #    #if not state["commandKeyQueue"] and shadowCharacter.macroState["commandKeyQueue"]:
                        #    #    char.timeTaken += 1
                        #    #    char.runCommandString("~",nativeKey=True)
                        #    #    #renderGameDisplay()

                        #if src.gamestate.gamestate.timedAutoAdvance:
                        #    if time.time() > startTime + src.gamestate.gamestate.timedAutoAdvance:
                        #        char.timeTaken += 1

            hasAutosolveQuest = False
            for quest in char.getActiveQuests():
                if not quest.autoSolve:
                    continue
                hasAutosolveQuest = True

loop = None

s = None
conn = None

HOST = "127.0.0.1"
PORT = 65475

shadowCharacter = None

def getNetworkedEvents():
    global shadowCharacter
    global s
    global conn

    if not s:
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.setblocking(False)
        s.listen()

    if not conn:
        try:
            conn, addr = s.accept()
        except:
            conn = None

    if not conn:
        return

    if not shadowCharacter:
        shadowCharacter = src.characters.Character()
        shadowCharacter.personality["doIdleAction"] = False
        shadowCharacter.personality["autoCounterAttack"] = False
        src.gamestate.gamestate.mainChar.personality["doIdleAction"] = False
        pos = src.gamestate.gamestate.mainChar.getPosition()
        src.gamestate.gamestate.mainChar.container.addCharacter(shadowCharacter,pos[0],pos[1])

    s.setblocking(False)
    conn.setblocking(False)
    try:
        chunkData = conn.recv(1024)
    except:
        return

    if not len(chunkData):
        return

    for data in chunkData.split(b"\n"):
        if not len(data):
            continue

        data = data.decode("utf-8")
        raw = json.loads(data)

        for command in raw["commands"]:
            keyboardListener(command,targetCharacter=shadowCharacter)

def sendNetworkDraw(pseudoDisplay):
    """
    basically a copy of the main loop for networked multiplayer

    Parameters:
        loop: the main loop (urwids main loop)
        user_data: parameter that needs to be there but is not used
    """

    global s
    global conn

    if not s:
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.setblocking(False)
        s.listen()

    if not conn:
        try:
            conn, addr = s.accept()
        except:
            conn = None

    if not conn:
        return

    import json

    #data = conn.recv(1024 * 1024 * 1024)

    info = {"pseudoDisplay":pseudoDisplay}
    info = json.dumps(info)
    data = info.encode("utf-8")
    data = gzip.compress(data)
    seperator = b"\n-*_*-\n"

    if seperator in data:
        raise Exception("seperator in data => hard fuckup")
    conn.sendall(data+seperator)

    return

def handleMultiplayerClients():
    return
    if 1==1:
        realMainChar = src.gamestate.gamestate.mainChar

        if len(multi_chars) > 1:
            src.gamestate.gamestate.mainChar = multi_chars[1]

        if data == b"redraw":
            pass
        else:
            for key in json.loads(data.decode("utf-8")):
                keyboardListener(key)

        canvas = render(src.gamestate.gamestate.mainChar)
        info = {
            "head": ["adsada"],
            "main": [(urwid.AttrSpec("#999", "black"), canvas.getUrwirdCompatible())],
            "footer": ["asdasdasf sf"],
        }
        src.gamestate.gamestate.mainChar = realMainChar

        def serializeUrwid(inData):
            """
            """

            outData = []
            for item in inData:
                if isinstance(item, tuple):
                    outData.append(
                        [
                            "tuple",
                            [item[0].foreground, item[0].background],
                            serializeUrwid(item[1]),
                        ]
                    )
                if isinstance(item, list):
                    outData.append(["list", serializeUrwid(item)])
                if isinstance(item, str):
                    outData.append(["str", item])
            return outData

        info["head"] = serializeUrwid(info["head"])
        info["main"] = serializeUrwid(info["main"])
        info["footer"] = serializeUrwid(info["footer"])

        info = json.dumps(info)
        data = info.encode("utf-8")
        conn.sendall(data)

    loop.set_alarm_in(0.1, handleMultiplayerClients)


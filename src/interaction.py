"""
code for interacation with the user belongs here
bad pattern: logic should be moved somewhere else
"""
# load libraries
import time
import uuid
import json
import random
import cProfile
import collections

# load internal libraries
import src.rooms
import src.items
import src.quests
import src.canvas
import src.saveing
import src.chats
import src.terrains
import config.commandChars as commandChars
import src.cinematics as cinematics
import src.gamestate

################################################################################
#
#        setting up the basic user interaction library
#         bad code: urwid specific code should be somewhere else
#
################################################################################

continousOperation = 0
main = None
frame = None
urwid = None
fixedTicks = False
speed = None
libtcodpy = None

# bad code: should be contained in gamestate
def advanceGame():
    """
    advance the game
    """
    for row in src.gamestate.gamestate.terrainMap:
        for specificTerrain in row:
            specificTerrain.advance()

    for item in src.gamestate.gamestate.extraRoots:
        for character in item.characters:
            character.advance()

    src.gamestate.gamestate.tick += 1


class AbstractedDisplay(object):
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

def playSound(soundName,channelName,loop=False):
    return
    channel = src.interaction.tcodMixer.get_channel(channelName)
    if not channel.busy:
        channel.play(sounds[soundName])

def setUpTcod():
    import tcod as internalTcod
    global tcod
    tcod = internalTcod

    screen_width = 200
    screen_height = 51

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
    tileset = tcod.tileset.load_tilesheet(
        "Acorntileset2.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    """
    tileset =  tcod.tileset.load_truetype_font("./config/font/dejavu-sans-mono-fonts-ttf-2.35/ttf/DejaVuSansMono.ttf",48,24)
    """

    context = tcod.context.new_terminal(
            screen_width,
            screen_height,
            tileset=tileset,
            title="OfMiceAndMechs",
            vsync=True,
                )
    root_console = tcod.Console(screen_width, screen_height, order="F")
    global tcodConsole
    global tcodContext
    tcodConsole = root_console
    tcodContext = context

    root_console.print(x=1,y=1,string="loading game")

    context.present(root_console)

    import tcod.sdl.audio as audio
    import soundfile as sf

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
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/itemDropped.ogg',dtype='float32')
    sounds["itemDropped"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/itemPickedUp.ogg',dtype='float32')
    sounds["itemPickedUp"] = sound_clip
    sound_clip, samplerate = src.interaction.soundloader.read('sounds/machineUsed.ogg',dtype='float32')
    sounds["machineUsed"] = sound_clip

    global tcodAudio
    tcodAudio = audio

    global tcodMixer
    global tcodAudioDevice
    device = src.interaction.tcodAudio.open()
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

footer = None
main = None
header = None

def setUpUrwid():
    """
    initialise console based rendering
    """

    import urwid

    # the containers for the shown text
    urwidHeader = urwid.Text(u"")
    urwidMain = urwid.Text(u"")
    urwidFooter = urwid.Text(u"", align="right")

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
        "oo / öö = furnce",
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

def show_or_exit(key):
    """
    add keystrokes from urwid to the players command queue

    Parameters:
        key: the key pressed
        charState: the state of the char to add the keystroke to
    """

    src.gamestate.gamestate.mainChar.runCommandString((key,),nativeKey=True,addBack=True)

shownStarvationWarning = False

def moveCharacter(direction,char,noAdvanceGame,header,urwid):

    # do inner room movement
    if char.room:
        item = char.room.moveCharacterDirection(char, direction)

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

    # do movement on terrain
    # bad code: these calculation should be done elsewhere
    else:
        if not char.terrain:
            return

        return char.terrain.moveCharacterDirection(char, direction)

def handleCollision(char,charState):
    if charState["itemMarkedLast"] and char.personality["moveItemsOnCollision"]:
        char.runCommandString("kl")
        return
    if charState["itemMarkedLast"] and char.personality["avoidItems"]:
        char.runCommandString(random.choice(("a","w","s","d",)))
        return

def handleActivityKeypress(char, header, main, footer, flags):
    if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
        text = """

press key to select action

* g = run guard mode for 10 ticks
"""
        header.set_text(
            (urwid.AttrSpec("default", "default"), "action menu")
        )
        main.set_text((urwid.AttrSpec("default", "default"), text))
        footer.set_text((urwid.AttrSpec("default", "default"), ""))
        char.specialRender = True

    char.interactionState["runaction"] = {}

def handleActivitySelection(char):
    char.startGuarding(1)
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

            text += """
%s - %s""" % (
                key,
                compressedMacro,
            )

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

                        text += """
    %s - %s""" % (
                            macroName,
                            compressedMacro,
                        )

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "record macro")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                return

            if charState["replay"][-1] in charState["macros"]:
                char.addMessage(
                    "replaying %s: %s"
                    % (
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
            char.timeTaken -= 0.99

def stitchCommands(charState):
    """
    commands = []
    for keyPress in charState["macros"][charState["replay"][-1]]:
        commands.append((keyPress, ["norecord"]))
    charState["commandKeyQueue"] = (
        commands + charState["commandKeyQueue"]
    )
    """
    if not charState["replay"][-1] in charState["macros"]:
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
        or char.interactionState["varActions"]
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

                        text += """
%s - %s""" % (
                            key,
                            compressedMacro,
                        )

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "record macro")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True

            return
        else:
            if "norecord" not in flags:
                charState["macros"][charState["recordingTo"]].append(key)
    return (1,key)

def checkStaggered(char):
    if char.staggered and 1==0: # HACK: disabled staggering
        char.staggered -= 1
        char.addMessage("you are still staggered")
        return
    return (1,)

def checkRecording(key,char,charState,main,header,footer,urwid,flags):
    return handleRecordingChar(key,char,charState,main,header,footer,urwid,flags)

def handlePriorityActions(char,charState,flags,key,main,header,footer,urwid):
    char.specialRender = False

    if not checkStaggered(char):
        return

    if charState["recording"]:
        result = checkRecording(key,char,charState,main,header,footer,urwid,flags)
        if not (result and result[0]):
            return
        key = result[1]

    if (
        charState["submenue"]
        and charState["submenue"].stealAllKeys
        and (key not in ("|", ">", "<") and not charState["submenue"].escape)
    ):

        # let the submenu handle the keystroke
        lastSubmenu = charState["submenue"]
        noRender = True
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            noRender = False
        done = charState["submenue"].handleKey(key, noRender=noRender, character=char)

        if not lastSubmenu == charState["submenue"]:
            charState["submenue"].handleKey("~", noRender=noRender, character=char)
            done = False

        # reset rendering flags
        if done:
            charState["submenue"] = None
            char.specialRender = False
            doAdvanceGame = False
        key = commandChars.ignore

    if key in ("|",):
        char.interactionState["stateChange"] = True
        return

    if "stateChange" in char.interactionState and char.interactionState["stateChange"]:
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
        return

    if char.doStackPop:
        if key in char.registers:
            char.registers[key].pop()
            if not len(char.registers[key]):
                del char.registers[key]
        char.doStackPop = False
        return
    if char.doStackPush:
        if key not in char.registers:
            char.registers[key] = []
        char.registers[key].append(0)
        char.doStackPush = False
        return

    if "fireDirection" in char.interactionState:
        char.doRangedAttack(direction=key)
        del char.interactionState["fireDirection"]
        return

    if "runaction" in char.interactionState:
        handleActivitySelection(char)
        return

    if "advancedInteraction" in char.interactionState:
        if not char.container:
            del char.interactionState["advancedInteraction"]
            return
        if key == "w":
            items = char.container.getItemByPosition(
                (char.xPosition, char.yPosition - 1, char.zPosition)
            )
            if items:
                items[0].apply(char)
        elif key == "s":
            items = char.container.getItemByPosition(
                (char.xPosition, char.yPosition + 1, char.zPosition)
            )
            if items:
                items[0].apply(char)
        elif key == "d":
            items = char.container.getItemByPosition(
                (char.xPosition + 1, char.yPosition, char.zPosition)
            )
            if items:
                items[0].apply(char)
        elif key == "a":
            items = char.container.getItemByPosition(
                (char.xPosition - 1, char.yPosition, char.zPosition)
            )
            if items:
                items[0].apply(char)
        elif key == ".":
            items = char.container.getItemByPosition(
                (char.xPosition, char.yPosition, char.zPosition)
            )
            if items:
                items[0].apply(char)
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
                if isinstance(item, src.items.itemMap["GooFlask"]):
                    if item.uses > 0:
                        item.apply(character)
                        break
                if (
                    isinstance(item, src.items.itemMap["Bloom"])
                    or isinstance(item, src.items.itemMap["BioMass"])
                    or isinstance(item, src.items.itemMap["PressCake"])
                    or isinstance(item, src.items.itemMap["SickBloom"])
                ):
                    item.apply(character)
                    character.inventory.remove(item)
                    break
                if isinstance(item, src.items.itemMap["Corpse"]):
                    item.apply(character)
                    break
        del char.interactionState["advancedInteraction"]
        return

    if "advancedPickup" in char.interactionState:
        if len(char.inventory) >= 10:
            char.addMessage("you cannot carry more items")
        elif not char.container:
            pass
        else:
            if key == "w":
                items = char.container.getItemByPosition(
                    (char.xPosition, char.yPosition - 1, char.zPosition)
                )
                if items:
                    item = items[0]
                    item.pickUp(char)
            elif key == "s":
                items = char.container.getItemByPosition(
                    (char.xPosition, char.yPosition + 1, char.zPosition)
                )
                if items:
                    item = items[0]
                    item.pickUp(char)
            elif key == "d":
                items = char.container.getItemByPosition(
                    (char.xPosition + 1, char.yPosition, char.zPosition)
                )
                if items:
                    item = items[0]
                    item.pickUp(char)
            elif key == "a":
                items = char.container.getItemByPosition(
                    (char.xPosition - 1, char.yPosition, char.zPosition)
                )
                if items:
                    item = items[0]
                    item.pickUp(char)
            elif key == ".":
                items = char.container.getItemByPosition(
                    (char.xPosition, char.yPosition, char.zPosition)
                )
                if items:
                    item = items[0]
                    item.pickUp(char)
        del char.interactionState["advancedPickup"]
        return

    if "functionCall" in char.interactionState:
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
        char.timeTaken -= 0.99
        return

    if "advancedDrop" in char.interactionState:
        if key == "w":
            if char.inventory:
                char.drop(
                    char.inventory[-1],
                    (char.xPosition, char.yPosition - 1, char.zPosition),
                )
        elif key == "s":
            if char.inventory:
                char.drop(
                    char.inventory[-1],
                    (char.xPosition, char.yPosition + 1, char.zPosition),
                )
        elif key == "d":
            if char.inventory:
                char.drop(
                    char.inventory[-1],
                    (char.xPosition + 1, char.yPosition, char.zPosition),
                )
        elif key == "a":
            if char.inventory:
                char.drop(
                    char.inventory[-1],
                    (char.xPosition - 1, char.yPosition, char.zPosition),
                )
        elif key == ".":
            if char.inventory:
                char.drop(
                    char.inventory[-1], (char.xPosition, char.yPosition, char.zPosition)
                )
        del char.interactionState["advancedDrop"]
        return

    if "enumerateState" not in char.interactionState:
        char.interactionState["enumerateState"] = []

    if char.interactionState["enumerateState"]:

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
            char.timeTaken -= 0.99
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
                    "found in direction %sa %ss %sd %sw"
                    % (
                        char.registers["a"][-1],
                        char.registers["s"][-1],
                        char.registers["d"][-1],
                        char.registers["w"][-1],
                    )
                )
                char.interactionState["enumerateState"].pop()
                char.timeTaken -= 0.99
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
                char.timeTaken -= 0.99
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
                char.timeTaken -= 0.99
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

            if "roomTile" in char.interactionState["enumerateState"][-1]["target"]:
                if char.terrain:
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
                char.timeTaken -= 0.99
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
                + " found in direction %sa %ss %sd %sw"
                % (
                    char.registers["a"][-1],
                    char.registers["s"][-1],
                    char.registers["d"][-1],
                    char.registers["w"][-1],
                )
            )
            char.interactionState["enumerateState"].pop()
            return

        char.interactionState["enumerateState"].pop()
        char.timeTaken -= 0.99
        return

    if key == "esc":
        charState["replay"] = []

    if "varActions" not in char.interactionState:
        char.interactionState["varActions"] = []

    if key == "$":
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            text = """

press key for register to modify or press = to load value from a register

current registers:

"""
            for itemKey, value in char.registers.items():
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(item))
                text += """
%s - %s""" % (
                    itemKey,
                    ",".join(convertedValues),
                )

            header.set_text((urwid.AttrSpec("default", "default"), "registers"))
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

        char.interactionState["varActions"].append({"outOperator": None})
        char.timeTaken -= 0.99
        return

    if char.interactionState["varActions"]:

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

        if lastVarAction["outOperator"] == True:
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
                        text += """
%s - %s""" % (
                            key,
                            ",".join(convertedValues),
                        )

                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "reading registers")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                char.timeTaken -= 0.99
                return

            else:
                if register:
                    key = register + key

                def getValue():
                    if key not in char.registers:
                        char.addMessage("no value in register using %s" % (key,))
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
                char.timeTaken -= 0.99
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
                            text += """
%s - %s""" % (
                                key,
                                ",".join(convertedValues),
                            )

                        header.set_text(
                            (urwid.AttrSpec("default", "default"), "registers")
                        )
                        main.set_text((urwid.AttrSpec("default", "default"), text))
                        footer.set_text((urwid.AttrSpec("default", "default"), ""))
                        char.specialRender = True
                    char.timeTaken -= 0.99
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
* * - mulitply register
* % - apply modulo to register

"""
                        header.set_text(
                            (urwid.AttrSpec("default", "default"), "reading registers")
                        )
                        main.set_text((urwid.AttrSpec("default", "default"), text))
                        footer.set_text((urwid.AttrSpec("default", "default"), ""))
                        char.specialRender = True
                    char.timeTaken -= 0.99
                    return
            action = lastVarAction["action"]
            if action is None:
                lastVarAction["action"] = key

                if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                    text = """

input value for this operation ($%s%s)

type number or load value from register

""" % (
                        register,
                        action,
                    )
                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "reading registers")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                char.timeTaken -= 0.99
                return
            if key in "0123456789":
                lastVarAction["number"] += key

                if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                    text = """

input value for this operation ($%s%s%s)

type number

press any other key to finish

""" % (
                        register,
                        action,
                        lastVarAction["number"],
                    )
                    header.set_text(
                        (urwid.AttrSpec("default", "default"), "reading registers")
                    )
                    main.set_text((urwid.AttrSpec("default", "default"), text))
                    footer.set_text((urwid.AttrSpec("default", "default"), ""))
                    char.specialRender = True
                char.timeTaken -= 0.99
                return

            if action == "=":
                if register not in char.registers:
                    char.registers[register] = [0]
                try:
                    char.registers[register][-1] = int(lastVarAction["number"])
                except:
                    pass
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
            char.timeTaken -= 0.99
            return

    if "ifCondition" not in char.interactionState:
        char.interactionState["ifCondition"] = []
    if "ifParam1" not in char.interactionState:
        char.interactionState["ifParam1"] = []
    if "ifParam2" not in char.interactionState:
        char.interactionState["ifParam2"] = []
    if key in ("%",):
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

        return

    if len(char.interactionState["ifCondition"]) and key not in (
        "%",
        "lagdetection",
        "lagdetection_",
    ):
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

                            text += """
%s - %s""" % (
                                key,
                                compressedMacro,
                            )

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

                        text += """
%s - %s""" % (
                            key,
                            compressedMacro,
                        )

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
                                and not character.faction == char.faction
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
        return

    if key in "0123456789":
        if charState["number"] is None:
            charState["number"] = ""
        charState["number"] += key
        key = commandChars.ignore
        char.timeTaken -= 0.99
        return

    if key in ("%",):
        charState["loop"].append(2)
        return

    if charState["loop"] and key not in (
        "lagdetection",
        "lagdetection_",
        commandChars.ignore,
        "_",
        "~",
    ):
        if not charState["replay"]:
            char.runCommandString("§"+key)
            charState["loop"].pop()
        else:
            char.runCommandString("§_"+key)
            charState["loop"].pop()

    if key in ("-",) and not char.interactionState["varActions"]:
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

                    text += """
%s - %s""" % (
                        key,
                        compressedMacro,
                    )

                header.set_text((urwid.AttrSpec("default", "default"), "record macro"))
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            charState["recording"] = True
            return
        else:
            charState["recording"] = False
            if charState["recordingTo"]:
                if charState["recordingTo"] in charState["macros"]:
                    if charState["macros"][charState["recordingTo"]]:
                        char.addMessage(
                            "recorded: %s to %s"
                            % (
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

    if charState["replay"] and key not in (
        "lagdetection",
        "lagdetection_",
        "~",
    ):
        handleMacroReplayChar(key,char,charState,main,header,footer,urwid,flags)
        return

    if key in ("_",):
        handleStartMacroReplayChar(key,char,charState,main,header,footer,urwid,flags)
        return

    if charState["number"] and key not in (
        commandChars.ignore,
        "lagdetection",
        "lagdetection_",
    ):
        num = int(charState["number"])
        charState["number"] = None

        charState["doNumber"] = True

        counter = 0
        commands = ""
        while counter < num:
            commands += key
            counter += 1
        char.runCommandString(commands)

        charState["doNumber"] = False
        char.timeTaken -= 0.99
        return

    # save and quit
    if key in (commandChars.quit_normal, commandChars.quit_instant):
        if hasattr(urwid,"ExitMainLoop"):
            raise urwid.ExitMainLoop()
        else:
            raise SystemExit()

    """
    if key in ('S',):
        src.gamestate.gamestate.save()
        return
    """

    if key in ("<",):
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            text = """

type key for the register to pop.

current registers

"""
            for key, value in char.registers.items():
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(item))
                text += """
%s - %s""" % (
                    key,
                    ",".join(convertedValues),
                )

            header.set_text((urwid.AttrSpec("default", "default"), "popping registers"))
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

        char.doStackPop = True
        return
    if key in (">",):
        if src.gamestate.gamestate.mainChar == char and "norecord" in flags:
            text = """

type key for the register to push.

current registers

"""
            for key, value in char.registers.items():
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(item))
                text += """
%s - %s""" % (
                    key,
                    ",".join(convertedValues),
                )

            header.set_text((urwid.AttrSpec("default", "default"), "pushing registers"))
            main.set_text((urwid.AttrSpec("default", "default"), text))
            footer.set_text((urwid.AttrSpec("default", "default"), ""))
            char.specialRender = True

        char.doStackPush = True
        return
    return (1,key)

def handleNoContextKeystroke(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame):
    if key in ("u",):
        char.setInterrupt = True
        return

    if key in ("ESC","lESC",):
        if char.rememberedMenu:
            menu = char.rememberedMenu.pop()
            char.macroState["submenue"] = menu
            char.macroState["submenue"].handleKey("~", noRender=False, character=char)
            char.specialRender = True
        return
    if key in ("rESC",):
        if char.rememberedMenu2:
            menu = char.rememberedMenu2.pop()
            char.macroState["submenue"] = menu
            char.macroState["submenue"].handleKey("~", noRender=False, character=char)
            char.specialRender = True
        return
    if key in ("esc",):
        options = [("save", "save"), ("quit", "save and quit"), ("actions", "actions"),
                   ("macros", "macros"), ("help", "help"), ("keybinding", "keybinding"),
                   ("changeFaction", "changeFaction"),
                   ("change personality settings", "change personality settings")]
        submenu = SelectionMenu("What do you want to do?", options)
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
                    submenu3 = InputMenu("input value")
                    char.macroState["submenue"] = submenu3
                    char.macroState["submenue"].followUp = setValue
                    return

                options = []
                for (key, value) in char.personality.items():
                    options.append((key, "%s: %s" % (key, value)))
                submenu2 = SelectionMenu("select personality setting", options)
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
                if hasattr(urwid,"ExitMainLoop"):
                    raise urwid.ExitMainLoop()
                else:
                    raise SystemExit()
                return
            elif selection == "actions":
                pass
            elif selection == "macros":
                pass
            elif selection == "changeFaction":
                if char.faction == "player":
                    char.faction = "monster"
                else:
                    char.faction = "player"
                pass
            elif selection == "help":
                charState["submenue"] = HelpMenu()
            elif selection == "keybinding":
                pass

        char.macroState["submenue"].followUp = trigger
        key = "."

    if key in ("y",):
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
        char.timeTaken -= 0.99
        return
    if key in ("o",) and 1==0:
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
        char.timeTaken -= 0.99
        return

    # handle cinematics
    if src.gamestate.gamestate.mainChar == char and len(cinematics.cinematicQueue):
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            char.specialRender = True

        # get current cinematic
        cinematic = cinematics.cinematicQueue[0]
        char.timeTaken -= 0.99

        # allow to quit even within a cutscene
        if key in (commandChars.quit_normal, commandChars.quit_instant):
            src.gamestate.gamestate.save()
            # bad code: directly calls urwid
            raise urwid.ExitMainLoop()

        # skip the cinematic if requested
        elif (
            key
            in (
                commandChars.pause,
                commandChars.advance,
                commandChars.autoAdvance,
                commandChars.redraw,
                "enter",
            )
            and cinematic.skipable
        ):
            cinematic.abort()
            cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
            if loop:
                loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
            else:
                callShow_or_exit(None, commandChars.ignore)
            return

        # advance the cutscene
        else:
            if not cinematic.advance():
                return
            if not cinematic.background:
                # bad code: changing the key mid function
                key = commandChars.ignore

    # set the flag to advance the game
    doAdvanceGame = True
    if key in (commandChars.ignore,):
        doAdvanceGame = False

    # invalidate input for unconscious char
    if char.unconcious:
        key = commandChars.wait

    # show a few rounds after death and exit
    if char.dead:
        if not ticksSinceDeath:
            ticksSinceDeath = src.gamestate.gamestate.tick
        key = commandChars.wait
        if src.gamestate.gamestate.tick == ticksSinceDeath + 5:
            char.clearCommandString()
            char.macroState["submenue"] = TextMenu(
                "You died. press ctrl-c and reload to start from last save"
            )
            # destroy the gamestate
            # bad pattern: should not always destroy gamestate
            # saveFile = open("gamestate/gamestate.json","w")
            # saveFile.write("you lost")
            # saveFile.close()
            # raise urwid.ExitMainLoop()
            pass

    # call callback if key was overwritten
    if "stealKey" in charState and key in charState["stealKey"]:
        charState["stealKey"][key]()

    # handle the keystroke for a char on the map
    else:
        # open the debug menue
        if key in ("´",):
            if debug:
                charState["submenue"] = DebugMenu()
            else:
                char.addMessage("debug not enabled")

        # destroy save and quit
        if key in (commandChars.quit_delete,):
            saveFile = open("gamestate/gamestate.json", "w")
            saveFile.write("reset")
            saveFile.close()
            raise urwid.ExitMainLoop()

        # kill one of the autoadvance keystrokes
        # bad pattern: doesn't actually pause
        if key in (commandChars.pause,):
            charState["ignoreNextAutomated"] = True
            doAdvanceGame = False

        """
        move the player into a direction
        bad code: huge inline function + player vs. npc movement should use same code
        """

        # move the player
        if key in (commandChars.move_north, "up"):
            charState["itemMarkedLast"] = moveCharacter("north",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
                return
        if key in (commandChars.move_south, "down"):
            charState["itemMarkedLast"] = moveCharacter("south",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
                return
        if key in (commandChars.move_east, "right"):
            charState["itemMarkedLast"] = moveCharacter("east",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
                return
        if key in (commandChars.move_west, "left"):
            charState["itemMarkedLast"] = moveCharacter("west",char,noAdvanceGame,header,urwid)
            if charState["itemMarkedLast"]:
                handleCollision(char,charState)
                return

        # move the player
        if key in (
            "W",
            "S",
            "D",
            "A",
        ):

            if isinstance(char.container,src.rooms.Room):
                charPos = char.container.getPosition()
            else:
                charPos = (char.xPosition//15,char.yPosition//15,0)

            if key in ("W",):
                newPos = (charPos[0],charPos[1]-1,charPos[2])
            if key in ("S",):
                newPos = (charPos[0],charPos[1]+1,charPos[2])
            if key in ("A",):
                newPos = (charPos[0]-1,charPos[1],charPos[2])
            if key in ("D",):
                newPos = (charPos[0]+1,charPos[1],charPos[2])

            quest = src.quests.GoToTile(targetPosition=newPos,paranoid=True)
            quest.autoSolve = True
            quest.assignToCharacter(char)
            quest.activate()

            char.quests.insert(0,quest)

        # murder the next available character
        # bad pattern: player should be able to select whom to kill if there are multiple targets
        if key in ("M",):
            if char.combatMode is None:
                char.combatMode = "agressive"
            elif char.combatMode == "agressive":
                char.combatMode = "defensive"
            else:
                char.combatMode = None
            char.addMessage("switched combatMode to: %s" % (char.combatMode,))
        if key in (commandChars.attack,):
            if (
                "NaiveMurderQuest" not in char.solvers and not char.godMode
            ):  # disabled
                char.addMessage("you do not have the nessecary solver yet (murder)")
            else:
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
                        not char.combatMode == "agressive"
                        and enemy.faction == char.faction
                    ):
                        continue
                    if (enemy.xPosition, enemy.yPosition) not in adjascentFields:
                        continue
                    if isinstance(char, src.characters.Monster) and char.phase == 4:
                        char.addMessage("entered stage 5")
                        char.enterPhase5()
                    char.attack(enemy)
                    break

        # activate an item
        if key in ("c",):
            if "NaiveActivateQuest" not in char.solvers and not char.godMode:
                char.addMessage(
                    "you do not have the nessecary solver yet (activate)"
                )
            else:
                # activate the marked item
                if charState["itemMarkedLast"]:
                    if not charState["itemMarkedLast"].container:
                        if charState["itemMarkedLast"].room:
                            charState["itemMarkedLast"].container = charState[
                                "itemMarkedLast"
                            ].room
                        elif charState["itemMarkedLast"].terrain:
                            charState["itemMarkedLast"].container = charState[
                                "itemMarkedLast"
                            ].terrain

                    charState["itemMarkedLast"].configure(char)

                # activate an item on floor
                else:
                    # for item in char.container.itemsOnFloor:
                    #    if item.xPosition == char.xPosition and item.yPosition == char.yPosition:
                    #        item.apply(char)
                    #        break
                    entry = char.container.getItemByPosition(
                        (char.xPosition, char.yPosition, char.zPosition)
                    )
                    if len(entry):
                        entry[0].configure(char)

        # activate an item
        if key in (commandChars.activate,):
            if "NaiveActivateQuest" not in char.solvers and not char.godMode:
                char.addMessage(
                    "you do not have the nessecary solver yet (activate)"
                )
            else:
                # activate the marked item
                if charState["itemMarkedLast"]:
                    if not charState["itemMarkedLast"].container:
                        return

                    charState["itemMarkedLast"].apply(char)

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
                    ):
                        entry = char.container.getItemByPosition(
                            (char.xPosition, char.yPosition, char.zPosition)
                        )

                        if entry:
                            entry[0].apply(char)

        # examine an item
        if key in (commandChars.examine,):
            if "ExamineQuest" not in char.solvers and not char.godMode:
                char.addMessage(
                    "you do not have the nessecary solver yet (examine)"
                )
            else:
                # examine the marked item
                if charState["itemMarkedLast"]:
                    char.examine(charState["itemMarkedLast"])

                # examine an item on floor
                else:
                    itemList = char.container.getItemByPosition(
                        (char.xPosition, char.yPosition, char.zPosition)
                    )
                    for item in itemList:
                        char.examine(item)
                        break

        # drop first item from inventory
        # bad pattern: the user has to have the choice for what item to drop
        if key in (commandChars.drop,):
            if "NaiveDropQuest" not in char.solvers and not char.godMode:
                char.addMessage("you do not have the nessecary solver yet (drop)")
            else:
                if len(char.inventory):
                    char.drop(char.inventory[-1])

        # drink from the first available item in inventory
        # bad pattern: the user has to have the choice from what item to drink from
        # bad code: drinking should happen in character
        if key in ("J",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for the advanced interaction

* w = activate north
* a = activate west
* s = activate east
* d = activate south
* . = activate item on floor
* f = eat food
* j = activate job order

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced activate")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedInteraction"] = {}
            return

        if key in ("g",):
            handleActivityKeypress(char, header, main, footer, flags)
            return

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
            return

        if key in ("K",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for advanced pickup

* w = pick up north
* a = pick up west
* s = pick up east
* d = pick up south
* . = pick item on floor

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced pick up")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedPickup"] = {}
            return

        if key in ("L",):
            if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
                text = """

press key for advanced drop

* w = drop north
* a = drop west
* s = drop east
* d = drop south
* . = drop on floor

"""

                header.set_text(
                    (urwid.AttrSpec("default", "default"), "advanced drop")
                )
                main.set_text((urwid.AttrSpec("default", "default"), text))
                footer.set_text((urwid.AttrSpec("default", "default"), ""))
                char.specialRender = True

            char.interactionState["advancedDrop"] = {}
            return

        if key in ("#",):
            activeQuest = char.getActiveQuest()
            if activeQuest:
                activeQuest.reroll()
            return


        # pick up items
        # bad code: picking up should happen in character
        if key in (commandChars.pickUp,):
            if len(char.inventory) >= 10:
                char.addMessage("you cannot carry more items")
            else:
                item = charState["itemMarkedLast"]

                if not item:
                    itemList = char.container.getItemByPosition(
                        (char.xPosition, char.yPosition, char.zPosition)
                    )

                    if len(itemList):
                        item = itemList[0]

                if not item:
                    char.addMessage("no item to pick up found")
                    return

                item.pickUp(char)

        # open chat partner selection
        if key in (commandChars.hail,):
            charState["submenue"] = ChatPartnerselection()

        if key in ("r",):
            if char.room:
                charState["submenue"] = RoomMenu(char.room)

        # do automated movement for the main character
        if key in (commandChars.advance, commandChars.autoAdvance):
            char.showThinking = True
            if len(char.quests):
                charState["lastMoveAutomated"] = True
                if not char.automated:
                    char.runCommandString("~")
                char.applysolver()
            else:
                pass

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
        charState["submenue"] = QuestMenu()

    # open help menu
    if key in (commandChars.show_help,"z"):
        charState["submenue"] = HelpMenu()
        char.changed("openedHelp")

    # open inventory
    if key in (commandChars.show_inventory,):
        charState["submenue"] = InventoryMenu(char)

    # open the menu for giving quests
    if key in (commandChars.show_quests_detailed,):
        charState["submenue"] = AdvancedQuestMenu(char)

    # open the character information
    if key in (commandChars.show_characterInfo,"v",):
        charState["submenue"] = CharacterInfoMenu(char=char)

    # open the character information
    if key in (commandChars.show_characterInfo,"t",):
        charState["submenue"] = ChangeViewsMenu()

    # open the character information
    if key in ("x",):
        charState["submenue"] = MessagesMenu(char=char)

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

    if char.dead:
        return

    char.timeTaken += 1

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

    priorityActionResult = handlePriorityActions(char,charState,flags,key,main,header,footer,urwid)
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
    if key not in ignoreList:
        if lastLagDetection < time.time() - 0.4:
            pass
            # return

    # repeat autoadvance keystrokes
    # bad code: keystrokes are abused here, a timer would be more appropriate
    if key in (commandChars.autoAdvance,):
        if not charState["ignoreNextAutomated"]:
            char.runCommandString(commandChars.autoAdvance)
        else:
            charState["ignoreNextAutomated"] = False

    # handle a keystroke while on map or in cinematic
    if not charState["submenue"]:
        result = handleNoContextKeystroke(char,charState,flags,key,main,header,footer,urwid,noAdvanceGame)
        if not (result and result[0] == 1):
            return
        key = result[1]

    # render submenus
    if charState["submenue"]:
        char.timeTaken -= 0.99

        # set flag to not render the game
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            char.specialRender = True

        noRender = True
        if src.gamestate.gamestate.mainChar == char and "norecord" not in flags:
            noRender = False

        # let the submenu handle the keystroke
        lastSubmenu = charState["submenue"]
        done = charState["submenue"].handleKey(key, noRender=noRender, character=char)

        if not lastSubmenu == charState["submenue"]:
            charState["submenue"].handleKey("~", noRender=noRender, character=char)
            done = False

        # reset rendering flags
        if done:
            charState["submenue"] = None
            char.specialRender = False
            doAdvanceGame = False

    if charState["replay"] or charState["doNumber"]:
        text = ""
        for cmd in reversed(charState["commandKeyQueue"]):
            item = cmd[0]
            if (
                isinstance(item, list)
                or isinstance(item, tuple)
                or item in ("lagdetection", "lagdetection_")
            ):
                continue
            text += str(cmd[0])
        footer.set_text((urwid.AttrSpec("default", "default"), text))




# bad code: there is redundant code from the specific submenus that should be put here
# bad code: there is spcific code from the selection submenu that should NOT be here
class SubMenu(src.saveing.Saveable):
    """
    The base class for submenus offering selections
    """

    def __init__(self, default=None, targetParamName="selection"):
        """
        set up basic state

        Parameters:
            default: the default selection
            targetParamName: name of the parameter the selection should be stored in
        """

        self.stealAllKeys = False
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.footerText = "press w / s to move selection up / down, press enter / j / k to select, press esc to exit"
        self.followUp = None
        self.done = False

        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        self.default = default
        self.targetParamName = targetParamName
        super().__init__()
        self.attributesToStore.extend(
            [
                "state",
                "selectionIndex",
                "persistentText",
                "footerText",
                "type",
                "query",
                "lockOptions",
                "selection",
            ]
        )
        self.callbacksToStore.extend(["followUp"])
        self.id = str(random.random())

        self.escape = False

    def getQuestMarkersTile(self, character):
        return []

    def setState(self, state):
        """
        set internal state from state dictionary
        
        Parameters:
            state: the state to set
        """

        super().setState(state)

        # load options
        if "options" in state:
            if state["options"] is None:
                self.options = None
            else:
                newOptions = collections.OrderedDict()
                for option in state["options"]:
                    newOptions[option[0]] = option[1]
                self.options = newOptions
        if "niceOptions" in state:
            if state["niceOptions"] is None:
                self.niceOptions = None
            else:
                newNiceOptions = collections.OrderedDict()
                for option in state["niceOptions"]:
                    newNiceOptions[option[0]] = option[1]
                self.niceOptions = newNiceOptions

    def getState(self):
        """
        get state in semi-serialised form

        Returns:
            the state
        """

        state = super().getState()

        # store options
        if self.options is None:
            serialisedOptions = None
        else:
            serialisedOptions = []
            for k, v in self.options.items():
                serialisedOptions.append((k, str(v)))
        state["options"] = serialisedOptions
        if self.niceOptions is None:
            serialisedOptions = None
        else:
            serialisedOptions = []
            for k, v in self.niceOptions.items():
                serialisedOptions.append((k, str(v)))
        state["niceOptions"] = serialisedOptions

        return state

    def setOptions(self, query, options):
        """
        set the options to select from

        Parameters:
            query: the text shown for the selection
            options: the options to choose from
        """

        # convert options to ordered dict

        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        counter = 1
        for option in options:
            self.options[str(counter)] = option[0]
            self.niceOptions[str(counter)] = option[1]
            counter += 1

        # set related state
        self.query = query
        self.selectionIndex = 1
        self.lockOptions = True
        self.selection = None

    def getSelection(self):
        """
        get the selected item
        """

        return self.selection

    def handleKey(self, key, noRender=False, character=None):
        """
        show the options and allow the user to select one

        Parameters:
            key: the key pressed
            noRender: flag for skipping the rendering
        Returns:
            returns True when done
        """

        if not self.options:
            self.done = True
            return True
        if self.done:
            return True

        # exit submenu
        if key == "esc":
            return True

        if key == "a":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            while counter < len(oldOptions):
                self.options[str(counter)] = oldOptions[str(counter + 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter + 1)]
                counter += 1
            self.options[str(counter)] = oldOptions[str(1)]
            self.niceOptions[str(counter)] = oldNiceOptions[str(1)]

        if key == "d":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            self.options[str(counter)] = oldOptions[str(len(oldOptions))]
            self.niceOptions[str(counter)] = oldNiceOptions[str(len(oldOptions))]
            counter = 2
            while counter < len(oldOptions) + 1:
                self.options[str(counter)] = oldOptions[str(counter - 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter - 1)]
                counter += 1

        if key in (commandChars.autoAdvance, commandChars.advance):
            if self.default is not None:
                self.selection = self.default
            else:
                self.selection = list(self.options.values())[0]
            self.options = None
            if self.followUp:
                self.followUp()
            return True

        # show question
        out = "\n"
        out += self.query + "\n"

        # handle the selection of options
        if not self.lockOptions:
            # change the marked option
            if key in (
                "w",
                "up",
            ):
                self.selectionIndex -= 1
                if self.selectionIndex == 0:
                    self.selectionIndex = len(self.options)
            if key in (
                "s",
                "down",
            ):
                self.selectionIndex += 1
                if self.selectionIndex > len(self.options):
                    self.selectionIndex = 1
            # select the marked option
            if key in ["enter", "j", "k", "right"]:
                # bad code: transforming the key to the shortcut is needlessly complicated
                if len(self.options.items()):
                    key = list(self.options.items())[self.selectionIndex - 1][0]
                else:
                    self.selection = None
                    self.done = True
                    return True

            # select option by shortcut
            if key in self.options:
                self.selection = self.options[key]
                self.options = None
                if self.followUp:
                    self.callIndirect(self.followUp,extraParams={self.targetParamName:self.selection})
                return True
        else:
            self.lockOptions = False

        if not noRender:
            # render the options
            counter = 0
            for k, v in self.niceOptions.items():
                counter += 1
                if counter == self.selectionIndex:
                    out += " -> " + str(v) + "\n"
                else:
                    out += "    " + str(v) + "\n"

            # show the rendered options
            # bad code: urwid specific code
            main.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    self.persistentText + "\n\n" + out,
                )
            )

        return False

    # bad code: should either be used everywhere or be removed
    # bad code: urwid specific code
    def set_text(self, text):
        """
        set text in urwid

        Parameters:
            text: the text to set
        """

        main.set_text((urwid.AttrSpec("default", "default"), text))

# bad code: this does nothing the Submenu doesn't do
class ListActionMenu(SubMenu):
    """
    does a simple selection and terminates
    """

    def __init__(self, options, actions, text="", default=None, targetParamName="selection"):
        """
        set up the selection

        Parameters:
            text: the text to show next to the selection
            options: the options to select from
            default: the default value
            targetParamName: name of the parameter the selection should be stored in
        """

        self.type = "ListActionMenu"
        super().__init__(default=default,targetParamName=targetParamName)
        self.setOptions(text, options)
        self.actions = actions

    def handleKey(self, key, noRender=False, character = None):
        """
        handles a keypress

        Parameters:
            key: the key pressed
            noRender: flag for skipping rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            self.selection = None
            if self.followUp:
                self.callIndirect(self.followUp)
            return True
        if not noRender:
            header.set_text("")

        if key == "a":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            while counter < len(oldOptions):
                self.options[str(counter)] = oldOptions[str(counter + 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter + 1)]
                counter += 1
            self.options[str(counter)] = oldOptions[str(1)]
            self.niceOptions[str(counter)] = oldNiceOptions[str(1)]

        if key == "d":
            # convert options to ordered dict
            oldOptions = self.options
            oldNiceOptions = self.niceOptions

            self.options = collections.OrderedDict()
            self.niceOptions = collections.OrderedDict()
            counter = 1
            self.options[str(counter)] = oldOptions[str(len(oldOptions))]
            self.niceOptions[str(counter)] = oldNiceOptions[str(len(oldOptions))]
            counter = 2
            while counter < len(oldOptions) + 1:
                self.options[str(counter)] = oldOptions[str(counter - 1)]
                self.niceOptions[str(counter)] = oldNiceOptions[str(counter - 1)]
                counter += 1

        if key in (commandChars.autoAdvance, commandChars.advance):
            if self.default is not None:
                self.selection = self.default
            else:
                self.selection = list(self.options.values())[0]
            self.options = None
            if self.followUp:
                self.followUp()
            return True

        # show question
        out = "\n"
        out += self.query + "\n"

        # change the marked option
        if key in (
            "w",
            "up",
        ):
            self.selectionIndex -= 1
            if self.selectionIndex == 0:
                self.selectionIndex = len(self.options)
        if key in (
            "s",
            "down",
        ):
            self.selectionIndex += 1
            if self.selectionIndex > len(self.options):
                self.selectionIndex = 1
        # select the marked option
        if key in ["enter", "j", "k", "right"]:
            key = "default"
        
        if key in self.actions:
            option = list(self.options.items())[self.selectionIndex - 1][1]
            print("running the call")
            callback = self.actions[key]["callback"]
            if not callback.get("params"):
                callback["params"] = {}
            self.callIndirect(callback,extraParams={self.targetParamName:option})
            print(callback)
            print("ran the call")
            return True

        if not noRender:
            # render the options
            counter = 0
            for k, v in self.niceOptions.items():
                counter += 1
                if counter == self.selectionIndex:
                    out += str(k) + " ->" + str(v) + "\n"
                else:
                    out += str(k) + " - " + str(v) + "\n"

            # show the rendered options
            # bad code: urwid specific code
            main.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    self.persistentText + "\n\n" + out,
                )
            )

        return False

# bad code: this does nothing the Submenu doesn't do
class SelectionMenu(SubMenu):
    """
    does a simple selection and terminates
    """

    def __init__(self, text="", options=None, default=None, targetParamName="selection"):
        """
        set up the selection

        Parameters:
            text: the text to show next to the selection
            options: the options to select from
            default: the default value
            targetParamName: name of the parameter the selection should be stored in
        """

        if not options:
            options = []

        self.type = "SelectionMenu"
        super().__init__(default=default,targetParamName=targetParamName)
        self.setOptions(text, options)

    def handleKey(self, key, noRender=False, character = None):
        """
        handles a keypress

        Parameters:
            key: the key pressed
            noRender: flag for skipping rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            self.selection = None
            if self.followUp:
                self.callIndirect(self.followUp)
            return True
        if not noRender:
            header.set_text("")

        # let superclass handle the actual selection
        if not self.getSelection():
            super().handleKey(key, noRender=noRender, character=character)

        # stop when done
        if self.getSelection():
            return True
        else:
            return False

# bad code: since there is no need to wait for some return this submenue should not wrap around the Chat menu
# bad code: sub menues should be implemented in the base class
class ChatPartnerselection(SubMenu):
    """
    Spawns a Chat submenu with a player selected character
    """

    def __init__(self):
        """
        initialise internal state
        """

        self.type = "ChatPartnerselection"
        self.subMenu = None
        super().__init__()

    def getState(self):
        """
        get state in semi serialised form

        Returns:
            the state
        """

        state = super().getState()
        if self.subMenu:
            state["subMenu"] = self.subMenu.getState()
        else:
            state["subMenu"] = None

        return state

    def setState(self, state):
        """
        set internal state from state in semi-serialised form

        Parameters:
            state: the state to set
        """

        super().setState(state)

        if "subMenu" in state:
            if state["subMenu"]:
                self.subMenu = getSubmenuFromState(state["subMenu"])
            else:
                self.subMenu = None

    def handleKey(self, key, noRender=False, character = None):
        """
        set up the selection and spawn the chat 
        keystrokes after the setup will be delegated

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """

        # wrap around the chat menu
        if self.subMenu:
            return self.subMenu.handleKey(key, noRender=noRender, character=character)

        # exit the submenu
        if key == "esc":
            return True

        # set title
        header.set_text((urwid.AttrSpec("default", "default"), "\nConversation menu\n"))
        out = "\n"

        # offer the player the option to select from characters to talk to
        # bad code: should be done in __init__
        if not self.options and not self.getSelection():
            options = []
            # get characters in room
            if src.gamestate.gamestate.mainChar.room:
                for char in src.gamestate.gamestate.mainChar.room.characters:
                    if char == src.gamestate.gamestate.mainChar:
                        continue
                    if not char.faction == src.gamestate.gamestate.mainChar.faction:
                        continue
                    if not (char.xPosition//15 == src.gamestate.gamestate.mainChar.xPosition//15 and char.yPosition//15 == src.gamestate.gamestate.mainChar.yPosition//15):
                        continue
                    options.append((char, char.name))
            # get character on terrain
            else:
                for char in src.gamestate.gamestate.mainChar.terrain.characters:
                    # bad pattern: should only list nearby characters
                    if char == src.gamestate.gamestate.mainChar:
                        continue
                    if not char.faction == src.gamestate.gamestate.mainChar.faction:
                        continue
                    if not (char.xPosition//15 == src.gamestate.gamestate.mainChar.xPosition//15 and char.yPosition//15 == src.gamestate.gamestate.mainChar.yPosition//15):
                        continue
                    if not char.rank:
                        continue

                    if char.rank < src.gamestate.gamestate.mainChar.rank:
                        options.append((char, char.name + " (outranks you)"))
                    elif char.rank == src.gamestate.gamestate.mainChar.rank:
                        options.append((char, char.name + " (same rank)"))
                    else:
                        options.append((char, char.name))

                """
                # get nearby rooms
                bigX = src.gamestate.gamestate.mainChar.xPosition // 15
                bigY = src.gamestate.gamestate.mainChar.yPosition // 15
                rooms = []
                coordinates = [
                    (bigX, bigY),
                    (bigX - 1, bigY),
                    (bigX + 1, bigY),
                    (bigX, bigY - 1),
                    (bigX, bigY + 1),
                ]
                for coordinate in coordinates:
                    if coordinate not in char.terrain.roomByCoordinates:
                        continue
                    rooms.extend(char.terrain.roomByCoordinates[coordinate])

                # add character from nearby open rooms
                for room in rooms:
                    if not room.open:
                        continue

                    for char in room.characters:
                        if not char.faction == src.gamestate.gamestate.mainChar.faction:
                            continue
                        options.append((char, char.name))
                """

            self.setOptions("talk with whom?", options)

        # delegate the actual selection to the super class
        if not self.getSelection():
            super().handleKey(key, noRender=noRender, character=character)

        # spawn the chat submenu
        if self.getSelection():
            self.subMenu = src.chats.ChatMenu(self.selection)
            self.subMenu.handleKey(key, noRender=noRender, character=character)

        # wait for input
        else:
            return False

class DebugMenu(SubMenu):
    """
    menu offering minimal debug ability
    (actually does nothing)
    """

    def __init__(self):
        """
        initialise internal state
        """

        self.type = "DebugMenu"
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        """
        show some debug output
        (actually does nothing)

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """
        # exit submenu
        if key == "esc":
            return True

class QuestMenu(SubMenu):
    """
    show the quests for a character and allow player interaction
    """

    def __init__(self, char=None):
        """
        initialise internal state

        Parameters:
            char: the character to show the quests for
        """

        self.type = "QuestMenu"
        self.lockOptions = True
        if not char:
            char = src.gamestate.gamestate.mainChar
        self.char = char
        self.offsetX = 0
        self.questIndex = 0
        super().__init__()
    
    def render(self, char):
        return renderQuests(char=self.char, asList=True, questIndex=self.questIndex)

    # overrides the superclasses method completely
    def handleKey(self, key, noRender=False, character = None):
        """
        show a questlist and handle interactions

        Parameters:
            key: the key pressed
            noRender: a flag toskip rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        # scrolling
        # bad code: doesn't actually work
        if key == "W":
            self.offsetX -= 1
        if key == "S":
            self.offsetX += 1
        if self.offsetX < 0:
            self.offsetX = 0

        # move the marker that marks the selected quest
        if key == "w":
            self.questIndex -= 1
        if key == "s":
            self.questIndex += 1
        if self.questIndex < 0:
            self.questIndex = 0
        if self.questIndex > len(self.char.quests) - 1:
            self.questIndex = len(self.char.quests) - 1

        # make the selected quest active
        if key == "j":
            if self.questIndex:
                quest = self.char.quests[self.questIndex]
                self.char.quests.remove(quest)
                self.char.quests.insert(0, quest)
                self.char.setPathToQuest(quest)
                self.questIndex = 0

        # render the quests
        addition = ""
        if self.char == src.gamestate.gamestate.mainChar:
            addition = " (you)"
        header.set_text(
            (
                urwid.AttrSpec("default", "default"),
                "\nquest overview for "
                + self.char.name
                + ""
                + addition
                + "\n(press "
                + commandChars.show_quests_detailed
                + " for the extended quest menu)\n\n",
            )
        )
        self.persistentText = []
        self.persistentText.append(
            self.render(self.char)
        )

        self.lockOptions = False

        # add interaction instructions
        self.persistentText.extend(
            [
                "\n",
                "* press q for advanced quests\n",
                "* press W to scroll up",
                "\n",
                "* press S to scroll down",
                "\n",
                "\n",
            ]
        )

        # flatten the mix of strings and urwid format so that it is less recursive to workaround an urwid bug
        # bad code: should be elsewhere
        def flatten(pseudotext):
            newList = []
            for item in pseudotext:
                if isinstance(item, list):
                    for subitem in flatten(item):
                        newList.append(subitem)
                elif isinstance(item, tuple):
                    newList.append((item[0], flatten(item[1])))
                else:
                    newList.append(item)
            return newList

        self.persistentText = flatten(self.persistentText)

        # show rendered quests via urwid
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

# bad code: should be abstracted
# bad code: uses global functions to render
class InventoryMenu(SubMenu):
    """
    shows and interacts with a characters inventory
    """

    type = "InventoryMenu"

    def __init__(self, char=None):
        """
        initialise the internal state

        Parameters:
            char: the character that owns the inventory that should be shown
        """

        self.subMenu = None
        self.skipKeypress = False
        self.activate = False
        self.drop = False
        self.char = char
        super().__init__()
        self.footerText = "press j to activate, press l to drop, press esc to exit"

    def render(self,char=None):
        return renderInventory()

    def handleKey(self, key, noRender=False, character = None):
        """
        show the inventory

        Parameters:
            key: the key pressed
            noRender: a flag to skip rendering
        Returns:
            returns True when done
        """

        if self.subMenu:
            self.subMenu.handleKey(key, noRender=noRender, character=character)
            if not self.subMenu.getSelection() is None:
                if self.activate:
                    if (
                        "NaiveActivateQuest" not in self.char.solvers
                        and not char.godMode
                    ):
                        self.persistentText = (
                            urwid.AttrSpec("default", "default"),
                            "you do not have the nessecary solver yet (activate)",
                        )
                        main.set_text(
                            (urwid.AttrSpec("default", "default"), self.persistentText)
                        )
                    else:
                        text = (
                            "you activate the "
                            + self.char.inventory[self.subMenu.getSelection()].name
                        )
                        self.persistentText = (
                            urwid.AttrSpec("default", "default"),
                            text,
                        )
                        if not noRender:
                            main.set_text(
                                (
                                    urwid.AttrSpec("default", "default"),
                                    self.persistentText,
                                )
                            )
                        self.char.addMessage(text)
                        self.char.inventory[self.subMenu.getSelection()].apply(
                            self.char
                        )
                    self.activate = False
                    self.subMenu = None
                    return True
                if self.drop:
                    if "NaiveDropQuest" not in self.char.solvers and not char.godMode:
                        self.persistentText = (
                            urwid.AttrSpec("default", "default"),
                            "you do not have the nessecary solver yet (acivate)",
                        )
                        main.set_text(
                            (urwid.AttrSpec("default", "default"), self.persistentText)
                        )
                    else:
                        text = (
                            "you drop the "
                            + self.char.inventory[self.subMenu.getSelection()].name
                        )
                        self.persistentText = (
                            urwid.AttrSpec("default", "default"),
                            text,
                        )
                        if not noRender:
                            main.set_text(
                                (
                                    urwid.AttrSpec("default", "default"),
                                    self.persistentText,
                                )
                            )
                        self.char.addMessage(text)
                        self.char.drop(self.char.inventory[self.subMenu.getSelection()])
                    self.drop = False
                    self.subMenu = None
                    return True
                self.subMenu = None
                self.skipKeypress = True
                return False
            else:
                return False

        if self.skipKeypress:
            self.skipKeypress = False
        else:
            # exit the submenu
            if key == "esc":
                return True
            if key in ("ESC","lESC",):
                self.char.rememberedMenu.append(self)
                return True
            if key in ("rESC",):
                self.char.rememberedMenu2.append(self)
                return True

            if key == "j":
                if not len(self.char.inventory):
                    return True

                options = []
                counter = 0
                for item in self.char.inventory:
                    options.append([counter, item.name])
                    counter += 1
                self.subMenu = SelectionMenu("activate what?", options)
                self.subMenu.handleKey(".", noRender=noRender,character=character)
                self.activate = True
                return False

            if key == "l":
                if not len(self.char.inventory):
                    return True

                options = []
                counter = 0
                for item in self.char.inventory:
                    options.append([counter, item.name])
                    counter += 1
                self.subMenu = SelectionMenu("drop what?", options)
                self.subMenu.handleKey(".", noRender=noRender, character=character)
                self.drop = True
                return False

        if not noRender:
            header.set_text(
                (urwid.AttrSpec("default", "default"), "\ninventory overview\n\n")
            )

            # bad code: uses global function
            self.persistentText = (
                urwid.AttrSpec("default", "default"),
                self.render(),
            )

            # show the render
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

class InputMenu(SubMenu):
    """
    menu to get a string input from the user
    """

    type = "InputMenu"

    def __init__(self, query="", ignoreFirst=False, targetParamName="text"):
        """
        initialise internal state

        Parameters:
            query: the text to be shown along with the input prompt
            ignoreFirst: flag to ignore first keypress
        """

        self.query = query
        self.text = ""
        super().__init__()
        self.footerText = "enter the text press enter to confirm"
        self.firstHit = True
        self.ignoreFirst = ignoreFirst
        self.escape = False
        self.position = 0
        self.targetParamName = targetParamName
        self.stealAllKeys = True

    def handleKey(self, key, noRender=False, character = None):
        """
        gather the input keystrokes

        Parameters:
            key: the key pressed
            noRender: a flag to skip rendering
        Returns:
            returns True when done
        """

        if key == "enter" and not self.escape:
            if self.followUp:
                self.callIndirect(self.followUp,extraParams={self.targetParamName:self.text})
            return True

        if self.ignoreFirst and self.firstHit:
            pass
        elif key == "\\" and not self.escape:
            self.escape = True
        elif key == "backspace" and not self.escape:
            if self.position:
                self.text = (
                    self.text[0: self.position - 1] + self.text[self.position:]
                )
                self.position -= 1
        elif key == "delete" and not self.escape:
            if self.position < len(self.text):
                self.text = (
                    self.text[0: self.position] + self.text[self.position + 1:]
                )
        elif key == "~":
            pass
        elif key == "left":
            self.position -= 1
        elif key == "right":
            self.position += 1
        else:
            if key == "enter":
                key = "\n"
            if len(self.text):
                self.text = (
                    self.text[0: self.position] + key + self.text[self.position:]
                )
            else:
                self.text = key
            self.position += 1
            self.escape = False

        if len(self.text):
            text = self.text[0: self.position] + "█" + self.text[self.position:]
        else:
            text = "█"

        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), "\ntext input\n\n"))
            footer.set_text((urwid.AttrSpec("default", "default"), "\ntext input\n\n"))

            self.persistentText = (
                urwid.AttrSpec("default", "default"),
                "\n" + self.query + "\n\n" + text,
            )

            # show the render
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        if self.firstHit:
            self.firstHit = False

        return False

class MessagesMenu(SubMenu):
    def render(self,char):
        try:
            if self.scrollIndex:
                return "\n".join(reversed(char.messages[-46-self.scrollIndex:-self.scrollIndex]))
            else:
                return "\n".join(reversed(char.messages[-46:]))
        except:
            print(char.messages)
            1/0
            return "error"

    type = "MessagesMenu"

    def __init__(self, char=None):
        self.char = char
        self.scrollIndex = 0
        super().__init__()

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key == "a":
            if self.scrollIndex > 0:
                self.scrollIndex -= 1
        if key == "d":
            self.scrollIndex += 1
        if key == "esc":
            character.changed("closedMessages")
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        char = self.char

        text = "press a/d to scroll\noldest message on top - skipping %s messages\n\n"%(self.scrollIndex,)+self.render(char)

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "messages"))
        main.set_text((urwid.AttrSpec("default", "default"), [text]))
        header.set_text((urwid.AttrSpec("default", "default"), ""))

# bad code: should be abstracted
# bad code: uses global function to render
class CharacterInfoMenu(SubMenu):
    """
    menu to show the players attributes
    """

    type = "CharacterInfoMenu"

    def __init__(self, char=None):
        self.char = char
        super().__init__()

    def render(self,char):
        if char.dead:
            return ""

        text = ""

        armorValue = None
        if char.armor:
            armorValue = char.armor.armorValue
        weaponBaseDamage = None
        if char.weapon:
            weaponBaseDamage = char.weapon.baseDamage

        text += "name:       %s\n" % char.name
        text += "\n"
        text += "\n"
        text += "baseDamage: %s\n" % char.baseDamage
        text += "weapon:     %s\n" % weaponBaseDamage
        text += "armor:      %s\n" % armorValue
        text += "faction:    %s\n" % char.faction
        text += "health:     %s" % char.health + "\n"
        text += "max health: %s" % char.maxHealth + "\n"

        text += "\n"

        if hasattr(char,"rank"):
            text += "rank:       %s\n" % char.rank
        if hasattr(char,"superior"):
            text += "superior:   %s\n" % char.superior

        text += "\n"
        for jobOrder in char.jobOrders:
            text += str(jobOrder.taskName)
            text += ": %s \n" % json.dumps(jobOrder.tasks)#,indent=4)
        text += "\n"
        text += "lastJobOrder: %s\n" % char.lastJobOrder
        text += "numAttackedWithoutResponse: %s\n" % char.numAttackedWithoutResponse

        text += "\n\n\n"

        text += char.getDetailedInfo() + "\n\n"
        text += "internal id: %s\n" % (char,)
        char.setRegisterValue("HEALTh", char.health)
        char.setRegisterValue("SELFx", char.xPosition % 15)
        text += "SELFx - %s" % (char.xPosition % 15) + "\n"
        char.setRegisterValue("SELFy", char.yPosition % 15)
        text += "SELFy - %s" % (char.yPosition % 15) + "\n"
        if isinstance(char.container,src.rooms.Room):
            char.setRegisterValue("SELF BIG x", char.container.xPosition)
            text += "SELF BIG x - %s" % (char.container.xPosition) + "\n"
            char.setRegisterValue("SELF BIG y", char.container.yPosition)
            text += "SELF BIG y - %s" % (char.container.yPosition) + "\n"
        else:
            char.setRegisterValue("SELF BIG x", char.xPosition // 15)
            text += "SELF BIG x - %s" % (char.xPosition // 15) + "\n"
            char.setRegisterValue("SELF BIG y", char.yPosition // 15)
            text += "SELF BIG y - %s" % (char.yPosition // 15) + "\n"
        char.setRegisterValue("SATIATIOn", char.satiation)
        text += "SATIATIOn - %s" % char.satiation + "\n"
        char.setRegisterValue("NUM INVENTORY ITEMs", len(char.inventory))
        text += "NUM INVENTORY ITEMs - %s" % (len(char.inventory)) + "\n"
        char.setRegisterValue("frustration", char.frustration)
        text += "frustration: %s\n" % char.frustration

        return text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the attributes and ignore keystrokes

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key == "esc":
            return True
        if key in ("ESC","lESC",):
            self.char.rememberedMenu.append(self)
            return True
        if key in ("rESC",):
            self.char.rememberedMenu2.append(self)
            return True

        char = self.char

        text = self.render(char)

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\ncharacter overview"))
        main.set_text((urwid.AttrSpec("default", "default"), [text]))
        header.set_text((urwid.AttrSpec("default", "default"), ""))

class CreateQuestMenu(SubMenu):
    type = "CreateQuestMenu"

    def __init__(self, questType=None, assignTo=None, activeChar=None):
        self.requiredParams = None
        self.questParams = {}
        self.questType = questType
        self.quest = None
        self.submenu = None
        self.assignTo = assignTo
        super().__init__()
        self.stealAllKeys = False
        self.parameterName = None
        self.parameterValue = None
        self.activeChar = activeChar

        self.attributesToStore.extend(
                [ "requiredParams","questParams","questType","stealAllKeys","parameterName","parameterValue"])
        self.objectsToStore.append("activeChar")
        self.objectsToStore.append("quest")
        self.objectsToStore.append("submenu")
        self.objectListsToStore.append("assignTo")

    def handleKey(self, key, noRender=False, character = None):
        # exit submenu
        if key == "esc":
            return True

        if not self.quest:
            self.quest = src.quests.questMap[self.questType]()

        if self.submenu:
            if not self.submenu.handleKey(key, noRender=noRender, character=character):
                return False
            param = self.requiredParams.pop()
            
            rawParameter = self.submenu.text
            if param["type"] == "int":
                try:
                    self.questParams[param["name"]] = int(rawParameter)
                except:
                    print(rawParameter)
                    print(self.quest)
                    return True
            elif param["type"] == "string":
                self.questParams[param["name"]] = rawParameter
            elif param["type"] == "coordinate":
                try:
                    self.questParams[param["name"]] = (int(rawParameter.split(",")[0]),int(rawParameter.split(",")[1]),0) 
                except:
                    print(rawParameter)
                    print(self.quest)
                    return True
            self.submenu = None

        if self.requiredParams == None:
            self.requiredParams = self.quest.getRequiredParameters()

        if self.requiredParams and not self.submenu:
            param = self.requiredParams[-1]
            self.submenu = src.interaction.InputMenu("%s"%(param,))
            self.submenu.handleKey("~", noRender=noRender, character=character)
            self.stealAllKeys = True
            return False

        if not self.requiredParams and key == " ":
            for char in self.assignTo:
                if char == None or char.dead:
                    continue

                quest = src.quests.questMap[self.questType]()
                quest.setParameters(self.questParams)
                foundQuest = None
                for targetQuest in char.quests:
                    if targetQuest.type == "Serve":
                        foundQuest = targetQuest
                        break

                if not foundQuest:
                    char.assignQuest(quest)
                else:
                    foundQuest.addQuest(quest)
                quest.activate()
                char.showGotCommand = True
            self.activeChar.showGaveCommand = True
            return True

        self.optionalParams = self.quest.getOptionalParameters()

        if not key in ("enter","~"):
            self.stealAllKeys = True
            if self.parameterName == None:
                self.parameterName = ""

            if self.parameterValue == None:
                if key == ":":
                    self.parameterValue = ""
                elif key == "backspace":
                    if len(self.parameterName):
                        self.parameterName = self.parameterName[:-1]
                else:
                    self.parameterName += key
            else:
                if key == ";":
                    value = None
                    if self.parameterValue == "None":
                        value = None
                    else:
                        value = int(self.parameterValue)

                    self.questParams[self.parameterName] = value
                    self.parameterName = None
                    self.parameterValue = None
                elif key == "backspace":
                    if len(self.parameterValue):
                        self.parameterValue = self.parameterValue[:-1]
                else:
                    self.parameterValue += key

        # start rendering
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), "\ncreate Quest\n"))
            # show rendered text via urwid
            main.set_text((urwid.AttrSpec("default", "default"), "type: %s\n\nparameters: \n\n%s\n\ncurrent parameter: \n\n%s : %s\n\noptional parameters: \n\n%s\n\npress space to confirm"%(self.questType,self.questParams,self.parameterName,self.parameterValue,self.optionalParams)))
        return False

class AdvancedQuestMenu(SubMenu):
    """
    player interaction for delegating a quest
    """

    type = "AdvancedQuestMenu"

    def __init__(self,activeChar=None):
        """
        set up internal state
        """

        self.character = None
        self.quest = None
        self.questParams = {}
        self.activeChar = activeChar
        super().__init__()
        self.objectsToStore.append("activeChar")

    def handleKey(self, key, noRender=False, character = None):
        """
        gather the quests parameters and assign the quest

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit submenu
        if key == "esc":
            return True

        # start rendering
        if not noRender:
            header.set_text(
                (urwid.AttrSpec("default", "default"), "\nadvanced Quest management\n")
            )
            out = "\n"
            #if self.character:
            #    out += "character: " + str(self.character.name) + "\n"
            if self.quest:
                out += "quest: " + str(self.quest) + "\n"
            out += "\n"

        # let the player select the character to assign the quest to
        if self.state is None:
            self.state = "participantSelection"
        if self.state == "participantSelection":

            if key == "S":
                self.state = "questSelection"
                self.character = "ALL"
                self.selection = None
                self.lockOptions = True
                self.options = None
            else:
                # set up the options
                if not self.options and not self.getSelection():

                    # add the active player as target
                    options = [(
                        self.activeChar,
                        self.activeChar.name+ " (you)",
                    )]

                    # add the main players subordinates as target
                    for char in self.activeChar.subordinates:
                        if char == None:
                            continue
                        options.append((char, char.name))
                    self.setOptions("whom to give the order to: \n(press S for all subordinates)", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the character to assign the quest to
                if self.getSelection():
                    self.state = "questSelection"
                    self.character = self.selection
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

        # let the player select the type of quest to create
        if self.state == "questSelection":

            if key == "N":
                self.state = "questByName"
                self.selection = ""
                key = "~"
            else:
                # add quests to select from
                if not self.options and not self.getSelection():
                    options = []
                    for key, value in src.quests.questMap.items():

                        # show only quests the character has done
                        if key not in self.activeChar.questsDone:
                            continue

                        # do not show naive quests
                        if key.startswith("Naive"):
                            continue

                        options.append((value.type, key))
                    self.setOptions("what type of quest: (press N for quest by name)", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the type of quest to create
                if self.getSelection():
                    self.state = "parameter selection"
                    self.quest = self.selection
                    self.selection = None
                    self.lockOptions = True
                    self.questParams = {}
                else:
                    return False

        if self.state == "questByName":
            if key == "enter":
                self.state = "parameter selection"
                if not self.selection in src.quests.questMap:
                    print(self.selection)
                    return True
                self.quest = self.selection
                self.selection = None
                self.lockOptions = True
                self.questParams = {}
            else:
                if key == "~":
                    pass
                elif key == "backspace":
                    if len(self.selection) > 0:
                        self.selection = self.selection[:-1]
                else:
                    self.selection += key

                if not noRender:
                    main.set_text((urwid.AttrSpec("default", "default"), self.selection+"\n\n%s"%(self.activeChar.questsDone)))
                return False

        # let the player select the parameters for the quest
        if self.state == "parameter selection":
            if self.quest == "EnterRoomQuestMeta":

                # set up the options
                if not self.options and not self.getSelection():

                    # add a list of of rooms
                    options = []
                    for room in src.gamestate.gamestate.terrain.rooms:
                        # do not show unimportant rooms
                        if isinstance(room, src.rooms.MechArmor) or isinstance(
                            room, src.rooms.CpuWasterRoom
                        ):
                            continue
                        options.append((room, room.name))
                    self.setOptions("select the room:", options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key, noRender=noRender, character=character)

                # store the parameter
                if self.getSelection():
                    self.questParams["room"] = self.selection
                    self.state = "confirm"
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

            elif self.quest == "StoreCargo":

                # set up the options for selecting the cargo room
                if "cargoRoom" not in self.questParams:
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in src.gamestate.gamestate.terrain.rooms:
                            # show only cargo rooms
                            if not isinstance(room, src.rooms.CargoRoom):
                                continue
                            options.append((room, room.name))
                        self.setOptions("select the room:", options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key, noRender=noRender, character=character)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["cargoRoom"] = self.selection
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
                else:
                    # set up the options for selecting the storage room
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in src.gamestate.gamestate.terrain.rooms:
                            # show only storage rooms
                            if not isinstance(room, src.rooms.StorageRoom):
                                continue
                            options.append((room, room.name))
                        self.setOptions("select the room:", options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key, noRender=noRender, character=character)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["storageRoom"] = self.selection
                        self.state = "confirm"
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
            elif self.quest:
                if self.character == "ALL":
                    self.activeChar.macroState["submenue"] = CreateQuestMenu(self.quest, self.activeChar.subordinates, self.activeChar)
                else:
                    self.activeChar.macroState["submenue"] = CreateQuestMenu(self.quest, [self.character], self.activeChar)
                return False
            else:
                # skip parameter selection
                self.state = "confirm"

        # get confirmation and assign quest
        if self.state == "confirm":

            # set the options for confirming the selection
            if not self.options and not self.getSelection():
                options = [("yes", "yes"), ("no", "no")]
                if self.quest == src.quests.EnterRoomQuestMeta:
                    self.setOptions(
                        "you chose the following parameters:\nroom: "
                        + str(self.questParams)
                        + "\n\nDo you confirm?",
                        options,
                    )
                else:
                    self.setOptions("Do you confirm?", options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key, noRender=noRender, character=character)

            if self.getSelection():
                # instantiate quest
                # bad code: repetitive code
                if self.selection == "yes":
                    if self.quest == src.quests.MoveQuestMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.mainChar.room, 2, 2
                        )
                    elif self.quest == src.quests.ActivateQuestMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.terrain.tutorialMachineRoom.furnaces[
                                0
                            ]
                        )
                    elif self.quest == src.quests.EnterRoomQuestMeta:
                        questInstance = self.quest(self.questParams["room"])
                    elif self.quest == src.quests.FireFurnaceMeta:
                        questInstance = self.quest(
                            src.gamestate.gamestate.terrain.tutorialMachineRoom.furnaces[
                                0
                            ]
                        )
                    elif self.quest == src.quests.WaitQuest:
                        questInstance = self.quest()
                    elif self.quest == src.quests.LeaveRoomQuest:
                        try:
                            questInstance = self.quest(self.character.room)
                        except:
                            pass
                    elif self.quest == src.quests.ClearRubble:
                        questInstance = self.quest()
                    elif self.quest == src.quests.RoomDuty:
                        questInstance = self.quest()
                    elif self.quest == src.quests.ConstructRoom:
                        for room in src.gamestate.gamestate.terrain.rooms:
                            if isinstance(room, src.rooms.ConstructionSite):
                                constructionSite = room
                                break
                        questInstance = self.quest(
                            constructionSite,
                            src.gamestate.gamestate.terrain.tutorialStorageRooms,
                        )
                    elif self.quest == src.quests.StoreCargo:
                        for room in src.gamestate.gamestate.terrain.rooms:
                            if isinstance(room, src.rooms.StorageRoom):
                                storageRoom = room
                        questInstance = self.quest(
                            self.questParams["cargoRoom"],
                            self.questParams["storageRoom"],
                        )
                    elif self.quest == src.quests.MoveToStorage:
                        questInstance = self.quest(
                            [
                                src.gamestate.gamestate.terrain.tutorialLab.itemByCoordinates[
                                    (1, 9)
                                ][
                                    0
                                ],
                                src.gamestate.gamestate.terrain.tutorialLab.itemByCoordinates[
                                    (2, 9)
                                ][
                                    0
                                ],
                            ],
                            src.gamestate.gamestate.terrain.tutorialStorageRooms[1],
                        )
                    elif self.quest == "special_furnace":
                        questInstance = src.quests.KeepFurnaceFiredMeta(
                            self.character.room.furnaces[0]
                        )
                    else:
                        questInstance = self.quest()

                    # assign the quest
                    self.character.assignQuest(questInstance, active=True)

                    self.state = "done"

                # reset progress
                else:
                    self.state = "questSelection"

                self.selection = None
                self.lockOptions = False
            else:
                return False

        # close submenu
        if self.state == "done":
            if self.lockOptions:
                self.lockOptions = False
            else:
                return True

        # show rendered text via urwid
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

# bad pattern: should be configurable
def renderHeader(character):
    """
    render the information section on top of the screen

    Parameters:
        character: the character to use to get the information from
    """

    return ""

    # render the sections to display
    questSection = renderQuests(maxQuests=2)
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

# bad code: the asList and questIndex parameters are out of place
def renderQuests(maxQuests=0, char=None, asList=False, questIndex=0):
    """
    render the quests into a string or list

    Parameters:
        maxQuests: the maximal number of quests rendered (0=no maximum)
        char: the character the quests belong to
        asList: flag to switch from rendering as string to rendering as list
        questsIndex: index pointing to the active quest

    Returns:
        the rendered messages
    """

    # basic set up
    if not char:
        char = src.gamestate.gamestate.mainChar
    if asList:
        txt = []
    else:
        txt = ""

    # render the quests
    if len(char.quests):
        solvingCommangString = char.getActiveQuest().getSolvingCommandString(char)
        if solvingCommangString:
            solvingCommangString = solvingCommangString.replace("\n","\\n")

        nextstep = "next step: %s \n"%(solvingCommangString,)
        if asList:
            txt.append(src.interaction.ActionMeta(payload="+",content=nextstep))
        else:
            txt += nextstep

        counter = 0
        for quest in char.quests:
            # render quest
            if asList:
                if counter == questIndex:
                    txt.extend(
                        [
                            (urwid.AttrSpec("#0f0", "default"), "QUEST: "),
                            quest.getDescription(
                                asList=asList, colored=True, active=True
                            ),
                            "\n",
                        ]
                    )
                else:
                    txt.extend(
                        [
                            (urwid.AttrSpec("#090", "default"), "QUEST: "),
                            quest.getDescription(asList=asList, colored=True),
                            "\n",
                        ]
                    )
            else:
                txt += "QUEST: " + quest.getDescription(asList=asList) + "\n"

            # break if maximum reached
            counter += 1
            if counter == maxQuests:
                break

    # return placeholder for no quests
    else:
        if asList:
            txt.append("No Quest")
        else:
            txt += "No Quest"

    return txt


#bad code: global function
#bad code: should be abstracted
def renderInventory():
    """
    render the inventory of the player into a string

    Returns:
        the rendered string
    """

    char = src.gamestate.gamestate.mainChar
    txt = []
    if len(char.inventory):
        counter = 0
        for item in char.inventory:
            counter += 1
            if isinstance(item.render(), int):
                txt.extend(
                    [
                        str(counter),
                        " - ",
                        src.canvas.displayChars.indexedMapping[item.render()],
                        " - ",
                        item.name,
                        "\n     ",
                        item.getDetailedInfo(),
                        "\n",
                    ]
                )
            else:
                txt.extend(
                    [
                        str(counter),
                        " - ",
                        item.render(),
                        " - ",
                        item.name,
                        "\n     ",
                        item.getDetailedInfo(),
                        "\n",
                    ]
                )
    else:
        txt = "empty Inventory"
    return txt

# bad code: uses global function to render
class HelpMenu(SubMenu):
    """
    the help submenue
    """

    type = "HelpMenu"

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," "):
            character.changed("closedHelp")
            return True

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = ""
        self.persistentText += renderHelp()
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

class ViewNPCsMenu(SubMenu):
    type = "ViewNPCsMenu"

    def __init__(self,personnelArtwork):
        super().__init__()
        self.index = 0
        self.personnelArtwork = personnelArtwork

    def handleKey(self, key, noRender=False, character = None):

        # exit the submenu
        if key in ("esc"," ",):
            return True

        self.persistentText = "press w/a and s/d to scroll\n\n"

        characters = self.personnelArtwork.getPersonnelList()

        if key in ("w","a",):
            if self.index > 0:
                self.index -= 1

        if key in ("s","d"):
            if self.index < len(characters)-1:
                self.index += 1

        self.persistentText += "%s of %s\n\n"%(self.index+1,len(characters),)

        selectedCharacter = characters[self.index]
        self.persistentText += "\ninternal id: %s"%(selectedCharacter)
        self.persistentText += "\nname: %s"%(selectedCharacter.name)
        self.persistentText += "\nrank: %s"%(selectedCharacter.rank)
        if selectedCharacter.weapon:
            self.persistentText += "\nweapon: %s"%(selectedCharacter.weapon.baseDamage)
        else:
            self.persistentText += "\nweapon: None"
        if selectedCharacter.armor:
            self.persistentText += "\narmor: %s"%(selectedCharacter.armor.armorValue)
        else:
            self.persistentText += "\narmor: None"
        self.persistentText += "\nstaff: %s"%(selectedCharacter.isStaff)
        self.persistentText += "\nduties: %s"%(", ".join(selectedCharacter.duties),)
        quest = selectedCharacter.getActiveQuest()
        if quest:
            self.persistentText += "\nactive quest: %s"%(quest.description,)
        else:
            self.persistentText += "\nactive quest: None"

        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

class StaffAsMatrixMenu(SubMenu):
    type = "StaffAsMatrixMenu"

    def __init__(self,staffArtwork):
        super().__init__()
        self.index = [0,0]
        self.staffArtwork = staffArtwork
        self.roomTypes = ["TrapRoom","WorkshopRoom"]


    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        text = ["press wasd to move cursor\npress j to increase\npress k to decrease\n"]

        if key in ("w",):
            if self.index[1] > 0:
                self.index[1] -= 1
        if key in ("s",):
            if self.index[1] < len(self.roomTypes)-1:
                self.index[1] += 1
        if key in ("a",):
            if self.index[0] > 0:
                self.index[0] -= 1
        if key in ("d",):
            self.index[0] += 1

        if key in ("j",):
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == self.roomTypes[self.index[1]]:
                    if self.index[0] == 0 or self.index[0] == roomCounter:
                        self.staffArtwork.autoFillStaffFromMap({"character":character,"coordinate":(room.xPosition,room.yPosition)},redirect=False)
                    roomCounter += 1
        if key in ("k",):
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == self.roomTypes[self.index[1]]:
                    if self.index[0] == 0 or self.index[0] == roomCounter:
                        self.staffArtwork.autoRemoveStaffFromMap({"character":character,"coordinate":(room.xPosition,room.yPosition)},redirect=False)
                    roomCounter += 1

        counter = 0
        for roomType in self.roomTypes:
            color = "#fff"
            if counter == self.index[1] and self.index[0] == 0:
                color = "#f00"
            text.append((urwid.AttrSpec(color, "default"),"%s"%(roomType,)))
            roomCounter = 1
            for room in self.staffArtwork.container.container.rooms:
                if room.objType == roomType:
                    color = "#fff"
                    if counter == self.index[1] and roomCounter == self.index[0]:
                        color = "#f00"
                    text.append((urwid.AttrSpec(color, "default")," %s"%(len(room.staff))))
                    roomCounter += 1
            text.append("\n")
            counter += 1

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

    def getQuestMarkersTile(self, character):
        out = []

        roomType = self.roomTypes[self.index[1]]
        roomCounter = 1
        for room in self.staffArtwork.container.container.rooms:
            if not room.objType == roomType:
                continue
            if self.index[0] == 0 or self.index[0] == roomCounter:
                out.append((room.getPosition(),"selected"))
            roomCounter += 1
        return out


class JobAsMatrixMenu(SubMenu):
    type = "JobAsMatrixMenu"

    def __init__(self,cityLeader):
        super().__init__()
        self.cityLeader = cityLeader 
        self.index = [0,0]

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        duties = ["trap setting","resource fetching","hauling","clearing","scratch checking","resource gathering","guarding","painting","machine placing"]
        if key == "w":
            if not self.index[0] < 1:
                self.index[0] -= 1
        if key == "s":
            self.index[0] += 1
        if key == "a":
            if not self.index[1] < 1:
                self.index[1] -= 1
        if key == "d":
            if not self.index[1] > len(duties)-2:
                self.index[1] += 1
        if key == "j":
            rowCounter = 0
            if rowCounter == self.index[0]:
                dutyname = duties[self.index[1]]
                if dutyname in self.cityLeader.duties:
                    self.cityLeader.duties.remove(dutyname)
                else:
                    self.cityLeader.duties.append(dutyname)
            rowCounter += 1

            for subleader in self.cityLeader.subordinates:
                if rowCounter == self.index[0]:
                    dutyname = duties[self.index[1]]
                    if dutyname in subleader.duties:
                        subleader.duties.remove(dutyname)
                    else:
                        subleader.duties.append(dutyname)
                rowCounter += 1

            for subleader in self.cityLeader.subordinates:
                for subsubleader in subleader.subordinates:
                    if rowCounter == self.index[0]:
                        dutyname = duties[self.index[1]]
                        if dutyname in subsubleader.duties:
                            subsubleader.duties.remove(dutyname)
                        else:
                            subsubleader.duties.append(dutyname)
                    rowCounter += 1

            for subleader in self.cityLeader.subordinates:
                for subsubleader in subleader.subordinates:
                    for worker in subsubleader.subordinates:
                        if rowCounter == self.index[0]:
                            dutyname = duties[self.index[1]]
                            if dutyname in worker.duties:
                                worker.duties.remove(dutyname)
                            else:
                                worker.duties.append(dutyname)
                        rowCounter += 1

        cityLeader = self.cityLeader

        text = "press wasd to move cursor"
        text += "press j to enable/disable"

        text = [text]

        text.append("\ncharacter                 ")
        rowCounter = 0
        for duty in duties:
            color = "default"
            if rowCounter == self.index[1]:
                color = "#333"
            text.append(" | ")
            text.append((urwid.AttrSpec("default", color),duty))
            rowCounter += 1

        def convertName(name):
            return name.ljust(25," ")[0:24]


        lineCounter = 0
        text.append("\nrank 3 ----\n")
        color = "default"
        rowCounter = 0
        if lineCounter == self.index[0]:
            color = "#333"
        text.append((urwid.AttrSpec("default", color),"%s: "%(convertName(cityLeader.name),)))
        for duty in duties:
            if lineCounter == self.index[0] and rowCounter == self.index[1]:
                text.append("=>")
            else:
                color = "default"
                if rowCounter == self.index[1] or lineCounter == self.index[0]:
                    color = "#333"
                text.append((urwid.AttrSpec("default", color),"  "))
            if duty in cityLeader.duties:
                text.append("X")
            else:
                color = "default"
                if rowCounter == self.index[1] or lineCounter == self.index[0]:
                    color = "#333"
                text.append((urwid.AttrSpec("default", color)," "))
            text.append("|")
            rowCounter += 1
        lineCounter += 1

        text.append("\nrank 4 ----\n")
        for subleader in cityLeader.subordinates:
            color = "default"
            if lineCounter == self.index[0]:
                color = "#333"
            text.append((urwid.AttrSpec("default", color),"%s: "%(convertName(subleader.name),)))
            rowCounter = 0
            for duty in duties:
                if lineCounter == self.index[0] and rowCounter == self.index[1]:
                    text.append("=>")
                else:
                    color = "default"
                    if rowCounter == self.index[1] or lineCounter == self.index[0]:
                        color = "#333"
                    text.append((urwid.AttrSpec("default", color),"  "))
                if duty in subleader.duties:
                    text.append("X")
                else:
                    color = "default"
                    if rowCounter == self.index[1] or lineCounter == self.index[0]:
                        color = "#333"
                    text.append((urwid.AttrSpec("default", color)," "))
                text.append("|")
                rowCounter += 1
            lineCounter += 1
            text.append("\n")

        text.append("rank 5 ----\n")
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                color = "default"
                if lineCounter == self.index[0]:
                    color = "#333"
                text.append((urwid.AttrSpec("default", color),"%s: "%(convertName(subsubleader.name),)))
                rowCounter = 0
                for duty in duties:
                    if lineCounter == self.index[0] and rowCounter == self.index[1]:
                        text.append("=>")
                    else:
                        color = "default"
                        if rowCounter == self.index[1] or lineCounter == self.index[0]:
                            color = "#333"
                        text.append((urwid.AttrSpec("default", color),"  "))
                    if duty in subsubleader.duties:
                        text.append("X")
                    else:
                        color = "default"
                        if rowCounter == self.index[1] or lineCounter == self.index[0]:
                            color = "#333"
                        text.append((urwid.AttrSpec("default", color)," "))
                    text.append("|")
                    rowCounter += 1
                lineCounter += 1
                text.append("\n")

        text.append("rank 6 ----\n")
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                for worker in subsubleader.subordinates:

                    color = "default"
                    if lineCounter == self.index[0]:
                        color = "#333"
                    text.append((urwid.AttrSpec("default", color),"%s: "%(convertName(worker.name),)))

                    rowCounter = 0
                    for duty in duties:
                        if lineCounter == self.index[0] and rowCounter == self.index[1]:
                            text.append("=>")
                        else:
                            color = "default"
                            if rowCounter == self.index[1] or lineCounter == self.index[0]:
                                color = "#333"
                            text.append((urwid.AttrSpec("default", color),"  "))
                        if duty in worker.duties:
                            text.append("X")
                        else:
                            color = "default"
                            if rowCounter == self.index[1] or lineCounter == self.index[0]:
                                color = "#333"
                            text.append((urwid.AttrSpec("default", color)," "))
                        text.append("|")
                        rowCounter += 1
                    lineCounter += 1
                    text.append("\n")

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False
        
class JobByRankMenu(SubMenu):
    """
    the help submenue
    """

    type = "JobByRankMenu"

    def __init__(self,cityLeader):
        super().__init__()
        self.cityLeader = cityLeader 
        self.index = [0,0]

    def handleKey(self, key, noRender=False, character = None):
        """
        show the help text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("esc"," ",):
            return True

        duties = ["trap setting","resource fetching","hauling","clearing","scratch checking","resource gathering","guarding","painting","machine placing"]
        if key == "w":
            if not self.index[0] < 1:
                self.index[0] -= 1
        if key == "s":
            if not self.index[0] > 2:
                self.index[0] += 1
        if key == "a":
            if not self.index[1] < 1:
                self.index[1] -= 1
        if key == "d":
            if not self.index[1] > len(duties)-2:
                self.index[1] += 1
        if key == "j":
            if self.index[0] == 0:
                dutyname = duties[self.index[1]]
                if not dutyname in self.cityLeader.duties:
                   self.cityLeader.duties.append(dutyname)
            if self.index[0] == 1:
                dutyname = duties[self.index[1]]
                for subleader in self.cityLeader.subordinates:
                    if not dutyname in subleader.duties:
                       subleader.duties.append(dutyname)
                       break
            if self.index[0] == 2:
                dutyname = duties[self.index[1]]
                firstSubsubleaderFound = None
                for subleader in self.cityLeader.subordinates:
                    for subsubleader in subleader.subordinates:
                        if not dutyname in subsubleader.duties:
                           subsubleader.duties.append(dutyname)
                           firstSubsubleaderFound = subsubleader
                           break
                    if firstSubsubleaderFound:
                        break
            if self.index[0] == 3:
                dutyname = duties[self.index[1]]
                firstWorkerFound = None
                for subleader in self.cityLeader.subordinates:
                    for subsubleader in subleader.subordinates:
                        for worker in subsubleader.subordinates:
                            if not dutyname in worker.duties:
                               worker.duties.append(dutyname)
                               firstWorkerFound = worker
                               break
                        if firstWorkerFound:
                            break
                    if firstWorkerFound:
                        break

        if key == "k":
            if self.index[0] == 0:
                dutyname = duties[self.index[1]]
                if dutyname in self.cityLeader.duties:
                   self.cityLeader.duties.remove(dutyname)
            if self.index[0] == 1:
                dutyname = duties[self.index[1]]
                for subleader in self.cityLeader.subordinates:
                    if dutyname in subleader.duties:
                       subleader.duties.remove(dutyname)
                       break
            if self.index[0] == 2:
                dutyname = duties[self.index[1]]
                firstSubsubleaderFound = None
                for subleader in self.cityLeader.subordinates:
                    for subsubleader in subleader.subordinates:
                        if dutyname in subsubleader.duties:
                           subsubleader.duties.remove(dutyname)
                           firstSubsubleaderFound = subsubleader
                           break
                    if firstSubsubleaderFound:
                        break
            if self.index[0] == 3:
                dutyname = duties[self.index[1]]
                firstWorkerFound = None
                for subleader in self.cityLeader.subordinates:
                    for subsubleader in subleader.subordinates:
                        for worker in subsubleader.subordinates:
                            if dutyname in worker.duties:
                               worker.duties.remove(dutyname)
                               firstWorkerFound = worker
                               break
                        if firstWorkerFound:
                            break
                    if firstWorkerFound:
                        break


        cityLeader = self.cityLeader

        text = "press wasd to move cursor\n\n"
        text += "press j to increase\n"
        text += "press k to decrease\n"

        dutyCount = {}
        for duty in duties:
            dutyCount[duty] = 0
        npcCount = 0
        npcCount += 1
        for duty in cityLeader.duties:
            dutyCount[duty] += 1
        text += "rank 3 (%s): \n"%(npcCount,)
        counter = 0
        for duty in duties:
            count = dutyCount[duty]
            if self.index[0] == 0 and self.index[1] == counter:
                text += "=> "
            text += "%s: %s "%(duty,count)
            counter += 1
        text += "\n"

        dutyCount = {}
        for duty in duties:
            dutyCount[duty] = 0
        npcCount = 0
        for subleader in cityLeader.subordinates:
            npcCount += 1
            for duty in subleader.duties:
                dutyCount[duty] += 1
        text += "rank 4 (%s): \n"%(npcCount,)
        counter = 0
        for duty in duties:
            count = dutyCount[duty]
            if self.index[0] == 1 and self.index[1] == counter:
                text += "=> "
            text += "%s: %s "%(duty,count)
            counter += 1
        text += "\n"

        dutyCount = {}
        for duty in duties:
            dutyCount[duty] = 0
        npcCount = 0
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                npcCount += 1
                for duty in subsubleader.duties:
                    dutyCount[duty] += 1
        text += "rank 5 (%s): \n"%(npcCount,)
        counter = 0
        for duty in duties:
            count = dutyCount[duty]
            if self.index[0] == 2 and self.index[1] == counter:
                text += "=> "
            text += "%s: %s "%(duty,count)
            counter += 1
        text += "\n"

        dutyCount = {}
        for duty in duties:
            dutyCount[duty] = 0
        npcCount = 0
        for subleader in cityLeader.subordinates:
            for subsubleader in subleader.subordinates:
                for worker in subsubleader.subordinates:
                    npcCount += 1
                    for duty in worker.duties:
                        dutyCount[duty] += 1
        text += "rank 6 (%s): \n"%(npcCount,)
        counter = 0
        for duty in duties:
            count = dutyCount[duty]
            if self.index[0] == 3 and self.index[1] == counter:
                text += "=> "
            text += "%s: %s "%(duty,count)
            counter += 1
        text += "\n"

        # show info
        header.set_text((urwid.AttrSpec("default", "default"), "\n\nhelp\n\n"))
        self.persistentText = text
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

class MapMenu(SubMenu):
    """
    a menu for triggering actions from a map
    """
    
    type = "MapMenu"

    def __init__(self, mapContent=None,functionMap=None, extraText = "", cursor = None):
        """
        initialise internal state

        Parameters:
            mapContent: the content to show
        """

        super().__init__()
        self.mapContent = mapContent
        self.functionMap = functionMap
        self.extraText = extraText
        if cursor:
            self.cursor = cursor
        else:
            self.cursor = (7,7)

    def handleKey(self, key, noRender=False, character = None):
        """
        show the map and trigger functions depending on key presses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        closeMenu = False
        mappedFunctions = self.functionMap.get(self.cursor, {})
        if key in mappedFunctions:
            closeMenu = True
            self.callIndirect(mappedFunctions[key]["function"],{"coordinate":self.cursor})

        # exit the submenu
        if key in ("w",):
            if self.cursor[1] > 1:
                self.cursor = (self.cursor[0],self.cursor[1]-1)
        if key in ("s",):
            if self.cursor[1] < 13:
                self.cursor = (self.cursor[0],self.cursor[1]+1)
        if key in ("a",):
            if self.cursor[0] > 1:
                self.cursor = (self.cursor[0]-1,self.cursor[1])
        if key in ("d",):
            if self.cursor[0] < 13:
                self.cursor = (self.cursor[0]+1,self.cursor[1])

        if closeMenu or key in (
            "esc",
            "enter",
            "space",
            "j",
        ):
            if self.followUp:
                self.followUp()
            return True

        # show rendered map
        mapText = []
        for y in range(0, 15):
            mapText.append([])
            for x in range(0, 15):
                if (x,y) == self.cursor:
                    mapText[-1].append("██")
                else:
                    mapText[-1].append(self.mapContent[y][x])
            mapText[-1].append("\n")

        mapText.append("\n press wasd to move cursor %s"%(self.cursor,))

        mappedFunctions = self.functionMap.get(self.cursor, {})
        for (key,item) in mappedFunctions.items():
            mapText.append("\n press %s to %s"%(key,item["description"],))

        mapText.append(self.extraText)

        if not noRender:
            # show info
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = mapText
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))


        return False

class TextMenu(SubMenu):
    """
    a menu showing a text
    """
    
    type = "TextMenu"

    def __init__(self, text=""):
        """
        initialise internal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.text = text

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and ignore keypresses

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in (
            "esc",
            "enter",
            "space",
            " ",
        ):
            if self.followUp:
                self.callIndirect(self.followUp)
            return True

        if not noRender:
            # show info
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = ""
            self.persistentText += self.text
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        return False

class OneKeystrokeMenu(SubMenu):
    """
    a menu getting a single keystroke from the character
    """

    type = "OneKeystrokeMenu"

    def __init__(self, text=""):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.text = text
        self.firstRun = True
        self.keyPressed = ""
        self.done = False

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and quit on second keypress

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # show info
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = ""
            self.persistentText += self.text
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        # exit the submenu
        if key not in ("~",) and not self.firstRun:
            self.keyPressed = key
            if self.followUp:
                self.callIndirect(self.followUp,{"keyPressed":key})
            self.done = True
            return True

        self.firstRun = False

        return False

class ImplantConnection(SubMenu):
    type = "ImplantConnection"

    def __init__(self, connectionTarget):
        super().__init__()
        self.connectionTarget = connectionTarget
        self.submenu = None

    def handleKey(self, key, noRender=False, character = None):
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = "implant connection to %s"%(self.connectionTarget.type,)
            self.persistentText += "\n\n"
            self.persistentText += "press j to use connection\n"
            self.persistentText += "press x to close connection\n"
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        if self.submenu and self.submenu.done:
            self.submenu = None
            return False

        if self.submenu:
            self.submenu.handleKey(key, noRender, character)
            return False

        if key in ("x",):
            self.done = True
            return True
        if character and key in ("ESC","lESC",):
            character.rememberedMenu.append(self)
            return True
        if character and key in ("rESC",):
            character.rememberedMenu2.append(self)
            return True

        if character and key in ("j",):
            self.connectionTarget.apply(character)
            character.rememberedMenu.append(self)

        return False

    def render(self, char):
        return "implant connection to %s"%(self.connectionTarget.type,)

class ChangeViewsMenu(SubMenu):
    type = "ChangeViewsMenu"

    def __init__(self):
        super().__init__()
        self.firstKey = True

    def handleKey(self, key, noRender=False, character = None):
        
        if character and key in ("a",):
            character.personality["viewChar"] = "activity"
        if character and key in ("A",):
            character.personality["viewColour"] = "activity"
        if character and key in ("r",):
            character.personality["viewChar"] = "rank"
        if character and key in ("R",):
            character.personality["viewColour"] = "rank"
        if character and key in ("h",):
            character.personality["viewChar"] = "health"
        if character and key in ("H",):
            character.personality["viewColour"] = "health"
        if character and key in ("n",):
            character.personality["viewChar"] = "name"
        if character and key in ("N",):
            character.personality["viewColour"] = "name"
        if character and key in ("f",):
            character.personality["viewChar"] = "faction"
        if character and key in ("F",):
            character.personality["viewColour"] = "faction"

        viewChar = character.personality["viewChar"]
        viewColour = character.personality["viewColour"]

        self.persistentText = []
        self.persistentText.append("change view menu\n\n")
        color = "#fff"
        if viewChar == "activity":
            color = "#f00"
        if viewColour == "activity":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"),"press a/A to show NPC activity marking\n"))
        color = "#fff"
        if viewChar == "rank":
            color = "#f00"
        if viewColour == "rank":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"),"press r/R to rank marking\n"))
        color = "#fff"
        if viewChar == "health":
            color = "#f00"
        if viewColour == "health":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"),"press h/H to show health marking\n"))
        color = "#fff"
        if viewChar == "name":
            color = "#f00"
        if viewColour == "name":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"),"press n/N to show name marking\n"))
        color = "#fff"
        if viewChar == "faction":
            color = "#f00"
        if viewColour == "faction":
            color = "#0f0"
        self.persistentText.append((urwid.AttrSpec(color, "default"),"press f/F to show faction indicator\n"))
        self.persistentText.append("\n\nsmall letters for display color, big letters for display char")
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True

class RoomMenu(SubMenu):
    type = "RoomMenu"

    def __init__(self, room):
        super().__init__()
        self.room = room
        self.firstKey = True

    def handleKey(self, key, noRender=False, character = None):
        self.persistentText = "room menu \n\n"

        self.persistentText = [self.persistentText]
        self.persistentText.append("%s - %s\n"%(self.room.objType,self.room.name,))
        try:
            self.persistentText.append( "electricalCharges: " + str(self.room.electricalCharges)+"\n")
        except:
            pass
        try:
            self.persistentText.append("maxElectricalCharges: " + str(self.room.maxElectricalCharges)+"\n")
        except:
            pass
        self.persistentText.append("\n\n")
        if self.room.staff:
            self.persistentText.append("staff:\n")
            for staffNpc in self.room.staff:
                deadText = ""
                if staffNpc.dead:
                    deadText = " (dead)"
                questText = ""
                if not staffNpc.dead and staffNpc.quests:
                    questText = staffNpc.quests[0].description.split("\n")[0]
                    try:
                        questText += staffNpc.quests[0].description.split("\n")[1]
                    except:
                        pass
                self.persistentText.append("%s%s - %s\n"%(staffNpc.name,deadText,questText,))
        else:
                self.persistentText.append("There is no staff assigned assign staff by using the staff artwork (SA)")

        self.persistentText.append("\n\n- q: open staff section\n- r: show resource sources")

        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        if self.firstKey:
            self.firstKey = False
            return

        if character and key in ("q",):
            character.macroState["submenue"] = RoomDutyMenu(self.room)

        if character and key in ("r",):
            character.macroState["submenue"] = RoomSourceMenu(self.room)

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True

class RoomSourceMenu(SubMenu):
    """
    """
    
    type = "RoomSourceMenu"
    def __init__(self, room):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.room = room

    def handleKey(self, key, noRender=False, character = None):
        self.persistentText = "sources to fetch resources from:\n\n"
        for source in self.room.sources:
            self.persistentText += "%s: %s\n"%(source[1],source[0],)
        main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))
        
        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True

class RoomDutyMenu(SubMenu):
    """
    """

    type = "RoomDutyMenu"

    def __init__(self, room):
        """
        initialise inernal state

        Parameters:
            text: the text to show
        """

        super().__init__()
        self.room = room
        self.keyPressed = ""
        self.done = False
        self.index = (0,0)

    def handleKey(self, key, noRender=False, character = None):
        """
        show the text and quit on second keypress

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        """

        # exit the submenu
        if key in ("w",):
            if self.index[1] > 0:
                self.index = (self.index[0],self.index[1]-1)
        if key in ("s",):
            if self.index[1] < len(self.room.duties)-1:
                self.index = (self.index[0],self.index[1]+1)
        if key in ("a",):
            if self.index[0] > 0:
                self.index = (self.index[0]-1,self.index[1])
        if key in ("d",):
            if self.index[0] < len(self.room.staff)-1:
                self.index = (self.index[0]+1,self.index[1])

        if key in ("j","enter"):
            duty = self.room.duties[self.index[1]]
            staffCharacter = self.room.staff[self.index[0]]
            if duty in staffCharacter.duties:
                staffCharacter.duties.remove(duty)
            else:
                staffCharacter.duties.append(duty)

        # show info
        if not noRender:
            header.set_text((urwid.AttrSpec("default", "default"), ""))
            self.persistentText = """
move the cursor using w/a/s/d.
press j or enter to select

"""
            self.persistentText = [self.persistentText]
            self.persistentText.append("%s - %s\n"%(self.room.objType,self.room.name,))
            try:
                self.persistentText.append( "electricalCharges: " + str(self.room.electricalCharges)+"\n")
            except:
                pass
            try:
                self.persistentText.append("maxElectricalCharges: " + str(self.room.maxElectricalCharges)+"\n")
            except:
                pass
            self.persistentText.append("\n\n")
            if self.room.staff:
                self.persistentText.append("staff:\n")
                for staffNpc in self.room.staff:
                    deadText = ""
                    if staffNpc.dead:
                        deadText = " (dead)"
                    questText = ""
                    if not staffNpc.dead and staffNpc.quests:
                        questText = staffNpc.quests[0].description.split("\n")[0]
                        try:
                            questText += staffNpc.quests[0].description.split("\n")[1]
                        except:
                            pass
                    self.persistentText.append("%s%s - %s\n"%(staffNpc.name,deadText,questText,))
            else:
                    self.persistentText.append("There is no staff assigned assign staff by using the staff artwork (SA)")

            self.persistentText += "\n"

            if self.room.staff:
                rowCounter = 0
                for duty in self.room.duties:
                    self.persistentText.append( duty + " |")
                    colCounter = 0
                    for staffCharacter in self.room.staff:
                        frontColor = "#fff"
                        if duty in staffCharacter.duties:
                            frontColor = "#0e0"
                        backColor = "#000"
                        if (colCounter,rowCounter) == self.index:
                            backColor = "#444"
                        self.persistentText.append((urwid.AttrSpec(frontColor, backColor),staffCharacter.name))
                        self.persistentText.append(" |")
                        colCounter += 1
                    self.persistentText.append("\n")
                    rowCounter += 1
            main.set_text((urwid.AttrSpec("default", "default"), self.persistentText))

        # exit the submenu
        if key in ("esc",):
            self.done = True
            return True

        self.firstRun = False

        return False


# bad code: should not be a global function
def renderHelp():
    """
    renders the help text

    Returns:
        the rendered help text
    """

    char = src.gamestate.gamestate.mainChar
    txt = "the Goal of the Game is to stay alive and build a base.\nThe daily Grind can be delageted to subordinates.\n\nThe game is focused on automation so try to use Commands and NPCs to automate production.\n\nUse the Auto tutor to do challenges and to learn how to play the game.\n\n"
    txt += "your keybindings are:\n\n"
    txt += "* move_north: " + commandChars.move_north + "\n"
    txt += "* move_east: " + commandChars.move_east + "\n"
    txt += "* move_west: " + commandChars.move_west + "\n"
    txt += "* move_south: " + commandChars.move_south + "\n"
    txt += "* activate: " + commandChars.activate + "\n"
    txt += "* drink: " + commandChars.drink + "\n"
    txt += "* pickUp: " + commandChars.pickUp + "\n"
    txt += "* drop: " + commandChars.drop + "\n"
    txt += "* hail: " + commandChars.hail + "\n"
    txt += "* examine: " + commandChars.examine + "\n"
    txt += "* quit_normal: " + commandChars.quit_normal + "\n"
    txt += "* quit_instant: " + commandChars.quit_instant + "\n"
    txt += "* quit_delete: " + commandChars.quit_delete + "\n"
    txt += "* autoAdvance: " + commandChars.autoAdvance + "\n"
    txt += "* advance: " + commandChars.advance + "\n"
    txt += "* pause: " + commandChars.pause + "\n"
    txt += "* ignore: " + commandChars.ignore + "\n"
    txt += "* wait: " + commandChars.wait + "\n"
    txt += "* show_quests " + commandChars.show_quests + "\n"
    txt += "* show_quests_detailed: " + commandChars.show_quests_detailed + "\n"
    txt += "* show_inventory: " + commandChars.show_inventory + "\n"
    txt += "* show_inventory_detailed: " + commandChars.show_inventory_detailed + "\n"
    txt += "* show_characterInfo: " + commandChars.show_characterInfo + "\n"
    txt += "* redraw: " + commandChars.redraw + "\n"
    txt += "* show_help: " + commandChars.show_help + "\n"
    txt += "* attack: " + commandChars.attack + "\n"
    txt += "* devMenu: " + commandChars.devMenu + "\n"
    txt += "\n\nMove onto an item and press the key to interact with it. Move against big items and press the key to interact with it\n\n"
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
        src.gamestate.gamestate.mainChar.room
        and src.gamestate.gamestate.mainChar.room.xPosition
    ):
        centerX = (
            src.gamestate.gamestate.mainChar.room.xPosition * 15
            + src.gamestate.gamestate.mainChar.room.offsetX
            + src.gamestate.gamestate.mainChar.xPosition
        )
        centerY = (
            src.gamestate.gamestate.mainChar.room.yPosition * 15
            + src.gamestate.gamestate.mainChar.room.offsetY
            + src.gamestate.gamestate.mainChar.yPosition
        )
    else:
        centerX = src.gamestate.gamestate.mainChar.xPosition
        centerY = src.gamestate.gamestate.mainChar.yPosition

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
        src.gamestate.gamestate.mainChar.room
        and not src.gamestate.gamestate.mainChar.room.xPosition
    ):
        chars = src.gamestate.gamestate.mainChar.room.render()
    else:
        chars = thisTerrain.render(size=(viewsize, viewsize),coordinateOffset=(centerY - halfviewsite, centerX - halfviewsite))
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
        size=(viewsize, viewsize+20),
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


def keyboardListener(key):
    """
    handles true key presses from the player

    Parameters:
        key: the key pressed
    """

    global multi_currentChar
    multi_chars = src.gamestate.gamestate.multi_chars
    global charindex

    global continousOperation
    continousOperation = -1

    if not multi_currentChar:
        multi_currentChar = src.gamestate.gamestate.mainChar
    if multi_chars is None:
        multi_chars = src.gamestate.gamestate.terrain.characters[:]
        for room in src.gamestate.gamestate.terrain.rooms:
            for character in room.characters[:]:
                if character not in multi_chars:
                    multi_chars.add(character)

    state = src.gamestate.gamestate.mainChar.macroState

    if key == "ctrl d":
        src.gamestate.gamestate.mainChar.clearCommandString()
        state["loop"] = []
        state["replay"].clear()
        src.gamestate.gamestate.mainChar.huntkilling = False
        if "ifCondition" in src.gamestate.gamestate.mainChar.interactionState:
            src.gamestate.gamestate.mainChar.interactionState["ifCondition"].clear()
            src.gamestate.gamestate.mainChar.interactionState["ifParam1"].clear()
            src.gamestate.gamestate.mainChar.interactionState["ifParam2"].clear()
        activeQuest = src.gamestate.gamestate.mainChar.getActiveQuest()
        if activeQuest and activeQuest.autoSolve:
            activeQuest.autoSolve = False

    elif key == "ctrl t":
        if src.gamestate.gamestate.gameHalted:
            src.gamestate.gamestate.gameHalted = False
        else:
            src.gamestate.gamestate.gameHalted = True

    elif key == "ctrl p":
        if not src.gamestate.gamestate.mainChar.macroStateBackup:
            src.gamestate.gamestate.mainChar.macroStateBackup = (
                src.gamestate.gamestate.mainChar.macroState
            )
            src.gamestate.gamestate.mainChar.setDefaultMacroState()
            src.gamestate.gamestate.mainChar.macroState[
                "macros"
            ] = src.gamestate.gamestate.mainChar.macroStateBackup["macros"]

            state = src.gamestate.gamestate.mainChar.macroState
        else:
            src.gamestate.gamestate.mainChar.macroState = (
                src.gamestate.gamestate.mainChar.macroStateBackup
            )
            src.gamestate.gamestate.mainChar.macroState[
                "macros"
            ] = src.gamestate.gamestate.mainChar.macroStateBackup["macros"]
            src.gamestate.gamestate.mainChar.macroStateBackup = None

    elif key == "ctrl x":
        src.gamestate.gamestate.save()
        raise urwid.ExitMainLoop()

    elif key == "ctrl o":
        with open("macros.json", "r") as macroFile:
            import json

            rawMacros = json.loads(macroFile.read())
            parsedMacros = {}

            state = "normal"
            for key, value in rawMacros.items():
                parsedMacro = []
                for char in value:
                    if state == "normal":
                        if char == "/":
                            state = "multi"
                            combinedKey = ""
                            continue
                        parsedMacro.append(char)
                    if state == "multi":
                        if char == "/":
                            state = "normal"
                            parsedMacro.append(combinedKey)
                        else:
                            combinedKey += char
                parsedMacros[key] = parsedMacro

            src.gamestate.gamestate.mainChar.macroState["macros"] = parsedMacros

    elif key == "ctrl k":
        with open("macros.json", "w") as macroFile:
            import json

            compressedMacros = {}
            for key, value in src.gamestate.gamestate.mainChar.macroState[
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

        src.gamestate.gamestate.mainChar = newChar
        state = src.gamestate.gamestate.mainChar.macroState

    elif key == "ctrl w":
        if not src.gamestate.gamestate.mainChar.room:
            return
        import json

        state = src.gamestate.gamestate.mainChar.room.getState()
        serializedState = json.dumps(state, indent=10, sort_keys=True)

        with open("roomExport.json", "w") as exportFile:
            exportFile.write(serializedState)
    elif key == "ctrl i":
        foundChar = None
        for character in src.gamestate.gamestate.mainChar.container.characters:
            if character == src.gamestate.gamestate.mainChar:
                continue
            if character.xPosition == src.gamestate.gamestate.mainChar.xPosition and character.yPosition == src.gamestate.gamestate.mainChar.yPosition:
                foundChar = character
                break

        if not foundChar:
            for character in src.gamestate.gamestate.mainChar.container.characters:
                if abs(character.xPosition-src.gamestate.gamestate.mainChar.xPosition) + abs(character.yPosition-src.gamestate.gamestate.mainChar.yPosition):
                    foundChar = character
                    break

        if not foundChar:
            for character in src.gamestate.gamestate.mainChar.container.characters:
                foundChar = character
                break

        if foundChar:
            src.gamestate.gamestate.mainChar = character
            state = src.gamestate.gamestate.mainChar.macroState
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
        show_or_exit(key)


lastAdvance = 0
lastAutosave = 0

lastcheck = time.time()
def getTcodEvents():
    global lastcheck

    events = tcod.event.get()

    if lastcheck < time.time()-0.05:
        for event in events:
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.WindowEvent):
                if event.type == "WINDOWCLOSE":
                    raise SystemExit()
                if event.type == "WINDOWEXPOSED":
                    renderGameDisplay()
            if isinstance(event,tcod.event.MouseButtonDown):# or isinstance(event,tcod.event.MouseButtonUp):
                tcodContext.convert_event(event)
                clickPos = (event.tile.x,event.tile.y)
                if src.gamestate.gamestate.clickMap:
                    if not clickPos in src.gamestate.gamestate.clickMap:
                        continue

                    value = src.gamestate.gamestate.clickMap[clickPos]
                    if isinstance(value,str) or isinstance(value,list):
                        src.gamestate.gamestate.mainChar.runCommandString(value,nativeKey=True)
                    elif isinstance(value,dict):
                        if not "params" in value:
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
                if key == tcod.event.KeySym.LSHIFT:
                    continue
                if key == tcod.event.KeySym.RETURN:
                    translatedKey = "enter"
                if key == tcod.event.KeySym.BACKSPACE:
                    translatedKey = "backspace"
                if key == tcod.event.KeySym.SPACE:
                    translatedKey = " "
                if key == tcod.event.KeySym.PERIOD:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = ":"
                    else:
                        translatedKey = "."
                if key == tcod.event.KeySym.HASH:
                    translatedKey = "#"
                if key == tcod.event.KeySym.ESCAPE:
                    if event.mod in (tcod.event.Modifier.RSHIFT,):
                        translatedKey = "rESC"
                    elif event.mod in (tcod.event.Modifier.LSHIFT,):
                        translatedKey = "lESC"
                    elif event.mod in (tcod.event.Modifier.SHIFT,):
                        translatedKey = "ESC"
                    else:
                        translatedKey = "esc"
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
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = ";"
                    else:
                        translatedKey = ","
                if key == tcod.event.KeySym.MINUS:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "_"
                    else:
                        translatedKey = "-"
                if key == tcod.event.KeySym.PLUS or key == tcod.event.KeySym.KP_PLUS:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "*"
                    else:
                        translatedKey = "+"
                if key == tcod.event.KeySym.a:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl a"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "A"
                    else:
                        translatedKey = "a"
                if key == tcod.event.KeySym.b:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "B"
                    else:
                        translatedKey = "b"
                if key == tcod.event.KeySym.c:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl c"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "C"
                    else:
                        translatedKey = "c"
                if key == tcod.event.KeySym.d:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl d"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "D"
                    else:
                        translatedKey = "d"
                if key == tcod.event.KeySym.e:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "E"
                    else:
                        translatedKey = "e"
                if key == tcod.event.KeySym.f:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "F"
                    else:
                        translatedKey = "f"
                if key == tcod.event.KeySym.g:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "G"
                    else:
                        translatedKey = "g"
                if key == tcod.event.KeySym.h:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "H"
                    else:
                        translatedKey = "h"
                if key == tcod.event.KeySym.i:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl i"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "I"
                    else:
                        translatedKey = "i"
                if key == tcod.event.KeySym.j:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "J"
                    else:
                        translatedKey = "j"
                if key == tcod.event.KeySym.k:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "K"
                    else:
                        translatedKey = "k"
                if key == tcod.event.KeySym.l:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "L"
                    else:
                        translatedKey = "l"
                if key == tcod.event.KeySym.m:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "M"
                    else:
                        translatedKey = "m"
                if key == tcod.event.KeySym.n:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "N"
                    else:
                        translatedKey = "n"
                if key == tcod.event.KeySym.o:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "O"
                    else:
                        translatedKey = "o"
                if key == tcod.event.KeySym.p:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "P"
                    else:
                        translatedKey = "p"
                if key == tcod.event.KeySym.q:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "Q"
                    else:
                        translatedKey = "q"
                if key == tcod.event.KeySym.r:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "R"
                    else:
                        translatedKey = "r"
                if key == tcod.event.KeySym.s:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "S"
                    else:
                        translatedKey = "s"
                if key == tcod.event.KeySym.t:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl t"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "T"
                    else:
                        translatedKey = "t"
                if key == tcod.event.KeySym.u:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "U"
                    else:
                        translatedKey = "u"
                if key == tcod.event.KeySym.v:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "V"
                    else:
                        translatedKey = "v"
                if key == tcod.event.KeySym.w:
                    if event.mod in (tcod.event.Modifier.LCTRL,tcod.event.Modifier.RCTRL,):
                        translatedKey = "ctrl w"
                    elif event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "W"
                    else:
                        translatedKey = "w"
                if key == tcod.event.KeySym.x:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "X"
                    else:
                        translatedKey = "x"
                if key == tcod.event.KeySym.y:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "Y"
                    else:
                        translatedKey = "y"
                if key == tcod.event.KeySym.z:
                    if event.mod in (tcod.event.Modifier.SHIFT,tcod.event.Modifier.RSHIFT,tcod.event.Modifier.LSHIFT,):
                        translatedKey = "Z"
                    else:
                        translatedKey = "z"

                if translatedKey == None:
                    print(event)
                    continue

                keyboardListener(translatedKey)
                lastcheck = time.time()

class UiAnchor(object):
    def __init__(self,tag=""):
        pass

class ActionMeta(object):
    def __init__(self, payload=None,content=None):
        self.payload = payload
        self.content = content

def renderGameDisplay():
    src.gamestate.gamestate.clickMap = {}

    text = ""

    char = src.gamestate.gamestate.mainChar

    if char.room:
        thisTerrain = char.room.terrain
    else:
        thisTerrain = char.terrain


    global lastTerrain
    if thisTerrain:
        lastTerrain = thisTerrain
    else:
        thisTerrain = lastTerrain

    stepSize = char.maxHealth/15
    healthRate = int(char.health/stepSize)

    if char.health == 0:
        healthDisplay = "---------------"
    else:
        healthDisplay = [(urwid.AttrSpec("#f00", "default"),"x"*healthRate),(urwid.AttrSpec("#444", "default"),"."*(15-healthRate))]

    if char.satiation == 0:
        satiationDisplay = (urwid.AttrSpec("#f00", "default"),"starved")
    elif char.satiation < 200:
        satiationDisplay = (urwid.AttrSpec("#f00", "default"),"starving")
    elif char.satiation < 400:
        satiationDisplay = (urwid.AttrSpec("#f60", "default"),"hungry")
    else:
        satiationDisplay = (urwid.AttrSpec("#0f0", "default"),"satiated")

    text = [
        "health: " , healthDisplay ,
        "    satiation: " , satiationDisplay
    ]

    footer.set_text(text)

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

    def printUrwidToTcod(inData,offset,color=None,internalOffset=None,size=None, actionMeta=None):
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
                        for i in range(0,len(toPrint)):
                            src.gamestate.gamestate.clickMap[(x+i,y)] = actionMeta
                    tcodConsole.print(x=x,y=y,string=toPrint,fg=color[0],bg=color[1])

                internalOffset[0] += len(line)
                counter += 1


        if isinstance(inData,tuple):
            printUrwidToTcod(inData[1],offset,(inData[0].get_rgb_values()[:3],inData[0].get_rgb_values()[3:]),internalOffset,size,actionMeta)

        if isinstance(inData,list):
            for item in inData:
                printUrwidToTcod(item,offset,color,internalOffset,size,actionMeta)

        if isinstance(inData, ActionMeta):
            printUrwidToTcod(inData.content,offset,color,internalOffset,size,inData.payload)
        
        #footertext = stringifyUrwid(inData)

    # render the game
    if not src.gamestate.gamestate.mainChar.specialRender or tcodConsole:

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
            if not src.gamestate.gamestate.mainChar.godMode and (
                src.gamestate.gamestate.mainChar.satiation < 300
                or src.gamestate.gamestate.mainChar.health < 30
            ):
                warning = True
            else:
                warning = False
            header.set_text(
                (
                    urwid.AttrSpec("default", "default"),
                    renderHeader(src.gamestate.gamestate.mainChar),
                )
            )
            if useTiles:
                canvas = render(src.gamestate.gamestate.mainChar)
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
                tcodConsole.clear()

                for uiElement in src.gamestate.gamestate.uiElements:
                    if uiElement["type"] == "gameMap":
                        canvas = render(src.gamestate.gamestate.mainChar)
                        canvas.printTcod(tcodConsole,uiElement["offset"][0],uiElement["offset"][1],warning=warning)
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
                        canvas.printTcod(tcodConsole,uiElement["offset"][0],uiElement["offset"][1],warning=warning)

                    if uiElement["type"] == "healthInfo":
                        if src.gamestate.gamestate.dragState:
                            continue
                        offset = (uiElement["offset"][0]+44-len(stringifyUrwid(footer.get_text()))//2,uiElement["offset"][1])
                        width = uiElement["width"]
                        printUrwidToTcod(footer.get_text(),offset,size=(width,100))
                    if uiElement["type"] == "indicators":
                        autoIndicator = ActionMeta(content="*",payload="*")
                        if src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"] or (src.gamestate.gamestate.mainChar.getActiveQuest() and src.gamestate.gamestate.mainChar.getActiveQuest().autoSolve):
                            def test():
                                src.gamestate.gamestate.mainChar.clearCommandString()
                                src.gamestate.gamestate.mainChar.macroState["loop"] = []
                                src.gamestate.gamestate.mainChar.macroState["replay"].clear()
                                src.gamestate.gamestate.mainChar.huntkilling = False
                                if "ifCondition" in src.gamestate.gamestate.mainChar.interactionState:
                                    src.gamestate.gamestate.mainChar.interactionState["ifCondition"].clear()
                                    src.gamestate.gamestate.mainChar.interactionState["ifParam1"].clear()
                                    src.gamestate.gamestate.mainChar.interactionState["ifParam2"].clear()
                                activeQuest = src.gamestate.gamestate.mainChar.getActiveQuest()
                                if activeQuest and activeQuest.autoSolve:
                                    activeQuest.autoSolve = False
                                src.gamestate.gamestate.mainChar.runCommandString("~")

                            autoIndicator = ActionMeta(content=(urwid.AttrSpec("#f00", "default"),"*"),payload=test)
                        indicators = [ActionMeta(content="x",payload="x~")," ",ActionMeta(content="q",payload="q~")," ",ActionMeta(content="v",payload="v~")," ",autoIndicator," ",ActionMeta(content="t",payload="t~")]

                        x = max(uiElement["offset"][0]+uiElement["width"]//2-len(indicators)//2,0)
                        y = uiElement["offset"][1]

                        printUrwidToTcod(indicators,(x,y),size=(uiElement["width"],1))

                    if uiElement["type"] == "text":
                        printUrwidToTcod(uiElement["text"],uiElement["offset"])
                    if uiElement["type"] == "rememberedMenu":
                        if src.gamestate.gamestate.mainChar.rememberedMenu:
                            chars = []
                            counter = 0
                            for menu in reversed(src.gamestate.gamestate.mainChar.rememberedMenu):
                                chars.extend(["------------- ",ActionMeta(content=">",payload=["lESC"]),"\n\n"])
                                chars.extend(menu.render(src.gamestate.gamestate.mainChar))
                                counter += 1
                            size = uiElement["size"]
                            offset = uiElement["offset"]
                            printUrwidToTcod(chars,offset,size=size)

                    if uiElement["type"] == "rememberedMenu2":
                        if src.gamestate.gamestate.mainChar.rememberedMenu2:
                            chars = []
                            for menu in reversed(src.gamestate.gamestate.mainChar.rememberedMenu2):
                                chars.extend(["------------- ",ActionMeta(content="<",payload=["rESC"]),"\n\n"])
                                chars.extend(menu.render(src.gamestate.gamestate.mainChar))
                            size = uiElement["size"]
                            offset = uiElement["offset"]
                            printUrwidToTcod(chars,offset,size=size)
                            

                if not src.gamestate.gamestate.mainChar.specialRender:
                    tcodContext.present(tcodConsole)
            if not useTiles and not tcodConsole:
                main.set_text(
                    (
                        urwid.AttrSpec("#999", "black"),
                        canvas.getUrwirdCompatible(warning=warning),
                    )
                )

                canvas = render(src.gamestate.gamestate.mainChar)
    if src.gamestate.gamestate.mainChar.specialRender:
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

            counter = offsetTop
            tcodConsole.print(x=offsetLeft, y=counter-1, string="|",fg=(255,255,255),bg=(0,0,0))
            tcodConsole.print(x=offsetLeft+width+3, y=counter-1, string="|",fg=(255,255,255),bg=(0,0,0))
            tcodConsole.print(x=offsetLeft+width+0, y=counter-1, string="<",fg=(255,255,255),bg=(0,0,0))
            src.gamestate.gamestate.clickMap[(offsetLeft+width+0,counter-1)] = ["lESC"]
            tcodConsole.print(x=offsetLeft+width+1, y=counter-1, string="X",fg=(255,255,255),bg=(0,0,0))
            src.gamestate.gamestate.clickMap[(offsetLeft+width+1,counter-1)] = ["esc"]
            tcodConsole.print(x=offsetLeft+width+2, y=counter-1, string=">",fg=(255,255,255),bg=(0,0,0))
            src.gamestate.gamestate.clickMap[(offsetLeft+width+2,counter-1)] = ["rESC"]

            tcodConsole.print(x=offsetLeft+width+5, y=counter-1, string=stringifyUrwid(header.get_text()),fg=(255,255,255),bg=(0,0,0))
            tcodConsole.print(x=offsetLeft-2, y=counter, string="--+-"+"-"*width+"-+--",fg=(255,255,255),bg=(0,0,0))
            counter += 1
            tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
            counter += 1
            for line in plainText.split("\n"):
                tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
                counter += 1
            tcodConsole.print(x=offsetLeft, y=counter, string="| "+" "*width+" |",fg=(255,255,255),bg=(0,0,0))
            counter += 1
            tcodConsole.print(x=offsetLeft-2, y=counter, string="--+-"+"-"*width+"-+--",fg=(255,255,255),bg=(0,0,0))
            tcodConsole.print(x=offsetLeft, y=counter+1, string="|",fg=(255,255,255),bg=(0,0,0))
            tcodConsole.print(x=offsetLeft+width+3, y=counter+1, string="|",fg=(255,255,255),bg=(0,0,0))

            #printUrwidToTcod(main.get_text(),(offsetLeft+2,offsetTop+2),size=(width,height))
            printUrwidToTcod(main.get_text(),(offsetLeft+2,offsetTop+2))
            tcodContext.present(tcodConsole)

def gameLoop(loop, user_data=None):
    """
    run the game for one tick

    Parameters:
        loop: the main loop (urwids main loop)
        user_data: parameter have to handle but is ignored
    """

    if not src.gamestate.gamestate.stopGameInTicks is None:
        if src.gamestate.gamestate.stopGameInTicks == 0:
            src.gamestate.gamestate.gameHalted = True
            src.gamestate.gamestate.stopGameInTicks = None
        else:
            src.gamestate.gamestate.stopGameInTicks -= 1

    if src.gamestate.gamestate.gameHalted:
        loop.set_alarm_in(0.001, gameLoop)
        return

    import time

    global lastAdvance
    global fixedTicks
    global lastAutosave

    runFixedTick = False
    if speed:
        fixedTicks = speed
    if fixedTicks and time.time() - lastAdvance > fixedTicks:
        runFixedTick = True

    global multi_currentChar
    multi_chars = src.gamestate.gamestate.multi_chars
    global new_chars

    firstRun = True
    lastcheck = time.time()

    while not loop or firstRun:
        #profiler = cProfile.Profile()
        #profiler.enable()

        startTime = time.time()
        origTick = src.gamestate.gamestate.tick

        if 1== 1:
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

            if tcod:
                getTcodEvents()

            hasAutosolveQuest = False
            for quest in src.gamestate.gamestate.mainChar.getActiveQuests():
                if not quest.autoSolve:
                    continue
                hasAutosolveQuest = True

            global continousOperation
            if (
                src.gamestate.gamestate.mainChar.macroState["commandKeyQueue"] and not speed
            ) or runFixedTick or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest:
                continousOperation += 1

                if not len(cinematics.cinematicQueue):
                    lastAdvance = time.time()
                    advanceGame()

                removeChars = []
                for char in multi_chars:
                    advanceChar(char,removeChars)
                    pass

                multi_chars.update(new_chars)
                new_chars = set()

                for char in removeChars:
                    multi_chars.remove(char)

                renderGameDisplay()

        #endTime = time.time()
        #if endTime-startTime > 0.1:
        #    print("tick time %s for %s"%(endTime-startTime,origTick,))

        #profiler.dump_stats("tmpFolder/tick%s"%(origTick,))

        endTime = time.time()
        if endTime-startTime < 0.09999:
            time.sleep(0.1-(endTime-startTime))

    else:
        continousOperation = 0

    loop.set_alarm_in(0.001, gameLoop)

def advanceChar(char,removeChars):
    if char.dead and not char == src.gamestate.gamestate.mainChar:
        removeChars.append(char)
    if char.stasis:
        return
    if char.disabled:
        return

    if (
        len(cinematics.cinematicQueue)
        and not char == src.gamestate.gamestate.mainChar
    ):
        return

    state = char.macroState

    hasAutosolveQuest = False
    for quest in char.getActiveQuests():
        if not quest.autoSolve:
            continue
        hasAutosolveQuest = True

    # do random action
    if not (len(state["commandKeyQueue"]) or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest):
        #if not char == src.gamestate.gamestate.mainChar:
        char.startIdling()

    """
    while len(state["commandKeyQueue"]) > 1000:
        state["commandKeyQueue"].pop()
    """

    while len(char.messages) > 100:
        char.messages = char.messages[-100:]

    if len(state["commandKeyQueue"]) or src.gamestate.gamestate.timedAutoAdvance or hasAutosolveQuest:
        if state["commandKeyQueue"]:
            key = state["commandKeyQueue"][-1]
            while (
                isinstance(key[0], list)
                or isinstance(key[0], tuple)
                or key[0] in ("lagdetection", "lagdetection_")
            ):
                if len(state["commandKeyQueue"]):
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
                    renderGameDisplay()
                    startTime = time.time()

                    while (not state["commandKeyQueue"]) and char.timeTaken < 1:
                        hasAutosolveQuest = False
                        for quest in char.getActiveQuests():
                            if not quest.autoSolve:
                                continue
                            hasAutosolveQuest = True

                        getTcodEvents()
                        if src.gamestate.gamestate.timedAutoAdvance:
                            if time.time() > startTime + src.gamestate.gamestate.timedAutoAdvance:
                                char.timeTaken += 1

            hasAutosolveQuest = False
            for quest in char.getActiveQuests():
                if not quest.autoSolve:
                    continue
                hasAutosolveQuest = True


        char.timeTaken -= 1

loop = None

s = None


def handleMultiplayerClients(loop, user_data):
    """
    basically a copy of the main loop for networked multiplayer

    Parameters:
        loop: the main loop (urwids main loop)
        user_data: parameter that needs to be there but is not used
    """

    if not multiplayer:
        return

    HOST = "127.0.0.1"
    PORT = 65440

    global s
    if not s:
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()

    import json
    import urwid

    conn, addr = s.accept()
    with conn:
        data = conn.recv(1024 * 1024 * 1024)

        if data == b"ignore":
            loop.set_alarm_in(0.1, handleMultiplayerClients)
            return

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


# the directory for the submenus
subMenuMap = {
    "SelectionMenu": SelectionMenu,
    "ListActionMenu": ListActionMenu,
    "ChatPartnerselection": ChatPartnerselection,
    "DebugMenu": DebugMenu,
    "QuestMenu": QuestMenu,
    "InventoryMenu": InventoryMenu,
    "CharacterInfoMenu": CharacterInfoMenu,
    "AdvancedQuestMenu": AdvancedQuestMenu,
    "HelpMenu": HelpMenu,
    "TextMenu": TextMenu,
    "MapMenu": MapMenu,
    "OneKeystrokeMenu": OneKeystrokeMenu,
    "CreateQuestMenu": CreateQuestMenu,
    "JobByRankMenu": JobByRankMenu,
    "JobAsMatrixMenu": JobAsMatrixMenu,
    "StaffAsMatrixMenu": StaffAsMatrixMenu,
    "RoomMenu": RoomMenu,
}

def getSubmenuFromState(state):
    """
    load a submenu from a serialised state

    Parameters:
        state: the state to load from
    Returns:
        the submenu
    """

    subMenu = subMenuMap[state["type"]]()
    subMenu.setState(state)
    src.saveing.loadingRegistry.register(subMenu)
    return subMenu

##################################################################################################################################
###
##        code for interacation with the user belongs here
#         bad pattern: logic should be moved somewhere else
#
#################################################################################################################################

# load libraries
import time
import urwid

# load internal libraries
import src.rooms
import src.items
import src.quests
import src.canvas
import src.saveing
import src.chats
import src.terrains

##################################################################################################################################
###
##        setting up the basic user interaction library
#         bad code: urwid specific code should be somewhere else
#
#################################################################################################################################

# the containers for the shown text
header = urwid.Text(u"")
main = urwid.Text(u"")
footer = urwid.Text(u"",align = 'right')
main.set_layout('left', 'clip')

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)

##################################################################################################################################
###
##        the main interaction loop
#
#################################################################################################################################

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
doubleFooterText = footerText+footerText
footerPosition = 0
footerLength = len(footerText)
footerSkipCounter = 20

macros = {}

'''
calculate footer text
'''
def setFooter():
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
    "press "+commandChars.show_help+" for help",
    "press "+commandChars.move_north+" to move north",
    "press "+commandChars.move_south+" to move south",
    "press "+commandChars.show_quests+" for quests",
    "press "+commandChars.show_quests_detailed+" for advanced quests",
    "press "+commandChars.show_inventory+" for inventory",
    "press "+commandChars.move_west+" to move west",
    "press "+commandChars.move_east+" to move east",
    "press "+commandChars.activate+" to activate",
    "press "+commandChars.pickUp+" to pick up",
    "press "+commandChars.hail+" to talk",
    "press "+commandChars.drop+" to drop",
    ]
    footerText = ", ".join(footerInfo)+", "

    # calculate meta information for footer
    doubleFooterText = footerText+footerText
    doubleFooterText = "- press "+commandChars.show_help+" for an help text -"
    doubleFooterText = doubleFooterText*20
    footerPosition = 0
    footerLength = len(footerText)
    footerSkipCounter = 20

'''
calls show_or_exit with on param less
bad code: keystrokes should not be injected in the first place
'''
def callShow_or_exit(loop,key):
    show_or_exit(key)

'''
the callback for urwid keystrokes
bad code: this is abused as the main loop for this game
'''
def show_or_exit(key,charState=None):
    if charState == None:
        charState = mainChar.macroState

    # store the commands for later processing
    charState["commandKeyQueue"].append((key,[]))

    # transform and store the keystrokes that accumulated in pygame
    if useTiles:
        import pygame
        for item in pygame.event.get():
            if not hasattr(key,"unicode"):
                continue
            key = item.unicode
            if key == "\x1b":
                key = "esc"
            state["commandKeyQueue"].append((key,[]))
            debugMessages.append("pressed "+key+" ")

    # handle the keystrokes
    #processAllInput(commandKeyQueue)

'''
the abstracted processing for keystrokes.
Takes a list of keystrokes, that have been converted to a common format
'''
def processAllInput(commandKeyQueue):
    for key in commandKeyQueue:
        processInput(key)


shownStarvationWarning = False

pauseGame = False

'''
handle a keystroke
bad code: there are way too much lines of code in this function
'''
def processInput(key,charState=None,noAdvanceGame=False,char=None):
    
    if charState == None:
        charState = mainChar.macroState

    if char == None:
        char = mainChar

    if char.room:
        terrain = char.room.terrain
    else:
        terrain = char.terrain

    if terrain == None:
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

    char.specialRender = False

    if char.doStackPop:
        if key in char.registers:
            char.registers[key].pop()
            if not len(char.registers[key]):
                del char.registers[key]
        char.doStackPop = False
        return
    if char.doStackPush:
        if not key in char.registers:
            char.registers[key] = []
        char.registers[key].append(0)
        char.doStackPush = False
        return

    if char.enumerateState:
        if charState["recordingTo"] and not "norecord" in flags:
            charState["macros"][charState["recordingTo"]].append(key)

        if char.enumerateState[-1]["type"] == None:
            char.enumerateState[-1]["type"] = key
            if mainChar == char and not "norecord" in flags:
                header.set_text((urwid.AttrSpec("default","default"),"observe"))
                main.set_text((urwid.AttrSpec("default","default"),"""

get position for what thing

* d - drill
* s - scrap
* f - goo flask
* c - character
* m - marker bean
* t - tree
* C - coal

"""))
                footer.set_text((urwid.AttrSpec("default","default"),""))
                char.specialRender = True
            return

        if char.enumerateState[-1]["type"] == "p":
            char.messages.append("type:"+key)

            if key == "d":
                char.enumerateState[-1]["target"] = ["Drill"]
            elif key == "s":
                char.enumerateState[-1]["target"] = ["Scrap"]
            elif key == "f":
                char.enumerateState[-1]["target"] = ["GooFlask"]
            elif key == "c":
                char.enumerateState[-1]["target"] = ["character"]
            elif key == "m":
                char.enumerateState[-1]["target"] = ["MarkerBean"]
            elif key == "t":
                char.enumerateState[-1]["target"] = ["Tree"]
            elif key == "C":
                char.enumerateState[-1]["target"] = ["Coal"]
            else:
                char.messages.append("not a valid target")
                char.enumerateState.pop()
                return

            if not "a" in char.registers:
                char.registers["a"] = [0]
            char.registers["a"][-1] = 0
            if not "w" in char.registers:
                char.registers["w"] = [0]
            char.registers["w"][-1] = 0
            if not "s" in char.registers:
                char.registers["s"] = [0]
            char.registers["s"][-1] = 0
            if not "d" in char.registers:
                char.registers["d"] = [0]
            char.registers["d"][-1] = 0

            if not char.container:
                char.messages.append("character is nowhere")
                char.enumerateState.pop()
                return

            foundItems = []

            if not char.enumerateState[-1]["target"] == ["character"]:
                listFound = char.container.itemsOnFloor

                for item in listFound:
                    if not item.type in char.enumerateState[-1]["target"]:
                        continue
                    if item.xPosition < char.xPosition-20:
                        continue
                    if item.xPosition > char.xPosition+20:
                        continue
                    if item.yPosition < char.yPosition-20:
                        continue
                    if item.yPosition > char.yPosition+20:
                        continue
                    foundItems.append(item)

            if "character" in char.enumerateState[-1]["target"]:
                listFound = char.container.itemsOnFloor
                for otherChar in char.container.characters:
                    if otherChar == char:
                        continue
                    if otherChar.xPosition < char.xPosition-20:
                        continue
                    if otherChar.xPosition > char.xPosition+20:
                        continue
                    if otherChar.yPosition < char.yPosition-20:
                        continue
                    if otherChar.yPosition > char.yPosition+20:
                        continue
                    foundItems.append(otherChar)

            found = None
            if len(foundItems):
                found = foundItems[gamestate.tick%len(foundItems)]

            if not found:
                char.messages.append("no "+",".join(char.enumerateState[-1]["target"])+" found")
                char.enumerateState.pop()
                return

            char.registers["d"][-1] = found.xPosition-char.xPosition
            char.registers["s"][-1] = found.yPosition-char.yPosition
            char.registers["a"][-1] = -char.registers["d"][-1]
            char.registers["w"][-1] = -char.registers["s"][-1]

            char.messages.append(",".join(char.enumerateState[-1]["target"])+" found in direction %sa %ss %sd %sw"%(char.registers["a"][-1],char.registers["s"][-1],char.registers["d"][-1],char.registers["w"][-1],))
            char.enumerateState.pop()
            return
            
        char.enumerateState.pop()
        return

    if key == "esc":
        charState["replay"] = []

    if not "varActions" in charState:
        charState["varActions"] = []

    if key == "$":
        if mainChar == char and not "norecord" in flags:
            text = """

press key for register to modify or press = to load value from a register

current registers:

"""
            for itemKey,value in char.registers.items(): 
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(itemKey))
                text += """
%s - %s"""%(itemKey,",".join(convertedValues))

            header.set_text((urwid.AttrSpec("default","default"),"registers"))
            main.set_text((urwid.AttrSpec("default","default"),text))
            footer.set_text((urwid.AttrSpec("default","default"),""))
            char.specialRender = True

        charState["varActions"].append({"outOperator":None})

        if charState["recordingTo"] and not "norecord" in flags:
            charState["macros"][charState["recordingTo"]].append(key)
        return
    if charState["varActions"]:

        if charState["recordingTo"] and not "norecord" in flags:
            charState["macros"][charState["recordingTo"]].append(key)

        lastVarAction = charState["varActions"][-1]
        if lastVarAction["outOperator"] == None:
            if key == "=":
                lastVarAction["outOperator"] = True
                if mainChar == char and not "norecord" in flags:
                    text = """

press key for register to load value from

current registers:

"""
                    for key,value in char.registers.items(): 
                        convertedValues = []
                        for item in reversed(value):
                            convertedValues.append(str(item))
                        text += """
%s - %s"""%(key,",".join(convertedValues))

                    header.set_text((urwid.AttrSpec("default","default"),"reading registers"))
                    main.set_text((urwid.AttrSpec("default","default"),text))
                    footer.set_text((urwid.AttrSpec("default","default"),""))
                    char.specialRender = True
                return
            else:
                lastVarAction["outOperator"] = False
                lastVarAction["register"] = None
                lastVarAction["action"] = None
                lastVarAction["number"] = ""

        if lastVarAction["outOperator"] == True:
            def getValue():
                if not key in char.registers:
                    char.messages.append("no value in register using %s"%(key,))
                    return 0

                if char.registers[key][-1] < 0:
                    char.messages.append("negative value in register using %s"%(key,))
                    return 0

                char.messages.append("found value %s for register using %s"%(char.registers[key][-1],key,))
                return char.registers[key][-1]

            value = getValue()

            valueCommand = []
            for numChar in str(value):
                valueCommand.append((numChar,["norecord"]))

            char.messages.append(valueCommand)

            charState["varActions"].pop()
            charState["commandKeyQueue"] = valueCommand + charState["commandKeyQueue"]
            return
        else:
            if lastVarAction["register"] == None:
                lastVarAction["register"] = key

                if mainChar == char and not "norecord" in flags:
                    text = """

press key for the action you want to do on the register

* = - assign value to register
* + - add to register
* - - subtract from register
* / - divide register
* * - mulitply register
* % - apply modulo to register

"""
                    header.set_text((urwid.AttrSpec("default","default"),"reading registers"))
                    main.set_text((urwid.AttrSpec("default","default"),text))
                    footer.set_text((urwid.AttrSpec("default","default"),""))
                    char.specialRender = True

                return
            if lastVarAction["action"] == None:
                lastVarAction["action"] = key

                if mainChar == char and not "norecord" in flags:
                    text = """

input value for this operation ($%s%s)

type number or load value from register

"""%( lastVarAction["register"], lastVarAction["action"])
                    header.set_text((urwid.AttrSpec("default","default"),"reading registers"))
                    main.set_text((urwid.AttrSpec("default","default"),text))
                    footer.set_text((urwid.AttrSpec("default","default"),""))
                    char.specialRender = True

                return
            if key in "0123456789":
                lastVarAction["number"] += key

                if mainChar == char and not "norecord" in flags:
                    text = """

input value for this operation ($%s%s%s)

type number

press any other key to finish

"""%( lastVarAction["register"], lastVarAction["action"], lastVarAction["number"])
                    header.set_text((urwid.AttrSpec("default","default"),"reading registers"))
                    main.set_text((urwid.AttrSpec("default","default"),text))
                    footer.set_text((urwid.AttrSpec("default","default"),""))
                    char.specialRender = True

                return

            if lastVarAction["action"] == "=":
                if not lastVarAction["register"] in char.registers:
                    char.registers[lastVarAction["register"]] = [0]
                char.registers[lastVarAction["register"]][-1] = int(lastVarAction["number"])
            if lastVarAction["action"] == "+":
                 char.registers[lastVarAction["register"]][-1] += int(lastVarAction["number"])
            if lastVarAction["action"] == "-":
                 char.registers[lastVarAction["register"]][-1] -= int(lastVarAction["number"])
            if lastVarAction["action"] == "/":
                 char.registers[lastVarAction["register"]][-1] //= int(lastVarAction["number"])
            if lastVarAction["action"] == "%":
                 char.registers[lastVarAction["register"]][-1] %= int(lastVarAction["number"])
            if lastVarAction["action"] == "*":
                 char.registers[lastVarAction["register"]][-1] *= int(lastVarAction["number"])

            charState["commandKeyQueue"] = [(key,flags+["norecord"])] + charState["commandKeyQueue"]
            charState["varActions"].pop()
            return

    if not "ifCondition" in charState:
        charState["ifCondition"] = []
    if not "ifParam1" in charState:
        charState["ifParam1"] = []
    if not "ifParam2" in charState:
        charState["ifParam2"] = []
    if key in ("%",):
        if charState["recordingTo"] and not "norecord" in flags:
            charState["macros"][charState["recordingTo"]].append("%")
        charState["ifCondition"].append(None)
        charState["ifParam1"].append([])
        charState["ifParam2"].append([])
        return

    if len(charState["ifCondition"]) and not key in ("%","lagdetection","lagdetection_"):
        if charState["recordingTo"] and not "norecord" in flags:
            charState["macros"][charState["recordingTo"]].append(key)
        if charState["ifCondition"][-1] == None:
            charState["ifCondition"][-1] = key
            char.messages.append(charState["ifCondition"][-1])
        elif charState["ifParam1"][-1] in ([],[("_",["norecord"])]):
            charState["ifParam1"][-1].append((key,["norecord"]))
            char.messages.append(charState["ifParam1"][-1])
        elif charState["ifParam2"][-1] in ([],[("_",["norecord"])]):
            charState["ifParam2"][-1].append((key,["norecord"]))
            char.messages.append(charState["ifParam2"][-1])

            if not charState["ifParam2"][-1] in ([],[("_",["norecord"])]):
                conditionTrue = True

                if charState["ifCondition"][-1] == "i":
                    if len(char.inventory) == 0:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "b":
                    if charState["itemMarkedLast"]:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "I":
                    char.messages.append(len(char.inventory))
                    if len(char.inventory) >= 10:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == ">":
                    if "c" in char.registers and char.registers["c"][-1] > 0:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "<":
                    if "c" in char.registers and char.registers["c"][-1] < 0:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "=":
                    if "c" in char.registers and "v" in char.registers and char.registers["c"][-1] == char.registers["v"][-1]:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "f":
                    pos = (char.xPosition,char.yPosition)
                    if char.container and pos in char.container.itemByCoordinates and len(char.container.itemByCoordinates[pos]) > 0:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "t":
                    if char.satiation < 250:
                        conditionTrue = True
                    else:
                        conditionTrue = False
                if charState["ifCondition"][-1] == "e":
                    conditionTrue = False
                    for item in char.inventory:
                        if isinstance(item,src.items.GooFlask) and item.uses > 1:
                            conditionTrue = True
                            break
                if conditionTrue:
                    charState["commandKeyQueue"] = charState["ifParam1"][-1] + charState["commandKeyQueue"]
                else:
                    charState["commandKeyQueue"] = charState["ifParam2"][-1] + charState["commandKeyQueue"]

                char.messages.append((charState["ifCondition"][-1],charState["ifParam1"][-1],charState["ifParam2"][-1]))
                charState["ifCondition"].pop()
                charState["ifParam1"].pop()
                charState["ifParam2"].pop()
        return

    if charState["recording"]:
        if not key in ("lagdetection","lagdetection_","-"):
            if charState["recordingTo"] == None:
                charState["recordingTo"] = key
                charState["macros"][charState["recordingTo"]] = []
                char.messages.append("start recording to: %s"%(charState["recordingTo"]))
                return
            else:
                if not charState["replay"] and not charState["doNumber"] and not "norecord" in flags:
                    charState["macros"][charState["recordingTo"]].append(key)

    if key in "0123456789":
        if charState["number"] == None:
            charState["number"] = ""
        charState["number"] += key
        key = commandChars.ignore

    if key in ("%",):
        charState["loop"].append(2)
        return
    
    if charState["loop"] and not key in ("lagdetection","lagdetection_",commandChars.ignore,"_","~"):
        if not charState["replay"]:
            commands = []
            commands.append(("§",["norecord"]))
            commands.append((key,["norecord"]))
            charState["commandKeyQueue"] = commands+charState["commandKeyQueue"]
            charState["loop"].pop()
        else:
            commands = []
            commands.append(("§",["norecord"]))
            commands.append(("_",["norecord"]))
            commands.append((key,["norecord"]))
            charState["commandKeyQueue"] = commands+charState["commandKeyQueue"]
            charState["loop"].pop()

    if key in ("-",):
        if not charState["recording"]:
            char.messages.append("press key to record to")
            if mainChar == char and not "norecord" in flags:
                header.set_text((urwid.AttrSpec("default","default"),"observe"))
                text = """

press key to record to.

current macros:

"""
                for key,value in charState["macros"].items():
                    compressedMacro = ""
                    for keystroke in value:
                        if len(keystroke) == 1:
                            compressedMacro += keystroke
                        else:
                            compressedMacro += "/"+keystroke+"/"

                    text += """
%s - %s"""%(key,compressedMacro)

                header.set_text((urwid.AttrSpec("default","default"),"record macro"))
                main.set_text((urwid.AttrSpec("default","default"),text))
                footer.set_text((urwid.AttrSpec("default","default"),""))
                char.specialRender = True

            charState["recording"] = True
            return
        else:
            charState["recording"] = False
            if charState["recordingTo"]:
                char.messages.append("recorded: %s to %s"%(''.join(charState["macros"][charState["recordingTo"]]),charState["recordingTo"]))
            charState["recordingTo"] = None

    if charState["replay"] and not key in ("lagdetection","lagdetection_","~",):
        if charState["replay"] and charState["replay"][-1] == 2:
            if not charState["number"]:

                charState["replay"][-1] = 1
                if charState["recording"] and not charState["doNumber"] and not "norecord" in flags and charState["recordingTo"]:
                    charState["macros"][charState["recordingTo"]].append(key)

                if key in charState["macros"]:
                    char.messages.append("replaying %s: %s"%(key,''.join(charState["macros"][key])))
                    commands = []
                    for keyPress in charState["macros"][key]:
                        commands.append((keyPress,["norecord"]))
                    #processAllInput(commands)
                    charState["commandKeyQueue"] = commands+charState["commandKeyQueue"]
                else:
                    char.messages.append("no macro recorded to %s"%(key))

                charState["replay"].pop()
            else:
                num = int(charState["number"])
                charState["number"] = None

                charState["doNumber"] = True

                if charState["recording"] and not "norecord" in flags and charState["recordingTo"]:
                    charState["macros"][charState["recordingTo"]].append(key)

                commands = []
                counter = 0
                while counter < num:
                    commands.append(("_",["norecord"]))
                    commands.append((key,["norecord"]))
                    counter += 1
                charState["replay"].pop()
                #processAllInput(commands)
                charState["commandKeyQueue"] = commands+charState["commandKeyQueue"]

                charState["doNumber"] = False

        return
    if key in ("_",):

        if mainChar == char and not "norecord" in flags:
            header.set_text((urwid.AttrSpec("default","default"),"observe"))
            text = """

press key for macro to replay

current macros:

"""
            for key,value in charState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"

                text += """
    %s - %s"""%(key,compressedMacro)

            header.set_text((urwid.AttrSpec("default","default"),"record macro"))
            main.set_text((urwid.AttrSpec("default","default"),text))
            footer.set_text((urwid.AttrSpec("default","default"),""))
            char.specialRender = True

        charState["replay"].append(2)
        return

    if charState["number"] and not key in (commandChars.ignore,"lagdetection","lagdetection_"):
            num = int(charState["number"])
            charState["number"] = None

            charState["doNumber"] = True

            commands = []
            counter = 0
            while counter < num:
                commands.append((key,["norecord"]))
                counter += 1
            #processAllInput(commands)
            charState["commandKeyQueue"] = commands+charState["commandKeyQueue"]

            charState["doNumber"] = False
            return

    # save and quit
    if key in (commandChars.quit_normal, commandChars.quit_instant):
        gamestate.save()
        raise urwid.ExitMainLoop()

    if key in ('S',):
        gamestate.save()
        return

    if key in ('o',):
        if mainChar == char and not "norecord" in flags:
            header.set_text((urwid.AttrSpec("default","default"),"observe"))
            main.set_text((urwid.AttrSpec("default","default"),"""

select what you want to observe

* p - get position of something

"""))
            footer.set_text((urwid.AttrSpec("default","default"),""))
            char.specialRender = True
        char.enumerateState.append({"type":None}) 
        return

    if key in ('<',):
        if mainChar == char and not "norecord" in flags:
            text = """

type key for the register to pop.

current registers

"""
            for key,value in char.registers.items(): 
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(item))
                text += """
%s - %s"""%(key,",".join(convertedValues))

            header.set_text((urwid.AttrSpec("default","default"),"popping registers"))
            main.set_text((urwid.AttrSpec("default","default"),text))
            footer.set_text((urwid.AttrSpec("default","default"),""))
            char.specialRender = True

        char.doStackPop = True
        return
    if key in ('>',):
        if mainChar == char and "norecord" in flags:
            text = """

type key for the register to push.

current registers

"""
            for key,value in char.registers.items(): 
                convertedValues = []
                for item in reversed(value):
                    convertedValues.append(str(item))
                text += """
%s - %s"""%(key,",".join(convertedValues))

            header.set_text((urwid.AttrSpec("default","default"),"pushing registers"))
            main.set_text((urwid.AttrSpec("default","default"),text))
            footer.set_text((urwid.AttrSpec("default","default"),""))
            char.specialRender = True

        char.doStackPush = True
        return

    # bad code: global variables
    global lastLagDetection
    global idleCounter
    global pauseGame
    global ticksSinceDeath

    # show the scrolling footer
    # bad code: this should be contained in an object
    if key in ("lagdetection","lagdetection_"):
        # show the scrolling footer
        if (not charState["submenue"]) and (not len(cinematics.cinematicQueue) or not cinematics.cinematicQueue[0].overwriteFooter):
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
                   footer.set_text(doubleFooterText[footerPosition:screensize[0]-1+footerPosition])
                   if footerPosition == footerLength:
                       footerPosition = 0
                   else:
                       footerPosition += 1
               footerSkipCounter += 1

        # set the cinematic specific footer
        else:
            footerSkipCounter = 20
            if not charState["submenue"]:
                footer.set_text(" "+cinematics.cinematicQueue[0].footerText)
                if isinstance(cinematics.cinematicQueue[0], src.cinematics.TextCinematic) and cinematics.cinematicQueue[0].firstRun:
                    cinematics.cinematicQueue[0].advance()
            else:
                footer.set_text(" "+charState["submenue"].footerText)

    # handle lag detection
    # bad code: lagdetection is abused as a timer
    if key in ("lagdetection","lagdetection_"):

        # trigger the next lagdetection keystroke
        lastLagDetection = time.time()

        # advance the game if the character stays idle
        if len(cinematics.cinematicQueue) or pauseGame:
            return
        idleCounter += 1
        if idleCounter < 15 or not idleCounter%10 == 0:
            return
        key = commandChars.wait

    # reset activity counter
    else:
        idleCounter = 0

    # discard keysstrokes, if they were not processed for too long
    ignoreList = (commandChars.autoAdvance, commandChars.quit_instant, commandChars.ignore,commandChars.quit_delete, commandChars.pause, commandChars.show_quests, commandChars.show_quests_detailed, commandChars.show_inventory, commandChars.show_inventory_detailed, commandChars.show_characterInfo)
    if not key in ignoreList:
        if lastLagDetection < time.time()-0.4:
            pass
            #return

    pauseGame = False

    # repeat autoadvance keystrokes
    # bad code: keystrokes are abused here, a timer would be more appropriate
    if key in (commandChars.autoAdvance):
        if not charState["ignoreNextAutomated"]:
            loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)
        else:
            charState["ignoreNextAutomated"] = False

    # handle a keystroke while on map or in cinemetic
    if not charState["submenue"]:

        # handle cinematics
        if len(cinematics.cinematicQueue):
            if mainChar == char and not "norecord" in flags:
                char.specialRender = True
            
            # get current cinematic
            cinematic = cinematics.cinematicQueue[0]

            # allow to quit even within a cutscene
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                # bad code: directly calls urwid
                raise urwid.ExitMainLoop()

            # skip the cinematic if requested
            elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance,commandChars.redraw,"enter") and cinematic.skipable:
                cinematic.abort()
                cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
                loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
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
        if key in (commandChars.ignore):
            doAdvanceGame = False

        # invalidate input for unconcious char
        if char.unconcious:
            key = commandChars.wait

        # show a few rounds after death and exit
        if char.dead:
            if not ticksSinceDeath:
                ticksSinceDeath = gamestate.tick
            key = commandChars.wait
            if gamestate.tick > ticksSinceDeath+5:
                # destroy the gamestate
                # bad pattern: should not always destroy gamestate
                #saveFile = open("gamestate/gamestate.json","w")
                #saveFile.write("you lost")
                #saveFile.close()
                #raise urwid.ExitMainLoop()
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
                    char.messages.append("debug not enabled")

            # destroy save and quit
            if key in (commandChars.quit_delete,):
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("reset")
                saveFile.close()
                raise urwid.ExitMainLoop()

            # kill one of the autoadvance keystrokes
            # bad pattern: doesn't actually pause
            if key in (commandChars.pause):
                charState["ignoreNextAutomated"] = True
                doAdvanceGame = False

            '''
            move the player into a direction
            bad code: huge inline function + player vs. npc movement should use same code
            '''
            def moveCharacter(direction):
                if not char.room:
                    global terrain
                    if direction == "west":
                        if char.xPosition == 0+1:
                            char.messages.append("a force field pushes you back")
                            #char.messages.append("switch to")
                            #char.messages.append((terrain.xPosition-1,terrain.yPosition))
                            #terrain = gamestate.terrainMap[terrain.yPosition][terrain.xPosition-1]
                            #char.xPosition = 15*15
                            #char.terrain = terrain
                            return
                    if direction == "east":
                        if char.xPosition == 15*15-2:
                            char.messages.append("a force field pushes you back")
                            #char.messages.append("switch to")
                            #char.messages.append((terrain.xPosition+1,terrain.yPosition))
                            #terrain = gamestate.terrainMap[terrain.yPosition][terrain.xPosition+1]
                            #char.xPosition = 0
                            #char.terrain = terrain
                            return
                    if direction == "north":
                        if char.yPosition == 0+1:
                            char.messages.append("a force field pushes you back")
                            #terrain = gamestate.terrainMap[terrain.xPosition][terrain.yPosition-1]
                            #char.yPosition = 15*15
                            #char.terrain = terrain
                            return
                    if direction == "south":
                        if char.yPosition == 15*15-2:
                            char.messages.append("a force field pushes you back")
                            #terrain = gamestate.terrainMap[terrain.xPosition][terrain.yPosition+1]
                            #char.yPosition = 0
                            #char.terrain = terrain
                            return

                # do inner room movement
                if char.room:
                    item = char.room.moveCharacterDirection(char,direction)

                    # remember items bumped into for possible interaction
                    if item:
                        char.messages.append("You cannot walk there "+str(direction))
                        char.messages.append("press "+commandChars.activate+" to apply")
                        if noAdvanceGame == False:
                            header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))
                        return item

                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    if direction == "north":
                        bigX = (char.xPosition)//15
                        bigY = (char.yPosition-1)//15
                    elif direction == "south":
                        bigX = (char.xPosition)//15
                        bigY = (char.yPosition+1)//15
                    elif direction == "east":
                        bigX = (char.xPosition+1)//15
                        bigY = (char.yPosition)//15
                    elif direction == "west":
                        bigX = (char.xPosition)//15
                        bigY = (char.yPosition-1)//15

                    # gather the rooms the player might step into
                    roomCandidates = []
                    for coordinate in [(bigX,bigY),
                                       (bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY),
                                       (bigX-2,bigY),(bigX-2,bigY-1),(bigX-2,bigY-2),(bigX-1,bigY-2),(bigX,bigY-2),(bigX+1,bigY-2),(bigX+2,bigY-2),(bigX+2,bigY-1),
                                       (bigX+2,bigY),(bigX+2,bigY-1),(bigX+2,bigY-2),(bigX+1,bigY-2),(bigX,bigY-2),(bigX-1,bigY-2),(bigX-2,bigY-2),(bigX-1,bigY-2),
                                      ]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    '''
                    move a player into a room
                    bad code: inline function within inline function
                    '''
                    def enterLocalised(room,localisedEntry):

                        # get the entry point in room coordinates
                        if localisedEntry in room.walkingAccess:
                            # check if the entry point is blocked (by a door)
                            for item in room.itemByCoordinates[localisedEntry]:

                                # handle collisions
                                if not item.walkable:
                                    # print some info
                                    char.messages.append("you need to open the door first")
                                    char.messages.append("press "+commandChars.activate+" to apply")
                                    if noAdvanceGame == False:
                                        header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                                    # remember the item for interaction and abort
                                    return item

                                # teleport the character into the room
                                room.addCharacter(char,localisedEntry[0],localisedEntry[1])
                                char.messages.append(("removing from terrain",room))
                                try:
                                    terrain.characters.remove(char)
                                except:
                                    char.messages.append("fail,fail,fail")

                                return

                        # do not move player into the room
                        else:
                            char.messages.append("you cannot move there")

                    # check if character has entered a room
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check north
                        if direction == "north":
                            # check if the character crossed the edge of the room
                            if room.yPosition*15+room.offsetY+room.sizeY == char.yPosition:
                                if room.xPosition*15+room.offsetX-1 < char.xPosition and room.xPosition*15+room.offsetX+room.sizeX > char.xPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = (char.xPosition%15-room.offsetX,char.yPosition%15-room.offsetY-1)
                                    if localisedEntry[1] == -1:
                                        localisedEntry = (localisedEntry[0],room.sizeY-1)

                        # check south
                        elif direction == "south":
                            # check if the character crossed the edge of the room
                            if room.yPosition*15+room.offsetY == char.yPosition+1:
                                if room.xPosition*15+room.offsetX-1 < char.xPosition and room.xPosition*15+room.offsetX+room.sizeX > char.xPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((char.xPosition-room.offsetX)%15,(char.yPosition-room.offsetY+1)%15)

                        # check east
                        elif direction == "east":
                            # check if the character crossed the edge of the room
                            if room.xPosition*15+room.offsetX == char.xPosition+1:
                                if room.yPosition*15+room.offsetY < char.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > char.yPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((char.xPosition-room.offsetX+1)%15,(char.yPosition-room.offsetY)%15)

                        # check west
                        elif direction == "west":
                            # check if the character crossed the edge of the room
                            if room.xPosition*15+room.offsetX+room.sizeX == char.xPosition:
                                if room.yPosition*15+room.offsetY < char.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > char.yPosition:
                                    # get the entry point in room coordinates
                                    hadRoomInteraction = True
                                    localisedEntry = ((char.xPosition-room.offsetX-1)%15,(char.yPosition-room.offsetY)%15)

                        else:
                            debugMessages.append("moved into invalid direction: "+str(direction))

                        # move player into the room
                        if hadRoomInteraction:
                            item = enterLocalised(room,localisedEntry)
                            if item:
                                return item
                            break

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        if direction == "north":
                            destCoord = (char.xPosition,char.yPosition-1)
                        elif direction == "south":
                            destCoord = (char.xPosition,char.yPosition+1)
                        elif direction == "east":
                            destCoord = (char.xPosition+1,char.yPosition)
                        elif direction == "west":
                            destCoord = (char.xPosition-1,char.yPosition)

                        if destCoord in terrain.itemByCoordinates:
                            foundItems = terrain.itemByCoordinates[destCoord]
                        else:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        item = None
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                char.messages.append("You cannot walk there")
                                char.messages.append("press "+commandChars.activate+" to apply")
                                if noAdvanceGame == False:
                                    header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

                                # remember the item for interaction and abort
                                foundItem = True
                                break

                        # move the character
                        if not foundItem:
                            if direction == "north":
                                char.yPosition -= 1
                            elif direction == "south":
                                char.yPosition += 1
                            elif direction == "east":
                                char.xPosition += 1
                            elif direction == "west":
                                char.xPosition -= 1
                            char.changed()

                        return item

            # move the player
            if key in (commandChars.move_north,"up"):
                charState["itemMarkedLast"] = moveCharacter("north")
                if charState["itemMarkedLast"] and not charState["itemMarkedLast"].walkable:
                    return
            if key in (commandChars.move_south,"down"):
                charState["itemMarkedLast"] = moveCharacter("south")
                if charState["itemMarkedLast"] and not charState["itemMarkedLast"].walkable:
                    return
            if key in (commandChars.move_east,"right"):
                charState["itemMarkedLast"] = moveCharacter("east")
                if charState["itemMarkedLast"] and not charState["itemMarkedLast"].walkable:
                    return
            if key in (commandChars.move_west,"left"):
                charState["itemMarkedLast"] = moveCharacter("west")
                if charState["itemMarkedLast"] and not charState["itemMarkedLast"].walkable:
                    return

            # murder the next available character
            # bad pattern: player should be able to select whom to kill if there are multiple targets
            if key in (commandChars.attack):
                if not "NaiveMurderQuest" in char.solvers:
                    char.messages.append("you do not have the nessecary solver yet")
                else:
                    # bad code: should be part of a position object
                    adjascentFields = [(char.xPosition,char.yPosition),
                                       (char.xPosition-1,char.yPosition),
                                       (char.xPosition+1,char.yPosition),
                                       (char.xPosition,char.yPosition-1),
                                       (char.xPosition,char.yPosition+1),
                                      ]
                    for enemy in char.container.characters:
                        if enemy == char:
                            continue
                        if not (enemy.xPosition,char.yPosition) in adjascentFields:
                            continue
                        enemy.die()
                        break

            # activate an item 
            if key in (commandChars.activate):
                if not "NaiveActivateQuest" in char.solvers:
                    char.messages.append("you do not have the nessecary solver yet")
                else:
                    # activate the marked item
                    if charState["itemMarkedLast"]:
                        charState["itemMarkedLast"].apply(char)

                    # activate an item on floor
                    else:
                        for item in char.container.itemsOnFloor:
                            if item.xPosition == char.xPosition and item.yPosition == char.yPosition:
                                item.apply(char)
                                break

            # examine an item 
            if key in (commandChars.examine):
                if not "ExamineQuest" in char.solvers:
                    char.messages.append("you do not have the nessecary solver yet")
                else:
                    # examine the marked item
                    if charState["itemMarkedLast"]:
                        char.examine(charState["itemMarkedLast"])

                    # examine an item on floor
                    else:
                        for item in char.container.itemsOnFloor:
                            if item.xPosition == char.xPosition and item.yPosition == char.yPosition:
                                char.examine(item)
                                break

            # drop first item from inventory
            # bad pattern: the user has to have the choice for what item to drop
            if key in (commandChars.drop):
                if not "NaiveDropQuest" in char.solvers:
                    char.messages.append("you do not have the nessecary solver yet")
                else:
                    if len(char.inventory):
                        char.drop(char.inventory[-1])

            # drink from the first available item in inventory
            # bad pattern: the user has to have the choice from what item to drink from
            # bad code: drinking should happen in character
            if key in (commandChars.drink):
                character = char
                for item in character.inventory:
                    if isinstance(item,src.items.GooFlask):
                        if item.uses > 0:
                            item.apply(character)
                            break

            # pick up items
            # bad code: picking up should happen in character
            if key in (commandChars.pickUp):
                if not "NaivePickupQuest" in char.solvers:
                    char.messages.append("you do not have the nessecary solver yet")
                else:
                    if len(char.inventory) >= 10:
                        char.messages.append("you cannot carry more items")
                    else:
                        # get the position to pickup from
                        if charState["itemMarkedLast"]:
                            try:
                                pos = (charState["itemMarkedLast"].xPosition,charState["itemMarkedLast"].yPosition)
                            except:
                                print(charState["itemMarkedLast"])
                                pos = (0,0)
                        else:
                            pos = (char.xPosition,char.yPosition)

                        # pickup an item from this coordinate
                        itemByCoordinates = char.container.itemByCoordinates
                        if pos in itemByCoordinates:
                            for item in itemByCoordinates[pos]:
                                item.pickUp(char)
                                if not item.walkable:
                                    char.container.calculatePathMap()
                                break

            # open chat partner selection
            if key in (commandChars.hail):
                charState["submenue"] = ChatPartnerselection()

            char.automated = False
            # do automated movement for the main character
            if key in (commandChars.advance,commandChars.autoAdvance):
                if len(char.quests):
                    charState["lastMoveAutomated"] = True
                    char.automated = True
                else:
                    pass

            # recalculate the questmarker since it could be tainted
            elif not key in (commandChars.pause):
                charState["lastMoveAutomated"] = False
                if char.quests:
                    char.setPathToQuest(char.quests[0])

        # drop the marker for interacting with an item after bumping into it 
        # bad code: ignore autoadvance opens up an unintended exploit
        if not key in ("lagdetection","lagdetection_",commandChars.wait,commandChars.autoAdvance):
            charState["itemMarkedLast"] = None

        # enforce 60fps
        # bad code: urwid specific code should be isolated
        global lastRedraw
        if lastRedraw < time.time()-0.016:
            loop.draw_screen()
            lastRedraw = time.time()

        char.specialRender = False

        # doesn't open the dev menu and toggles rendering mode instead
        # bad code: code should act as advertised
        if key in (commandChars.devMenu):
            if displayChars.mode == "unicode":
                displayChars.setRenderingMode("pureASCII")
            else:
                displayChars.setRenderingMode("unicode")

        # open quest menu
        if key in (commandChars.show_quests):
            charState["submenue"] = QuestMenu()

        # open help menu
        if key in (commandChars.show_help):
            charState["submenue"] = HelpMenu()

        # open inventory
        if key in (commandChars.show_inventory):
            charState["submenue"] = InventoryMenu(char)

        # open the menu for giving quests
        if key in (commandChars.show_quests_detailed):
            charState["submenue"] = AdvancedQuestMenu()

        # open the character information
        if key in (commandChars.show_characterInfo):
            charState["submenue"] = CharacterInfoMenu()

        # open the help screen
        if key in (commandChars.show_help):
            char.specialRender = True        
            pauseGame = True

    # render submenues
    if charState["submenue"]:

        # set flag to not render the game
        if mainChar == char and not "norecord" in flags:
            char.specialRender = True        
        pauseGame = True

        # let the submenu handle the keystroke
        lastSubmenu = charState["submenue"]
        done = charState["submenue"].handleKey(key)

        if not lastSubmenu == charState["submenue"]:
            charState["submenue"].handleKey("~")
            done = False

        # reset rendering flags
        if done:
            charState["submenue"] = None
            pauseGame = False
            char.specialRender = False
            doAdvanceGame = False

    if noAdvanceGame:
        return
        
    # render the game
    if not char.specialRender:
        
        """
        # advance the game
        if doAdvanceGame:
            global shownStarvationWarning
            if char.satiation < 30 and char.satiation > -1:
                if not shownStarvationWarning:
                    #cinematics.showCinematic("you will starve in %s ticks. drink something"%(char.satiation))
                    shownStarvationWarning = True
                if char.satiation == 0:
                    char.messages.append("you starved")
            else:
                shownStarvationWarning = False
            advanceGame()
        """

        # render information on top
        if noAdvanceGame == False:
            header.set_text((urwid.AttrSpec("default","default"),renderHeader(char)))

        # render map
        # bad code: display mode specific code
        canvas = render(char)
        main.set_text((urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible()));
        if (useTiles):
            canvas.setPygameDisplay(pydisplay,pygame,tileSize)


    if charState["replay"] or charState["doNumber"]:
        text = ""
        for cmd in reversed(charState["commandKeyQueue"]):
            item = cmd[0]
            if isinstance(item,list) or isinstance(item,tuple) or item in ("lagdetection","lagdetection_"):
                continue
            text += str(cmd[0])
        footer.set_text((urwid.AttrSpec("default","default"),text))

    # show the game won screen
    # bad code: display mode specific code
    if gamestate.gameWon:
        main.set_text((urwid.AttrSpec("default","default"),""))
        main.set_text((urwid.AttrSpec("default","default"),"credits"))
        header.set_text((urwid.AttrSpec("default","default"),"good job"))

'''
The base class for submenues offering selections
bad code: there is redundant code from the specific submenus that should be put here
'''
class SubMenu(src.saveing.Saveable):
    '''
    straightforward state initialization
    '''
    def __init__(self, default=None):
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.footerText = "press w / s to move selection up / down, press enter / j / k to select, press esc to exit"
        self.followUp = None
        import collections
        self.options = collections.OrderedDict()
        self.niceOptions = collections.OrderedDict()
        self.default = default
        super().__init__()
        self.attributesToStore.extend(["state","selectionIndex","persistentText","footerText","type","query","lockOptions"])
        self.initialState = self.getState()

    '''
    set internal state from state dictionary
    '''
    def setState(self,state):
        super().setState(state)

        # load options
        if "options" in state:
            if state["options"] == None:
                self.options = None
            else:
                import collections
                newOptions = collections.OrderedDict()
                for option in state["options"]:
                    newOptions[option[0]] = option[1]
                self.options = newOptions
        if "niceOptions" in state:
            if state["niceOptions"] == None:
                self.niceOptions = None
            else:
                import collections
                newNiceOptions = collections.OrderedDict()
                for option in state["niceOptions"]:
                    newNiceOptions[option[0]] = option[1]
                self.niceOptions = newNiceOptions
        
    '''
    get state as dictionary
    '''
    def getState(self):
        state = super().getState()

        # store options
        if self.options == None:
            serialisedOptions = None
        else:
            serialisedOptions = []
            for k,v in self.options.items():
                serialisedOptions.append((k,str(v)))
        state["options"] = serialisedOptions
        if self.niceOptions == None:
            serialisedOptions = None
        else:
            serialisedOptions = []
            for k,v in self.niceOptions.items():
                serialisedOptions.append((k,str(v)))
        state["niceOptions"] = serialisedOptions
           
        return state


    '''
    sets the options to select from
    '''
    def setOptions(self, query, options):
        # convert options to ordered dict
        import collections
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

    '''
    straightforward getter for the selected item
    '''
    def getSelection(self):
        return self.selection

    '''
    show the options and allow the user to select one
    '''
    def handleKey(self, key):
        # exit submenue
        if key == "esc":
            return True

        if key in (commandChars.autoAdvance, commandChars.advance):
            if not self.default == None:
                self.selection = self.default
            else:
                self.selection = list(self.options.values())[0]
            self.options = None
            if self.followUp:
                self.followUp()
            return True

        # show question
        out = "\n"
        out += self.query+"\n"

        # handle the selection of options
        if not self.lockOptions:
            # change the marked option
            if key in ("w","up",):
                self.selectionIndex -= 1
                if self.selectionIndex == 0:
                    self.selectionIndex = len(self.options)
            if key in ("s","down",):
                self.selectionIndex += 1
                if self.selectionIndex > len(self.options):
                    self.selectionIndex = 1
            # select the marked option
            if key in ["enter","j","k","right"]:
                # bad code: transforming the key to the shortcut is needlessly complicated
                if len(self.options.items()):
                    key = list(self.options.items())[self.selectionIndex-1][0]
                else:
                    self.selection = None
                    self.done = True
                    return True

            # select option by shortcut
            if key in self.options:
                self.selection = self.options[key]
                self.options = None
                if self.followUp:
                    self.followUp()
                return True
        else:
             self.lockOptions = False

        # render the options
        counter = 0
        for k,v in self.niceOptions.items():
            counter += 1
            if counter == self.selectionIndex:
                out += str(k)+" ->"+str(v)+"\n"
            else:
                out += str(k)+" - "+str(v)+"\n"

        # show the rendered options 
        # bad code: uwrid specific code
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText+"\n\n"+out))

        return False

    '''
    set text in urwid
    bad code: should either be used everywhere or be removed
    bad code: urwid specific code
    '''
    def set_text(self,text):
        main.set_text((urwid.AttrSpec("default","default"),text))

'''
does a simple selection and terminates
bad code: this does nothing the Submenu doesn't do
'''
class SelectionMenu(SubMenu):
    '''
    set up the selection
    '''
    def __init__(self, text, options, default=None):
        self.type = "SelectionMenu"
        super().__init__(default=default)
        self.setOptions(text, options)

    '''
    handles the key
    '''
    def handleKey(self, key):
        # exit submenue
        if key == "esc":
            return True
        header.set_text("")

        # let superclass handle the actual selection
        if not self.getSelection():
             super().handleKey(key)

        # stop when done
        if self.getSelection():
            return True
        else:
            return False

'''
Spawns a Chat submenu with a player selected character
bad code: since there is no need to wait for some return this submenue should not wrap around the Chat menu
bad code: sub menues should be implemented in the base class
'''
class ChatPartnerselection(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.type = "ChatPartnerselection"
        self.subMenu = None
        super().__init__()

    '''
    get state as dictionary
    '''
    def getState(self):
        state = super().getState()
        if self.subMenu:
            state["subMenu"] = self.subMenu.getState()
        else:
            state["subMenu"] = None

        return state
    
    '''
    set internal state from state as dictionary
    '''
    def setState(self,state):
        super().setState(state)

        if "subMenu" in state:
            if state["subMenu"]:
                self.subMenu = getSubmenuFromState(state["subMenu"])
            else:
                self.subMenu = None

    '''
    set up the selection and spawn the chat 
    '''
    def handleKey(self, key):
        # wrap around the chat menu
        if self.subMenu:
            return self.subMenu.handleKey(key)

        # exit the submenu
        if key == "esc":
            return True

        # set title
        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # offer the player the option to select from characters to talk to
        # bad code: should be done in __init__
        if not self.options and not self.getSelection():
            options = []
            # get characters in room
            if mainChar.room:
                for char in mainChar.room.characters:
                    if char == mainChar:
                        continue
                    options.append((char,char.name))
            # get character on terrain
            else:
                for char in mainChar.terrain.characters:
                    # bad pattern: should only list nearby characters
                    if char == mainChar:
                        continue
                    options.append((char,char.name))

                # get nearby rooms
                bigX = mainChar.xPosition//15
                bigY = mainChar.yPosition//15
                rooms = []
                coordinates = [(bigX,bigY),(bigX-1,bigY),(bigX+1,bigY),(bigX,bigY-1),(bigX,bigY+1)]
                for coordinate in coordinates:
                    if not coordinate in terrain.roomByCoordinates:
                        continue
                    rooms.extend(terrain.roomByCoordinates[coordinate])

                # add character from nearby open rooms
                for room in rooms:
                    if not room.open:
                        continue 

                    for char in room.characters:
                        options.append((char,char.name))
                
            self.setOptions("talk with whom?",options)

        # delegate the actual selection to the super class
        if not self.getSelection():
             super().handleKey(key)

        # spawn the chat submenu
        if self.getSelection():
            self.subMenu = src.chats.ChatMenu(self.selection)
            self.subMenu.handleKey(key)

        # wait for input
        else:
            return False

'''
minimal debug ability
'''
class DebugMenu(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self,char=None):
        self.type = "DebugMenu"
        super().__init__()
        self.firstRun = True

    '''
    show some debug output
    '''
    def handleKey(self, key):
        # exit submenu
        if key == "esc":
            return True

        if self.firstRun:
            # show debug output
            main.set_text(str(terrain.tutorialStorageRooms[3].storageSpace)+"\n"+str(list(reversed(terrain.tutorialStorageRooms[3].storageSpace)))+"\n\n"+str(terrain.tutorialStorageRooms[3].storedItems))
            self.firstRun = False
            return False
        else:
            return True

'''
show the quests for a character and allow player interaction
'''
class QuestMenu(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self,char=None):
        self.type = "QuestMenu"
        self.lockOptions = True
        if not char:
            char = mainChar
        self.char = char
        self.offsetX = 0
        self.questIndex = 0
        super().__init__()

    '''
    show a questlist and handle interactions
    overrides the superclasses method completely
    '''
    def handleKey(self, key):
        # exit submenu
        if key == "esc":
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
        if self.questIndex > len(self.char.quests)-1:
            self.questIndex = len(self.char.quests)-1

        # make the selected quest active
        if key == "j":
            if self.questIndex:
                quest = self.char.quests[self.questIndex]
                self.char.quests.remove(quest)
                self.char.quests.insert(0,quest)
                self.char.setPathToQuest(quest)
                self.questIndex = 0

        # render the quests
        addition = ""
        if self.char == mainChar:
            addition = " (you)"
        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview for "+self.char.name+""+addition+"\n(press "+commandChars.show_quests_detailed+" for the extended quest menu)\n\n"))
        self.persistentText = []
        self.persistentText.append(renderQuests(char=self.char,asList=True,questIndex = self.questIndex))

        # spawn the quest menu for complex quest handling
        if not self.lockOptions:
            if key in ["q"]:
                global submenue
                submenue = AdvancedQuestMenu()
                submenue.handleKey(key)
                return False
        self.lockOptions = False

        # add interaction instructions
        self.persistentText.extend(["\n","* press q for advanced quests\n","* press W to scroll up","\n","* press S to scroll down","\n","\n"])

        # flatten the mix of strings and urwid format so that it is less recursive to workaround an urwid bug
        # bad code: should be elsewhere
        def flatten(pseudotext):
            newList = []
            for item in pseudotext:
                if isinstance(item,list):
                   for subitem in flatten(item):
                      newList.append(subitem) 
                elif isinstance(item,tuple):
                   newList.append((item[0],flatten(item[1])))
                else:
                   newList.append(item)
            return newList
        self.persistentText = flatten(self.persistentText)

        # show rendered quests via urwid
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
show the players inventory
bad code: should be abstracted
bad code: uses global functions to render
'''
class InventoryMenu(SubMenu):
    type = "InventoryMenu"

    def __init__(self,char=None):
        self.subMenu = None
        self.skipKeypress = False
        self.activate = False
        self.drop = False
        self.char = char
        super().__init__()
        self.footerText = "press j to activate, press l to drop, press esc to exit"

    '''
    show the inventory
    bad pattern: no player interaction
    '''
    def handleKey(self, key):
        if self.subMenu:
            self.subMenu.handleKey(key)
            if not self.subMenu.getSelection() == None:
                if self.activate:
                    if not "NaiveActivateQuest" in self.char.solvers:
                        self.persistentText = (urwid.AttrSpec("default","default"),"you do not have the nessecary solver yet")
                        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
                    else:
                        text = "you activate the "+self.char.inventory[self.subMenu.getSelection()].name
                        self.persistentText = (urwid.AttrSpec("default","default"),text)
                        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
                        self.char.messages.append(text)
                        self.char.inventory[self.subMenu.getSelection()].apply(self.char)
                    self.activate = False
                if self.drop:
                    if not "NaiveDropQuest" in self.char.solvers:
                        self.persistentText = (urwid.AttrSpec("default","default"),"you do not have the nessecary solver yet")
                        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
                    else:
                        text = "you drop the "+self.char.inventory[self.subMenu.getSelection()].name
                        self.persistentText = (urwid.AttrSpec("default","default"), text)
                        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))
                        self.char.messages.append(text)
                        self.char.drop(self.char.inventory[self.subMenu.getSelection()])
                    self.drop = False
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

            if key == "j":
                if not len(self.char.inventory):
                    return True

                options = []
                counter = 0
                for item in self.char.inventory:
                    options.append([counter,item.name])
                    counter += 1
                self.subMenu = SelectionMenu("activate what?",options)
                self.subMenu.handleKey(".")
                self.activate = True
                return False

            if key == "l":
                if not len(self.char.inventory):
                    return True

                options = []
                counter = 0
                for item in self.char.inventory:
                    options.append([counter,item.name])
                    counter += 1
                self.subMenu = SelectionMenu("drop what?",options)
                self.subMenu.handleKey(".")
                self.drop = True
                return False

        header.set_text((urwid.AttrSpec("default","default"),"\ninventory overview\n\n"))

        # bad code: uses global function
        self.persistentText = (urwid.AttrSpec("default","default"),renderInventory())

        # show the render
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
show the players inventory
'''
class InputMenu(SubMenu):
    type = "InputMenu"

    def __init__(self,query="",char=None):
        self.query = query
        self.text = ""
        super().__init__()
        self.footerText = "enter the text press enter to confirm"
        self.firstHit = True

    '''
    show the inventory
    '''
    def handleKey(self, key):

        if key == "enter":
            if self.followUp:
                self.followUp()
            return True

        if self.firstHit:
            self.firstHit = False
        else:
            self.text += key

        header.set_text((urwid.AttrSpec("default","default"),"\ntext input\n\n"))

        self.persistentText = (urwid.AttrSpec("default","default"),"\n"+self.query+"\n\n"+self.text)

        # show the render
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False


'''
show the players attributes
bad code: should be abstracted
bad code: uses global function to render
'''
class CharacterInfoMenu(SubMenu):
    type = "CharacterInfoMenu"

    '''
    show the attributes
    '''
    def handleKey(self, key):
        # exit the submenu
        if key == "esc":
            return True

        # show info
        header.set_text((urwid.AttrSpec("default","default"),"\ncharacter overview"))
        main.set_text((urwid.AttrSpec("default","default"),[mainChar.getDetailedInfo()]))
        header.set_text((urwid.AttrSpec("default","default"),""))

'''
player interaction for delegating a quest
'''
class AdvancedQuestMenu(SubMenu):
    type = "AdvancedQuestMenu"

    '''
    straighforwad state initalisation
    '''
    def __init__(self):
        self.character = None
        self.quest = None
        self.questParams = {}
        super().__init__()

    '''
    gather the quests parameters and assign the quest
    '''
    def handleKey(self, key):
        # exit submenu
        if key == "esc":
            return True

        # start rendering
        header.set_text((urwid.AttrSpec("default","default"),"\nadvanced Quest management\n"))
        out = "\n"
        if self.character:
            out += "character: "+str(self.character.name)+"\n"
        if self.quest:
            out += "quest: "+str(self.quest)+"\n"
        out += "\n"

        # let the player select the character to assign the quest to 
        if self.state == None:
            self.state = "participantSelection"
        if self.state == "participantSelection":

            # set up the options
            if not self.options and not self.getSelection():

                # add the main player as target
                options = []
                options.append((mainChar,mainChar.name+" (you)"))

                # add the main players subordinates as target
                for char in mainChar.subordinates:
                    options.append((char,char.name))
                self.setOptions("whom to give the order to: ",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)
                
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

            # add quests to select from
            if not self.options and not self.getSelection():
                options = []
                for key,value in src.quests.questMap.items():

                    # show only quests the character has done
                    if not key in mainChar.questsDone:
                        continue

                    # do not show naive quests
                    if key.startswith("Naive"):
                        continue

                    options.append((value,key))
                options.append(("special_furnace","vehicle fueling"))
                self.setOptions("what type of quest:",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            # store the type of quest to create
            if self.getSelection():
                self.state = "parameter selection"
                self.quest = self.selection
                self.selection = None
                self.lockOptions = True
                self.questParams = {}
            else:
                return False

        # let the player select the parameters for the quest
        if self.state == "parameter selection":
            if self.quest == src.quests.EnterRoomQuestMeta:

                # set up the options
                if not self.options and not self.getSelection():

                    # add a list of of rooms
                    options = []
                    for room in terrain.rooms:
                        # do not show unimportant rooms
                        if isinstance(room,src.rooms.MechArmor) or isinstance(room,src.rooms.CpuWasterRoom):
                            continue
                        options.append((room,room.name))
                    self.setOptions("select the room:",options)

                # let the superclass handle the actual selection
                if not self.getSelection():
                    super().handleKey(key)

                # store the parameter
                if self.getSelection():
                    self.questParams["room"] = self.selection
                    self.state = "confirm"
                    self.selection = None
                    self.lockOptions = True
                else:
                    return False

            elif self.quest == src.quests.StoreCargo:

                # set up the options for selecting the cargo room
                if "cargoRoom" not in self.questParams:
                    if not self.options and not self.getSelection():
                        # add a list of of rooms
                        options = []
                        for room in terrain.rooms:
                            # show only cargo rooms
                            if not isinstance(room,src.rooms.CargoRoom):
                                continue
                            options.append((room,room.name))
                        self.setOptions("select the room:",options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key)

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
                        for room in terrain.rooms:
                            # show only storage rooms
                            if not isinstance(room,src.rooms.StorageRoom):
                                continue
                            options.append((room,room.name))
                        self.setOptions("select the room:",options)

                    # let the superclass handle the actual selection
                    if not self.getSelection():
                        super().handleKey(key)

                    # store the parameter
                    if self.getSelection():
                        self.questParams["storageRoom"] = self.selection
                        self.state = "confirm"
                        self.selection = None
                        self.lockOptions = True
                    else:
                        return False
            else:
                # skip parameter selection
                self.state = "confirm"

        # get confirmation and assign quest
        if self.state == "confirm":

            # set the options for confirming the selection
            if not self.options and not self.getSelection():
                options = [("yes","yes"),("no","no")]
                if self.quest == src.quests.EnterRoomQuestMeta:
                    self.setOptions("you chose the following parameters:\nroom: "+str(self.questParams)+"\n\nDo you confirm?",options)
                else:
                    self.setOptions("Do you confirm?",options)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            if self.getSelection():
                # instanciate quest
                # bad code: repetetive code
                if self.selection == "yes":
                    if self.quest == src.quests.MoveQuestMeta:
                       questInstance = self.quest(mainChar.room,2,2,creator=void)
                    elif self.quest == src.quests.ActivateQuestMeta:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0],creator=void)
                    elif self.quest == src.quests.EnterRoomQuestMeta:
                       questInstance = self.quest(self.questParams["room"],creator=void)
                    elif self.quest == src.quests.FireFurnaceMeta:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0],creator=void)
                    elif self.quest == src.quests.WaitQuest:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.LeaveRoomQuest:
                       try:
                           questInstance = self.quest(self.character.room,creator=void)
                       except:
                           pass
                    elif self.quest == src.quests.ClearRubble:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.RoomDuty:
                       questInstance = self.quest(creator=void)
                    elif self.quest == src.quests.ConstructRoom:
                       for room in terrain.rooms:
                           if isinstance(room,src.rooms.ConstructionSite):
                               constructionSite = room
                               break
                       questInstance = self.quest(constructionSite,terrain.tutorialStorageRooms,creator=void)
                    elif self.quest == src.quests.StoreCargo:
                       for room in terrain.rooms:
                           if isinstance(room,src.rooms.StorageRoom):
                               storageRoom = room
                       questInstance = self.quest(self.questParams["cargoRoom"],self.questParams["storageRoom"],creator=void)
                    elif self.quest == src.quests.MoveToStorage:
                       questInstance = self.quest([terrain.tutorialLab.itemByCoordinates[(1,9)][0],terrain.tutorialLab.itemByCoordinates[(2,9)][0]],terrain.tutorialStorageRooms[1],creator=void)
                    elif self.quest == "special_furnace":
                        questInstance = src.quests.KeepFurnaceFiredMeta(self.character.room.furnaces[0],creator=void)
                    else:
                       questInstance = self.quest(creator=void)

                    # show some fluff
                    if not self.character == mainChar:
                       self.persistentText += self.character.name+": \"understood?\"\n"
                       self.persistentText += mainChar.name+": \"understood and in execution\"\n"

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
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
render the information section on top of the screen
bad pattern: should be configurable
'''
def renderHeader(character):
    # render the sections to display
    questSection = renderQuests(maxQuests=2)
    messagesSection = renderMessages(character)

    # calculate the size of the elements
    screensize = loop.screen.get_cols_rows()
    questWidth = (screensize[0]//3)-2
    messagesWidth = screensize[0]-questWidth-3

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
        if (rowCounter > 5):
            break

        # cut off left line
        if len(questLine) > questWidth:
            txt += questLine[:questWidth]+"┃ "
            questLine = questLine[questWidth:]

        # pad left line
        else:
            txt += questLine+" "*(questWidth-len(questLine))+"┃ "
            # bug?: doen't this pop twice?
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
            # bug?: doen't this pop twice?
            if splitedMessages:
                messagesLine = splitedMessages.pop(0)
            else:
                messagesLine = ""
        txt += "\n"
            
    # add the lower decoration
    txt += "━"*+questWidth+"┻"+"━"*(screensize[0]-questWidth-1)+"\n"

    return txt

'''
render the last x messages into a string
bad code: global function
'''
def renderMessages(character,maxMessages=5):
    txt = ""
    messages = character.messages
    if len(messages) > maxMessages:
        for message in messages[-maxMessages+1:]:
            txt += str(message)+"\n"
    else:
        for message in messages:
            txt += str(message)+"\n"

    return txt


'''
render the quests into a string or list
bad code: the asList and questIndex parameters are out of place
'''
def renderQuests(maxQuests=0,char=None, asList=False, questIndex=0):
    # basic set up
    if not char:
        char = mainChar
    if asList:
        txt = []
    else:
        txt = ""

    # render the quests
    if len(char.quests):
        counter = 0
        for quest in char.quests:
            # render quest
            if asList:
                if counter == questIndex:
                    txt.extend([(urwid.AttrSpec("#0f0","default"),"QUEST: "),quest.getDescription(asList=asList,colored=True,active=True),"\n"])
                else:
                    txt.extend([(urwid.AttrSpec("#090","default"),"QUEST: "),quest.getDescription(asList=asList,colored=True),"\n"])
            else:
                txt+= "QUEST: "+quest.getDescription(asList=asList)+"\n"

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

'''
render the inventory of the player into a string
bad code: global function
bad code: should be abstracted
'''
def renderInventory():
    char = mainChar
    txt = []
    if len(char.inventory):
        counter = 0
        for item in char.inventory:
            counter += 1
            if isinstance(item.display,int):
                txt.extend([str(counter)," - ",displayChars.indexedMapping[item.display]," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
            else:
                txt.extend([str(counter)," - ",item.display," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
    else:
        txt = "empty Inventory"
    return txt

'''
the help submenue
bad code: uses global function to render
'''
class HelpMenu(SubMenu):
    type = "AdvancedQuestMenu"
    '''
    show the help text
    '''
    def handleKey(self, key):
        # exit the submenu
        if key == "esc":
            return True

        # show info
        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview\n\n"))
        self.persistentText = ""
        self.persistentText += renderHelp()
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
'''
class TextMenu(SubMenu):
    type = "TextMenu"
    
    def __init__(self, text = ""):
        super().__init__()
        self.text = text

    '''
    '''
    def handleKey(self, key):
        # exit the submenu
        if key in ("esc","enter","space","j",):
            if self.followUp:
                self.followUp()
            return True

        # show info
        header.set_text((urwid.AttrSpec("default","default"),""))
        self.persistentText = ""
        self.persistentText += self.text
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
'''
class OneKeystokeMenu(SubMenu):
    type = "OneKeystokeMenu"
    
    def __init__(self, text = ""):
        super().__init__()
        self.text = text
        self.firstRun = True
        self.keyPressed = ""
        self.done = False

    '''
    '''
    def handleKey(self, key):

        # show info
        header.set_text((urwid.AttrSpec("default","default"),""))
        self.persistentText = ""
        self.persistentText += self.text
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        # exit the submenu
        if not key in ("~",) and not self.firstRun:
            self.keyPressed = key
            if self.followUp:
                self.followUp()
            self.done = True
            return True

        self.firstRun = False

        return False

'''
return the help text
bad code: should not be a global function
'''
def renderHelp():
    char = mainChar
    txt = "the Goal of the Game is to stay alive and to gain Influence.\nThe daily Grind can be delageted to subordinates.\nBe useful, gain Power and use your Power to be more useful.\n\n"
    txt += "your keybindings are:\n\n"
    txt += "* move_north: "+commandChars.move_north+"\n"
    txt += "* move_east: "+commandChars.move_east+"\n"
    txt += "* move_west: "+commandChars.move_west+"\n"
    txt += "* move_south: "+commandChars.move_south+"\n"
    txt += "* activate: "+commandChars.activate+"\n"
    txt += "* drink: "+commandChars.drink+"\n"
    txt += "* pickUp: "+commandChars.pickUp+"\n"
    txt += "* drop: "+commandChars.drop+"\n"
    txt += "* hail: "+commandChars.hail+"\n"
    txt += "* examine: "+commandChars.examine+"\n"
    txt += "* quit_normal: "+commandChars.quit_normal+"\n"
    txt += "* quit_instant: "+commandChars.quit_instant+"\n"
    txt += "* quit_delete: "+commandChars.quit_delete+"\n"
    txt += "* autoAdvance: "+commandChars.autoAdvance+"\n"
    txt += "* advance: "+commandChars.advance+"\n"
    txt += "* pause: "+commandChars.pause+"\n"
    txt += "* ignore: "+commandChars.ignore+"\n"
    txt += "* wait: "+commandChars.wait+"\n"
    txt += "* show_quests "+commandChars.show_quests+"\n"
    txt += "* show_quests_detailed: "+commandChars.show_quests_detailed+"\n"
    txt += "* show_inventory: "+commandChars.show_inventory+"\n"
    txt += "* show_inventory_detailed: "+commandChars.show_inventory_detailed+"\n"
    txt += "* show_characterInfo: "+commandChars.show_characterInfo+"\n"
    txt += "* redraw: "+commandChars.redraw+"\n"
    txt += "* show_help: "+commandChars.show_help+"\n"
    txt += "* attack: "+commandChars.attack+"\n"
    txt += "* devMenu: "+commandChars.devMenu+"\n"
    return txt
    
'''
render the map
bad code: should be contained somewhere
'''
def render(char):
    if char.room:
        thisTerrain = char.room.terrain
    else:
        thisTerrain = char.terrain

    # render the map
    chars = terrain.render()

    # center on player
    # bad code: should focus on arbitrary positions
    if mainChar.room:
        centerX = mainChar.room.xPosition*15+mainChar.room.offsetX+mainChar.xPosition
        centerY = mainChar.room.yPosition*15+mainChar.room.offsetY+mainChar.yPosition
    else:
        centerX = mainChar.xPosition
        centerY = mainChar.yPosition

    # set size of the window into the world
    viewsize = 41
    halfviewsite = (viewsize-1)//2

    # calculate the windows position
    screensize = loop.screen.get_cols_rows()
    decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(),True)
    screensize = (screensize[0]-decorationSize[0][0],screensize[1]-decorationSize[0][1])
    shift = (screensize[1]//2-20,screensize[0]//4-20)

    # place rendering in screen
    canvas = src.canvas.Canvas(size=(viewsize,viewsize),chars=chars,coordinateOffset=(centerY-halfviewsite,centerX-halfviewsite),shift=shift,displayChars=displayChars,tileMapping=tileMapping)

    return canvas

multi_currentChar = None
multi_chars = None
charindex = 0

def keyboardListener(key):
    global mainChar
    global multi_currentChar
    global multi_chars
    global charindex

    if not multi_currentChar:
        multi_currentChar = mainChar
    if multi_chars == None:
        multi_chars = terrain.characters[:]
        for room in terrain.rooms:
            for character in room.characters[:]:
                if not character in multi_chars:
                    multi_chars.append(character)

    state = mainChar.macroState

    if key == "ctrl d":
        state["commandKeyQueue"].clear()
        state["loop"] = []
        state["replay"].clear()
        if "ifCondition" in state:
            state["ifCondition"].clear()
            state["ifParam1"].clear()
            state["ifParam2"].clear()

    elif key == "ctrl p":
        if not mainChar.macroStateBackup:
            mainChar.macroStateBackup = mainChar.macroState
            mainChar.setDefaultMacroState()
            mainChar.macroState["macros"] = mainChar.macroStateBackup["macros"]

            state = mainChar.macroState
        else:
            mainChar.macroState = mainChar.macroStateBackup
            mainChar.macroState["macros"] = mainChar.macroStateBackup["macros"]
            mainChar.macroStateBackup = None

    elif key == "ctrl x":
        gamestate.save()
        raise urwid.ExitMainLoop()

    elif key == "ctrl o":
        with open("macros.json","r") as macroFile:
            import json
            rawMacros = json.loads(macroFile.read())
            parsedMacros = {}

            state = "normal"
            for key,value in rawMacros.items():
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


            mainChar.macroState["macros"] = parsedMacros

    elif key == "ctrl k":
        with open("macros.json","w") as macroFile:
            import json

            compressedMacros = {} 
            for key,value in mainChar.macroState["macros"].items():
                compressedMacro = ""
                for keystroke in value:
                    if len(keystroke) == 1:
                        compressedMacro += keystroke
                    else:
                        compressedMacro += "/"+keystroke+"/"
                compressedMacros[key] = compressedMacro
            macroFile.write(json.dumps(compressedMacros,indent = 10, sort_keys = True))

    elif key == "ctrl a":
        for character in terrain.characters:
            if not character in multi_chars:
                multi_chars.append(character)
        for room in terrain.rooms:
            for character in room.characters[:]:
                if not character in multi_chars:
                    multi_chars.append(character)

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
        newChar = multi_chars[charindex]

        if not newChar:
            messages.append("charindex %s"%(charindex))
            return

        mainChar = newChar
        state = mainChar.macroState

    elif key == "ctrl w":
        if not mainChar.room:
            return
        import json
        state = mainChar.room.getState()
        serializedState = json.dumps(state, indent = 10, sort_keys = True)

        with open("roomExport.json","w") as exportFile:
            exportFile.write(serializedState)

    else:
        show_or_exit(key,charState=state)

def gameLoop(loop,user_data):

    """
    if mainChar.macroState["commandKeyQueue"]:
        for char in multi_chars:
            if char == mainChar:
                noAdvanceGame = False
            else:
                noAdvanceGame = True
            state = char.macroState
            if len(state["commandKeyQueue"]):
                key = state["commandKeyQueue"][0]
                state["commandKeyQueue"].remove(key)
                processInput(key,charState=state,noAdvanceGame=noAdvanceGame,char=char)
    """

    global multi_currentChar
    global multi_chars

    if not multi_currentChar:
        multi_currentChar = mainChar
    if multi_chars == None:
        multi_chars = []

    for char in terrain.characters[:]:
        if not char in multi_chars:
            multi_chars.append(char)

    for room in terrain.rooms:
        for character in room.characters[:]:
            if not character in multi_chars:
                multi_chars.append(character)

    if mainChar.macroState["commandKeyQueue"]:
        if not len(cinematics.cinematicQueue):
            advanceGame()
        for char in multi_chars:
            if char.stasis:
                continue

            if len(cinematics.cinematicQueue) and not char == mainChar:
                continue

            state = char.macroState

            if len(state["commandKeyQueue"]):
                key = state["commandKeyQueue"][0]
                while isinstance(key[0],list) or isinstance(key[0],tuple) or key[0] in ("lagdetection","lagdetection_"):
                    if len(state["commandKeyQueue"]):
                        key = state["commandKeyQueue"][0]
                        state["commandKeyQueue"].remove(key)
                    else:
                        key = ("~",[])

                if len(state["commandKeyQueue"]):
                    key = state["commandKeyQueue"][0]
                    state["commandKeyQueue"].remove(key)
                    processInput(key,charState=state,noAdvanceGame=True,char=char)

        text = ""
        for cmd in mainChar.macroState["commandKeyQueue"]:
            item = cmd[0]
            if isinstance(item,list) or isinstance(item,tuple) or item in ("lagdetection","lagdetection_"):
                continue
            text += str(cmd[0])
        text += " | satiation: "+str(mainChar.satiation)
        footer.set_text((urwid.AttrSpec("default","default"),text))

        # render the game
        if not mainChar.specialRender:
            
            """
            global shownStarvationWarning
            if char.satiation < 30 and char.satiation > -1:
                if not shownStarvationWarning:
                    #cinematics.showCinematic("you will starve in %s ticks. drink something"%(char.satiation))
                    shownStarvationWarning = True
                if char.satiation == 0:
                    char.messages.append("you starved")
            else:
                shownStarvationWarning = False

            # render information on top
            if noAdvanceGame == False:
            """

            # render map
            # bad code: display mode specific code
            canvas = render(mainChar)
            main.set_text((urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible()));
            if (useTiles):
                canvas.setPygameDisplay(pydisplay,pygame,tileSize)
            header.set_text((urwid.AttrSpec("default","default"),renderHeader(mainChar)))
        
    loop.set_alarm_in(0.0001, gameLoop)

# get the interaction loop from the library
loop = urwid.MainLoop(frame, unhandled_input=keyboardListener)

def tmp(loop,user_data):
    gameLoop(loop,user_data)

loop.set_alarm_in(0.1, tmp)

s = None

def tmp2(loop,user_data):
    if not multiplayer:
        return

    HOST = '127.0.0.1'
    PORT = 65440

    global s
    if not s:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.bind((HOST, PORT))
        s.listen()

    import json
    import urwid

    global mainChar
    
    conn, addr = s.accept()
    with conn:
        data = conn.recv(1024*1024*1024)
        
        if data == b'ignore':
            loop.set_alarm_in(0.1, tmp2)
            return

        realMainChar = mainChar

        if len(multi_chars) > 1:
            mainChar = multi_chars[1]
            
        if data == b'redraw':
            pass
        else:
            for key in json.loads(data.decode("utf-8")):
                keyboardListener(key)

        canvas = render(mainChar)
        info = {"head":["adsada"],"main":[(urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible())],"footer":["asdasdasf sf"]}
        mainChar = realMainChar

        def serializeUrwid(inData):
            outData = []
            for item in inData:
                if isinstance(item,tuple):
                    outData.append(["tuple",[item[0].foreground,item[0].background],serializeUrwid(item[1])])
                if isinstance(item,list):
                    outData.append(["list",serializeUrwid(item)])
                if isinstance(item,str):
                    outData.append(["str",item])
            return outData

        info["head"] = serializeUrwid(info["head"])
        info["main"] = serializeUrwid(info["main"])
        info["footer"] = serializeUrwid(info["footer"])

        info = json.dumps(info)
        data = info.encode("utf-8")
        conn.sendall(data)

    loop.set_alarm_in(0.1, tmp2)

loop.set_alarm_in(0.1, tmp2)

# the directory for the submenues
subMenuMap = {
               "SelectionMenu":SelectionMenu,
               "ChatPartnerselection":ChatPartnerselection,
               "DebugMenu":DebugMenu,
               "QuestMenu":QuestMenu,
               "InventoryMenu":InventoryMenu,
               "CharacterInfoMenu":CharacterInfoMenu,
               "AdvancedQuestMenu":AdvancedQuestMenu,
               "HelpMenu":HelpMenu,
               "TextMenu":TextMenu,
               "OneKeystokeMenu":OneKeystokeMenu,
             }

'''
get item instances from dict state
'''
def getSubmenuFromState(state):
    subMenu = subMenuMap[state["type"]]()
    subMenu.setState(state)
    loadingRegistry.register(subMenu)
    return subMenu


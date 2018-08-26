import src.rooms as rooms
import src.items as items
import src.quests as quests
import src.canvas as canvaslib
import time
import urwid

##################################################################################################################################
###
##        setting up the basic user interaction library
#
#################################################################################################################################

# the containers for the shown text
header = urwid.Text(u"")
main = urwid.Text(u"")
footer = urwid.Text(u"")
main.set_layout('left', 'clip')

frame = urwid.Frame(urwid.Filler(main,"top"),header=header,footer=footer)

##################################################################################################################################
###
##        the main interaction loop
#
#################################################################################################################################

# the keys that should not be handled like usual but are overwritten by other places
stealKey = {}
# bad code: common variables with modules
items.stealKey = stealKey

# timestamps for detecting periods in inactivity etc
lastLagDetection = time.time()
lastRedraw = time.time()

# states for stateful interaction
itemMarkedLast = None
lastMoveAutomated = False
fullAutoMode = False
idleCounter = 0
pauseGame = False # bad code: this variable seems to be important but isn't used
submenue = None
ignoreNextAutomated = False
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
    doubleFooterText = footerText+footerText
    footerPosition = 0
    footerLength = len(footerText)
    footerSkipCounter = 20

# bad code: unused variable
commandHistory = []

'''
calls show_or_exit with on param less
'''
def callShow_or_exit(loop,key):
    show_or_exit(key)


'''
the callback for urwid keystrokes
bad code: this is abused as the main loop for this game
'''
def show_or_exit(key):
    # store the commands for later processing
    commandKeyQueue = []
    commandKeyQueue.append(key)

    # transform and store the keystrokes that accumulated in pygame
    try:
        import pygame
        for item in pygame.event.get():
            try:
                key = item.unicode
                if key == "\x1b":
                    key = "esc"
                commandKeyQueue.append(key)
                debugMessages.append("pressed "+key+" ")
            except:
                pass
    except:
        pass

    # handle the keystrokes
    processAllInput(commandKeyQueue)

'''
the abstracted processing for keystrokes.
Takes a list of keystrokes, that have been converted to a common format
'''
def processAllInput(commandKeyQueue):
    for key in commandKeyQueue:
        processInput(key)

'''
handle a keystroke
bad code: there are way too much lines of code in this function
'''
def processInput(key):
    # ignore mouse interaction
    if type(key) == tuple:
        return

    # bad code: global variables
    global lastLagDetection
    global idleCounter
    global pauseGame
    global submenue
    global ignoreNextAutomated
    global ticksSinceDeath

    # show the scrolling footer
    # bad code: this should be contained in an object
    if key in ("lagdetection",):
        # show the scrolling footer
        if (not submenue) and (not len(cinematics.cinematicQueue) or not cinematics.cinematicQueue[0].overwriteFooter):
            # bad code: global variables
            global footerPosition
            global footerLength
            global footerSkipCounter

            # scroll footer every 20 lagdetection events (about 2 seconds)
            # bad code: using the lagdetection as timer is abuse
            if footerSkipCounter == 20:
               footerSkipCounter = 0
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
            if not submenue:
                footer.set_text(" "+cinematics.cinematicQueue[0].footerText)
            else:
                footer.set_text(" "+submenue.footerText)

    # handle lag detection
    # bad code: lagdetection is abused as a timer
    if key in ("lagdetection",):
        # trigger the next lagdetection keystroke
        loop.set_alarm_in(0.1, callShow_or_exit, "lagdetection")
        lastLagDetection = time.time()

        # ring alarm if appropriate
        if terrain.alarm:
            print('\007')

        # advance the game if the character stays idle
        # bad code: commented out code
        if len(cinematics.cinematicQueue) or pauseGame:
            return
        idleCounter += 1
        if idleCounter < 4:
            return
        else:
            if idleCounter%5 == 0:
                key = commandChars.wait
                # bad code: commented out code
                """
                if idleCounter < 4:
                    key = commandChars.wait
                if idleCounter > 40:
                    key = commandChars.advance
                """
            else:
                return
    else:
        # reset activity counter
        idleCounter = 0

    # discard keysstrokes if they were not processed for too long
    if not key in (commandChars.autoAdvance, commandChars.quit_instant, commandChars.ignore,commandChars.quit_delete, commandChars.pause, commandChars.show_quests, commandChars.show_quests_detailed, commandChars.show_inventory, commandChars.show_inventory_detailed, commandChars.show_characterInfo):
        if lastLagDetection < time.time()-0.4:
            return

    pauseGame = False

    # repeat auoadvance keystrokes
    # bad code: keystrokes are abused here, a timer would be more appropriate
    if key in (commandChars.autoAdvance):
        if not ignoreNextAutomated:
            loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)
        else:
            ignoreNextAutomated = False

    # handle a keystroke while on map or in cinemetic
    if not submenue:
        # bad code: global variables
        global itemMarkedLast
        global lastMoveAutomated

        stop = False # bad code: useless variable

        # handle cinematics
        if len(cinematics.cinematicQueue):
            cinematic = cinematics.cinematicQueue[0]

            # allow to quit even in a cutscene
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()
            # skip the cinematic if requested
            elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance) and cinematic.skipable:
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

        # show a few rounds after death and exit
        if mainChar.dead:
            if not ticksSinceDeath:
                ticksSinceDeath = gamestate.tick
            key = commandChars.wait
            if gamestate.tick > ticksSinceDeath+5:
                # destroy the gamestate
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("you lost")
                saveFile.close()
                raise urwid.ExitMainLoop()

        # call callback if key was overwritten
        if key in stealKey:
            stealKey[key]()
        # handle the keystroke for a char on the map
        else:
            if key in ("´",):
                # open the debug menue
                if debug:
                    submenue = DebugMenu()
                else:
                    messages.append("debug not enabled")
            if key in (commandChars.quit_delete,):
                # destroy save and quit
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("reset")
                saveFile.close()
                raise urwid.ExitMainLoop()
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                # save and quit
                gamestate.save()
                raise urwid.ExitMainLoop()
            if key in (commandChars.pause):
                # kill one of the autoadvance keystrokes
                ignoreNextAutomated = True
                doAdvanceGame = False
            # bad code: code repetition for each direction
            if key in (commandChars.move_north):
                # do inner room movement
                if mainChar.room:
                    item = mainChar.room.moveCharacterNorth(mainChar)

                    # remeber items bumped into for possible interaction
                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
                        return
                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition-1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    # gather the rooms the character might have entered
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check if the character crossed the edge of the room
                        if room.yPosition*15+room.offsetY+room.sizeY == mainChar.yPosition:
                            if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                # get the entry point in room coordinates
                                hadRoomInteraction = True
                                localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
                                if localisedEntry[1] == -1:
                                    localisedEntry = (localisedEntry[0],room.sizeY-1)

                                if localisedEntry in room.walkingAccess:
                                    # check if the entry point is blocked (by a door)
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            # print some info
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                            # remember the item for interaction and abort
                                            itemMarkedLast = item
                                            return
                                    # teleport the character into the room
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition-1]
                        except Exception as e:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                # remember the item for interaction and abort
                                itemMarkedLast = item
                                foundItem = True

                        # move the character
                        if not foundItem:
                            mainChar.yPosition -= 1
                            mainChar.changed()

            # bad code: code repetition for each direction
            if key in (commandChars.move_south):
                # do inner room movement
                if mainChar.room:
                    item = mainChar.room.moveCharacterSouth(mainChar)

                    # remeber items bumped into for possible interaction
                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
                        return
                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition+1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    # gather the rooms the character might have entered
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check if the character crossed the edge of the room
                        if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
                            if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                # get the entry point in room coordinates
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)

                                if localisedEntry in room.walkingAccess:
                                    # check if the entry point is blocked (by a door)
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            # print some info
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                            # remember the item for interaction and abort
                                            itemMarkedLast = item
                                            return
                                    
                                    # teleport the character into the room
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition+1]
                        except Exception as e:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                # remember the item for interaction and abort
                                itemMarkedLast = item
                                foundItem = True

                        # move the character
                        if not foundItem:
                            mainChar.yPosition += 1
                            mainChar.changed()

            # bad code: code repetition for each direction
            if key in (commandChars.move_east):
                # do inner room movement
                if mainChar.room:
                    item = mainChar.room.moveCharacterEast(mainChar)

                    # remeber items bumped into for possible interaction
                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
                        return
                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    roomCandidates = []
                    bigX = (mainChar.xPosition+1)//15
                    bigY = (mainChar.yPosition)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    # gather the rooms the character might have entered
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check if the character crossed the edge of the room
                        if room.xPosition*15+room.offsetX == mainChar.xPosition+1:
                            if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                # get the entry point in room coordinates
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX+1)%15,(mainChar.yPosition-room.offsetY)%15)

                                if localisedEntry in room.walkingAccess:
                                    # check if the entry point is blocked (by a door)
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            # print some info
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                            # remember the item for interaction and abort
                                            itemMarkedLast = item
                                            return
                                    
                                    # teleport the character into the room
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition+1,mainChar.yPosition]
                        except Exception as e:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                # remember the item for interaction and abort
                                itemMarkedLast = item
                                foundItem = True

                        # move the character
                        if not foundItem:
                            mainChar.xPosition += 1
                            mainChar.changed()

            # bad code: code repetition for each direction
            if key in (commandChars.move_west):
                # do inner room movement
                if mainChar.room:
                    item = mainChar.room.moveCharacterWest(mainChar)

                    # remeber items bumped into for possible interaction
                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
                        return
                # do movement on terrain
                # bad code: these calculation should be done elsewhere
                else:
                    # gather the rooms the character might have entered
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition-1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    # gather the rooms the character might have entered
                    hadRoomInteraction = False
                    for room in roomCandidates:
                        # check if the character crossed the edge of the room
                        if room.xPosition*15+room.offsetX+room.sizeX == mainChar.xPosition:
                            if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                # get the entry point in room coordinates
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX-1)%15,(mainChar.yPosition-room.offsetY)%15)

                                if localisedEntry in room.walkingAccess:
                                    # check if the entry point is blocked (by a door)
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            # print some info
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                            # remember the item for interaction and abort
                                            itemMarkedLast = item
                                            return
                                    
                                    # teleport the character into the room
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")

                    # handle walking without room interaction
                    if not hadRoomInteraction:
                        # get the items on the destination coordinate 
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition-1,mainChar.yPosition]
                        except Exception as e:
                            foundItems = []

                        # check for items blocking the move to the destination coordinate
                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                # print some info
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

                                # remember the item for interaction and abort
                                itemMarkedLast = item
                                foundItem = True

                        # move the character
                        if not foundItem:
                            mainChar.xPosition -= 1
                            mainChar.changed()

            # murder the next available character
            if key in (commandChars.attack):
                if mainChar.room:
                    for char in mainChar.room.characters:
                        if char == mainChar:
                            continue
                        if not (mainChar.xPosition == char.xPosition and mainChar.yPosition == char.yPosition):
                            continue
                        char.die()
                # bad code: no else, so characters can only be killed within rooms -_-

            # activate an item 
            if key in (commandChars.activate):
                if itemMarkedLast:
                    # active marked item
                    itemMarkedLast.apply(mainChar)
                else:
                    # active an item on floor
                    if mainChar.room:
                        itemList = mainChar.room.itemsOnFloor
                    else:
                        itemList = terrain.itemsOnFloor
                    for item in itemList:
                        if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                            item.apply(mainChar)

            # examine an item 
            if key in (commandChars.examine):
                if itemMarkedLast:
                    # examine marked item
                    messages.append(itemMarkedLast.description)
                    if itemMarkedLast.description != itemMarkedLast.getDetailedInfo():
                        messages.append(itemMarkedLast.getDetailedInfo())
                else:
                    # examine an item on floor
                    if mainChar.room:
                        itemList = mainChar.room.itemsOnFloor
                    else:
                        itemList = terrain.itemsOnFloor
                    for item in itemList:
                        if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                            messages.append(item.description)
                            if item.description != item.getDetailedInfo():
                                messages.append(item.getDetailedInfo())

            # drop first item from inventory
            # bad pattern: the user has to have the choice for what item to drop
            if key in (commandChars.drop):
                if len(mainChar.inventory):
                    item = mainChar.inventory.pop()    
                    item.xPosition = mainChar.xPosition        
                    item.yPosition = mainChar.yPosition        
                    if mainChar.room:
                        mainChar.room.addItems([item])
                    else:
                        mainChar.terrain.addItems([item])
                    item.changed()
                    mainChar.changed()

            # drint from the first available item in inventory
            # bad pattern: the user has to have the choice for what item to drop
            if key in (commandChars.drink):
                character = mainChar
                for item in character.inventory:
                    if isinstance(item,items.GooFlask):
                        if item.uses > 0:
                            item.apply(character)
                            break

            # pick up items
            if key in (commandChars.pickUp):
                
                # check inventory space
                if len(mainChar.inventory) > 10:
                    messages.append("you cannot carry more items")
                    # bad code: continuing after a failed action is not smart. ^^

                # get the list of items from room or terrain
                # bad code: getting abtracted lists is a start but there should be a container class
                if mainChar.room:
                    itemByCoordinates = mainChar.room.itemByCoordinates
                    itemList = mainChar.room.itemsOnFloor
                else:
                    itemByCoordinates = terrain.itemByCoordinates
                    itemList = terrain.itemsOnFloor

                # get the position to pickup from
                if itemMarkedLast:
                    pos = (itemMarkedLast.xPosition,itemMarkedLast.yPosition)
                else:
                    pos = (mainChar.xPosition,mainChar.yPosition)

                # pickup all items from this coordinate
                if pos in itemByCoordinates:
                    for item in itemByCoordinates[pos]:
                        item.pickUp(mainChar)

            # open chat menu
            if key in (commandChars.hail):
                submenue = ChatPartnerselection()

            mainChar.automated = False
            if key in (commandChars.advance,commandChars.autoAdvance):
                # do the next step for the main character
                if len(mainChar.quests):
                    lastMoveAutomated = True

                    mainChar.automated = True
                else:
                    pass
            elif not key in (commandChars.pause):
                # recalculate the questmarker since it could be tainted
                lastMoveAutomated = False
                if mainChar.quests:
                    mainChar.setPathToQuest(mainChar.quests[0])

        # drop the marker for interacting with an item after bumping into it 
        if not key in ("lagdetection",commandChars.wait,):
            itemMarkedLast = None

        # enforce 60fps
        # bad code: urwid specific code should be isolated
        global lastRedraw
        if lastRedraw < time.time()-0.016:
            loop.draw_screen()
            lastRedraw = time.time()

        specialRender = False

        # doesn't open the dev menu and toggles 
        # bad code: code should act as advertised
        if key in (commandChars.devMenu):
            if displayChars.mode == "unicode":
                displayChars.setRenderingMode("pureASCII")
            else:
                displayChars.setRenderingMode("unicode")

        # open quest menu
        if key in (commandChars.show_quests):
            submenue = QuestMenu()

        # open help menu
        if key in (commandChars.show_help):
            submenue = HelpMenu()

        # open inventory
        if key in (commandChars.show_inventory):
            submenue = InventoryMenu()

        # open the menu for giving quests
        if key in (commandChars.show_quests_detailed):
            submenue = AdvancedQuestMenu()

        # open the character information
        if key in (commandChars.show_characterInfo):
            submenue = CharacterInfoMenu()

        # open the help screen
        if key in (commandChars.show_help):
            specialRender = True        
            pauseGame = True

        # show the game won screen
        if gamestate.gameWon:
            main.set_text((urwid.AttrSpec("default","default"),""))
            main.set_text((urwid.AttrSpec("default","default"),"credits"))
            header.set_text((urwid.AttrSpec("default","default"),"good job"))

    # render submenues
    if submenue:
        # set flag to not render the game
        specialRender = True        
        pauseGame = True

        # let the submenu handle the keystroke
        # bad code: the name success lies
        if not key in (commandChars.autoAdvance):
            success = submenue.handleKey(key)
        else:
            success = False

        # abort rendering submenue when done
        if key in ["esc"] or success:
            submenue = None
            pauseGame = False
            specialRender = False
            doAdvanceGame = False
        
    # render the game
    if not specialRender:
        
        # advance the game
        if doAdvanceGame:
            if mainChar.satiation < 30 and mainChar.satiation > -1:
                if mainChar.satiation == 0:
                    messages.append("you starved")
                else:
                    messages.append("you'll starve in "+str(mainChar.satiation)+" ticks!")
            advanceGame()

        # render information on top
        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

        # render map
        canvas = render()
        main.set_text((urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible()));
        if (useTiles):
            canvas.setPygameDisplay(pydisplay,pygame,tileSize)

'''
The base class for submenues offer selections
bad code: there is redundant code from the specific submenus that should be put here
'''
class SubMenu(object):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.footerText = "press w / s to move selection up / down, press enter / j / k to select"
        self.followUp = None
        super().__init__()

    '''
    sets the options to select from
    bad code: the name of this method lies
    '''
    def setSelection(self, query, options, niceOptions):
        import collections
        self.options = collections.OrderedDict(sorted(options.items()))
        self.niceOptions = collections.OrderedDict(sorted(niceOptions.items()))
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
    
    '''
    def handleKey(self, key):
        out = "\n"
        out += self.query+"\n"

        if not self.lockOptions:
            if key == "w":
                # change the marked option
                self.selectionIndex -= 1
                if self.selectionIndex == 0:
                    self.selectionIndex = len(self.options)
            if key == "s":
                # change the marked option
                self.selectionIndex += 1
                if self.selectionIndex > len(self.options):
                    self.selectionIndex = 1
            if key in ["enter","j","k"]:
                # select the marked option
                # bad code: transforming the key to the shortcut is needlessly complicated
                key = list(self.options.items())[self.selectionIndex-1][0]

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
        main.set_text((urwid.AttrSpec("default","default"),self.persistentText+"\n\n"+out))

        return False

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
    def __init__(self, text, options, niceOptions):
        super().__init__()
        self.setSelection(text, options, niceOptions)

    '''
    handles the key
    '''
    def handleKey(self, key):
        header.set_text("")

        if not self.getSelection():
             super().handleKey(key)

        if self.getSelection():
            return True
        else:
            return False

'''
Spawns a Chat submenu with a player selected character
bad code: only works within rooms right now
bad code: since there is no need to wait for some return this submenue should not wrap around the Chat menu
bad code: sub menues should be implemented in the base class
'''
class ChatPartnerselection(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__()
        self.subMenu = None

    '''
    set up the selection and spawn the chat 
    '''
    def handleKey(self, key):
        # wrao around the chat menu
        if self.subMenu:
            return self.subMenu.handleKey(key)

        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # initialize the options
        # bad code: should be done in __init__
        if not self.options and not self.getSelection():
            counter = 1
            options = {}
            niceOptions = {}
            if mainChar.room:
                for char in mainChar.room.characters:
                    if char == mainChar:
                        continue
                    options[counter] = char
                    niceOptions[counter] = char.name
                    counter += 1
            self.setSelection("talk with whom?",options,niceOptions)

        # delegate the actual selection to the super class
        if not self.getSelection():
             super().handleKey(key)

        if self.getSelection():
            # spawn the chat submenu
            self.subMenu = ChatMenu(self.selection)
            self.subMenu.handleKey(key)
        else:
            return False

'''
the chat option for recruiting a character
'''
class RecruitChat(SubMenu):
    dialogName = "follow my orders." # the name for this chat when presented as dialog option

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    '''
    show dialog and recruit character depending on success
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog and reactions should be generated within the characters
    '''
    def handleKey(self, key):
        if self.firstRun:
            # add player text
            self.persistentText += mainChar.name+": \"come and help me.\"\n"

            if self.partner.reputation > mainChar.reputation:
                # reject player
                if mainChar.reputation <= 0:
                    # reject player harshly
                    self.persistentText += self.partner.name+": \"No.\""
                    mainChar.reputation -= 5
                    messages.append("You were rewarded -5 reputation")
                else:
                    if self.partner.reputation//mainChar.reputation:
                        # reject player harshly
                        self.persistentText += self.partner.name+": \"you will need at least have to have "+str(self.partner.reputation//mainChar.reputation)+" times as much reputation to have me consider that\"\n"
                        messages.append("You were rewarded -"+str(2*(self.partner.reputation//mainChar.reputation))+" reputation")
                        mainChar.reputation -= 2*(self.partner.reputation//mainChar.reputation)
                    else:
                        # reject player somewhat nicely
                        self.persistentText += self.partner.name+": \"maybe if you come back later\""
                        mainChar.reputation -= 2
                        messages.append("You were rewarded -2 reputation")
            else:
                if gamestate.tick%2:
                    # reject player
                    self.persistentText += self.partner.name+": \"sorry, too busy.\"\n"
                    mainChar.reputation -= 1
                    messages.append("You were rewarded -1 reputation")
                else:
                    # allow the recruitment
                    self.persistentText += self.partner.name+": \"on it!\"\n"
                    mainChar.subordinates.append(self.partner)
            text = self.persistentText+"\n\n-- press any key --"
            main.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        else:
            # continue after the first keypress
            # bad code: the first keystroke is the second keystroke that is handled
            self.done = True
            return False

'''
a chat with a character, partially hardcoded partially dynamically genrated 
bad code: sub menues should be implemented in the base class
'''
class ChatMenu(SubMenu):

    '''
    straightforward state initialization
    '''
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.subMenu = None
        super().__init__()

    '''
    show the dialog options and wrap the corresponding submenus
    bad code: showing the messages should be handled in __init__ or a setup method
    bad code: the dialog should be generated within the characters
    '''
    def handleKey(self, key):
        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        # wrap around chat submenue
        if self.subMenu:
            # let the submenue handle the key
            if not self.subMenu.done:
                self.subMenu.handleKey(key)
                if not self.subMenu.done:
                    return False

            # return to main dialog menu
            self.subMenu = None
            self.state = "mainOptions"
            self.selection = None
            self.lockOptions = True
            self.options = []

        # display greetings
        if self.state == None:
            self.state = "mainOptions"
            self.persistentText += self.partner.name+": \"Everything in Order, "+mainChar.name+"?\"\n"
            self.persistentText += mainChar.name+": \"All sorted, "+self.partner.name+"!\"\n"

        if self.state == "mainOptions":
            # set up selection for the main dialog options 
            # bad code: bad data structure leads to ugly code
            if not self.options and not self.getSelection():
                # add the chat partners special dialog options
                options = {}
                niceOptions = {}
                counter = 1
                for option in self.partner.getChatOptions(mainChar):
                    options[counter] = option
                    niceOptions[counter] = option.dialogName
                    counter += 1

                # add default dialog options
                options[counter] = "showQuests"
                niceOptions[counter] = "what are you dooing?"
                counter += 1
                options[counter] = "exit"
                niceOptions[counter] = "let us proceed, "+self.partner.name
                counter += 1

                # set the options
                self.setSelection("answer:",options,niceOptions)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            # spawn the dialog options submenu
            if self.getSelection():
                if not isinstance(self.selection,str):
                    # spawn the selected dialog option
                    self.subMenu = self.selection(self.partner)
                    self.subMenu.handleKey(key)
                elif self.selection == "showQuests":
                    # spawn quest submenu for partner
                    submenue = QuestMenu(char=self.partner)
                    submenue.handleKey(key)
                    return False
                elif self.selection == "exit":
                    # end the conversation
                    self.state = "done"
                self.selection = None
                self.lockOptions = True
            else:
                return False

        # say goodbye
        if self.state == "done":
            if self.lockOptions:
                self.persistentText += self.partner.name+": \"let us proceed, "+mainChar.name+".\"\n"
                self.persistentText += mainChar.name+": \"let us proceed, "+self.partner.name+".\"\n"
                self.lockOptions = False
            else:
                return True

        # show redered text via urwid
        if not self.subMenu:
            main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
minimal debug ability
'''
class DebugMenu(SubMenu):
    '''
    straightforward state initialization
    '''
    def __init__(self,char=None):
        super().__init__()
        self.firstRun = True

    '''
    show some debug output
    '''
    def handleKey(self, key):
        if self.firstRun:
            # bad code: commented out code
            import objgraph
            #objgraph.show_backrefs(mainChar, max_depth=4)
            """
            msg = ""
            for item in objgraph.most_common_types(limit=50):
                msg += ("\n"+str(item))
            main.set_text(msg)

            constructionSite = terrain.roomByCoordinates[(4,2)][0]
            quest = quests.ConstructRoom(constructionSite,terrain.tutorialStorageRooms)
            mainChar.assignQuest(quest,active=True)
            """

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
        # scroll
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
        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview\n(press "+commandChars.show_quests_detailed+" for the extended quest menu)\n\n"))
        self.persistentText = []
        self.persistentText.append(renderQuests(char=self.char,asList=True,questIndex = self.questIndex))

        if not self.lockOptions:
            if key in ["q"]:
                # spawn the quest menu for adding quests
                global submenue
                submenue = AdvancedQuestMenu()
                submenue.handleKey(key)
                return False
        self.lockOptions = False

        # bad code: commented out code
        #self.persistentText = "\n".join(self.persistentText.split("\n")[self.offsetX:])

        self.persistentText.extend(["\n","* press q for advanced quests "+str(self.char),"\n","* press W to scroll up","\n","* press S to scroll down","\n","\n"])

        # flatten the mix of strings and urwid format so that it is less recursive to workaround an urwid bug
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
    '''
    straighforwad state initalisation
    bad code: has no effect
    '''
    def __init__(self):
        self.lockOptions = True
        super().__init__()

    '''
    show the inventory
    '''
    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\ninventory overview\n(press "+commandChars.show_inventory_detailed+" for the extended inventory menu)\n\n"))

        self.persistentText = (urwid.AttrSpec("default","default"),renderInventory())

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
show the players attributes
bad code: should be abstracted
bad code: uses global functions to render
'''
class CharacterInfoMenu(SubMenu):
    '''
    straighforwad state initalisation
    bad code: has no effect
    '''
    def __init__(self):
        self.lockOptions = True
        super().__init__()

    '''
    show the attributes
    '''
    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\ncharacter overview"))
        main.set_text((urwid.AttrSpec("default","default"),[mainChar.getDetailedInfo(),"\ntick: "+str(gamestate.tick)]))
        header.set_text((urwid.AttrSpec("default","default"),""))

'''
player interaction for delegating a quest
'''
class AdvancedQuestMenu(SubMenu):
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
        # start rendering
        header.set_text((urwid.AttrSpec("default","default"),"\nadvanced Quest management\n"))
        out = "\n"
        if self.character:
            out += "character: "+str(self.character.name)+"\n"
        if self.quest:
            out += "quest: "+str(self.quest)+"\n"
        out += "\n"

        # let the player select the charater to assign the quest to 
        if self.state == None:
            self.state = "participantSelection"
        if self.state == "participantSelection":
            # set up the options
            # bad code: bad data structure leads to ugly code
            if not self.options and not self.getSelection():
                # add the main player as target
                options = {}
                niceOptions = {}
                options[1] = mainChar
                niceOptions[1] = mainChar.name+" (you)"
                counter = 1

                # add the main players subordinates as target
                for char in mainChar.subordinates:
                    counter += 1
                    options[counter] = char
                    niceOptions[counter] = char.name
                self.setSelection("whom to give the order to: ",options,niceOptions)

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
            # add a list of hardcoded quests
            if not self.options and not self.getSelection():
                options = {1:quests.MoveQuest,2:quests.ActivateQuest,3:quests.EnterRoomQuest,4:quests.FireFurnaceMeta,5:quests.ClearRubble,6:quests.ConstructRoom,7:quests.StoreCargo,8:quests.WaitQuest,9:quests.LeaveRoomQuest,10:quests.MoveToStorage,11:quests.RoomDuty}
                niceOptions = {1:"MoveQuest",2:"ActivateQuest",3:"EnterRoomQuest",4:"FireFurnaceMeta",5:"ClearRubble",6:"ConstructRoom",7:"StoreCargo",8:"WaitQuest",9:"LeaveRoomQuest",10:"MoveToStorage",11:"RoomDuty"}
                self.setSelection("what type of quest:",options,niceOptions)

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

        # let the player select the paramters for the quest
        if self.state == "parameter selection":
            if self.quest == quests.EnterRoomQuest:
                # set up the options
                # bad code: bad data structure leads to ugly code
                if not self.options and not self.getSelection():
                    options = {}
                    niceOptions = {}
                    counter = 1

                    # add a list of of rooms
                    for room in terrain.rooms:
                        if isinstance(room,rooms.MechArmor) or isinstance(room,rooms.CpuWasterRoom):
                            continue
                        options[counter] = room
                        niceOptions[counter] = room.name
                        counter += 1
                    self.setSelection("select the room:",options,niceOptions)

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

            elif self.quest == quests.StoreCargo:
                # set up the options for selecting the cargo room
                # bad code: bad data structure leads to ugly code
                if "cargoRoom" not in self.questParams:
                    if not self.options and not self.getSelection():
                        options = {}
                        niceOptions = {}
                        counter = 1

                        # add a list of of rooms
                        for room in terrain.rooms:
                            if not isinstance(room,rooms.CargoRoom):
                                continue
                            options[counter] = room
                            niceOptions[counter] = room.name
                            counter += 1
                        self.setSelection("select the room:",options,niceOptions)

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
                    # bad code: bad data structure leads to ugly code
                    if not self.options and not self.getSelection():
                        options = {}
                        niceOptions = {}
                        counter = 1

                        # add a list of of rooms
                        for room in terrain.rooms:
                            if not isinstance(room,rooms.StorageRoom):
                                continue
                            options[counter] = room
                            niceOptions[counter] = room.name
                            counter += 1
                        self.setSelection("select the room:",options,niceOptions)

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
            # bad code: bad data structure leads to ugly code
            if not self.options and not self.getSelection():
                options = {1:"yes",2:"no"}
                niceOptions = {1:"yes",2:"no"}
                if self.quest == quests.EnterRoomQuest:
                    self.setSelection("you chose the following parameters:\nroom: "+str(self.questParams)+"\n\nDo you confirm?",options,niceOptions)
                else:
                    self.setSelection("Do you confirm?",options,niceOptions)

            # let the superclass handle the actual selection
            if not self.getSelection():
                super().handleKey(key)

            if self.getSelection():
                if self.selection == "yes":
                    # instanciate quest
                    if self.quest == quests.MoveQuest:
                       questInstance = self.quest(mainChar.room,2,2)
                    if self.quest == quests.ActivateQuest:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0])
                    if self.quest == quests.EnterRoomQuest:
                       questInstance = self.quest(self.questParams["room"])
                    if self.quest == quests.FireFurnaceMeta:
                       questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0])
                    if self.quest == quests.WaitQuest:
                       questInstance = self.quest()
                    if self.quest == quests.LeaveRoomQuest:
                       try:
                           questInstance = self.quest(self.character.room)
                       except:
                           pass
                    if self.quest == quests.ClearRubble:
                       questInstance = self.quest()
                    if self.quest == quests.RoomDuty:
                       questInstance = self.quest()
                    if self.quest == quests.ConstructRoom:
                       for room in terrain.rooms:
                           if isinstance(room,rooms.ConstructionSite):
                               constructionSite = room
                               break
                       questInstance = self.quest(constructionSite,terrain.tutorialStorageRooms)
                    if self.quest == quests.StoreCargo:
                       for room in terrain.rooms:
                           if isinstance(room,rooms.StorageRoom):
                               storageRoom = room
                       questInstance = self.quest(self.questParams["cargoRoom"],self.questParams["storageRoom"])
                    if self.quest == quests.MoveToStorage:
                       questInstance = self.quest([terrain.tutorialLab.itemByCoordinates[(1,9)][0],terrain.tutorialLab.itemByCoordinates[(2,9)][0]],terrain.tutorialStorageRooms[1])

                    # show some messages
                    if not self.character == mainChar:
                       self.persistentText += self.character.name+": \"understood?\"\n"
                       self.persistentText += mainChar.name+": \"understood and in execution\"\n"

                    # assign the quest
                    self.character.assignQuest(questInstance, active=True)

                    self.state = "done"
                else:
                    # reset progress
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
'''
def renderHeader():
    # render the sections to display
    questSection = renderQuests(maxQuests=2)
    messagesSection = renderMessages()

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

        if len(questLine) > questWidth:
            # cut off left line
            txt += questLine[:questWidth]+"┃ "
            questLine = questLine[questWidth:]
        else:
            # padd left line
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
'''
def renderMessages(maxMessages=5):
    txt = ""
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

    if len(char.quests):
        # render the quests
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
    else:
        # return placeholder for no quests
        if asList:
            txt.append("No Quest")
        else:
            txt += "No Quest"

    return txt

'''
render the inventory of the player into a string
'''
def renderInventory():
    char = mainChar
    txt = []
    if len(char.inventory):
        for item in char.inventory:
            if isinstance(item.display,int):
                txt.extend([displayChars.indexedMapping[item.display]," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
            else:
                txt.extend([item.display," - ",item.name,"\n     ",item.getDetailedInfo(),"\n"])
    else:
        txt = "empty Inventory"
    return txt

'''
the help submenue
'''
class HelpMenu(SubMenu):
    '''
    show the help text
    '''
    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview\n\n"))

        self.persistentText = ""

        self.persistentText += renderHelp()

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

'''
return the help text
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
'''
def render():
    # render the map
    chars = terrain.render()

    # center on player
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
    canvas = canvaslib.Canvas(size=(viewsize,viewsize),chars=chars,coordinateOffset=(centerY-halfviewsite,centerX-halfviewsite),shift=shift,displayChars=displayChars)

    # bad code: commented out code
    """


    result = []

    if offsetY > 0:
        result += "\n"*offsetY

    if offsetY < 0:
        topOffset = ((screensize[1]-viewsize)//2)+1
        result += "\n"*topOffset
        chars = chars[-offsetY+topOffset:-offsetY+topOffset+viewsize]


    for line in chars:
        lineRender = []
        rowCounter = 0

        visibilityOffsetX = ((screensize[0]-viewsize*2)//4)+1
        
        lineRender += "  "*visibilityOffsetX

        totalOffset = -centeringOffsetX+visibilityOffsetX
        offsetfix = 0
        if totalOffset<0:
            lineRender += "  "*-totalOffset
            offsetfix = -totalOffset
            totalOffset = 0
            
        line = line[totalOffset:totalOffset+viewsize-offsetfix]

        for char in line:
            lineRender.append(char)
            rowCounter += 1
        lineRender.append("\n")
        result.extend(lineRender)
    """

    return canvas

# get the interaction loop from the library
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)

# kick of the interaction loop
loop.set_alarm_in(0.2, callShow_or_exit, "lagdetection")
loop.set_alarm_in(0.0, callShow_or_exit, "~")


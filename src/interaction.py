import src.rooms as rooms
import src.items as items
import src.quests as quests
import time
import urwid

##################################################################################################################################
###
##        settng up the basic user interaction library
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
##        the main nteraction loop
#
#################################################################################################################################

# the keys that should not be handled like usual but are overwritten by other places
stealKey = {}
# HACK: common variables with modules
items.stealKey = stealKey

# timestamps for detecting periods in inactivity etc
lastLagDetection = time.time()
lastRedraw = time.time()

# states for statefull interaction
itemMarkedLast = None
lastMoveAutomated = False
fullAutoMode = False
idleCounter = 0
pauseGame = False
questMenuActive = False
submenue = None

commandHistory = []

# HACK: remove unnessecary param
def callShow_or_exit(loop,key):
    show_or_exit(key)

def show_or_exit(key):
    #mouse click
    if type(key) == tuple:
        return

    global lastLagDetection
    global idleCounter
    global pauseGame
    global questMenuActive
    global submenue

    if key in ("lagdetection",):
        loop.set_alarm_in(0.2, callShow_or_exit, "lagdetection")
        lastLagDetection = time.time()
        if len(cinematics.cinematicQueue) or pauseGame:
            return
        idleCounter += 1
        if idleCounter < 4:
            return
        else:
            if idleCounter%5 == 0:
                key = commandChars.wait
                """
                if idleCounter < 4:
                    key = commandChars.wait
                if idleCounter > 40:
                    key = commandChars.advance
                """
            else:
                return
    else:
        idleCounter = 0
    if not key in (commandChars.autoAdvance, commandChars.quit_instant, commandChars.ignore,commandChars.quit_delete):
        if lastLagDetection < time.time()-0.4:
            return

    pauseGame = False

    if key in (commandChars.autoAdvance):
        loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)

    if not submenue:
        global itemMarkedLast
        global lastMoveAutomated
        stop = False
        doAdvanceGame = True
        if len(cinematics.cinematicQueue):
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()
            elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance):
                cinematics.cinematicQueue[0].abort()
                cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
                loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
                return
            else:
                if not cinematics.cinematicQueue[0].advance():
                    return
                key = commandChars.ignore
        if key in (commandChars.ignore):
            doAdvanceGame = False

        if key in stealKey:
            stealKey[key]()
        else:
            if key in (commandChars.quit_delete,):
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("reset")
                saveFile.close()
                raise urwid.ExitMainLoop()
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()
            if key in (commandChars.move_north):
                if mainChar.room:
                    item = mainChar.room.moveCharacterNorth(mainChar)

                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text(renderHeader())
                        return
                else:
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition-1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    hadRoomInteraction = False
                    for room in roomCandidates:
                        if room.yPosition*15+room.offsetY+room.sizeY == mainChar.yPosition:
                            if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                hadRoomInteraction = True
                                localisedEntry = (mainChar.xPosition%15-room.offsetX,mainChar.yPosition%15-room.offsetY-1)
                                if localisedEntry[1] == -1:
                                    localisedEntry = (localisedEntry[0],room.sizeY-1)
                                if localisedEntry in room.walkingAccess:
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            itemMarkedLast = item
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text(renderHeader())
                                            return
                                    
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")
                    if not hadRoomInteraction:
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition-1]
                        except Exception as e:
                            foundItems = []

                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                itemMarkedLast = item
                                header.set_text(renderHeader())
                                foundItem = True
                        if not foundItem:
                            mainChar.yPosition -= 1
                            mainChar.changed()

            if key in (commandChars.move_south):
                if mainChar.room:
                    item = mainChar.room.moveCharacterSouth(mainChar)

                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text(renderHeader())
                        return
                else:
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition+1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    hadRoomInteraction = False
                    for room in roomCandidates:
                        if room.yPosition*15+room.offsetY == mainChar.yPosition+1:
                            if room.xPosition*15+room.offsetX-1 < mainChar.xPosition and room.xPosition*15+room.offsetX+room.sizeX > mainChar.xPosition:
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX)%15,(mainChar.yPosition-room.offsetY+1)%15)
                                if localisedEntry in room.walkingAccess:
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            itemMarkedLast = item
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text(renderHeader())
                                            return
                                    
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")
                    if not hadRoomInteraction:
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition,mainChar.yPosition+1]
                        except Exception as e:
                            foundItems = []

                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                itemMarkedLast = item
                                header.set_text(renderHeader())
                                foundItem = True
                        if not foundItem:
                            mainChar.yPosition += 1
                            mainChar.changed()

            if key in (commandChars.move_east):
                if mainChar.room:
                    item = mainChar.room.moveCharacterEast(mainChar)

                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text(renderHeader())
                        return
                else:
                    roomCandidates = []
                    bigX = (mainChar.xPosition+1)//15
                    bigY = (mainChar.yPosition)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    hadRoomInteraction = False
                    for room in roomCandidates:
                        if room.xPosition*15+room.offsetX == mainChar.xPosition+1:
                            if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX+1)%15,(mainChar.yPosition-room.offsetY)%15)
                                if localisedEntry in room.walkingAccess:
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            itemMarkedLast = item
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text(renderHeader())
                                            return
                                    
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")
                    if not hadRoomInteraction:
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition+1,mainChar.yPosition]
                        except Exception as e:
                            foundItems = []

                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                itemMarkedLast = item
                                header.set_text(renderHeader())
                                foundItem = True
                        if not foundItem:
                            mainChar.xPosition += 1
                            mainChar.changed()

            if key in (commandChars.move_west):
                if mainChar.room:
                    item = mainChar.room.moveCharacterWest(mainChar)

                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text(renderHeader())
                        return
                else:
                    roomCandidates = []
                    bigX = (mainChar.xPosition)//15
                    bigY = (mainChar.yPosition-1)//15
                    for coordinate in [(bigX,bigY),(bigX,bigY+1),(bigX,bigY-1),(bigX+1,bigY),(bigX-1,bigY)]:
                        if coordinate in terrain.roomByCoordinates:
                            roomCandidates.extend(terrain.roomByCoordinates[coordinate])

                    hadRoomInteraction = False
                    for room in roomCandidates:
                        if room.xPosition*15+room.offsetX+room.sizeX == mainChar.xPosition:
                            if room.yPosition*15+room.offsetY < mainChar.yPosition+1 and room.yPosition*15+room.offsetY+room.sizeY > mainChar.yPosition:
                                hadRoomInteraction = True
                                localisedEntry = ((mainChar.xPosition-room.offsetX-1)%15,(mainChar.yPosition-room.offsetY)%15)
                                if localisedEntry in room.walkingAccess:
                                    for item in room.itemByCoordinates[localisedEntry]:
                                        if not item.walkable:
                                            itemMarkedLast = item
                                            messages.append("you need to open the door first")
                                            messages.append("press "+commandChars.activate+" to apply")
                                            header.set_text(renderHeader())
                                            return
                                    
                                    room.addCharacter(mainChar,localisedEntry[0],localisedEntry[1])
                                    terrain.characters.remove(mainChar)
                                else:
                                    messages.append("you cannot move there")
                    if not hadRoomInteraction:
                        try:
                            foundItems = terrain.itemByCoordinates[mainChar.xPosition-1,mainChar.yPosition]
                        except Exception as e:
                            foundItems = []

                        foundItem = False
                        for item in foundItems:
                            if item and not item.walkable:
                                messages.append("You cannot walk there")
                                messages.append("press "+commandChars.activate+" to apply")
                                itemMarkedLast = item
                                header.set_text(renderHeader())
                                foundItem = True
                        if not foundItem:
                            mainChar.xPosition -= 1
                            mainChar.changed()

            if key in (commandChars.attack):
                if mainChar.room:
                    for char in mainChar.room.characters:
                        if char == mainChar:
                            continue
                        if not (mainChar.xPosition == char.xPosition and mainChar.yPosition == char.yPosition):
                            continue
                        mainChar.room.removeCharacter(char)
                        corpse = items.Corpse(mainChar.xPosition,mainChar.yPosition)
                        mainChar.room.addItems([corpse])

            if key in (commandChars.activate):
                if itemMarkedLast:
                    itemMarkedLast.apply(mainChar)
                else:
                    if mainChar.room:
                        itemList = mainChar.room.itemsOnFloor
                    else:
                        itemList = terrain.itemsOnFloor
                    for item in itemList:
                        if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                            item.apply(mainChar)

            if key in (commandChars.examine):
                if itemMarkedLast:
                    messages.append(itemMarkedLast.description)
                    messages.append(itemMarkedLast.getDetailedInfo())
                else:
                    if mainChar.room:
                        itemList = mainChar.room.itemsOnFloor
                    else:
                        itemList = terrain.itemsOnFloor
                    for item in itemList:
                        if item.xPosition == mainChar.xPosition and item.yPosition == mainChar.yPosition:
                            messages.append(item.description)
                            messages.append(item.getDetailedInfo())

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

            if key in (commandChars.pickUp):
                if len(mainChar.inventory) > 10:
                    messages.append("you cannot carry more items")
                if mainChar.room:
                    itemByCoordinates = mainChar.room.itemByCoordinates
                    itemList = mainChar.room.itemsOnFloor
                else:
                    itemByCoordinates = terrain.itemByCoordinates
                    itemList = terrain.itemsOnFloor

                if (mainChar.xPosition,mainChar.yPosition) in itemByCoordinates:
                    for item in itemByCoordinates[(mainChar.xPosition,mainChar.yPosition)]:
                        itemList.remove(item)
                        if hasattr(item,"xPosition"):
                            del item.xPosition
                        if hasattr(item,"yPosition"):
                            del item.yPosition
                        mainChar.inventory.append(item)
                        item.changed()
                    del itemByCoordinates[(mainChar.xPosition,mainChar.yPosition)]

            if key in (commandChars.hail):
                if mainChar.room and type(mainChar.room) == rooms.MiniMech:
                    if not mainChar.room.npc.quests:
                        messages.append("please fire the furnace.")
                        quest0 = quests.KeepFurnaceFired(mainChar.room.furnaces[0])
                        mainChar.room.npc.assignQuest(quest0)
                    else:
                        messages.append("you may stop now.")
                        for quest in mainChar.room.npc.quests:
                            quest.deactivate()
                        mainChar.room.npc.quests = []
                else:
                    submenue = ChatMenu()

            if key in (commandChars.advance,commandChars.autoAdvance):
                if len(mainChar.quests):
                    if not lastMoveAutomated:
                        try:
                            mainChar.setPathToQuest(mainChar.quests[0])
                        except:
                            pass

                    lastMoveAutomated = True

                    mainChar.automated = True
                    mainChar.advance()
                    mainChar.automated = False
                else:
                    pass
            else:
                lastMoveAutomated = False

        if not key in ("lagdetection",commandChars.wait,):
            itemMarkedLast = None

        global lastRedraw
        if lastRedraw < time.time()-0.016:
            loop.draw_screen()
            lastRedraw = time.time()

        specialRender = False
        if key in (commandChars.show_quests):
            submenue = QuestMenu()

        if key in (commandChars.show_quests_detailed):
            submenue = AdvancedQuestMenu()

        if key in (commandChars.show_inventory):
            specialRender = True        
            pauseGame = True
            
            header.set_text("\ninentory overview\n(press "+commandChars.show_inventory_detailed+" for the extended inventory menu)\n\n")
            main.set_text(renderInventory())
            header.set_text("")

        if key in (commandChars.show_help):
            specialRender = True        
            pauseGame = True

        if gamestate.gameWon:
            main.set_text("")
            main.set_text("credits")
            header.set_text("good job")

    if submenue:
        specialRender = True        
        pauseGame = True

        success = submenue.handleKey(key)

        if key in ["esc"] or success:
            submenue = None
            pauseGame = False
            specialRender = False
            doAdvanceGame = False
        
    if not specialRender:
        if doAdvanceGame:
            advanceGame()

        header.set_text(renderHeader())
        main.set_text(render());

class SubMenu(object):
    def __init__(self):
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        super().__init__()

    def setSelection(self, query, options):
        self.options = options
        self.query = query
        self.selection = None

    def getSelection(self):
        return self.selection

    def handleKey(self, key):
        out = "\n"
        out += self.query+"\n"

        if key == "w":
            self.selectionIndex -= 1
            if self.selectionIndex == 0:
                self.selectionIndex = len(self.options)
            key = self.selectionIndex
        if key == "s":
            self.selectionIndex += 1
            if self.selectionIndex > len(self.options):
                self.selectionIndex = 1
            key = self.selectionIndex
        if key in ["enter","j","k"]:
            key = str(self.selectionIndex)

        if key in self.options:
            self.selection = self.options[key]
            self.options = None
            return True

        for k,v in self.options.items():
            if k == str(self.selectionIndex):
                out += k+" ->"+str(v.name)+"\n"
            else:
                out += k+" - "+str(v.name)+"\n"
        out += str(self.selection)

        main.set_text(out)

        return False

class ChatMenu(SubMenu):
    def __init__(self):
        self.state = None
        super().__init__()

    def handleKey(self, key):
        header.set_text("\nConversation menu\n")
        out = "\n"

        if self.state == None:
            self.state = "participantSelection"

        if self.state == "participantSelection":
            if not self.options and not self.getSelection():
                counter = 1
                options = {}
                if mainChar.room:
                    for char in mainChar.room.characters:
                        options[str(counter)] = char
                        counter += 1
                self.setSelection("talk with whom?!",options)

            if not self.getSelection():
                 super().handleKey(key)

            if self.getSelection():
                self.state = "greetings"
            else:
                return False

        if self.state == "greetings":
                out += "you say hi to  "+str(self.getSelection().name)+"\n"
                out += str(self.getSelection().name)+" says hi to you"

        main.set_text(out)

        return False

class QuestMenu(SubMenu):
    def __init__(self):
        self.lockOptions = True
        super().__init__()

    def handleKey(self, key):
        global submenue

        header.set_text("\nquest overview\n(press "+commandChars.show_quests_detailed+" for the extended quest menu)\n\n")
        main.set_text(renderQuests())
        header.set_text("")

        if not self.lockOptions:
            if key in ["q"]:
                submenue = AdvancedQuestMenu()
                submenue.handleKey(key)
        self.lockOptions = False

class AdvancedQuestMenu(SubMenu):
    def __init__(self):
        self.state = None
        self.character = None
        self.quest = None
        self.lockOptions = True
        self.selectionIndex = 1
        super().__init__()

    def handleKey(self, key):
        header.set_text("\nadvanced Quest management\n")
        out = "\n"

        if self.character:
            out += "character: "+str(self.character.name)+"\n"
        if self.quest:
            out += "quest: "+str(self.quest)+"\n"
        out += "\n"

        if self.state == None:
            self.state = "participantSelection"

        if self.state == "participantSelection":
            self.options = {}
            self.options["1"] = mainChar
            self.options["2"] = terrain.wakeUpRoom.firstOfficer
            self.options["3"] = terrain.wakeUpRoom.secondOfficer

            if not self.lockOptions:
                if key == "w":
                    self.selectionIndex -= 1
                    if self.selectionIndex == 0:
                        self.selectionIndex = len(self.options)
                    key = self.selectionIndex
                if key == "s":
                    self.selectionIndex += 1
                    if self.selectionIndex > len(self.options):
                        self.selectionIndex = 1
                    key = self.selectionIndex
                if key in ["enter","j","k"]:
                    key = str(self.selectionIndex)
                if key in self.options:
                    self.character = self.options[key]
                    self.state = "questSelection"
                    self.lockOptions = True
                    out += "character: "
                    out += str(self.character.name)
                    out += "\n\n"
                    self.selectionIndex = 1

            if self.state == "participantSelection":
                out += "give quest to whom?\n"
                for k,v in self.options.items():
                    if str(self.selectionIndex) == k:
                        out += k+" ->"+str(v.name)+"\n"
                    else:
                        out += k+" - "+str(v.name)+"\n"
                self.lockOptions = False


        if self.state == "questSelection":
            self.options = {"1":quests.MoveQuest,"2":quests.ActivateQuest,"3":quests.EnterRoomQuest,"4":quests.FireFurnaceMeta}

            if not self.lockOptions:
                if key == "w":
                    self.selectionIndex -= 1
                    if self.selectionIndex == 0:
                        self.selectionIndex = len(self.options)
                    key = self.selectionIndex
                if key == "s":
                    self.selectionIndex += 1
                    if self.selectionIndex > len(self.options):
                        self.selectionIndex = 1
                    key = self.selectionIndex
                if key in ["enter","j","k"]:
                    key = str(self.selectionIndex)
                if key in self.options:
                    self.quest = self.options[key]
                    self.state = "confirm"
                    self.lockOptions = True
                    out += "quest: "+str(self.quest)+"\n\n"
                    self.selectionIndex = 1

            if self.state == "questSelection":
                out += "what quest to give?\n"
                for k,v in self.options.items():
                    if str(self.selectionIndex) == k:
                        out += k+" ->"+str(v)+"\n"
                    else:
                        out += k+" - "+str(v)+"\n"
                self.lockOptions = False

        if self.state == "confirm":
            if not self.lockOptions:
                questInstance = None
                if self.quest == quests.MoveQuest:
                    questInstance = self.quest(mainChar.room,2,2)
                if self.quest == quests.ActivateQuest:
                    questInstance = self.quest(mainChar.room.furnaces[0])
                if self.quest == quests.EnterRoomQuest:
                    questInstance = self.quest(terrain.tutorialMachineRoom)
                if self.quest == quests.FireFurnaceMeta:
                    questInstance = self.quest(mainChar.room.furnaces[0])
                self.character.assignQuest(questInstance, active=True)

                return True

            self.lockOptions = False

        main.set_text(out)
        return False

def renderHeader():
    questSection = renderQuests(maxQuests=2)
    messagesSection = renderMessages()

    screensize = loop.screen.get_cols_rows()

    questWidth = (screensize[0]//3)-2
    messagesWidth = screensize[0]-questWidth-3
    txt = ""
    counter = 0

    splitedQuests = questSection.split("\n")
    splitedMessages = messagesSection.split("\n")

    rowCounter = 0

    continueLooping = True
    questLine = ""
    messagesLine = ""
    while True:
        if questLine == "" and len(splitedQuests):
            questLine = splitedQuests.pop(0)
        if messagesLine == "" and len(splitedMessages):
            messagesLine = splitedMessages.pop(0)

        rowCounter += 1
        if (rowCounter > 5):
            break

        if len(questLine) > questWidth:
            txt += questLine[:questWidth]+"┃ "
            questLine = questLine[questWidth:]
        else:
            txt += questLine+" "*(questWidth-len(questLine))+"┃ "
            if splitedQuests:
                questLine = splitedQuests.pop(0)
            else:
                questLine = ""

        if len(messagesLine) > messagesWidth:
            txt += messagesLine[:messagesWidth]
            messagesLine = messagesLine[messagesWidth:]
        else:
            txt += messagesLine
            if splitedMessages:
                messagesLine = splitedMessages.pop(0)
            else:
                messagesLine = ""
        txt += "\n"
            

    txt += "━"*+questWidth+"┻"+"━"*(screensize[0]-questWidth-1)+"\n"

    return txt

def renderMessages(maxMessages=5):
    txt = ""
    if len(messages) > maxMessages:
        for message in messages[-maxMessages+1:]:
            txt += str(message)+"\n"
    else:
        for message in messages:
            txt += str(message)+"\n"

    return txt


def renderQuests(maxQuests=0):
    char = mainChar
    txt = ""
    if len(char.quests):
        counter = 0
        for quest in char.quests:
            txt+= "QUEST: "+quest.description+"\n"
            counter += 1
            if counter == maxQuests:
                break
    else:
        txt += "No Quest"

    return txt

def renderInventory():
    char = mainChar
    txt = ""
    if len(char.inventory):
        for item in char.inventory:
            txt+= str(item)+"\n"
    else:
        txt = "empty Inventory"
    return txt

def renderHelp():
    char = mainChar
    txt = "the Goal of the Game is to stay alive and to gain Influence. The daily Grind can be delageted to subordinates and you are able to take Control over and to design whole Mechs and ride the to Victory. Be useful, gain Power and use your Power to be more useful."
    return txt
    
def render():
    chars = terrain.render()

    if mainChar.room:
        centerX = mainChar.room.xPosition*15+mainChar.room.offsetX+mainChar.xPosition
        centerY = mainChar.room.yPosition*15+mainChar.room.offsetY+mainChar.yPosition
    else:
        centerX = mainChar.xPosition
        centerY = mainChar.yPosition

    screensize = loop.screen.get_cols_rows()
    decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(),True)
    screensize = (screensize[0]-decorationSize[0][0],screensize[1]-decorationSize[0][1])

    centeringOffsetX = int((screensize[0]//4)-centerX)
    offsetY = int((screensize[1]//2)-centerY)

    viewsize = 41

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

    return result

# get the interaction loop from the library
loop = urwid.MainLoop(frame, unhandled_input=show_or_exit)

# kick of the interaction loop
loop.set_alarm_in(0.2, callShow_or_exit, "lagdetection")
loop.set_alarm_in(0.0, callShow_or_exit, "~")


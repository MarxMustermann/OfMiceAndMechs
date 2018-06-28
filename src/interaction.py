import src.rooms as rooms
import src.items as items
import src.quests as quests
import src.canvas as canvaslib
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
ignoreNextAutomated = False
ticksSinceDeath = None
levelAutomated = 0

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
    global ignoreNextAutomated
    global ticksSinceDeath

    if key in ("lagdetection",):
        loop.set_alarm_in(0.1, callShow_or_exit, "lagdetection")
        lastLagDetection = time.time()
        if terrain.alarm:
            print('\007')
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
        if not ignoreNextAutomated:
            loop.set_alarm_in(0.2, callShow_or_exit, commandChars.autoAdvance)
        else:
            ignoreNextAutomated = False

    if not submenue:
        global itemMarkedLast
        global lastMoveAutomated
        stop = False
        doAdvanceGame = True
        if len(cinematics.cinematicQueue):
            cinematic = cinematics.cinematicQueue[0]

            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()
            elif key in (commandChars.pause,commandChars.advance,commandChars.autoAdvance):
                cinematic.abort()
                cinematics.cinematicQueue = cinematics.cinematicQueue[1:]
                loop.set_alarm_in(0.0, callShow_or_exit, commandChars.ignore)
                return
            else:
                if not cinematic.advance():
                    return
                if not cinematic.background:
                    key = commandChars.ignore
        if key in (commandChars.ignore):
            doAdvanceGame = False

        if mainChar.dead:
            if not ticksSinceDeath:
                ticksSinceDeath = gamestate.tick
            key = commandChars.wait
            if gamestate.tick > ticksSinceDeath+5:
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("you lost")
                saveFile.close()
                raise urwid.ExitMainLoop()

        if key in stealKey:
            stealKey[key]()
        else:
            if key in ("´",):
                mainChar.assignQuest(quests.TransportQuest(terrain.metalWorkshop.producedItems[0],None),active=True)
                #terrain.waitingRoom.secondOfficer.assignQuest(quests.MurderQuest(mainChar),active=True)
                #mainChar.assignQuest(quests.MurderQuest(terrain.waitingRoom.secondOfficer),active=True)
            if key in (commandChars.quit_delete,):
                saveFile = open("gamestate/gamestate.json","w")
                saveFile.write("reset")
                saveFile.close()
                raise urwid.ExitMainLoop()
            if key in (commandChars.quit_normal, commandChars.quit_instant):
                gamestate.save()
                raise urwid.ExitMainLoop()
            if key in (commandChars.pause):
                ignoreNextAutomated = True
                doAdvanceGame = False
            if key in (commandChars.move_north):
                if mainChar.room:
                    item = mainChar.room.moveCharacterNorth(mainChar)

                    if item:
                        messages.append("You cannot walk there")
                        messages.append("press "+commandChars.activate+" to apply")
                        itemMarkedLast = item
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                            header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                                header.set_text((urwid.AttrSpec("default","default"),renderHeader()))
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
                        char.die()

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

            if key in (commandChars.drink):
                character = mainChar
                for item in character.inventory:
                    if isinstance(item,items.GooFlask):
                        if item.uses > 0:
                            item.apply(character)
                            break

            if key in (commandChars.pickUp):
                if len(mainChar.inventory) > 10:
                    messages.append("you cannot carry more items")

                if mainChar.room:
                    itemByCoordinates = mainChar.room.itemByCoordinates
                    itemList = mainChar.room.itemsOnFloor
                else:
                    itemByCoordinates = terrain.itemByCoordinates
                    itemList = terrain.itemsOnFloor

                if itemMarkedLast:
                    pos = (itemMarkedLast.xPosition,itemMarkedLast.yPosition)
                else:
                    pos = (mainChar.xPosition,mainChar.yPosition)

                if pos in itemByCoordinates:
                    for item in itemByCoordinates[pos]:
                        messages.append(str(item))
                        item.pickUp(mainChar)

            if key in (commandChars.hail):
                submenue = ChatPartnerselection()

            mainChar.automated = False
            if key in (commandChars.advance,commandChars.autoAdvance):
                if len(mainChar.quests):
                    lastMoveAutomated = True

                    mainChar.automated = True
                else:
                    pass
            elif not key in (commandChars.pause):
                lastMoveAutomated = False
                if mainChar.quests:
                    mainChar.setPathToQuest(mainChar.quests[0])

        if not key in ("lagdetection",commandChars.wait,):
            itemMarkedLast = None

        global lastRedraw
        if lastRedraw < time.time()-0.016:
            loop.draw_screen()
            lastRedraw = time.time()

        specialRender = False

        if key in (commandChars.devMenu):
            if displayChars.mode == "unicode":
                displayChars.setRenderingMode("pureASCII")
            else:
                displayChars.setRenderingMode("unicode")

        if key in (commandChars.show_quests):
            submenue = QuestMenu()
        if key in (commandChars.show_inventory):
            submenue = InventoryMenu()
        if key in (commandChars.show_quests_detailed):
            submenue = AdvancedQuestMenu()
        if key in (commandChars.show_characterInfo):
            submenue = CharacterInfoMenu()

        if key in (commandChars.show_help):
            specialRender = True        
            pauseGame = True

        if gamestate.gameWon:
            main.set_text((urwid.AttrSpec("default","default"),""))
            main.set_text((urwid.AttrSpec("default","default"),"credits"))
            header.set_text((urwid.AttrSpec("default","default"),"good job"))

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
            if mainChar.satiation < 30 and mainChar.satiation > -1:
                if mainChar.satiation == 0:
                    messages.append("you starved")
                else:
                    messages.append("you'll starve in "+str(mainChar.satiation)+" ticks!")
            advanceGame()

        header.set_text((urwid.AttrSpec("default","default"),renderHeader()))

        canvas = render()
        main.set_text((urwid.AttrSpec("#999","black"),canvas.getUrwirdCompatible()));

        if (useTiles):
            canvas.setPygameDisplay(pydisplay,pygame)

class SubMenu(object):
    def __init__(self):
        self.state = None
        self.options = {}
        self.selection = None
        self.selectionIndex = 1
        self.persistentText = ""
        self.followUp = None
        super().__init__()

    def setSelection(self, query, options, niceOptions):
        self.options = options
        self.niceOptions = niceOptions
        self.query = query
        self.selectionIndex = 1
        self.lockOptions = True
        self.selection = None

    def getSelection(self):
        return self.selection

    def handleKey(self, key):
        out = "\n"
        out += self.query+"\n"

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
                self.selection = self.options[key]
                self.options = None
                if self.followUp:
                    self.followUp()
                return True
        else:
             self.lockOptions = False

        for k,v in self.niceOptions.items():
            if k == str(self.selectionIndex):
                out += k+" ->"+str(v)+"\n"
            else:
                out += k+" - "+str(v)+"\n"

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText+"\n\n"+out))

        return False

    def set_text(self,text):
        main.set_text((urwid.AttrSpec("default","default"),text))

class SelectionMenu(SubMenu):
    def __init__(self, text, options, niceOptions):
        super().__init__()
        self.setSelection(text, options, niceOptions)

    def handleKey(self, key):
        header.set_text("")

        if not self.getSelection():
             super().handleKey(key)

        if self.getSelection():
            return True
        else:
            return False

class ChatPartnerselection(SubMenu):
    def __init__(self):
        super().__init__()
        self.subMenu = None

    def handleKey(self, key):
        if self.subMenu:
            return self.subMenu.handleKey(key)

        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        if not self.options and not self.getSelection():
            counter = 1
            options = {}
            niceOptions = {}
            if mainChar.room:
                for char in mainChar.room.characters:
                    if char == mainChar:
                        continue
                    options[str(counter)] = char
                    niceOptions[str(counter)] = char.name
                    counter += 1
            self.setSelection("talk with whom?",options,niceOptions)

        if not self.getSelection():
             super().handleKey(key)

        if self.getSelection():
            self.subMenu = ChatMenu(self.selection)
            self.subMenu.handleKey(key)
        else:
            return False

class RecruitChat(SubMenu):
    dialogName = "follow my orders."
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.firstRun = True
        self.done = False
        self.persistentText = ""
        super().__init__()

    def handleKey(self, key):
        if self.firstRun:
            self.persistentText += mainChar.name+": \"come and help me.\"\n"

            if self.partner.reputation > mainChar.reputation:
                if mainChar.reputation <= 0:
                    self.persistentText += self.partner.name+": \"No.\""
                    mainChar.reputation -= 5
                    messages.append("You were rewarded -5 reputation")
                else:
                    if self.partner.reputation//mainChar.reputation:
                        self.persistentText += self.partner.name+": \"you will need at least have to have "+str(self.partner.reputation//mainChar.reputation)+" times as much reputation to have me consider that\"\n"
                        messages.append("You were rewarded -"+str(2*(self.partner.reputation//mainChar.reputation))+" reputation")
                        mainChar.reputation -= 2*(self.partner.reputation//mainChar.reputation)
                    else:
                        self.persistentText += self.partner.name+": \"maybe if you come back later\""
                        mainChar.reputation -= 2
                        messages.append("You were rewarded -2 reputation")
            else:
                if gamestate.tick%2:
                    self.persistentText += self.partner.name+": \"sorry, too busy.\"\n"
                    mainChar.reputation -= 1
                    messages.append("You were rewarded -1 reputation")
                else:
                    self.persistentText += self.partner.name+": \"on it!\"\n"
                    mainChar.subordinates.append(self.partner)
            text = self.persistentText+"\n\n-- press any key --"
            main.set_text((urwid.AttrSpec("default","default"),text))
            self.firstRun = False
            return True
        else:
            self.done = True
            return False

class ChatMenu(SubMenu):
    def __init__(self,partner):
        self.state = None
        self.partner = partner
        self.subMenu = None
        super().__init__()

    def handleKey(self, key):
        header.set_text((urwid.AttrSpec("default","default"),"\nConversation menu\n"))
        out = "\n"

        if self.state == None:
            self.state = "mainOptions"
            self.persistentText += self.partner.name+": \"Everything in Order, "+self.partner.name+"?\"\n"
            self.persistentText += mainChar.name+": \"All sorted, "+mainChar.name+"!\"\n"

        if self.subMenu:
            if not self.subMenu.done:
                self.subMenu.handleKey(key)
                if not self.subMenu.done:
                    return False
            self.subMenu = None
            self.state = "mainOptions"
            self.selection = None
            self.lockOptions = True
            self.options = []

        if self.state == "mainOptions":
            if not self.options and not self.getSelection():
                options = {}
                niceOptions = {}
                counter = 1
                for option in self.partner.getChatOptions(mainChar):
                    options[str(counter)] = option
                    niceOptions[str(counter)] = option.dialogName
                    counter += 1

                options[str(counter)] = "showQuests"
                niceOptions[str(counter)] = "what are you dooing?"
                counter += 1

                options[str(counter)] = "exit"
                niceOptions[str(counter)] = "let us proceed, "+self.partner.name
                counter += 1

                self.setSelection("answer:",options,niceOptions)

            if not self.getSelection():
                super().handleKey(key)
            if self.getSelection():
                if not isinstance(self.selection,str):
                    self.subMenu = self.selection(self.partner)
                    self.subMenu.handleKey(key)
                elif self.selection == "showQuests":
                    submenue = QuestMenu(char=self.partner)
                    submenue.handleKey(key)
                    return False
                elif self.selection == "exit":
                    self.state = "done"
                self.selection = None
                self.lockOptions = True
            else:
                return False

        if self.state == "done":
            if self.lockOptions:
                self.persistentText += self.partner.name+": \"let us proceed, "+self.partner.name+".\"\n"
                self.persistentText += mainChar.name+": \"let us proceed, "+mainChar.name+".\"\n"
                self.lockOptions = False
            else:
                return True

        if not self.subMenu:
            main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

class QuestMenu(SubMenu):
    def __init__(self,char=None):
        self.lockOptions = True
        self.char = char
        super().__init__()

    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\nquest overview\n(press "+commandChars.show_quests_detailed+" for the extended quest menu)\n\n"))

        self.persistentText = ""

        self.persistentText += renderQuests(char=self.char)

        if not self.lockOptions:
            if key in ["q"]:
                submenue = AdvancedQuestMenu()
                submenue.handleKey(key)
                return False
        self.lockOptions = False

        self.persistentText += "\n * press q for advanced quests "+str(self.char)+"\n\n"

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

class InventoryMenu(SubMenu):
    def __init__(self):
        self.lockOptions = True
        super().__init__()

    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\ninventory overview\n(press "+commandChars.show_inventory_detailed+" for the extended inventory menu)\n\n"))

        self.persistentText = (urwid.AttrSpec("default","default"),renderInventory())

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

        return False

class CharacterInfoMenu(SubMenu):
    def __init__(self):
        self.lockOptions = True
        super().__init__()

    def handleKey(self, key):
        global submenue

        header.set_text((urwid.AttrSpec("default","default"),"\ncharacter overview"))
        main.set_text((urwid.AttrSpec("default","default"),mainChar.getDetailedInfo()))
        header.set_text((urwid.AttrSpec("default","default"),""))

class AdvancedQuestMenu(SubMenu):
    def __init__(self):
        self.character = None
        self.quest = None
        super().__init__()

    def handleKey(self, key):
        header.set_text((urwid.AttrSpec("default","default"),"\nadvanced Quest management\n"))
        out = "\n"

        if self.character:
            out += "character: "+str(self.character.name)+"\n"
        if self.quest:
            out += "quest: "+str(self.quest)+"\n"
        out += "\n"

        if self.state == None:
            self.state = "participantSelection"

        if self.state == "participantSelection":
            if not self.options and not self.getSelection():
                options = {}
                niceOptions = {}
                options["1"] = mainChar
                niceOptions["1"] = mainChar.name+" (you)"
                counter = 1
                for char in mainChar.subordinates:
                    counter += 1
                    options[str(counter)] = char
                    niceOptions[str(counter)] = char.name
                self.setSelection("whom to give the order to: ",options,niceOptions)

            if not self.getSelection():
                super().handleKey(key)
                
            if self.getSelection():
                self.state = "questSelection"
                self.character = self.selection
                self.selection = None
                self.lockOptions = True
            else:
                return False

        if self.state == "questSelection":
            if not self.options and not self.getSelection():
                options = {"1":quests.MoveQuest,"2":quests.ActivateQuest,"3":quests.EnterRoomQuest,"4":quests.FireFurnaceMeta,"5":quests.ClearRubble,"6":quests.ConstructRoom}
                niceOptions = {"1":"MoveQuest","2":"ActivateQuest","3":"EnterRoomQuest","4":"FireFurnaceMeta","5":"ClearRubble","6":"ConstructRoom"}
                self.setSelection("what type of quest:",options,niceOptions)

            if not self.getSelection():
                super().handleKey(key)

            if self.getSelection():
                self.state = "confirm"
                self.quest = self.selection
                self.selection = None
                self.lockOptions = True
            else:
                return False

        if self.state == "confirm":
            if self.lockOptions:
                questInstance = None
                if self.quest == quests.MoveQuest:
                    questInstance = self.quest(mainChar.room,2,2)
                if self.quest == quests.ActivateQuest:
                    questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0])
                if self.quest == quests.EnterRoomQuest:
                    questInstance = self.quest(terrain.tutorialMachineRoom)
                if self.quest == quests.FireFurnaceMeta:
                    questInstance = self.quest(terrain.tutorialMachineRoom.furnaces[0])
                if self.quest == quests.ClearRubble:
                    questInstance = self.quest()
                if self.quest == quests.ConstructRoom:
                    storageRoom = terrain.roomByCoordinates[(5,4)][0]
                    construction = terrain.roomByCoordinates[(4,2)][0]
                    questInstance = self.quest(construction,storageRoom)
                self.character.assignQuest(questInstance, active=True)
                self.lockOptions = False
                if not self.character == mainChar:
                    self.persistentText += self.character.name+": \"understood?\"\n"
                    self.persistentText += mainChar.name+": \"understood and in execution\"\n"
                else:
                    return True

            else:
                self.state = "done"

        if self.state == "done":
            if self.lockOptions:
                self.lockOptions = False
            else:
                return True

        main.set_text((urwid.AttrSpec("default","default"),self.persistentText))

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


def renderQuests(maxQuests=0,char=None):
    if not char:
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

    viewsize = 41
    halfviewsite = (viewsize-1)//2

    screensize = loop.screen.get_cols_rows()
    decorationSize = frame.frame_top_bottom(loop.screen.get_cols_rows(),True)
    screensize = (screensize[0]-decorationSize[0][0],screensize[1]-decorationSize[0][1])

    shift = (screensize[1]//2-20,screensize[0]//4-20)
    canvas = canvaslib.Canvas(size=(viewsize,viewsize),chars=chars,coordinateOffset=(centerY-halfviewsite,centerX-halfviewsite),shift=shift,displayChars=displayChars)

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


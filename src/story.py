phasesByName = None
gamestate = None
names = None
characters = None
events = None

#####################################
###
##   convinience functions
#
#####################################

'''
add message cinematic
'''
def showMessage(message,trigger=None):
    cinematic = cinematics.ShowMessageCinematic(message)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add show game cinematic
'''
def showGame(duration,trigger=None):
    cinematic = cinematics.ShowGameCinematic(duration,tickSpan=1)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add show quest cinematic
'''
def showQuest(quest,assignTo=None,trigger=None):
    cinematic = cinematics.ShowQuestExecution(quest,tickSpan=1,assignTo=assignTo)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add text cinematic
'''
def showText(text,rusty=False,autocontinue=False,trigger=None,scrolling=False):
    cinematic = cinematics.TextCinematic(text,rusty=rusty,autocontinue=autocontinue,scrolling=scrolling)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add message cinematic mimicing speech
'''
def say(text,speaker=None,trigger=None):
    prefix = ""
    if speaker:
        display = speaker.display
        if isinstance(display,str):
            prefix = display
        elif isinstance(display,int):
            display = displayChars.indexedMapping[speaker.display]
            if isinstance(display,str):
                prefix = display
            else:
                prefix = display[1]
        else:
            prefix = display[1]
        prefix += ": "
    showMessage(prefix+'"'+text+'"',trigger=trigger)

"""
the base class for the all phases here
"""
class BasicPhase(object):
    '''
    state initialisation
    bad code: creating default attributes in init and set them externally later
    '''
    def __init__(self):
        self.mainCharXPosition = None
        self.mainCharYPosition = None
        self.mainCharRoom = None
        self.requiresMainCharRoomFirstOfficer = True 
        self.requiresMainCharRoomSecondOfficer = True 
        self.mainCharQuestList = []
        # bad code: these positions were convinient but should be removed
        self.firstOfficerXPosition = 4
        self.firstOfficerYPosition = 3
        self.secondOfficerXPosition = 5
        self.secondOfficerYPosition = 3

    '''
    start the game phase
    '''
    def start(self):
        # set state
        gamestate.currentPhase = self
        self.tick = gamestate.tick

        # place main character
        if self.mainCharRoom:
            if not (mainChar.room or mainChar.terrain):
                if self.mainCharXPosition and self.mainCharYPosition:
                    self.mainCharRoom.addCharacter(mainChar,self.mainCharXPosition,self.mainCharYPosition)
                else:
                    self.mainCharRoom.addCharacter(mainChar,3,3)

        # create first officer
        if self.requiresMainCharRoomFirstOfficer:
            if not self.mainCharRoom.firstOfficer:
                name = names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)]
                self.mainCharRoom.firstOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name)
                self.mainCharRoom.addCharacter(self.mainCharRoom.firstOfficer,self.firstOfficerXPosition,self.firstOfficerYPosition)
            self.mainCharRoom.firstOfficer.reputation = 1000

        # create second officer
        if self.requiresMainCharRoomSecondOfficer:
            if not self.mainCharRoom.secondOfficer:
                name = names.characterFirstNames[(gamestate.tick+4)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)]
                self.mainCharRoom.secondOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name)
                self.mainCharRoom.addCharacter(self.mainCharRoom.secondOfficer,self.secondOfficerXPosition,self.secondOfficerYPosition)
            self.mainCharRoom.secondOfficer.reputation = 100

        # save initial state
        gamestate.save()

    '''
    helper function to properly hook player quests
    '''
    def assignPlayerQuests(self):
        # do nothing
        if not self.mainCharQuestList:
            return

        # chain quests
        lastQuest = self.mainCharQuestList[0]
        for item in self.mainCharQuestList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        self.mainCharQuestList[-1].followup = None

        # chain last quest to the phases teardown
        self.mainCharQuestList[-1].endTrigger = self.end

        # assign the first quest
        mainChar.assignQuest(self.mainCharQuestList[0])

"""

the phase is intended to give the player access to the true gameworld without manipulations

this phase should be left as blank as possible

"""
class OpenWorld(object):
    '''
    place main char
    '''
    def __init__(self):
        cinematics.showCinematic("staring open world Scenario.")
        if terrain.wakeUpRoom:
            self.mainCharRoom = terrain.wakeUpRoom
            self.mainCharRoom.addCharacter(mainChar,2,4)
        else:
            mainChar.xPosition = 2
            mainChar.yPosition = 4
            mainChar.terrain = terrain
            terrain.characters.append(mainChar)

    '''
    forcebly do nothing
    bad code: superclass call should not be prevented
    '''
    def start(self):
        pass

"""

this phase is intended to be nice to watch and to be running as demo piece or something to stare at

right now experiments are done here, but that should be shifted somwhere else later

"""
class ScreenSaver(object):
    '''
    place main char and initiate some actions to look at
    '''
    def __init__(self):
        # place main char
        self.mainCharRoom = terrain.wakeUpRoom
        self.mainCharRoom.addCharacter(mainChar,2,4)

        self.mainCharQuestList = []
        # bad code: commented out code
        '''
        for x in range(1,6):
            for y in range(1,6):
                for z in range(1,1): # can be tweaked for performance testing (500(40) npc and more lag but don't grid the game to halt)
                    npc1 = characters.Character(displayChars.staffCharactersByLetter["e"],5,3,name="Eduart Knoblauch")
                    self.mainCharRoom.addCharacter(npc1,x,y)
                    npc1.terrain = terrain
                    self.mainCharRoom.firstOfficer = npc1
                    npcs.append(npc1)

        self.mainCharQuestList = []

        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

        """
        questlist = []
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[0])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[1])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[2])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[3])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[4])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[5])
        questlist.append(quest)
        quest = quests.KeepFurnaceFiredMeta(terrain.tutorialMachineRoom.furnaces[6])

        quest = quests.MetaQuest2(questlist,lifetime=100)
        self.mainCharQuestList.append(quest)

        self.addKeepFurnaceFired()
        self.cycleDetectionTest()
        self.addWaitQuest()
        self.addKeepFurnaceFired()
        self.addPseudeoFurnacefirering()
        self.addIntraRoomMovements()
        self.addInnerRoomMovements()
        """

        questlist = []
        for room in terrain.rooms:
            if not isinstance(room,rooms.MechArmor):
                quest = quests.EnterRoomQuest(room)
                questlist.append(quest)
        '''

        # add items to be picked up
		# bad code: should use transport quest
        questlist = []
        for item in terrain.testItems:
            quest = quests.PickupQuestMeta(item)
            questlist.append(quest)
            quest = quests.DropQuestMeta(item,terrain.tutorialMachineRoom,2,2)
            questlist.append(quest)

        # add npc to pick stuff up
        cleaner = characters.Character(displayChars.staffCharactersByLetter["f"],6,6,name="Friedrich Eisenhauch")
        self.mainCharRoom.addCharacter(cleaner,6,6)
        cleaner.terrain = terrain

        # add npc to pick stuff up
        lastQuest = questlist[0]
        for item in questlist[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questlist[-1].followup = None
        cleaner.assignQuest(questlist[0],active=True)

        # bad code: commented out code
        #self.addIntraRoomMovements()
        #self.addInnerRoomMovements()
        #self.mainCharQuestList[-1].followUp = self.mainCharQuestList[0]

        # add more active npcs
        self.addFurnitureMovingNpcs()

    '''
    add npcs moving furniture around
    '''
    def addFurnitureMovingNpcs(self):
        # create some npc
        npcs = []
        for i in range(0,2):
            npc = characters.Character(displayChars.staffCharactersByLetter["e"],5,3,name="Eduart Knoblauch")
            self.mainCharRoom.addCharacter(npc,2,2+i)
            npc.terrain = terrain
            npcs.append(npc)

        # make them move furniture
        self.assignFurnitureMoving(npcs+[mainChar])

    '''
    assign quests to make npc 
    '''
    def assignFurnitureMoving(self,chars):
        counter = 0
        for char in chars:
            # get source and target rooms
            targetRoom = terrain.tutorialCargoRooms[counter*3]
            targetIndex = len(targetRoom.storedItems)

            # generate transport quests
            # bad code: should actually use transport quest
            questlist = []
            for srcRoom in (terrain.tutorialCargoRooms[counter*3+1],terrain.tutorialCargoRooms[counter*3+2]):
                srcIndex = len(srcRoom.storedItems)-1
                while srcIndex > -1:
                    # pick up item
                    pos = srcRoom.storageSpace[srcIndex]
                    item = srcRoom.itemByCoordinates[pos][0]
                    quest = quests.PickupQuestMe(item)
                    questlist.append(quest)

                    # drop item
                    pos = targetRoom.storageSpace[targetIndex]
                    quest = quests.DropQuestMeta(item,targetRoom,pos[0],pos[1])
                    questlist.append(quest)

                    srcIndex -= 1
                    targetIndex += 1

            # bad code: commented out code
            """
            for i in range(3,8):
                for j in range(0,7):
                    item = terrain.tutorialCargoRooms[i+(counter*7)].storedItems[j]
                    quest = quests.PickupQuest(item)
                    questlist.append(quest)
                    quest = quests.DropQuest(item,terrain.tutorialCargoRooms[2+(counter*7)],1+j,12-i)
                    questlist.append(quest)
            """

            # chain the quests
            lastQuest = questlist[0]
            for item in questlist[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questlist[-1].followup = None

            # assign first quest
            char.assignQuest(questlist[0],active=True)

            counter += 1

    '''
    assign quests to walk into every room 
    '''
    def assignWalkQuest(self,chars):
        counter = 0
        for npc in npcs:
            counter += 1

            # hold questlists for each npc
            # bad code: should be outside of loop
            questlists = {}
            for index in range(0,counter):
                questlists[index] = []

            # generate quest lists with a pseudorandom split (shuffle)
            # bad code: should be outside of loop
            roomCounter = 0
            for room in terrain.rooms:
                roomCounter += 1
                if not isinstance(room,rooms.MechArmor):
                    quest = quests.EnterRoomQuest(room)
                    questlists[roomCounter%counter].append(quest)

            # recombine the quest to visit rooms to one big list (merge)
            questlist = []
            for index in range(0,counter):
                questlist.extend(questlists[index])

            # chain quests
            lastQuest = questlist[0]
            for item in questlist[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questlist[-1].followup = None

            # assign quests
            npc.assignQuest(questlist[0])

    '''
    make the main character run paths that were known to were bugged
    bad code: use unittests for testing
    '''
    def cycleDetectionTest(self):
        quest = quests.MoveQuest(terrain.tutorialVat,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialVatProcessing,6,6)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

    '''
    make the main character wait for some time
    '''
    def addWaitQuest(self):
        quest = quests.WaitQuest(lifetime=40)
        self.mainCharQuestList.append(quest)

    '''
    make the main char fire some furnaces
    '''
    def addKeepFurnaceFired(self):
        # move main chat to the machine room
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

        # generate fireing quests
        questList = []
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[0],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[1],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[2],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[3],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[4],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[5],lifetime=20)
        questList.append(quest)
        quest = quests.KeepFurnaceFired(terrain.tutorialMachineRoom.furnaces[6],lifetime=20)
        questList.append(quest)

        # assign quest
        # bad code: MetaQuest doesn't even exist anymore
        quest = quests.MetaQuest(questList)
        self.mainCharQuestList.append(quest)

    '''
    make the mainchar do the moves for firering furnaces
    '''
    def addPseudeoFurnacefirering(self):
        # move to machine room
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

        # collect fuel
        quest = quests.FillPocketsQuest()
        self.mainCharQuestList.append(quest)

        # activate furnace
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[0])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[1])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[2])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[3])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[4])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[5])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[6])
        self.mainCharQuestList.append(quest)
        quest = quests.ActivateQuest(terrain.tutorialMachineRoom.furnaces[7])
        self.mainCharQuestList.append(quest)

    '''
    make main char move within a room
    bad code: unit test should be unit tests
    '''
    def addInnerRoomMovements(self):
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,4)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,4)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,3)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,4)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,4)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,2)
        self.mainCharQuestList.append(quest)

    '''
    make main char move between rooms
    bad code: unit test should be unit tests
    '''
    def addIntraRoomMovements(self):
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialVat,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialVatProcessing,6,6)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialLab,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialVat,2,2)
        self.mainCharQuestList.append(quest)

    '''
    show off the
    bad code: debug code should be removed
    '''
    def start(self):
        messages.append("1")
        messages.append("2")
        messages.append("3")
        messages.append("4")
        messages.append("5")
        messages.append("6")
        messages.append("7")
        messages.append("8")
        messages.append("9")
        cinematics.showCinematic("testing message zoom")
        cinematic = cinematics.MessageZoomCinematic()
        cinematics.cinematicQueue.append(cinematic)
        pass

    '''
    do nothing when done
    bad code: overwriting super class should not be neccessary
    '''
    def end(self):
        pass

    '''
    bad code: duplicate code from super class
    '''
    def assignPlayerQuests(self):
        # do nothing
        if not self.mainCharQuestList:
            return

        # chain quests
        lastQuest = self.mainCharQuestList[0]
        for item in self.mainCharQuestList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        self.mainCharQuestList[-1].followup = None

        # chain last quest to the phases teardown
        self.mainCharQuestList[-1].endTrigger = self.end

        # assign the first quest
        mainChar.assignQuest(self.mainCharQuestList[0])

########################################################################################
###
##   these are the tutorial phases. The story phases are tweeked heavily regarding to cutscenes and timing
#    ideally this phase should force the player how rudementary use of the controls. This should be done by 
#    explaining first and then preventing progress until the player proves capability.
#
#    no experients here!
#    half arsed solutions are still welcome here but that should end when this reaches prototype
#
########################################################################################

'''
show some fluff messages and enforce learning how to use a selection
'''
class BrainTestingPhase(BasicPhase):
    '''
    straightforward state initialisation
    '''
    def __init__(self):
        self.name = "BrainTesting" # should be outside of constructor
        super().__init__()

    '''
    show some messages and place trigger
    bad code: closely married to urwid
    '''
    def start(self):
        import urwid

        # show fluff
        showText(["""
initialising subject ...................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""

testing subject with random input 

NyGUf8fDJO
g215e4Za8U
EpiSdpeNuV
7vqnf7ASAO
azZ1tESXGR
sR6jzKMBv3
eGAxLZCXXi
DW9H6uAW8R
dk8R9BXMfa
Ttbt9kp2wZ

checking subjects brain patterns .......................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""

testing subjects responsivity
"""],scrolling=True)

        # show info referenced later
        showText(["""
got response
responsivity .............................................. """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""

inititializing implant .................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""

checking implant .......................................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""

send test information

1.) Your name is """+mainChar.name+"""
2.) A Pipe is used to transfer fluids
3.) rust - Rust is the oxide of iron. Rust is the most common form of corrosion
"""],scrolling=True)

        # show fluff
        showText("""
checking stored information

entering interactive mode .................................
        """,autocontinue=True,scrolling=True)

        # add trigger for false and true answers
        options = {1:"nok",2:"ok",3:"nok"}
        niceOptions = {1:"Karl Weinberg",2:mainChar.name,3:"Susanne Kreismann"}
        text = "\nplease answer the question:\n\nwhat is your name?"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step2,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    show fluff and fail phase
    '''
    def infoFail(self):
        import urwid
        showText(["information storage ....................................... ",(urwid.AttrSpec("#f22",'default'),"NOT OK"),"                                        "],autocontinue=True,trigger=self.fail,scrolling=True)
        return

    '''
    ask question and place trigger
    bad code: bad name
    bad code: bad datastructure leads tu ugly code
    '''
    def step2(self):
        options = {1:"ok",2:"nok",3:"nok"}
        niceOptions = {1:"A Pipe is used to transfer fluids",2:"A Grate is used to transfer fluids",3:"A Hutch is used to transfer fluids"}
        text = "\nplease select the true statement:\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step3,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    ask question and place trigger
    bad code: bad name
    bad code: bad datastructure leads tu ugly code
    '''
    def step3(self):
        options = {1:"ok",2:"nok",3:"nok"}
        niceOptions = {1:"Rust is the oxide of iron. Rust is the most common form of corrosion",2:"Rust is the oxide of iron. Corrosion in form of Rust is common",3:"*deny answer*"}
        text = "\nplease repeat the definition of rust\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step4,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    show fluff info with effect and place trigger
    bad code: bad name
    bad code: bad datastructure leads tu ugly code
    '''
    def step4(self):
        import urwid
        
        # set bogus information
        definitions = {}
        definitions["pipe"] = "A Pipe is used to transfer fluids"
        definitions["wall"] = "A Wall is a non passable building element"
        definitions["lorem2"] = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."
        definitions["lorem3"] = "felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi."
        definitions["lorem4"] = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.
Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu.

In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus.

Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum.

Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum.

Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, """
        definitions["lorem5"] = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim.

Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus.

Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi.

Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, """

        # show fluff
        showText([""" 
information storage ....................................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""
setting up knowledge base

"""] ,autocontinue=True,scrolling=True)

        cinematic = cinematics.InformationTransfer(definitions)
        cinematics.cinematicQueue.append(cinematic)
        
        # show fluff (write copy to messages to have this show up during zoom
        messages.append("initializing metabolism ..................................... done")
        messages.append("initializing motion control ................................. done")
        messages.append("initializing sensory organs ................................. done")
        messages.append("transfer control to implant")

        # show fluff
        showText(["""
initializing metabolism ..................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
initializing motion control ................................. """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
initializing sensory organs ................................. """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
transfer control to implant"""],autocontinue=True,scrolling=True)

        # zooom out and end phase
        cinematic = cinematics.MessageZoomCinematic()
        cinematic.endTrigger = self.end
        cinematics.cinematicQueue.append(cinematic)

    '''
    call next phase
    '''
    def end(self):
        nextPhase = WakeUpPhase()
        nextPhase.start()

    '''
    kill the player
    '''
    def fail(self):
        # kill player
        mainChar.dead = True
        mainChar.deathReason = "reset of neural network due to inability to store information\nPrevent this by answering the questions correctly"

        # show fluff
        showText("""
aborting initialisation
resetting neural network ....................................""",autocontinue=True,trigger=self.forceExit,scrolling=True)

    '''
    exit game
    bad code: pretty direct call, should be indirect probably
    '''
    def forceExit(self):
        import urwid
        raise urwid.ExitMainLoop()

'''
show the main char waking up
'''
class WakeUpPhase(BasicPhase):
    '''
    basic state initialization
    '''
    def __init__(self):
        self.name = "WakeUpPhase"
        super().__init__()

    '''
    show some fluff and place trigger
    '''
    def start(self):
        # place characters
        self.mainCharXPosition = 1
        self.mainCharYPosition = 4
        self.firstOfficerXPosition = 6
        self.firstOfficerYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False

        # start timer for tracking performance
        mainChar.tutorialStart = gamestate.tick

        # make main char hungry and naked
        mainChar.satiation = 250
        mainChar.inventory = []
        mainChar.quests = []

        # set the wake up room as play area
        # bad code should be set elsewhere
        self.mainCharRoom = terrain.wakeUpRoom

        super().start()

        # hide main char from map
        self.mainCharRoom.characters.remove(mainChar)

        # select npc
        self.npc = self.mainCharRoom.firstOfficer

        # show fluff
        showGame(2)
        showMessage("implant has taken control")
        showGame(2)
        showMessage("please prepare to be ejected")
        showGame(2)
        showMessage("note that you will be unable to move until implant imprinting")
        showGame(6)
        showMessage("ejecting now")
        showGame(2)
        showMessage("*ting*")
        showGame(1)
        showMessage("*screetch*")

        # add trigger
        showGame(1,trigger=self.playerEject)

    '''
    spawn players body and place trigger
    '''
    def playerEject(self):
        # add players body
        item = items.UnconciousBody(2,4)
        terrain.wakeUpRoom.addItems([item])
        terrain.wakeUpRoom.itemByCoordinates[(1,4)][0].eject()

        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # show fluff
        showMessage("*schurp**splat*")
        showGame(2)
        showMessage("please wait for assistance")
        showGame(2)
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,4)
        showQuest(quest,firstOfficer)
        say("I AM "+firstOfficer.name.upper()+" AND I DEMAND YOUR SERVICE.",firstOfficer)
        showGame(1)
        showMessage("implant imprinted - setup complete")
        showGame(4)
        say("wake up, "+mainChar.name,firstOfficer)
        showGame(3)
        say("WAKE UP.",firstOfficer)
        showGame(2)
        say("WAKE UP.",firstOfficer)
        showMessage("*kicks "+mainChar.name+"*")

        # show fluff
        showGame(3,trigger=self.addPlayer)

    '''
    add the player and place triggers
    '''
    def addPlayer(self):
        # remove players body
        self.mainCharRoom.removeItem(terrain.wakeUpRoom.itemByCoordinates[(2,4)][0])

        # add player chracter
        self.mainCharRoom.addCharacter(mainChar,2,4)

        # redraw
        loop.set_alarm_in(0.1, callShow_or_exit, '.')

        # wrap up
        self.end()

    '''
    start next phase
    '''
    def end(self):
        phase = BasicMovementTraining()
        phase.start()

'''
explain and test basic movement and interaction
'''
class BasicMovementTraining(BasicPhase):
    '''
    basic state initialization
    '''
    def __init__(self):
        self.name = "BasicMovementTraining"
        super().__init__()
        self.didFurnaces = False
    
    '''
    make the player move around and place triggers
    '''
    def start(self):
        # minimal setup
        self.mainCharXPosition = 2
        self.mainCharYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False
        self.mainCharRoom = terrain.wakeUpRoom

        super().start()

        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        
        # show fluff
        showText("""
welcome to the trainingsenvironment.

please follow the orders """+firstOfficer.name+" gives you.",rusty=True,scrolling=True)

        # show instructions
        showText(["""
you are represented by the """,displayChars.indexedMapping[displayChars.main_char]," Character,  ",firstOfficer.name," is represented by the ",displayChars.indexedMapping[firstOfficer.display],""" Character. 

you can move using the keyboard. 

* press """,commandChars.move_north,""" to move up/north
* press """,commandChars.move_west,""" to move left/west
* press """,commandChars.move_south,""" to move down/south
* press """,commandChars.move_east,""" to move right/east

Your target is marked by """+displayChars.indexedMapping[displayChars.questTargetMarker][1]+""" and a path to your target is highlighted. You may follow this path or find your own way"""])
        showGame(1)

        # ask the player to follow npc
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,4)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        showMessage("the current quest destination is shown as: "+displayChars.indexedMapping[displayChars.questTargetMarker][1])
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,4)
        showQuest(quest,mainChar)
        quest = quests.MoveQuest(terrain.wakeUpRoom,5,4)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,4)
        showQuest(quest,mainChar)
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,7)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,5,7)
        showQuest(quest,mainChar)

        # ask player to move around
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,7)
        showQuest(quest,mainChar)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,3)
        showQuest(quest,mainChar)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,4)
        showQuest(quest,mainChar)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,3)
        showQuest(quest,mainChar)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,6)
        showQuest(quest,mainChar)
        say("great. You seemed be able to coordinate yourself",firstOfficer)
        showGame(1)
        say("you look thirsty, one more task and you get something to drink",firstOfficer)

        # ask player to move to the lever
        showGame(2)
        say("move over to the lever now",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,2)
        showQuest(quest,mainChar)
        
        import urwid
        # show instructions
        showText(["you can activate levers by moving onto the lever and then pressing "+commandChars.activate+"""\n
Here is how to do this:\n\nImagine you are standing next to a lever

""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],"""
""",displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.lever_notPulled],"U\\",displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.main_char],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],"""

press """+commandChars.move_north+""" to move onto the lever and press """+commandChars.activate+""" to activate the lever.
After pulling the lever a flask should apear like this.

""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],"""
""",displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.main_char],"U\\",displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],(urwid.AttrSpec("#3f3","black"),"ò="),displayChars.indexedMapping[displayChars.floor],"""

now, go and pull the lever
"""])
        showMessage("you can activate levers by moving onto the lever and then pressing "+commandChars.activate)

        # ask player to pull the lever and add trigger
        say("activate the lever",firstOfficer)
        quest = quests.ActivateQuest(terrain.wakeUpRoom.lever1)
        showQuest(quest,mainChar,trigger=self.fetchDrink)

    '''
    make the main char drink and have a chat
    '''
    def fetchDrink(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        drink = terrain.wakeUpRoom.itemsOnFloor[-1]

        # show instructions
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        showGame(3)
        msg = "you can pick up items by moving onto them and using "+commandChars.pickUp
        showText(msg)
        showMessage(msg)
        say("well done, go and fetch your drink",firstOfficer)

        # ask the player to pick up the flask
        quest = quests.PickupQuestMeta(drink)
        showQuest(quest,mainChar)

        # show instructions
        msg = "you can drink using "+commandChars.drink+". If you do not drink for a longer time you will starve"
        say("great. Drink from the flask you just fetched and come over for a quick talk.",firstOfficer)
        showMessage(msg)

        # ask the player to pick up the flask
        quest = quests.DrinkQuest()
        showQuest(quest,mainChar)

        # make the player talk to the npc
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,6)
        showQuest(quest,mainChar)
        msg = "you can talk to people by pressing "+commandChars.hail+" and selecting the person to talk to."
        showMessage(msg)
        showText(msg)

        '''
        a monologe explaining automovement
        '''
        class SternChat(interaction.SubMenu):
            dialogName = "What did Stern modify on the implant?"

            '''
            straight forwar state setting
            '''
            def __init__(subSelf,partner):
                subSelf.submenue = None
                subSelf.firstRun = True
                subSelf.done = False
                super().__init__()

            '''
            show the dialog for one keystroke
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    # show fluffed up information
                    subSelf.persistentText = """Stern did not actually modify the implant. The modification was done elsewhere.
But that is concerning the artworks, thats nothing you need to know.

You need to know however that Sterns modification enhanced the implants guidance, control and communication abilities.
If you stop thinking and allow the implant to take control, it will do so and continue your task.
You can do so by pressing """+commandChars.autoAdvance+"""

It is of limited practability though. It is mainly useful for stupid manual labor and often does not 
do things the most efficent way. It will even try to handle conversion, wich does not allways lead to optimal results"""
                    messages.append("press "+commandChars.autoAdvance+" to let the implant take control ")
                    subSelf.set_text(subSelf.persistentText)
                    subSelf.firstRun = False
                    return False
                else:
                    # remove chat option and finish
                    firstOfficer.basicChatOptions.remove(SternChat)
                    subSelf.done = True
                    return True

        '''
        a instruction to ask questions and hinting at the auto mode
        '''
        class InfoChat(interaction.SubMenu):
            dialogName = "Is there more i should know?"

            '''
            straight forwar state setting
            '''
            def __init__(subSelf,partner):
                subSelf.submenue = None
                subSelf.firstRun = True
                subSelf.done = False
                super().__init__()

            '''
            show the dialog for one keystroke
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    # show fluffed up information
                    subSelf.persistentText = """yes and a lot of it. I will give you two of these things on your way:\n
1. You will need to pick up most of the Information along the way. Ask around and talk to people.
   Asking questions may hurt your reputation, since you will apear like new growth. 
   You are, so do not heasitate to learn the neccesary Information before you have a reputation to loose.\n
2. Do not rely on the implant to guide you through dificult tasks. 
   Sterns modifications are doing a good job for repetitive tasks but are no replacement
   for a brain.\n\n"""
                    subSelf.set_text(subSelf.persistentText)
                    subSelf.firstRun = False
                    return False
                else:
                    # remove chat option and finish
                    firstOfficer.basicChatOptions.remove(InfoChat)
                    firstOfficer.basicChatOptions.append(SternChat)
                    subSelf.done = True
                    return True

        '''
        the chat to proof the player is able to chat
        '''
        class FirstChat(interaction.SubMenu):
            dialogName = "You wanted to have a chat"

            '''
            straightforward state setting
            '''
            def __init__(subSelf,partner):
                subSelf.done = False
                subSelf.persistentText = ""
                subSelf.firstRun = True
                super().__init__()

            '''
            show the dialog for one keystroke
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    # show fluffed up information
                    subSelf.persistentText = "indeed.\n\nI am "+firstOfficer.name+" and do the acceptance tests. This means i order you to do some things and you will comply.\n\nYour implant will store the orders given. When you press q you will get a list of your current orders. Try to get familiar with the implant,\nit is an important tool for keeping things in order.\n\nDo not mind that the tests seem somewhat without purpose, protocol demands them and after you complete the test you will serve as an hooper on the Falkenbaum."
                    messages.append("press q to see your questlist")
                    interaction.submenue = None
                    subSelf.set_text(subSelf.persistentText)

                    # remove chat option
                    firstOfficer.basicChatOptions.remove(FirstChat)

                    # trigger further action
                    self.examineStuff()
                    return False
                else:
                    # finish
                    subSelf.done = True
                    return True

        '''
        dialog to unlock a furnace firering option
        '''
        class FurnaceChat(interaction.SubMenu):
            dialogName = "What are these machines in this room?"

            '''
            straightforward state setting
            '''
            def __init__(subSelf,partner):
                subSelf.state = None
                subSelf.partner = partner
                subSelf.firstRun = True
                subSelf.done = False
                subSelf.persistentText = ""
                subSelf.submenue = None
                super().__init__()

            '''
            offer the player a option to go deeper
            '''
            def handleKey(subSelf, key):
                if subSelf.submenue:
                    if not subSelf.submenue.handleKey(key):
                        # let the selection option hande the keystroke
                        return False
                    else:
                        subSelf.done = True

                        # let the selection option hande the keystroke
                        firstOfficer.basicChatOptions.remove(FurnaceChat)
                        interaction.submenue = None
                        interaction.loop.set_alarm_in(0.0, callShow_or_exit, '~')
                        subSelf.submenue.selection()
                        return True

                # do first part of the dialog
                if subSelf.firstRun:
                    # show information
                    subSelf.persistentText = ["There are some growth tanks (",displayChars.indexedMapping[displayChars.growthTank_filled],"/",displayChars.indexedMapping[displayChars.growthTank_unfilled],"), walls (",displayChars.indexedMapping[displayChars.wall],"), a pile of coal (",displayChars.indexedMapping[displayChars.pile],") and a furnace (",displayChars.indexedMapping[displayChars.furnace_inactive],"/",displayChars.indexedMapping[displayChars.furnace_active],")."]
                    subSelf.set_text(subSelf.persistentText)

                    # add new chat option
                    firstOfficer.basicChatOptions.append(InfoChat)
                                
                    # set up the selection
                    options = {}
                    niceOptions = {}
                    counter = 1
                    for quest in terrain.waitingRoom.quests:
                        options[str(counter)] = quest
                        niceOptions[str(counter)] = quest.description.split("\n")[0]
                        counter += 1
                    options = {1:self.fireFurnaces,2:self.noFurnaceFirering}
                    niceOptions = {1:"Yes",2:"No"}
                    subSelf.submenue = interaction.SelectionMenu("Say, do you like furnaces?",options,niceOptions)

                return False
                   
        # add chat options
        firstOfficer.basicChatOptions.append(FirstChat)
        firstOfficer.basicChatOptions.append(FurnaceChat)

    '''
    make the player fire a furnace. no triggers placed
    '''
    def fireFurnaces(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        furnace = terrain.wakeUpRoom.furnace

        # show fluff
        showText("you are in luck. The furnace is for training and you are free to use it.\n\nYou need something to burn in the furnace first, so fetch some coal from the pile and then you can light the furnace.\nIt will stop burning after some ticks so keeping a fire burning can get quite tricky sometimes")

        # show instructions
        showText(["""Here is an example on how to do this:\n\nImagine you are standing next to a pile of coal

""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.main_char],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.furnace_inactive],displayChars.indexedMapping[displayChars.pile],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],"""

take a piece of coal by pressing """+commandChars.move_south+""" to walk against the pile and activating it by pressing """+commandChars.activate+""" immediatly afterwards.

You may press """+commandChars.show_inventory+""" to confirm you have a piece of coal in your inventory.

To activate the furnace press """+commandChars.move_west+""" to move next to it, press s to walk against it and press """+commandChars.activate+""" immediatly afterwards to activate it.

The furnace should be fired now and if you check your inventory afterwards you will see that
you have on piece of coal less than before."""]) 

        # ask the player to fire a furnace
        self.didFurnaces = True
        say("go on and fire the furnace",firstOfficer)
        quest = quests.FireFurnace(furnace)
        showQuest(quest,mainChar)

    '''
    abort the optional furnace fireing and place trigger
    '''
    def noFurnaceFirering(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # place trigger
        showText("i understand. The burns are somewhat unpleasant",trigger=self.iamready)

    '''

    '''
    def examineStuff(self):
        # show fluff
        showText("""you can now examine the room and learn to find your way around. talk to me when you are done and we can proceed""")

        # show instructions
        showText(["""Here is an example on how to do this:\n\nWalk onto or against the items you want to examine and press e directly afterwards to examine something.\nImagine you are standing next to a lever:

""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.lever_notPulled],displayChars.indexedMapping[displayChars.main_char],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],"""

To examine the lever you have to press """+commandChars.move_west+""" to move onto the lever and then press """+commandChars.examine+""" to examine it.

Imagine a situation where you want to examine an object you can not walk onto something:

""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.furnace_inactive],displayChars.indexedMapping[displayChars.main_char],displayChars.indexedMapping[displayChars.floor],"""
""",displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],displayChars.indexedMapping[displayChars.wall],"""

In this case you still have to press """+commandChars.move_west+""" to walk against the object and the press """+commandChars.examine+""" directly afterwards to examine it.
"""])
        showMessage("walk onto or into something and press e directly afterwards to examine something")

        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        '''
        Chat option to show the player is done examining
        '''
        class LetsGoChat(interaction.SubMenu):
            dialogName = "i am ready to continue"
            '''
            straightforward state setting
            '''
            def __init__(subSelf,partner):
                subSelf.state = None
                subSelf.done = False
                subSelf.persistentText = ""
                subSelf.firstRun = True
                subSelf.submenue = None
                super().__init__()

            '''
            straightforward state setting
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    # show fluff 
                    subSelf.persistentText = "let us continue then."
                    subSelf.set_text(subSelf.persistentText)

                    # remove this chat option
                    if LetsGoChat in firstOfficer.basicChatOptions:
                        firstOfficer.basicChatOptions.remove(LetsGoChat)

                    # inite wrap up
                    self.iamready()
                    subSelf.firstRun = False
                else:
                    # show dialog for one keystroke
                    subSelf.done = True

                return False

        # add chat option to continue
        firstOfficer.basicChatOptions.append(LetsGoChat)

    '''
    wait till expected completion time has passed
    '''
    def iamready(self):
        # get time needed
        timeTaken = gamestate.tick-mainChar.tutorialStart
        normTime = 500
        text = "it took you "+str(timeTaken)+" ticks to do it. The norm completion time is 500 ticks.\n\n"
            
        if timeTaken > normTime:
            # scold the player for taking to long
            text += "you better speed up and stop wasting time.\n\n"
            showText(text)
            self.trainingCompleted()
        else:
            # make the player wait till norm completion time
            text += "We are "+str(normTime-timeTaken)+" ticks ahead of plan. We need to make up for this. Please wait for "+str(normTime-timeTaken)+" ticks.\nIn order to not waste time, feel free to aks questions in the meantime.\n"
            quest = quests.WaitQuest(lifetime=normTime-timeTaken)
            showText(text)
            showQuest(quest,mainChar,trigger=self.trainingCompleted)
        

    '''
    wrap up
    '''
    def trainingCompleted(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # show evaluation
        text = "you completed the tests and it is time to take on your duty. You will no longer server under my command, but under "+terrain.wakeUpRoom.firstOfficer.name+" as a hopper.\n\nSo please go to the waiting room and report for room duty.\n\nThe waiting room is the next room to the north. Simply go there speak to "+terrain.wakeUpRoom.firstOfficer.name+" and confirm that you are reporting for duty.\nYou will get instruction on how to proceed afterwards.\n\n"
        if (self.didFurnaces):
            text += "A word of advice from my part:\nYou are able to just not report for duty, but you have to expect to die alone.\nAlso staying on a mech with expired permit will get the guards attention pretty fast.\nSo just follow your orders and work hard, so you will be giving the orders."
        showText(text,rusty=True,scrolling=True)
        for line in text.split("\n"):
            if line == "":
                continue
            say(line,firstOfficer)

        # make player mode to the next room
        # bad pattern: this should be part of the next phase
        quest = quests.MoveQuest(terrain.wakeUpRoom,5,1)
        firstOfficer.assignQuest(quest,active=True)

        # move npc to default position
        quest = quests.MoveQuest(terrain.waitingRoom,9,4)
        mainChar.assignQuest(quest,active=True)

        # trigger final wrap up
        quest.endTrigger = self.end

    '''
    start next phase
    '''
    def end(self):
        phase = FindWork()
        phase.start()

'''

'''
class FindWork(BasicPhase):
    '''
    basic state initialization
    '''
    def __init__(self):
        self.name = "FindWork"
        super().__init__()

    '''
    create selection and place triggrers
    '''
    def start(self):
        self.mainCharRoom = terrain.waitingRoom

        super().start()

        # create selection
        # bad code: bad datastructure leads to bad code
        options = {1:"yes",2:"no"}
        niceOptions = {1:"Yes",2:"No"}
        text = "you look like a fresh one. Were you sent to report for duty?"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"yes":self.getIntroInstant,"no":self.tmpFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    show fluff and show intro
    '''
    def getIntroInstant(self):
        showText("great, I needed to replace a hopper that was eaten by mice")
        self.getIntro()

    '''
    show intro and trigger teardown
    '''
    def getIntro(self):
        showText("I hereby confirm the transfer and welcome you as crew on the Falkenbaum.\n\nYou will serve as an hopper under my command nominally. This means you will make yourself useful and prove your worth.\n\nI often have tasks to relay, but try not to stay idle even when i do not have tasks for you. Just ask around and see if somebody needs help")
        showText("Remeber to report back, your worth will be counted in a mtick.",trigger=self.end)

    '''
    drop the player out of the command chain and place trigger for return
    '''
    def tmpFail(self):
        # show 
        say("go on then.")
        showText("go on then.")

        '''
        a dialog for reentering the command chain
        '''
        class ReReport(interaction.SubMenu):
            dialogName = "I want to report for duty"

            '''
            state initialization
            '''
            def __init__(subSelf,partner):
                subSelf.persistentText = ""
                subSelf.firstRun = True
                super().__init__()

            '''
            scold the player and start intro
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    # show message
                    subSelf.persistentText = "It seems you did not report for duty imediatly. Try to not repeat that"
                    subSelf.set_text(subSelf.persistentText)
                    subSelf.done = True
                    subSelf.firstRun = False

                    # punish player
                    mainChar.reputation -= 1
                    messages.append("rewarded -1 reputation")

                    # remove dialog option
                    terrain.waitingRoom.firstOfficer.basicChatOptions.remove(ReReport)

                    # start intro
                    self.getIntro()
                    return True
                else:
                    return False

        # add option to reenter the command chain
        terrain.waitingRoom.firstOfficer.basicChatOptions.append(ReReport)

    '''
    make the player to some task until allowing advancement elsewhere
    bad code: very chaotic. probably needs to be split up and partially rewritten
    '''
    def end(self):
        hopperDutyQuest = quests.HopperDuty(terrain.waitingRoom)
        mainChar.assignQuest(hopperDutyQuest,active=True)

        '''
        the dialog for asking somebody somwhat important for a job
        bad code: nameing
        '''
        class JobChat(interaction.SubMenu):
            dialogName = "Can you use some help?"

            '''
            basic state initialization
            '''
            def __init__(subSelf,partner):
                subSelf.state = None
                subSelf.partner = partner
                subSelf.firstRun = True
                subSelf.done = False
                subSelf.persistentText = ""
                subSelf.dispatchedPhase = False
                super().__init__()

            '''
            show dialog and assign quest 
            '''
            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    if not subSelf.dispatchedPhase:
                        if mainChar.reputation < 10:
                            # deny the request
                            subSelf.persistentText = "I have some work thats needs to be done, but you will have to proof your worth some more untill you can be trusted with this work.\n\nMaybe "+terrain.waitingRoom.secondOfficer.name+" has some work you can do"
                        else:
                            # show fluff
                            subSelf.persistentText = "Several Officers requested new assistants. First go to to the boiler room and apply for the position"

                            # start next story phase
                            quest = quests.MoveQuestMeta(terrain.tutorialMachineRoom,3,3)
                            phase = FirstTutorialPhase()
                            quest.endTrigger = phase.start
                            hopperDutyQuest.getQuest.quest = self.selectedQuest
                            hopperDutyQuest.getQuest.recalculate()
                            subSelf.dispatchedPhase = True
                    else:
                        # deny the request
                        subSelf.persistentText = "Not right now"

                    # show text
                    subSelf.set_text(subSelf.persistentText)
                    subSelf.done = True
                    subSelf.firstRun = False

                    return True
                else:
                    return False

        '''
        bad code:
        bad code: nameing
        '''
        class JobChat2(interaction.SubMenu):
            '''
            basic state initialization
            '''
            dialogName = "Can you use some help?"

            '''
            basic state initialization
            '''
            def __init__(self,partner):
                self.state = None
                self.partner = partner
                self.firstRun = True
                self.done = False
                self.persistentText = ""
                self.submenue = None
                self.selectedQuest = None
                super().__init__()

            '''
            show dialog and assign quest 
            '''
            def handleKey(self, key):
                # let the superclass do the selections
                if self.submenue:
                    if not self.submenue.handleKey(key):
                        return False
                    else:
                        self.selectedQuest = self.submenue.selection
                        self.submenue = None

                    self.firstRun = False

                if not self.selectedQuest:
                    if hopperDutyQuest.actualQuest:
                        # refuse to give two quests
                        self.persistentText = "you already have a quest. Complete it and you can get a new one."
                        self.set_text(self.persistentText)
                        self.done = True

                        return True
                    elif terrain.waitingRoom.quests:
                        # show fluff
                        self.persistentText = "Well, yes."
                        self.set_text(self.persistentText)
                                
                        # let the player select the quest to do
                        # bad code: bad datastructure leads to bad code
                        options = {}
                        niceOptions = {}
                        counter = 1
                        for quest in terrain.waitingRoom.quests:
                            options[counter] = quest
                            niceOptions[counter] = quest.description.split("\n")[0]
                            counter += 1
                        self.submenue = interaction.SelectionMenu("select the quest",options,niceOptions)

                        return False
                    else:
                        # refuse to give quests
                        self.persistentText = "Not right now. Ask again later"
                        self.set_text(self.persistentText)
                        self.done = True

                        return True
                else:
                    # assign the selected quest
                    hopperDutyQuest.getQuest.getQuest.quest = self.selectedQuest
                    hopperDutyQuest.getQuest.getQuest.recalculate()
                    if hopperDutyQuest.getQuest:
                        hopperDutyQuest.getQuest.recalculate()
                    terrain.waitingRoom.quests.remove(self.selectedQuest)
                    self.done = True
                    return True

        '''
        check reputation and punish/reward player
        '''
        class ProofOfWorth(object):
            '''
            basic state initialization
            '''
            def __init__(subself,tick,toCancel=[]):
                subself.tick = tick
                subself.toCancel = toCancel

            '''
            call player to the waiting room and give a short speech
            '''
            def handleEvent(subself):
                # cancel current quests
                # bad code: canceling destroys the ongoing process, pausing might be better
                for quest in subself.toCancel:
                     quest.deactivate()
                     mainChar.quests.remove(quest)

                '''
                bad code: should be a method
                '''
                def meeting():
                    showText("Time to prove your worth.")
                    if mainChar.reputation <= 0:
                            # punish player for low performance near to killing player
                            showText("You currently have no recieps on you. Please report to vat duty.",trigger=startVatPhase)
                    elif mainChar.reputation > 5:
                            # do nothing on ok performance
                            showText("great work. Keep on and maybe you will be one of us officers")
                    else:
                            # aplaud the player on good performance
                            showText("I see you did some work. Carry on")

                    # decrease reputation so the player will be forced to work continiously or to save up reputation
                    mainChar.reputation -= 3
                    self.mainCharRoom.addEvent(ProofOfWorth(gamestate.tick+(15*15*15)))

                '''
                bad code: should be a method
                '''
                def startVatPhase():
                    phase = VatPhase()
                    phase.start()

                # call the player for the speech
                quest = quests.MoveQuestMeta(self.mainCharRoom,6,5)
                quest.endTrigger = meeting
                mainChar.assignQuest(quest,active=True)

        '''
        the event for making the player coordinate unloding the cargo
        '''
        class StoreCargo(object):
            '''
            basic state initialization
            '''
            def __init__(subself,tick,char,toCancel=[]):
                subself.tick = tick
                subself.char = char

            '''
            set up the quests and lend npcs
            '''
            def handleEvent(subself):
                '''
                bad code: should be method
                '''
                def meeting():
                    # add the quest
                    showText("logistics command orders us to move some of the cargo in the long term store to accesible storage.\n3 rooms are to be cleared. One room needs to be cleared within 150 ticks\nThis requires the coordinated effort of the hoppers here. Since "+subself.char.name+" did well to far, "+subself.char.name+" will be given the lead.\nThis will be extra to the current workload")
                    quest = quests.HandleDelivery([terrain.tutorialCargoRooms[4]],[terrain.tutorialStorageRooms[1],terrain.tutorialStorageRooms[3],terrain.tutorialStorageRooms[5]])
                    quest.endTrigger = addRoomConstruction
                    mainChar.assignQuest(quest,active=True)

                    # add subordinates
                    for hopper in terrain.waitingRoom.hoppers:
                        if hopper == subself.char:
                            continue
                        if hopper in mainChar.subordinates:
                            continue
                        mainChar.subordinates.append(hopper)
                    
                # call the player for a meeting
                quest = quests.MoveQuestMeta(self.mainCharRoom,6,5)
                quest.endTrigger = meeting
                mainChar.assignQuest(quest,active=True)
                mainChar.reputation += 5

        '''
        helper function to make the main char build a room
        '''
        def addRoomConstruction():
            for room in terrain.rooms:
                if isinstance(room,rooms.ConstructionSite):
                    constructionSite = room
                    break
            quest = quests.ConstructRoom(constructionSite,terrain.tutorialStorageRooms)
            # bad code: commented out code
            #terrain.waitingRoom.quests.append(quest)
            mainChar.assignQuest(quest,active=True)

        # add events to keep loose control
        self.mainCharRoom.addEvent(StoreCargo(gamestate.tick+(15*15*40),mainChar))
        self.mainCharRoom.addEvent(ProofOfWorth(gamestate.tick+(15*15*15)))

        # add quest to pool
        quest = quests.ClearRubble()
        quest.reputationReward = 3
        terrain.waitingRoom.quests.append(quest)

        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest12():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(2,1)][0],(terrain.metalWorkshop,9,5))
            quest.endTrigger = addQuest1
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest11():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(3,1)][0],(terrain.metalWorkshop,9,4))
            quest.endTrigger = addQuest12
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest10():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(4,1)][0],(terrain.metalWorkshop,9,6))
            quest.endTrigger = addQuest11
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest9():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(5,1)][0],(terrain.metalWorkshop,9,3))
            quest.endTrigger = addQuest10
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest8():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(6,1)][0],(terrain.metalWorkshop,9,7))
            quest.endTrigger = addQuest9
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest7():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(7,1)][0],(terrain.metalWorkshop,9,2))
            quest.endTrigger = addQuest8
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest6():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[5],(terrain.tutorialLab,7,1))
            quest.endTrigger = addQuest7
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest5():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[4],(terrain.tutorialLab,6,1))
            quest.endTrigger = addQuest6
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest4():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[3],(terrain.tutorialLab,5,1))
            quest.endTrigger = addQuest5
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest3():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[2],(terrain.tutorialLab,4,1))
            quest.endTrigger = addQuest4
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest2():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[1],(terrain.tutorialLab,3,1))
            quest.endTrigger = addQuest3
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        '''
        quest to carry stuff and trigger adding a new quest afterwards
        bad code: very repetetive code
        '''
        def addQuest1():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[0],(terrain.tutorialLab,2,1))
            quest.endTrigger = addQuest2
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)

        # start series of quests that were looped to keep the system active
        addQuest1()

        # add the dialog for getting a job
        terrain.waitingRoom.firstOfficer.basicChatOptions.append(JobChat)
        terrain.waitingRoom.secondOfficer.basicChatOptions.append(JobChat2)
        terrain.wakeUpRoom.firstOfficer.basicChatOptions.append(JobChat)
        terrain.tutorialMachineRoom.firstOfficer.basicChatOptions.append(JobChat)


#######################################################
###
##     the old turorial, needs cleanup and reintegration
#
#######################################################

'''
explain how to steam generation works and give a demonstration
bad code: nameing
'''
class FirstTutorialPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "FirstTutorialPhase"
        super().__init__()

    '''

    bad code: many inline functions
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        # move player to machine room if it doesn't exist yet
        if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
            self.mainCharQuestList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))

        # properly hook the players quests
        self.assignPlayerQuests()

        '''
        greet player and trigger next function
        '''
        def doBasicSchooling():
            if not mainChar.gotBasicSchooling:
                # show greeting one time
                cinematics.showCinematic("welcome to the boiler room\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")
                # bad code: commented out code
                #cinematics.showCinematic("the Trainingenvironment will show now. take a look at Everything and press "+commandChars.wait+" afterwards. You will be able to move later")
                #cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
                #cinematics.showCinematic("you are represented by the "+str(displayChars.main_char)+" Character. find yourself on the Screen and press "+commandChars.wait)
                #cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
                #cinematics.showCinematic("right now you are in the Boilerroom\n\nthe Floor is represented by "+displayChars.indexedMapping[displayChars.floor][1]+" and Walls are shown as "+displayChars.indexedMapping[displayChars.wall][1]+". the Door is represented by "+displayChars.indexedMapping[displayChars.door_closed][1]+" or "+displayChars.indexedMapping[displayChars.door_opened][1]+" when closed.\n\na empty Room would look like this:\n\n"+displayChars.indexedMapping[displayChars.wall][1]*5+"\n"+displayChars.indexedMapping[displayChars.wall][1]+displayChars.indexedMapping[displayChars.floor][1]*3+displayChars.indexedMapping[displayChars.wall][1]+"\n"+displayChars.indexedMapping[displayChars.wall][1]+displayChars.indexedMapping[displayChars.floor][1]*3+displayChars.indexedMapping[displayChars.door_closed][1]+"\n"+displayChars.indexedMapping[displayChars.wall][1]+displayChars.indexedMapping[displayChars.floor][1]*3+displayChars.indexedMapping[displayChars.wall][1]+"\n"+displayChars.indexedMapping[displayChars.wall][1]*5+"\n\nthe Trainingenvironment will display now. please try to orient yourself in the Room.\n\npress "+commandChars.wait+" when successful")
                cinematic = cinematics.ShowGameCinematic(1)
                def wrapUp():
                    mainChar.gotBasicSchooling = True
                    doSteamengineExplaination()
                    gamestate.save()
                cinematic.endTrigger = wrapUp
                cinematics.cinematicQueue.append(cinematic)
            else:
                # start next step
                doSteamengineExplaination()

        '''
        explain how the steam engine work and continue
        '''
        def doSteamengineExplaination():
            # explain how the room works
            cinematics.showCinematic("on the southern Side of the Room you see the Steamgenerators. A Steamgenerator might look like this:\n\n"+displayChars.indexedMapping[displayChars.void][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_inactive][1]+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"\n"+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_inactive][1]+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"\n"+displayChars.indexedMapping[displayChars.void][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_active][1]+displayChars.indexedMapping[displayChars.furnace_active][1]+"\n\nit consist of Furnaces marked by "+displayChars.indexedMapping[displayChars.furnace_inactive][1]+" or "+displayChars.indexedMapping[displayChars.furnace_active][1]+" that heat the Water in the Boilers "+displayChars.indexedMapping[displayChars.boiler_inactive][1]+" till it boils. a Boiler with boiling Water will be shown as "+displayChars.indexedMapping[displayChars.boiler_active][1]+".\n\nthe Steam is transfered to the Pipes marked with "+displayChars.indexedMapping[displayChars.pipe][1]+" and used to power the Ships Mechanics and Weapons\n\nDesign of Generators are often quite unique. try to recognize the Genrators in this Room and press "+commandChars.wait+"")
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
            cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.indexedMapping[displayChars.coal][1]+" . if a Furnace is burning Coal, it is shown as "+displayChars.indexedMapping[displayChars.furnace_active][1]+" and shown as "+displayChars.indexedMapping[displayChars.furnace_inactive][1]+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.indexedMapping[displayChars.pile][1]+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.")
            
            # start next step
            cinematic = cinematics.ShowGameCinematic(0) # bad code: this cinamatic is a hack
            def wrapUp():
                doCoalDelivery()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        '''
        fake a coal delivery
        bad code: inline functions and classes
        '''
        def doCoalDelivery():
            # show fluff
            cinematics.showCinematic("Since a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the Ticks in the Messagebox now")
            
            '''
            the event for faking a coal delivery
            '''
            class CoalRefillEvent(object):
                '''
                basic state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                add coal
                '''
                def handleEvent(subself):
                    # show fluff
                    messages.append("*rumbling*")
                    messages.append("*rumbling*")
                    messages.append("*smoke and dust on Coalpiles and neighbourng Fields*")
                    messages.append("*a chunk of Coal drops onto the floor*")
                    messages.append("*smoke clears*")

                    # add delivered items (incuding mouse)
                    self.mainCharRoom.addItems([items.Coal(7,5)])
                    self.mainCharRoom.addCharacter(characters.Mouse(),6,5)

            # add the coal delivery
            self.mainCharRoom.addEvent(CoalRefillEvent(gamestate.tick+11))

            # count down to the coal delivery
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("8"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("7"))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("by the Way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches n the middle of the Room shown as "+displayChars.indexedMapping[displayChars.hutch_free][1]+" or "+displayChars.indexedMapping[displayChars.hutch_occupied][1]))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("6"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("5"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("4"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("3"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("2"))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("1"))
            cinematic = cinematics.ShowGameCinematic(1,tickSpan=1)
            '''
            advance the game
            '''
            def advance():
                loop.set_alarm_in(0.1, callShow_or_exit, '.')
            cinematic.endTrigger = advance
            cinematics.cinematicQueue.append(cinematic)
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("Coaldelivery now"))
            cinematic = cinematics.ShowGameCinematic(2)
            '''
            start next phase
            '''
            def wrapUp():
                doFurnaceFirering()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        '''
        make a npc fire a furnace 
        '''
        def doFurnaceFirering():
            # show fluff
            cinematics.showCinematic("your cohabitants in this Room are:\n '"+self.mainCharRoom.firstOfficer.name+"' ("+displayChars.indexedMapping[self.mainCharRoom.firstOfficer.display][1]+") is this Rooms 'Raumleiter' and therefore responsible for proper Steamgeneration in this Room\n '"+self.mainCharRoom.secondOfficer.name+"' ("+displayChars.indexedMapping[self.mainCharRoom.secondOfficer.display][1]+") was dispatched to support '"+self.mainCharRoom.firstOfficer.name+"' and is his Subordinate\n\nyou will likely report to '"+self.mainCharRoom.firstOfficer.name+"' later. please try to find them on the display and press "+commandChars.wait)
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
            cinematics.showCinematic(self.mainCharRoom.secondOfficer.name+" will demonstrate how to fire a furnace now.\n\nwatch and learn.")

            '''
            add the quests for firering a furnace
            bad code:
            '''
            class AddQuestEvent(object):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                add quests for firering a furnace
                bad code: should use the meta quest for this
                '''
                def handleEvent(subself):
                    quest0 = quests.CollectQuestMeta()
                    quest1 = quests.ActivateQuestMeta(self.mainCharRoom.furnaces[2])
                    quest2 = quests.MoveQuestMeta(self.mainCharRoom,4,3)
                    quest0.followUp = quest1
                    quest1.followUp = quest2
                    quest2.followUp = None
                    self.mainCharRoom.secondOfficer.assignQuest(quest0,active=True)

            '''
            event for showing a message
            bad code: should be abstracted
            '''
            class ShowMessageEvent(object):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                show the message
                '''
                def handleEvent(subself):
                    messages.append("*"+self.mainCharRoom.secondOfficer.name+", please fire the Furnace now*")

            # set up the events
            self.mainCharRoom.addEvent(ShowMessageEvent(gamestate.tick+1))
            self.mainCharRoom.addEvent(AddQuestEvent(gamestate.tick+2))
            cinematic = cinematics.ShowGameCinematic(22,tickSpan=1) #bad code: should be showQuest to prevent having a fixed timing

            '''
            start next step
            '''
            def wrapUp():
                doWrapUp()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        '''
        show some info and start next phase
        '''
        def doWrapUp():
            # show some information
            cinematics.showCinematic("there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("+displayChars.indexedMapping[displayChars.binStorage][1]+"): Used for storing Things intended to be transported further\n Pile ("+displayChars.indexedMapping[displayChars.pile][1]+"): a Pile of Things\n Door ("+displayChars.indexedMapping[displayChars.door_opened][1]+" or "+displayChars.indexedMapping[displayChars.door_closed][1]+"): you can move through it when open\n Lever ("+displayChars.indexedMapping[displayChars.lever_notPulled][1]+" or "+displayChars.indexedMapping[displayChars.lever_pulled][1]+"): a simple Man-Machineinterface\n Furnace ("+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"): used to generate heat burning Things\n Display ("+displayChars.indexedMapping[displayChars.display][1]+"): a complicated Machine-Maninterface\n Wall ("+displayChars.indexedMapping[displayChars.wall][1]+"): ensures the structural Integrity of basically any Structure\n Pipe ("+displayChars.indexedMapping[displayChars.pipe][1]+"): transports Liquids, Pseudoliquids and Gasses\n Coal ("+displayChars.indexedMapping[displayChars.coal][1]+"): a piece of Coal, quite usefull actually\n Boiler ("+displayChars.indexedMapping[displayChars.boiler_inactive][1]+" or "+displayChars.indexedMapping[displayChars.boiler_active][1]+"): generates Steam using Water and and Heat\n Chains ("+displayChars.indexedMapping[displayChars.chains][1]+"): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("+displayChars.indexedMapping[displayChars.commLink][1]+"): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("+displayChars.indexedMapping[displayChars.hutch_free][1]+"): a comfy and safe Place to sleep and eat")

            '''
            event for starting the next phase
            '''
            class StartNextPhaseEvent(object):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick):
                    subself.tick = tick

                '''
                start next phase
                '''
                def handleEvent(subself):
                    self.end()

            # shedule the wrap up
            self.mainCharRoom.addEvent(StartNextPhaseEvent(gamestate.tick+1))

            # save the game
            gamestate.save()

        # start the action
        doBasicSchooling()

    '''
    start next phase
    '''
    def end(self):
        cinematics.showCinematic("please try to remember the Information. The lesson will now continue with Movement.")
        phase2 = SecondTutorialPhase()
        phase2.start()

'''
teach basic interaction
bad code: nameing
'''
class SecondTutorialPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "SecondTutorialPhase"
        super().__init__()

    '''
    explain interaction and make the player apply lessons
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        # make the player make a simple move
        questList = []
        questList.append(quests.MoveQuest(self.mainCharRoom,5,5,startCinematics="Movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "+commandChars.move_north+"=up\n "+commandChars.move_east+"=right\n "+commandChars.move_south+"=down\n "+commandChars.move_west+"=right\n\nplease move to the designated Target. the Implant will mark your Way"))

        # make the player move around
        if not mainChar.gotMovementSchooling:
            quest = quests.MoveQuest(self.mainCharRoom,4,3)
            # bad code: commented out code
            #quest = quests.PatrolQuest([(self.mainCharRoom,7,5),(self.mainCharRoom,7,2),(self.mainCharRoom,2,2),(self.mainCharRoom,2,5)],startCinematics="now please patrol around the Room a few times.",lifetime=80)
            def setPlayerState():
                mainChar.gotMovementSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="thats enough. move back to waiting position"))

        # make the player examine the map
        if not mainChar.gotExamineSchooling:
            # bad code: commented out code
            #quest = quests.ExamineQuest(lifetime=100,startCinematics="use e to examine items. you can get Descriptions and more detailed Information about your Environment than just by looking at things.\n\nto look at something you have to walk into or over the item and press "+commandChars.examine+". For example if you stand next to a Furnace like this:\n\n"+displayChars.indexedMapping[displayChars.furnace_inactive][1]+displayChars.indexedMapping[displayChars.main_char][1]+"\n\npressing "+commandChars.move_west+" and then "+commandChars.examine+" would result in the Description:\n\n\"this is a Furnace\"\n\nyou have 100 Ticks to familiarise yourself with the Movementcommands and to examine the Room. please do.")
            quest = quests.MoveQuest(self.mainCharRoom,4,3)
            def setPlayerState():
                mainChar.gotExamineSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="Move back to Waitingposition"))

        # explain interaction
        if not mainChar.gotInteractionSchooling:
            quest = quests.CollectQuestMeta(startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nsee this Piles of Coal marked with ӫ on the right Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "+commandChars.move_west+" and "+commandChars.activate+" would result in Activation of the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.activate+" would result in Activation of the Pile\n pressing "+commandChars.move_west+" and "+commandChars.examine+" would result make you examine the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.examine+" would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.")
            def setPlayerState():
                mainChar.gotInteractionSchooling = True
                gamestate.save()
            quest.endTrigger = setPlayerState
            questList.append(quest)
        else:
            #bad code: assumtion of the player having failed the test is not always true
            quest = quests.CollectQuestMeta(startCinematics="Since you failed the Test last time i will quickly reiterate the interaction commands.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nmove over or walk into items and then press the interaction button to be able to interact with it.")
            questList.append(quest)
            
        # make the character
        questList.append(quests.ActivateQuestMeta(self.mainCharRoom.furnaces[0],startCinematics="now go and fire the top most Furnace."))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace"))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = self.end

        # assign first quest
        mainChar.assignQuest(questList[0],active=True)

    '''
    start next phase
    '''
    def end(self):
        cinematics.showCinematic("you recieved your Preparatorytraining. Time for the Test.")
        phase = ThirdTutorialPhase()
        phase.start()

'''
do a furnace firering competition 
bad code: nameing
'''
class ThirdTutorialPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "ThirdTutorialPhase"
        super().__init__()

    '''
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        cinematics.showCinematic("during the Test Messages and new Task will be shown on the Buttom of the Screen. start now.")

        # track competition results
        self.mainCharFurnaceIndex = 0
        self.npcFurnaceIndex = 0

        '''
        make the main char stop their turn
        bad code: basically the same structe within the function as around it
        '''
        def endMainChar():
            # stop current quests
            # bad code: deactivating all quests is too much
            cinematics.showCinematic("stop.")
            for quest in mainChar.quests:
                quest.deactivate()
            mainChar.quests = []

            # clear state
            self.mainCharRoom.removeEventsByType(AnotherOne)
            mainChar.assignQuest(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

            # let the npc prepare itself
            messages.append("your turn Ludwig")
            questList = []
            # bad code: commented out code
            #questList.append(quests.FillPocketsQuest())
            #questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[1]))
            #questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[2]))
            questList.append(quests.FillPocketsQuest())

            # chain quests
            lastQuest = questList[0]
            for item in questList[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questList[-1].followup = None

            '''
            event to make the npc fire another furnace
            '''
            class AnotherOne2(object):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,index):
                    subself.tick = tick
                    subself.furnaceIndex = index

                '''
                add another furnace for the npc to fire
                '''
                def handleEvent(subself):
                    self.mainCharRoom.secondOfficer.assignQuest(quests.KeepFurnaceFired(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=self.end),active=True)
                    newIndex = subself.furnaceIndex+1
                    self.npcFurnaceIndex = subself.furnaceIndex
                    if newIndex < 8:
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[newIndex]),active=True)
                        self.mainCharRoom.addEvent(AnotherOne2(gamestate.tick+gamestate.tick%20+10,newIndex))

            # remember event type to be able to remove it later
            self.anotherOne2 = AnotherOne2

            '''
            the event for waiting for a clean start and making the npc start
            '''
            class WaitForClearStart2(object):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,index):
                    subself.tick = tick

                '''
                wait for a clean start and make the npc start their part of the competition
                '''
                def handleEvent(subself):
                    # check wether the boilers cooled down
                    boilerStillBoiling = False
                    for boiler in self.mainCharRoom.boilers:
                        if boiler.isBoiling:
                            boilerStillBoiling = True    

                    if boilerStillBoiling:
                        # wait some more
                        self.mainCharRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))
                    else:
                        # make the npc start
                        cinematics.showCinematic("Liebweg start now.")
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[0]),active=True)
                        self.mainCharRoom.addEvent(AnotherOne2(gamestate.tick+10,0))

            '''
            kickstart the npcs part of the competition
            '''
            def tmp2():
                self.mainCharRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))

            questList[-1].endTrigger = tmp2
            self.mainCharRoom.secondOfficer.assignQuest(questList[0],active=True)

        '''
        event to make the player fire another furnace
        '''
        class AnotherOne(object):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick,index):
                subself.tick = tick
                subself.furnaceIndex = index

            '''
            add another furnace for the player to fire
            '''
            def handleEvent(subself):
                messages.append("another one")
                mainChar.assignQuest(quests.KeepFurnaceFired(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=endMainChar))
                newIndex = subself.furnaceIndex+1
                self.mainCharFurnaceIndex = subself.furnaceIndex
                if newIndex < 8:
                    mainChar.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[newIndex]))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+gamestate.tick%20+5,newIndex))

        '''
        the event for waiting for a clean start and making the player start
        '''
        class WaitForClearStart(object):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick,index):
                subself.tick = tick

            '''
            wait for a clean start and make the player start their part of the competition
            '''
            def handleEvent(subself):
                # check wether the boilers cooled down
                boilerStillBoiling = False
                for boiler in self.mainCharRoom.boilers:
                    if boiler.isBoiling:
                        boilerStillBoiling = True    

                if boilerStillBoiling:
                    # wait some more
                    self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))
                else:
                    # make the player start
                    cinematics.showCinematic("start now.")
                    mainChar.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[0]))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+10,0))

        '''
        kickstart the npcs part of the competition
        '''
        def tmp():
            cinematics.showCinematic("wait for the furnaces to burn out.")
            self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))

        tmp()

    '''
    evaluate results and branch phases
    '''
    def end(self):
        # show score
        messages.append("your Score: "+str(self.mainCharFurnaceIndex))
        messages.append("Liebweg Score: "+str(self.npcFurnaceIndex))

        # show score
        for quest in self.mainCharRoom.secondOfficer.quests:
            quest.deactivate()
        self.mainCharRoom.secondOfficer.quests = []
        self.mainCharRoom.removeEventsByType(self.anotherOne2)
        mainChar.assignQuest(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

        # start appropriate phase
        if self.npcFurnaceIndex >= self.mainCharFurnaceIndex:
            cinematics.showCinematic("considering your Score until now moving you directly to your proper assignment is the most efficent Way for you to proceed.")
            phase3 = VatPhase()
            phase3.start()
        elif self.mainCharFurnaceIndex == 7:
            cinematics.showCinematic("you passed the Test. in fact you passed the Test with a perfect Score. you will be valuable")
            phase3 = LabPhase()
            phase3.start()
        else:
            cinematics.showCinematic("you passed the Test. \n\nyour Score: "+str(self.mainCharFurnaceIndex)+"\nLiebwegs Score: "+str(self.npcFurnaceIndex))
            phase3 = MachineRoomPhase()
            phase3.start()


################################################################################################################
###
##   these are the room phases. The room phases are the midgame content of the to be prototype
#
#    ideally these phases should servre to teach the player about how the game, a mech and the hierarchy progession works.
#    There should be some events and cutscenes thrown in to not have a sudden drop of cutscene frequency between tutorial and the actual game
#
################################################################################################################

'''
dummmy for the lab phase
should serve as puzzle/testing area
'''
class LabPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "LabPhase"
        super().__init__()

    '''
    make the dummy movemnt and switch phase
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialLab

        super().start()

        # do a dummy action
        questList = []
        questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move to the waiting position"))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = self.end

        # assign player quest
        mainChar.assignQuest(questList[0])

    '''
    move on to next phase
    '''
    def end(self):
        cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.") # bad pattern: text is badly copy pasted
        SecondTutorialPhase().start()

'''
dummy for the vat phase
should serve as punishment for player with option to escape
'''
class VatPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "VatPhase"
        super().__init__()

    '''
    do a dummy action and switch phase
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialVat

        super().start()

        # do a dummy action
        questList = []
        questList.append(quests.MoveQuest(terrain.tutorialVat,3,3))

        # make the player move to the vat
        # bad code: does nothing in combination with the Move quest
        if not (mainChar.room and mainChar.room == terrain.tutorialVat):
            questList.append(quests.EnterRoomQuest(terrain.tutorialVat,startCinematics="please goto the Vat"))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        # assign player quest
        mainChar.assignQuest(questList[0],active=True)

    '''
    move on to next phase
    '''
    def end(self):
        cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
        SecondTutorialPhase().start()

'''
dummy for the machine room phase
should serve to train maintanance
'''
class MachineRoomPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        self.name = "MachineRoomPhase"
        super().__init__()

    '''
    switch completely the free play
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom
        self.requiresMainCharRoomSecondOfficer = False

        super().start()

        terrain.tutorialMachineRoom.secondOfficer = mainChar

        # assign task and hand over
        terrain.tutorialMachineRoom.endTraining()

        # do a dummy action
        questList = []
        if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
            questList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))
        questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="time to do some actual work. report to "+terrain.tutorialMachineRoom.firstOfficer.name))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        # assign player quest
        mainChar.assignQuest(questList[0])

    '''
    win the game
    bad code: is never called
    '''
    def end(self):
        gamestate.gameWon = True

###############################################################
###
##   the glue to be able to call the phases from configs etc
#
#    this should be automated some time
#
###############################################################

'''
reference the phases to be able to call them easier
bad code: registering here is easy to forget when adding a phase
'''
def registerPhases():
    phasesByName["OpenWorld"] = OpenWorld

    phasesByName["VatPhase"] = VatPhase
    phasesByName["MachineRoomPhase"] = MachineRoomPhase
    phasesByName["LabPhase"] = LabPhase
    phasesByName["FirstTutorialPhase"] = FirstTutorialPhase
    phasesByName["SecondTutorialPhase"] = SecondTutorialPhase
    phasesByName["ThirdTutorialPhase"] = ThirdTutorialPhase
    phasesByName["WakeUpPhase"] = WakeUpPhase
    phasesByName["BrainTesting"] = BrainTestingPhase
    phasesByName["BasicMovementTraining"] = BasicMovementTraining
    phasesByName["FindWork"] = FindWork

phasesByName = None
gamestate = None
names = None
characters = None
events = None

"""

the base class for the all phases here

"""
def showMessage(message,trigger=None):
    cinematic = cinematics.ShowMessageCinematic(message)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
def showGame(duration,trigger=None):
    cinematic = cinematics.ShowGameCinematic(duration,tickSpan=1)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
def showQuest(quest,assignTo=None,trigger=None):
    cinematic = cinematics.ShowQuestExecution(quest,tickSpan=1,assignTo=assignTo)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
def showText(text,rusty=False,autocontinue=False,trigger=None):
    cinematic = cinematics.ScrollingTextCinematic(text,rusty=rusty,autocontinue=autocontinue)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
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

class BasicPhase(object):
    def __init__(self):
        self.mainCharXPosition = None
        self.mainCharYPosition = None
        self.mainCharRoom = None
        self.requiresMainCharRoomFirstOfficer = True 
        self.requiresMainCharRoomSecondOfficer = True 
        self.mainCharQuestList = []
        self.firstOfficerXPosition = 4
        self.firstOfficerYPosition = 3
        self.secondOfficerXPosition = 5
        self.secondOfficerYPosition = 3

    def start(self):
        gamestate.currentPhase = self
        self.tick = gamestate.tick

        if self.mainCharRoom:
            if not (mainChar.room or mainChar.terrain):
                if self.mainCharXPosition and self.mainCharYPosition:
                    self.mainCharRoom.addCharacter(mainChar,self.mainCharXPosition,self.mainCharYPosition)
                else:
                    self.mainCharRoom.addCharacter(mainChar,3,3)

        if self.requiresMainCharRoomFirstOfficer:
            if not self.mainCharRoom.firstOfficer:
                name = names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)]
                self.mainCharRoom.firstOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name)
                self.mainCharRoom.addCharacter(self.mainCharRoom.firstOfficer,self.firstOfficerXPosition,self.firstOfficerYPosition)
            self.mainCharRoom.firstOfficer.reputation = 1000

        if self.requiresMainCharRoomSecondOfficer:
            if not self.mainCharRoom.secondOfficer:
                name = names.characterFirstNames[(gamestate.tick+4)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)]
                self.mainCharRoom.secondOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name)
                self.mainCharRoom.addCharacter(self.mainCharRoom.secondOfficer,self.secondOfficerXPosition,self.secondOfficerYPosition)
            self.mainCharRoom.secondOfficer.reputation = 100

        gamestate.save()

    def assignPlayerQuests(self):
        if not self.mainCharQuestList:
            return

        lastQuest = self.mainCharQuestList[0]
        for item in self.mainCharQuestList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        self.mainCharQuestList[-1].followup = None

        self.mainCharQuestList[-1].endTrigger = self.end

        mainChar.assignQuest(self.mainCharQuestList[0])

"""

the phase is intended to give the player access to the true gameworld without manipulations

this phase should be left as blank as possible

"""
class OpenWorld(object):
    def __init__(self):
        cinematics.showCinematic("staring open world Scenario.")
        self.mainCharRoom = terrain.wakeUpRoom
        self.mainCharRoom.addCharacter(mainChar,2,4)

    def start(self):
        pass

"""

this phase is intended to be nice to watch and to be running as demo piece or something to stare at

right now experiments are done here, but that should be shifted somwhere else later

"""
class ScreenSaver(object):
    def __init__(self):
        self.mainCharRoom = terrain.wakeUpRoom
        self.mainCharRoom.addCharacter(mainChar,2,4)

        self.mainCharQuestList = []
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

        questlist = []
        for item in terrain.testItems:
            quest = quests.PickupQuest(item)
            questlist.append(quest)
            quest = quests.DropQuest(item,terrain.tutorialMachineRoom,2,2)
            questlist.append(quest)

        cleaner = characters.Character(displayChars.staffCharactersByLetter["f"],6,6,name="Friedrich Eisenhauch")
        self.mainCharRoom.addCharacter(cleaner,6,6)
        cleaner.terrain = terrain

        lastQuest = questlist[0]
        for item in questlist[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questlist[-1].followup = None
        cleaner.assignQuest(questlist[0],active=True)


        #self.addIntraRoomMovements()
        #self.addInnerRoomMovements()

        #self.mainCharQuestList[-1].followUp = self.mainCharQuestList[0]

        self.addFurnitureMovingNpcs()

    def addFurnitureMovingNpcs(self):
        npcs = []
        for i in range(0,2):
            npc = characters.Character(displayChars.staffCharactersByLetter["e"],5,3,name="Eduart Knoblauch")
            self.mainCharRoom.addCharacter(npc,2,2+i)
            npc.terrain = terrain
            npcs.append(npc)

        self.assignFurnitureMoving(npcs+[mainChar])

    def assignFurnitureMoving(self,chars):
        counter = 0
        for char in chars:
            questlist = []

            targetRoom = terrain.tutorialCargoRooms[counter*3]
            targetIndex = len(targetRoom.storedItems)


            for srcRoom in (terrain.tutorialCargoRooms[counter*3+1],terrain.tutorialCargoRooms[counter*3+2]):
                srcIndex = len(srcRoom.storedItems)-1
                while srcIndex > -1:
                    pos = srcRoom.storageSpace[srcIndex]
                    item = srcRoom.itemByCoordinates[pos][0]
                    quest = quests.PickupQuest(item)
                    questlist.append(quest)
                    pos = targetRoom.storageSpace[targetIndex]
                    quest = quests.DropQuest(item,targetRoom,pos[0],pos[1])
                    questlist.append(quest)

                    srcIndex -= 1
                    targetIndex += 1

            """
            for i in range(3,8):
                for j in range(0,7):
                    item = terrain.tutorialCargoRooms[i+(counter*7)].storedItems[j]
                    quest = quests.PickupQuest(item)
                    questlist.append(quest)
                    quest = quests.DropQuest(item,terrain.tutorialCargoRooms[2+(counter*7)],1+j,12-i)
                    questlist.append(quest)
            """

            lastQuest = questlist[0]
            for item in questlist[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questlist[-1].followup = None

            char.assignQuest(questlist[0],active=True)

            counter += 1

    def assignWalkQuest(self,chars):
        counter = 0
        for npc in npcs:
            counter += 1
            questlists = {}
        
            for index in range(0,counter):
                questlists[index] = []

            roomCounter = 0
            for room in terrain.rooms:
                roomCounter += 1
                if not isinstance(room,rooms.MechArmor):
                    quest = quests.EnterRoomQuest(room)
                    questlists[roomCounter%counter].append(quest)

            questlist = []
            for index in range(0,counter):
                questlist.extend(questlists[index])

            lastQuest = questlist[0]
            for item in questlist[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questlist[-1].followup = None

            npc.assignQuest(questlist[0])

    def cycleDetectionTest(self):
        quest = quests.MoveQuest(terrain.tutorialVat,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialVatProcessing,6,6)
        self.mainCharQuestList.append(quest)
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

    def addWaitQuest(self):
        quest = quests.WaitQuest(lifetime=40)
        self.mainCharQuestList.append(quest)

    def addKeepFurnaceFired(self):
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)

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

        quest = quests.MetaQuest(questList)
        self.mainCharQuestList.append(quest)

    def addPseudeoFurnacefirering(self):
        quest = quests.MoveQuest(terrain.tutorialMachineRoom,2,2)
        self.mainCharQuestList.append(quest)
        quest = quests.FillPocketsQuest()
        self.mainCharQuestList.append(quest)
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

    def end(self):
        pass

    def assignPlayerQuests(self):
        if not self.mainCharQuestList:
            return

        lastQuest = self.mainCharQuestList[0]
        for item in self.mainCharQuestList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        self.mainCharQuestList[-1].followup = None

        self.mainCharQuestList[-1].endTrigger = self.end

        mainChar.assignQuest(self.mainCharQuestList[0])

"""

these are the tutorial phases. The story phases are tweeked heavily regarding to cutscenes and timing

ideally this phase should force the player how rudementary use of the controls. This should be done by explaining first and then preventing progress until the player proves capability.

no experients here!
half arsed solutions are still welcome here but that should end when this reaches prototype

"""

class BrainTestingPhase(BasicPhase):
    def __init__(self):
        self.name = "BrainTesting"
        super().__init__()

    def start(self):
        import urwid

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
"""])
        showText(["""
got response
responsivity .............................................. """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""

inititializing implant .................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""

checking implant .......................................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""

send test information

1.) Your name is """+mainChar.name+"""
2.) A Pipe is used to transfer fluids
3.) rust - Rust is the oxide of iron. Rust is the most common form of corrosion
"""])

        showText("""
checking stored information

entering interactive mode .................................
        """,autocontinue=True)

        options = {"1":"nok","2":"ok","3":"nok"}
        niceOptions = {"1":"Karl Weinberg","2":mainChar.name,"3":"Susanne Kreismann"}
        text = "\nplease answer the question:\n\nwhat is your name?"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step2,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    def infoFail(self):
        import urwid
        showText(["information storage ....................................... ",(urwid.AttrSpec("#f22",'default'),"NOT OK"),"                                        "],autocontinue=True,trigger=self.fail)
        return

    def step2(self):
        options = {"1":"ok","2":"nok","3":"nok"}
        niceOptions = {"1":"A Pipe is used to transfer fluids","2":"A Grate is used to transfer fluids","3":"A Hutch is used to transfer fluids"}
        text = "\nplease select the true statement:\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step3,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    def step3(self):
        options = {"1":"ok","2":"nok","3":"nok"}
        niceOptions = {"1":"Rust is the oxide of iron. Rust is the most common form of corrosion","2":"Rust is the oxide of iron. Corrosion in form of Rust is common","3":"*deny answer*"}
        text = "\nplease repeat the definition of rust\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"ok":self.step4,"nok":self.infoFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    def step4(self):
        import urwid
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

        showText([""" 
information storage ....................................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""
setting up knowledge base

"""] ,autocontinue=True)

        cinematic = cinematics.InformationTransfer(definitions)
        cinematics.cinematicQueue.append(cinematic)
        
        messages.append("initializing metabolism ..................................... done")
        messages.append("initializing motion control ................................. done")
        messages.append("initializing sensory organs ................................. done")
        messages.append("transfer control to implant")

        showText(["""
initializing metabolism ..................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
initializing motion control ................................. """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
initializing sensory organs ................................. """,(urwid.AttrSpec("#2f2",'default'),"done"),"""
transfer control to implant"""],autocontinue=True)

        cinematic = cinematics.MessageZoomCinematic()
        cinematic.endTrigger = self.end
        cinematics.cinematicQueue.append(cinematic)

    def end(self):
        nextPhase = WakeUpPhase()
        nextPhase.start()

    def fail(self):
        showText("""
aborting initialisation
resetting neural network ....................................""",autocontinue=True,trigger=self.forceExit)

    def forceExit(self):
        import urwid
        raise urwid.ExitMainLoop()

class WakeUpPhase(BasicPhase):
    def __init__(self):
        self.name = "WakeUpPhase"
        super().__init__()

    def start(self):
        self.mainCharXPosition = 1
        self.mainCharYPosition = 4
        self.firstOfficerXPosition = 6
        self.firstOfficerYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False

        self.mainCharRoom = terrain.wakeUpRoom

        super().start()

        self.mainCharRoom.characters.remove(mainChar)

        self.npc = self.mainCharRoom.firstOfficer

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
        showGame(1,trigger=self.playerEject)

    def playerEject(self):
        item = items.UnconciousBody(2,4)
        terrain.wakeUpRoom.addItems([item])
        terrain.wakeUpRoom.itemByCoordinates[(1,4)][0].eject()

        firstOfficer = terrain.wakeUpRoom.firstOfficer

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
        showGame(3,trigger=self.addPlayer)

    def addPlayer(self):
        self.mainCharRoom.removeItem(terrain.wakeUpRoom.itemByCoordinates[(2,4)][0])
        self.mainCharRoom.addCharacter(mainChar,2,4)
        loop.set_alarm_in(0.1, callShow_or_exit, '.')
        self.end()

    def end(self):
        phase = BasicMovementTraining()
        phase.start()

class BasicMovementTraining(BasicPhase):
    def __init__(self):
        self.name = "BasicMovementTraining"
        super().__init__()
    
    def start(self):
        self.mainCharXPosition = 2
        self.mainCharYPosition = 4
        self.requiresMainCharRoomFirstOfficer = True
        self.requiresMainCharRoomSecondOfficer = False

        self.mainCharRoom = terrain.wakeUpRoom

        super().start()

        firstOfficer = terrain.wakeUpRoom.firstOfficer

        showText("""
welcome to the trainingsenvironment.

please follow the orders """+firstOfficer.name+" gives you.",rusty=True)
        showText(["""
you are represented by the """,displayChars.indexedMapping[displayChars.main_char]," Character,  ",firstOfficer.name," is represented by the ",displayChars.indexedMapping[firstOfficer.display],""" Character. 

you can move using the keyboard. 

* press """,commandChars.move_north,""" to move up/north
* press """,commandChars.move_west,""" to move left/west
* press """,commandChars.move_south,""" to move down/south
* press """,commandChars.move_east,""" to move right/east"""])
        showGame(1)

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

        say("move to (2,7), please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,2,7)
        showQuest(quest,mainChar)
        say("move to (4,3), please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,3)
        showQuest(quest,mainChar)
        say("move to (4,4), please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,4,4)
        showQuest(quest,mainChar)
        say("move to (3,3), please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,3)
        showQuest(quest,mainChar)
        say("move to (6,6), please",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,6)
        showQuest(quest,mainChar)
        say("great. You seemed be able to coordinate yourself",firstOfficer)
        showGame(1)
        say("you look thirsty, one more task and you get something to drink",firstOfficer)

        showGame(2)
        say("move over to the lever now",firstOfficer)
        quest = quests.MoveQuest(terrain.wakeUpRoom,3,2)
        showQuest(quest,mainChar)
        
        showText("you can activate levers by moving onto the lever and then pressing "+commandChars.activate)
        showMessage("you can activate levers by moving onto the lever and then pressing "+commandChars.activate)
        say("activate the lever",firstOfficer)
        quest = quests.ActivateQuest(terrain.wakeUpRoom.lever1)
        showQuest(quest,mainChar,trigger=self.fetchDrink)

    def fetchDrink(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        drink = terrain.wakeUpRoom.itemsOnFloor[-1]

        msg = "you can pick up items by moving onto them and using "+commandChars.pickUp
        showText(msg)
        showMessage(msg)
        say("well done, come and fetch your drink",firstOfficer)
        quest = quests.PickupQuest(drink)
        showQuest(quest,mainChar)
        msg = "you can drink using "+commandChars.drink+". If you do not drink for a longer time you will starve"
        say("great. Drink something and come over for a quick talk.",firstOfficer)
        showMessage(msg)
        quest = quests.MoveQuest(terrain.wakeUpRoom,6,6)
        showQuest(quest,mainChar)
        showText("\nHello, I am "+mainChar.name+" and do the acceptance tests. \n\nAfter you complete the test you will serve as an hooper on the Falkenbaum.\n")

        options = {"1":"furnaces","2":"nofurnaces"}
        niceOptions = {"1":"Yes","2":"No"}
        text = "say, do you like Furnaces?"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"furnaces":self.fireFurnaces,"nofurnaces":self.noFurnaceFirering}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    def fireFurnaces(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        furnace = terrain.wakeUpRoom.furnace

        showText("you are in luck. We have a furnace for training purposes.")
        quest = quests.MoveQuest(terrain.wakeUpRoom,furnace.xPosition,furnace.yPosition-1)
        showQuest(quest,mainChar)
        self.didFurnaces = True
        say("go on and fire the furnace",firstOfficer)
        quest = quests.FireFurnace(furnace)
        showQuest(quest,mainChar,trigger=self.trainingCompleted)

    def noFurnaceFirering(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        self.didFurnaces = False

        showText("i understand. The burns are somewhat unpleasant",trigger=self.trainingCompleted)

    def trainingCompleted(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        text = "you completed the tests. Go to the waiting room and report for room duty.\n\nThe waiting room is the next room to the north\n\n"
        if (self.didFurnaces):
            text += "speak to me, if you need work"
        showText(text,rusty=True)
        for line in text.split("\n"):
            if line == "":
                continue
            say(line,firstOfficer)

        quest = quests.MoveQuest(terrain.wakeUpRoom,5,1)
        firstOfficer.assignQuest(quest,active=True)

        quest = quests.MoveQuest(terrain.waitingRoom,9,4)
        mainChar.assignQuest(quest,active=True)
        quest.endTrigger = self.end

    def end(self):
        phase = FindWork()
        phase.start()

class FindWork(BasicPhase):
    def __init__(self):
        self.name = "FindWork"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.waitingRoom

        super().start()

        options = {"1":"yes","2":"no"}
        niceOptions = {"1":"Yes","2":"No"}
        text = "you look like a fresh one. Were you sent to report for duty?"
        cinematic = cinematics.SelectionCinematic(text,options,niceOptions)
        cinematic.followUps = {"yes":self.getIntroInstant,"no":self.tmpFail}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    def getIntroInstant(self):
        showText("great, I needed to replace a hopper that was eaten by mice")
        self.getIntro()

    def getIntro(self):
        showText("I hereby confirm the transfer and welcome you as crew on the Falkenbaum.\n\nYou will serve as an hopper under my command nominally. This means you will make yourself useful and prove your worth.\n\nI often have tasks to relay, but try not to stay idle even when i do not have tasks for you. Just ask around and see if somebody needs help")
        showText("Remeber to bring recieps, your worth will be counted in a mtick.",trigger=self.end)

    def tmpFail(self):
        say("go on then.")
        showText("go on then.")

        class ReReport(interaction.SubMenu):
            dialogName = "I want to report for duty"
            def __init__(subSelf,partner):
                subSelf.persistentText = ""
                subSelf.firstRun = True
                super().__init__()

            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    subSelf.persistentText = "It seems you did not report for duty imediatly. I will remember that"
                    subSelf.set_text(subSelf.persistentText)
                    subSelf.done = True
                    subSelf.firstRun = False
                    mainChar.reputation -= 1
                    messages.append("rewarded -1 reputation")
                    terrain.waitingRoom.firstOfficer.basicChatOptions.remove(ReReport)
                    self.getIntro()
                    return True
                else:
                    return False

        terrain.waitingRoom.firstOfficer.basicChatOptions.append(ReReport)

    def end(self):
        class JobChat(interaction.SubMenu):
            dialogName = "Can you use some help?"
            def __init__(subSelf,partner):
                subSelf.state = None
                subSelf.partner = partner
                subSelf.firstRun = True
                subSelf.done = False
                subSelf.persistentText = ""
                subSelf.dispatchedPhase = False
                super().__init__()

            def handleKey(subSelf, key):
                if subSelf.firstRun:
                    if not subSelf.dispatchedPhase:
                        if mainChar.reputation < 10:
                            subSelf.persistentText = "I have some work thats needs to be done, but you will have to proof your worth some more untill you can be trusted with this work.\n\nMaybe "+terrain.waitingRoom.secondOfficer.name+" has some work you can do"
                        else:
                            subSelf.persistentText = "Several Officers requested new assistants. First go to to the boiler room and apply for the position"

                            quest = quests.MoveQuestMeta(terrain.tutorialMachineRoom,3,3)
                            phase = FirstTutorialPhase()
                            quest.endTrigger = phase.start
                            mainChar.assignQuest(quest,active=True)
                            subSelf.dispatchedPhase = True
                    else:
                        subSelf.persistentText = "Not right now"

                    subSelf.set_text(subSelf.persistentText)
                    subSelf.done = True
                    subSelf.firstRun = False

                    return True
                else:
                    return False

        class JobChat2(interaction.SubMenu):
            dialogName = "Can you use some help?"
            def __init__(self,partner):
                self.state = None
                self.partner = partner
                self.firstRun = True
                self.done = False
                self.persistentText = ""
                self.submenue = None
                self.selectedQuest = None
                super().__init__()

            def handleKey(self, key):
                if self.submenue:
                    if not self.submenue.handleKey(key):
                        return False
                    else:
                        self.selectedQuest = self.submenue.selection
                        self.submenue = None

                    self.firstRun = False

                if not self.selectedQuest:
                    if terrain.waitingRoom.quests:
                        self.persistentText = "Well, yes."
                        self.set_text(self.persistentText)
                                
                        options = {}
                        niceOptions = {}
                        counter = 1
                        for quest in terrain.waitingRoom.quests:
                            options[str(counter)] = quest
                            niceOptions[str(counter)] = quest.description.split("\n")[0]
                            counter += 1
                        self.submenue = interaction.SelectionMenu("select the quest",options,niceOptions)

                        return False
                    else:
                        self.persistentText = "No"
                        self.set_text(self.persistentText)
                        self.done = True

                        return True
                else:
                    mainChar.assignQuest(self.selectedQuest,active=True)
                    terrain.waitingRoom.quests.remove(self.selectedQuest)
                    self.done = True
                    return True

        quest = quests.HopperDuty(terrain.waitingRoom)
        mainChar.assignQuest(quest,active=True)

        class ProofOfWorth(object):
            def __init__(subself,tick,toCancel=[]):
                subself.tick = tick
                subself.toCancel = toCancel

            def handleEvent(subself):
                for quest in subself.toCancel:
                     quest.deactivate()
                     mainChar.quests.remove(quest)

                def meeting():
                    showText("Time to prove your worth.")
                    if mainChar.reputation <= 0:
                            showText("You currently have no recieps on you. Please report to vat duty.",trigger=startVatPhase)
                    elif mainChar.reputation > 5:
                            showText("great work. Keep on and maybe you will be one of us officers")
                    else:
                            showText("I see you did some work. Carry on")
                    mainChar.reputation -= 1

                def startVatPhase():
                    phase = VatPhase()
                    phase.start()

                quest = quests.MoveQuestMeta(self.mainCharRoom,6,5)
                quest.endTrigger = meeting
                mainChar.assignQuest(quest,active=True)

        self.mainCharRoom.addEvent(ProofOfWorth(gamestate.tick+(15*15*15)))

        quest = quests.ClearRubble()
        quest.reputationReward = 3
        terrain.waitingRoom.quests.append(quest)

        storageRoom = terrain.roomByCoordinates[(5,4)][0]
        constructionSite = terrain.roomByCoordinates[(4,2)][0]
        quest = quests.ConstructRoom(constructionSite,storageRoom)
        quest.reputationReward = 6
        terrain.waitingRoom.quests.append(quest)

        def addQuest12():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(2,1)][0],(terrain.metalWorkshop,9,5))
            quest.endTrigger = addQuest1
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest11():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(3,1)][0],(terrain.metalWorkshop,9,4))
            quest.endTrigger = addQuest12
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest10():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(4,1)][0],(terrain.metalWorkshop,9,6))
            quest.endTrigger = addQuest11
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest9():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(5,1)][0],(terrain.metalWorkshop,9,3))
            quest.endTrigger = addQuest10
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest8():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(6,1)][0],(terrain.metalWorkshop,9,7))
            quest.endTrigger = addQuest9
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest7():
            quest = quests.TransportQuest(terrain.tutorialLab.itemByCoordinates[(7,1)][0],(terrain.metalWorkshop,9,2))
            quest.endTrigger = addQuest8
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest6():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[5],(terrain.tutorialLab,7,1))
            quest.endTrigger = addQuest7
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest5():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[4],(terrain.tutorialLab,6,1))
            quest.endTrigger = addQuest6
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest4():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[3],(terrain.tutorialLab,5,1))
            quest.endTrigger = addQuest5
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest3():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[2],(terrain.tutorialLab,4,1))
            quest.endTrigger = addQuest4
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest2():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[1],(terrain.tutorialLab,3,1))
            quest.endTrigger = addQuest3
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        def addQuest1():
            quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[0],(terrain.tutorialLab,2,1))
            quest.endTrigger = addQuest2
            quest.reputationReward = 1
            terrain.waitingRoom.quests.append(quest)
        addQuest1()

        terrain.waitingRoom.firstOfficer.basicChatOptions.append(JobChat)
        terrain.waitingRoom.secondOfficer.basicChatOptions.append(JobChat2)
        terrain.wakeUpRoom.firstOfficer.basicChatOptions.append(JobChat)
        terrain.tutorialMachineRoom.firstOfficer.basicChatOptions.append(JobChat)

class FirstTutorialPhase(BasicPhase):
    def __init__(self):
        self.name = "FirstTutorialPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
            self.mainCharQuestList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))

        self.assignPlayerQuests()

        def doBasicSchooling():
            if not mainChar.gotBasicSchooling:
                cinematics.showCinematic("welcome to the boiler room\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")
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
                doSteamengineExplaination()

        def doSteamengineExplaination():
            cinematics.showCinematic("on the southern Side of the Room you see the Steamgenerators. A Steamgenerator might look like this:\n\n"+displayChars.indexedMapping[displayChars.void][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_inactive][1]+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"\n"+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_inactive][1]+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"\n"+displayChars.indexedMapping[displayChars.void][1]+displayChars.indexedMapping[displayChars.pipe][1]+displayChars.indexedMapping[displayChars.boiler_active][1]+displayChars.indexedMapping[displayChars.furnace_active][1]+"\n\nit consist of Furnaces marked by "+displayChars.indexedMapping[displayChars.furnace_inactive][1]+" or "+displayChars.indexedMapping[displayChars.furnace_active][1]+" that heat the Water in the Boilers "+displayChars.indexedMapping[displayChars.boiler_inactive][1]+" till it boils. a Boiler with boiling Water will be shown as "+displayChars.indexedMapping[displayChars.boiler_active][1]+".\n\nthe Steam is transfered to the Pipes marked with "+displayChars.indexedMapping[displayChars.pipe][1]+" and used to power the Ships Mechanics and Weapons\n\nDesign of Generators are often quite unique. try to recognize the Genrators in this Room and press "+commandChars.wait+"")
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
            cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.indexedMapping[displayChars.coal][1]+" . if a Furnace is burning Coal, it is shown as "+displayChars.indexedMapping[displayChars.furnace_active][1]+" and shown as "+displayChars.indexedMapping[displayChars.furnace_inactive][1]+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.indexedMapping[displayChars.pile][1]+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.")
            cinematic = cinematics.ShowGameCinematic(0)
            def wrapUp():
                doCoalDelivery()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        def doCoalDelivery():
            cinematics.showCinematic("Since a Coaldelivery is incoming anyway. please wait and pay Attention.\n\ni will count down the Ticks in the Messagebox now")
            
            class CoalRefillEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    messages.append("*rumbling*")
                    messages.append("*rumbling*")
                    messages.append("*smoke and dust on Coalpiles and neighbourng Fields*")
                    messages.append("*a chunk of Coal drops onto the floor*")
                    self.mainCharRoom.addItems([items.Coal(7,5)])
                    self.mainCharRoom.addCharacter(characters.Mouse(),6,5)
                    messages.append("*smoke clears*")

            self.mainCharRoom.addEvent(CoalRefillEvent(gamestate.tick+11))

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
            def advance():
                loop.set_alarm_in(0.1, callShow_or_exit, '.')
            cinematic.endTrigger = advance
            cinematics.cinematicQueue.append(cinematic)
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("Coaldelivery now"))
            cinematic = cinematics.ShowGameCinematic(2)
            def wrapUp():
                doFurnaceFirering()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        def doFurnaceFirering():
            cinematics.showCinematic("your cohabitants in this Room are:\n '"+self.mainCharRoom.firstOfficer.name+"' ("+displayChars.indexedMapping[self.mainCharRoom.firstOfficer.display][1]+") is this Rooms 'Raumleiter' and therefore responsible for proper Steamgeneration in this Room\n '"+self.mainCharRoom.secondOfficer.name+"' ("+displayChars.indexedMapping[self.mainCharRoom.secondOfficer.display][1]+") was dispatched to support '"+self.mainCharRoom.firstOfficer.name+"' and is his Subordinate\n\nyou will likely report to '"+self.mainCharRoom.firstOfficer.name+"' later. please try to find them on the display and press "+commandChars.wait)
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1))
            cinematics.showCinematic(self.mainCharRoom.secondOfficer.name+" will demonstrate how to fire a furnace now.\n\nwatch and learn.")
            class AddQuestEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    quest0 = quests.CollectQuestMeta()
                    quest1 = quests.ActivateQuestMeta(self.mainCharRoom.furnaces[2])
                    quest2 = quests.MoveQuestMeta(self.mainCharRoom,4,3)
                    quest0.followUp = quest1
                    quest1.followUp = quest2
                    quest2.followUp = None
                    self.mainCharRoom.secondOfficer.assignQuest(quest0,active=True)

            class ShowMessageEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    messages.append("*"+self.mainCharRoom.secondOfficer.name+", please fire the Furnace now*")

            self.mainCharRoom.addEvent(ShowMessageEvent(gamestate.tick+1))
            self.mainCharRoom.addEvent(AddQuestEvent(gamestate.tick+2))
            cinematic = cinematics.ShowGameCinematic(22,tickSpan=1)
            def wrapUp():
                doWrapUp()
                gamestate.save()
            cinematic.endTrigger = wrapUp
            cinematics.cinematicQueue.append(cinematic)

        def doWrapUp():
            cinematics.showCinematic("there are other Items in the Room that may or may not be important for you. Here is the full List for you to review:\n\n Bin ("+displayChars.indexedMapping[displayChars.binStorage][1]+"): Used for storing Things intended to be transported further\n Pile ("+displayChars.indexedMapping[displayChars.pile][1]+"): a Pile of Things\n Door ("+displayChars.indexedMapping[displayChars.door_opened][1]+" or "+displayChars.indexedMapping[displayChars.door_closed][1]+"): you can move through it when open\n Lever ("+displayChars.indexedMapping[displayChars.lever_notPulled][1]+" or "+displayChars.indexedMapping[displayChars.lever_pulled][1]+"): a simple Man-Machineinterface\n Furnace ("+displayChars.indexedMapping[displayChars.furnace_inactive][1]+"): used to generate heat burning Things\n Display ("+displayChars.indexedMapping[displayChars.display][1]+"): a complicated Machine-Maninterface\n Wall ("+displayChars.indexedMapping[displayChars.wall][1]+"): ensures the structural Integrity of basically any Structure\n Pipe ("+displayChars.indexedMapping[displayChars.pipe][1]+"): transports Liquids, Pseudoliquids and Gasses\n Coal ("+displayChars.indexedMapping[displayChars.coal][1]+"): a piece of Coal, quite usefull actually\n Boiler ("+displayChars.indexedMapping[displayChars.boiler_inactive][1]+" or "+displayChars.indexedMapping[displayChars.boiler_active][1]+"): generates Steam using Water and and Heat\n Chains ("+displayChars.indexedMapping[displayChars.chains][1]+"): some Chains dangling about. sometimes used as Man-Machineinterface or for Climbing\n Comlink ("+displayChars.indexedMapping[displayChars.commLink][1]+"): a Pipe based Voicetransportationsystem that allows Communication with other Rooms\n Hutch ("+displayChars.indexedMapping[displayChars.hutch_free][1]+"): a comfy and safe Place to sleep and eat")

            class StartNextPhaseEvent(object):
                def __init__(subself,tick):
                    subself.tick = tick

                def handleEvent(subself):
                    self.end()

            self.mainCharRoom.addEvent(StartNextPhaseEvent(gamestate.tick+1))
            gamestate.save()
        doBasicSchooling()

    def end(self):
        cinematics.showCinematic("please try to remember the Information. The lesson will now continue with Movement.")
        phase2 = SecondTutorialPhase()
        phase2.start()

class SecondTutorialPhase(BasicPhase):
    def __init__(self):
        self.name = "SecondTutorialPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        questList = []
        questList.append(quests.MoveQuest(self.mainCharRoom,5,5,startCinematics="Movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "+commandChars.move_north+"=up\n "+commandChars.move_east+"=right\n "+commandChars.move_south+"=down\n "+commandChars.move_west+"=right\n\nplease move to the designated Target. the Implant will mark your Way"))
        if not mainChar.gotMovementSchooling:
            quest = quests.MoveQuest(self.mainCharRoom,4,3)
            #quest = quests.PatrolQuest([(self.mainCharRoom,7,5),(self.mainCharRoom,7,2),(self.mainCharRoom,2,2),(self.mainCharRoom,2,5)],startCinematics="now please patrol around the Room a few times.",lifetime=80)
            def setPlayerState():
                mainChar.gotMovementSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="thats enough. move back to waiting position"))
        if not mainChar.gotExamineSchooling:
            #quest = quests.ExamineQuest(lifetime=100,startCinematics="use e to examine items. you can get Descriptions and more detailed Information about your Environment than just by looking at things.\n\nto look at something you have to walk into or over the item and press "+commandChars.examine+". For example if you stand next to a Furnace like this:\n\n"+displayChars.indexedMapping[displayChars.furnace_inactive][1]+displayChars.indexedMapping[displayChars.main_char][1]+"\n\npressing "+commandChars.move_west+" and then "+commandChars.examine+" would result in the Description:\n\n\"this is a Furnace\"\n\nyou have 100 Ticks to familiarise yourself with the Movementcommands and to examine the Room. please do.")
            quest = quests.MoveQuest(self.mainCharRoom,4,3)
            def setPlayerState():
                mainChar.gotExamineSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="Move back to Waitingposition"))

        if not mainChar.gotInteractionSchooling:
            quest = quests.CollectQuestMeta(startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nsee this Piles of Coal marked with ӫ on the right Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "+commandChars.move_west+" and "+commandChars.activate+" would result in Activation of the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.activate+" would result in Activation of the Pile\n pressing "+commandChars.move_west+" and "+commandChars.examine+" would result make you examine the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.examine+" would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.")
            def setPlayerState():
                mainChar.gotInteractionSchooling = True
                gamestate.save()
            quest.endTrigger = setPlayerState
            questList.append(quest)
        else:
            quest = quests.CollectQuestMeta(startCinematics="Since you failed the Test last time i will quickly reiterate the interaction commands.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nmove over or walk into items and then press the interaction button to be able to interact with it.")
            questList.append(quest)
            
        questList.append(quests.ActivateQuestMeta(self.mainCharRoom.furnaces[0],startCinematics="now go and fire the top most Furnace."))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace"))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        questList[-1].endTrigger = self.end

        mainChar.assignQuest(questList[0],active=True)

    def end(self):
        cinematics.showCinematic("you recieved your Preparatorytraining. Time for the Test.")
        phase = ThirdTutorialPhase()
        phase.start()

class ThirdTutorialPhase(BasicPhase):
    def __init__(self):
        self.name = "ThirdTutorialPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        cinematics.showCinematic("during the Test Messages and new Task will be shown on the Buttom of the Screen. start now.")

        self.mainCharFurnaceIndex = 0
        self.npcFurnaceIndex = 0

        def endMainChar():
            cinematics.showCinematic("stop.")
            for quest in mainChar.quests:
                quest.deactivate()
            mainChar.quests = []
            self.mainCharRoom.removeEventsByType(AnotherOne)
            mainChar.assignQuest(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

            messages.append("your turn Ludwig")

            questList = []
            #questList.append(quests.FillPocketsQuest())
            #questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[1]))
            #questList.append(quests.FireFurnace(terrain.tutorialMachineRoom.furnaces[2]))
            questList.append(quests.FillPocketsQuest())

            lastQuest = questList[0]
            for item in questList[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questList[-1].followup = None

            class AnotherOne2(object):
                def __init__(subself,tick,index):
                    subself.tick = tick
                    subself.furnaceIndex = index

                def handleEvent(subself):
                    self.mainCharRoom.secondOfficer.assignQuest(quests.KeepFurnaceFired(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=self.end),active=True)
                    newIndex = subself.furnaceIndex+1
                    self.npcFurnaceIndex = subself.furnaceIndex
                    if newIndex < 8:
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[newIndex]),active=True)
                        self.mainCharRoom.addEvent(AnotherOne2(gamestate.tick+gamestate.tick%20+10,newIndex))

            self.anotherOne2 = AnotherOne2

            class WaitForClearStart2(object):
                def __init__(subself,tick,index):
                    subself.tick = tick

                def handleEvent(subself):
                    boilerStillBoiling = False
                    for boiler in self.mainCharRoom.boilers:
                        if boiler.isBoiling:
                            boilerStillBoiling = True    
                    if boilerStillBoiling:
                        self.mainCharRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))
                    else:
                        cinematics.showCinematic("Liebweg start now.")
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[0]),active=True)
                        self.mainCharRoom.addEvent(AnotherOne2(gamestate.tick+10,0))

            def tmp2():
                self.mainCharRoom.addEvent(WaitForClearStart2(gamestate.tick+2,0))

            questList[-1].endTrigger = tmp2
            self.mainCharRoom.secondOfficer.assignQuest(questList[0],active=True)

        class AnotherOne(object):
            def __init__(subself,tick,index):
                subself.tick = tick
                subself.furnaceIndex = index

            def handleEvent(subself):
                messages.append("another one")
                mainChar.assignQuest(quests.KeepFurnaceFired(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=endMainChar))
                newIndex = subself.furnaceIndex+1
                self.mainCharFurnaceIndex = subself.furnaceIndex
                if newIndex < 8:
                    mainChar.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[newIndex]))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+gamestate.tick%20+5,newIndex))

        class WaitForClearStart(object):
            def __init__(subself,tick,index):
                subself.tick = tick

            def handleEvent(subself):
                boilerStillBoiling = False
                for boiler in self.mainCharRoom.boilers:
                    if boiler.isBoiling:
                        boilerStillBoiling = True    
                if boilerStillBoiling:
                    self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))
                else:
                    cinematics.showCinematic("start now.")
                    mainChar.assignQuest(quests.FireFurnace(self.mainCharRoom.furnaces[0]))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+10,0))

        def tmp():
            cinematics.showCinematic("wait for the furnaces to burn out.")
            self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0))

        tmp()

    def end(self):
        messages.append("your Score: "+str(self.mainCharFurnaceIndex))
        messages.append("Liebweg Score: "+str(self.npcFurnaceIndex))

        for quest in self.mainCharRoom.secondOfficer.quests:
            quest.deactivate()
        self.mainCharRoom.secondOfficer.quests = []
        self.mainCharRoom.removeEventsByType(self.anotherOne2)
        mainChar.assignQuest(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position"))

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


"""

these are the room phases. The room phases are the midgame content of the to be prototype

ideally these phases should servre to teach the player about how the game, a mech and the hierarchy progession works.

There should be some events and cutscenes thrown in to not have a sudden drop of cutscene frequency between tutorial and the actual game

"""

class LabPhase(BasicPhase):
    def __init__(self):
        self.name = "LabPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialLab

        super().start()

        questList = []

        questList.append(quests.MoveQuest(self.mainCharRoom,3,3,startCinematics="please move to the waiting position"))

        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        questList[-1].endTrigger = self.end

        mainChar.assignQuest(questList[0])

    def end(self):
        cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
        SecondTutorialPhase().start()

class VatPhase(BasicPhase):
    def __init__(self):
        self.name = "VatPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialVat

        super().start()

        questList = []
        questList.append(quests.MoveQuest(terrain.tutorialVat,3,3))
        if not (mainChar.room and mainChar.room == terrain.tutorialVat):
            questList.append(quests.EnterRoomQuest(terrain.tutorialVat,startCinematics="please goto the Vat"))

        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        mainChar.assignQuest(questList[0],active=True)

    def end(self):
        cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
        SecondTutorialPhase().start()

class MachineRoomPhase(BasicPhase):
    def __init__(self):
        self.name = "MachineRoomPhase"
        super().__init__()

    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom
        self.requiresMainCharRoomSecondOfficer = False

        super().start()

        terrain.tutorialMachineRoom.secondOfficer = mainChar

        terrain.tutorialMachineRoom.endTraining()

        questList = []
        if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
            questList.append(quests.EnterRoomQuest(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom"))
        questList.append(quests.MoveQuest(terrain.tutorialMachineRoom,3,3,startCinematics="time to do some actual work. report to "+terrain.tutorialMachineRoom.firstOfficer.name))

        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        mainChar.assignQuest(questList[0])

    def end(self):
        gamestate.gameWon = True

"""

the glue to be able to call the phases from configs etc

this should be automated some time

"""
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

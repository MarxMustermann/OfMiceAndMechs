##############################################################################
###
##      story code and story related code belongs here
#       most thing should be abstracted and converted to a game mechanism later
#
##############################################################################

import src.saveing

phasesByName = None
gamestate = None
names = None
characters = None
events = None

#####################################
###
##   convenience functions
#
#####################################

'''
add message cinematic
'''
def showMessage(message,trigger=None):
    cinematic = cinematics.ShowMessageCinematic(message,creator=void)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add show game cinematic
'''
def showGame(duration,trigger=None):
    cinematic = cinematics.ShowGameCinematic(duration,tickSpan=1,creator=void)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add show quest cinematic
'''
def showQuest(quest,assignTo=None,trigger=None,container=None):
    cinematic = cinematics.ShowQuestExecution(quest,tickSpan=1,assignTo=assignTo,container=container,creator=void)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add text cinematic
'''
def showText(text,rusty=False,autocontinue=False,trigger=None,scrolling=False):
    cinematic = cinematics.TextCinematic(text,rusty=rusty,autocontinue=autocontinue,scrolling=scrolling,creator=void)
    cinematics.cinematicQueue.append(cinematic)
    cinematic.endTrigger = trigger
'''
add message cinematic mimicing speech
'''
def say(text,speaker=None,trigger=None):
    prefix = ""
    if speaker:
        # add speakers icon as prefix
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

    # add message
    showMessage(prefix+'"'+text+'"',trigger=trigger)

#########################################################################
###
##    building block phases
#
#########################################################################

"""
the base class for the all phases here
"""
class BasicPhase(src.saveing.Saveable):
    '''
    state initialization
    bad code: creating default attributes in init and set them externally later
    '''
    def __init__(self,name):
        super().__init__()
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
        self.name = name

        # register with dummy id
        self.id = name
        loadingRegistry.register(self)
        self.initialState = self.getState()

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
                    if mainChar.xPosition == None or mainChar.yPosition == None:
                        self.mainCharRoom.addCharacter(mainChar,3,3)

        # create first officer
        if self.requiresMainCharRoomFirstOfficer:
            if not self.mainCharRoom.firstOfficer:
                # bad code: name generation should probably happen in one place
                name = names.characterFirstNames[(gamestate.tick+2)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)]
                self.mainCharRoom.firstOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+2)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name,creator=void)
                self.mainCharRoom.addCharacter(self.mainCharRoom.firstOfficer,self.firstOfficerXPosition,self.firstOfficerYPosition)
            self.mainCharRoom.firstOfficer.reputation = 1000

        # create second officer
        if self.requiresMainCharRoomSecondOfficer:
            if not self.mainCharRoom.secondOfficer:
                # bad code: name generation should probably happen in one place
                name = names.characterFirstNames[(gamestate.tick+4)%len(names.characterFirstNames)]+" "+names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)]
                self.mainCharRoom.secondOfficer = characters.Character(displayChars.staffCharactersByLetter[names.characterLastNames[(gamestate.tick+4)%len(names.characterLastNames)].split(" ")[-1][0].lower()],4,3,name=name,creator=void)
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
        self.mainCharQuestList[-1].endTrigger = {"container":self,"method":"end"}

        # assign the first quest
        mainChar.assignQuest(self.mainCharQuestList[0])

    '''
    do nothing when done
    '''
    def end(self):
        pass

    '''
    returns very simple state as dict
    '''
    def getState(self):
        state = super().getState()
        state["name"] = self.name
        return state

#########################################################################
###
##    general purpose phases
#
#########################################################################

"""
the phase is intended to give the player access to the true gameworld without manipulations

this phase should be left as blank as possible
"""
class OpenWorld(BasicPhase):
    def __init__(self):
        super().__init__("OpenWorld")
    '''
    place main char
    bad code: superclass call should not be prevented
    '''
    def start(self):
        cinematics.showCinematic("staring open world Scenario.")
        if terrain.wakeUpRoom:
            self.mainCharRoom = terrain.wakeUpRoom
            self.mainCharRoom.addCharacter(mainChar,2,4)
        else:
            mainChar.xPosition = 2
            mainChar.yPosition = 4
            mainChar.terrain = terrain
            terrain.addCharacter(mainChar)

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XX
#X   these are the tutorial phases. The story phases are tweeked heavily regarding to cutscenes and timing
#
#    no experiments here!
#    half arsed solutions are still welcome here but that should end when this reaches prototype
#
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#######################################################################################
###
##    The interaction between the implant before until birth
#
#     this should be a lot of fluff and guide the player into the game
#
#######################################################################################


'''
show some fluff messages and enforce learning how to use a selection
'''
class BrainTestingPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("BrainTesting")

    '''
    show some messages and place trigger
    bad code: closely married to urwid
    '''
    def start(self):
        import urwid

        # show fluff
        showText(["""
initializing subject ...................................... """,(urwid.AttrSpec("#2f2",'default'),"done"),"""

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
        options = [
                     ("nok","Karl Weinberg"),
                     ("ok",mainChar.name),
                     ("nok","Susanne Kreismann")
                  ]
        text = "\nplease answer the question:\n\nwhat is your name?"
        cinematic = cinematics.SelectionCinematic(text,options,creator=void)
        cinematic.followUps = {"ok":{"container":self,"method":"askSecondQuestion"},"nok":{"container":self,"method":"infoFail"}}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    show fluff and fail phase
    '''
    def infoFail(self):
        import urwid
        showText(["information storage ....................................... ",(urwid.AttrSpec("#f22",'default'),"NOT OK"),"                                        "],autocontinue=True,trigger={"container":self,"method":"fail"},scrolling=True)
        return

    '''
    ask question and place trigger
    '''
    def askSecondQuestion(self):
        options = [
                    ("ok","A Pipe is used to transfer fluids"),
                    ("nok","A Grate is used to transfer fluids"),
                    ("nok","A Hutch is used to transfer fluids"),
                  ]
        text = "\nplease select the true statement:\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,creator=void)
        cinematic.followUps = {"ok":{"container":self,"method":"askThirdQuestion"},"nok":{"container":self,"method":"infoFail"}}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    ask question and place trigger
    '''
    def askThirdQuestion(self):
        options = [
                     ("ok","Rust is the oxide of iron. Rust is the most common form of corrosion"),
                     ("nok","Rust is the oxide of iron. Corrosion in form of Rust is common"),
                     ("nok","*deny answer*"),
                  ]
        text = "\nplease repeat the definition of rust\n\n"
        cinematic = cinematics.SelectionCinematic(text,options,creator=void)
        cinematic.followUps = {"ok":{"container":self,"method":"flashInformation"},"nok":{"container":self,"method":"infoFail"}}
        self.cinematic = cinematic
        cinematics.cinematicQueue.append(cinematic)

    '''
    show fluff info with effect and place trigger
    '''
    def flashInformation(self):
        import urwid
        
        # set bogus information
        definitions = {}
        definitions["pipe"] = "A Pipe is used to transfer fluids"
        definitions["wall"] = "A Wall is a non passable building element"
        definitions["door"] = "A Door is a moveable facility used to close a Opening"
        definitions["door"] = "A Lever is a tangent Device used to operate Something"
        definitions["Flask"] = "A Flask, better known as Flachman is a Container used to store Fluids"
        definitions["Coal"] = "Coal is a dark sedimentary Rock used to generate Engergy"
        definitions["Furnace"] = "A Furnace is a Device used to produce Heat"
        definitions["Boiler"] = "A Boiler is a Device used to heat Fluids"
        definitions["GrowthTank"] = "A GrowthTank is a Container used to grow new operation Units"
        definitions["Hutch"] = "A Hutch is a hollowed closable Container used to sleep in"
        definitions["Wrench "] = "A Wrench is a Tool used to tighten or loosen a Screw"
        definitions["Screw"] = "A Screw is a cylindric Element with a Thread used to connect Components"
        definitions["Goo"] = "Goo is the common Food"
        definitions["GooFlask"] = "A GooFlask is a Container used to transport Goo"
        definitions["Goo Dispenser"] = "A GooDispenser is a Machine which does dispose Goo"
        definitions["Grate"] = "A Grate is a horizontal flat Facility which is permeable and used to close an Opening"
        definitions["Corpse"] = "A Corpse is the Remain of a human Body"
        definitions["UnconciousBody"] = "A UnconciousBody is a Person which is not able to move and does not react"
        definitions["Pile"] = "A Container used to store Items like Coal"
        definitions["Acid"] = "Acid is used to produce Goo"
        definitions["Floor"] = "A Floor is a horizontal Construction at the Bottom of a Room or Building"
        definitions["BinStorage"] = "A Bin is a Container used to store Items"
        definitions["Chain"] = "A Chain is made of consecutive linked MetalRings"
        definitions["Grid"] = "A Grid is a vertical flat Facility which is mermeable and used to close an Opening"
        definitions["FoodStuffs"] = "FoodStuffs can be used as an alternative for Goo"
        definitions["Machine"] = "A Machine is a Mechanism used to execute Work automatically"
        definitions["Hub"] = "A Hub is a Facility to distribute Media like Steam"
        definitions["Steam"] = "Steam is a Medium made of Water and Heat"
        definitions["Ramp"] = "A Ramp is a horizontal Construction with a Gradient which is used to move between different Levels"
        definitions["VatSnake"] = "A VatSnake is an Animal that lives between the Remains in the Vat"
        definitions["Outlet"] = "An Outlet is used to distribute or dispense Media"
        definitions["Barricade"] = "A Barricade prohibits movement"
        definitions["Clamp"] = "A Clamp is a Facility used to pick up or grasp something"
        definitions["Winch"] = "A Winch is a Facility to support Movement of Items by using a Chain"
        definitions["Scrap"] = "A Scrap is a Piece of Metal"
        definitions["MetalBar"] = "A Metal Bar is a standatized Piece of Metal"

        # show fluff
        showText([""" 
information storage ....................................... """,(urwid.AttrSpec("#2f2",'default'),"OK"),"""
setting up knowledge base

"""] ,autocontinue=True,scrolling=True)

        cinematic = cinematics.InformationTransfer(definitions,creator=void)
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
        cinematic = cinematics.MessageZoomCinematic(creator=void)
        cinematic.endTrigger = {"container":self,"method":"end"}
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
aborting initialization
resetting neural network ....................................""",autocontinue=True,trigger={"container":self,"method":"forceExit"},scrolling=True)

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
        super().__init__("WakeUpPhase")

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
        mainChar.satiation = 400
        mainChar.inventory = []
        # bad code: purging a characters quests should be a method
        for quest in mainChar.quests:
            quest.deactivate()
        mainChar.quests = []

        # set the wake up room as play area
        # bad code: should be set elsewhere
        self.mainCharRoom = terrain.wakeUpRoom

        super().start()

        # hide main char from map
        if mainChar in self.mainCharRoom.characters:
            self.mainCharRoom.characters.remove(mainChar)
        mainChar.terrain = None

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
        showGame(1,trigger={"container":self,"method":"playerEject"})

    '''
    spawn players body and place trigger
    '''
    def playerEject(self):
        # add players body
        terrain.wakeUpRoom.itemByCoordinates[(1,4)][0].eject(mainChar)

        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # show fluff
        showMessage("*schurp**splat*")
        showGame(2)
        showMessage("please wait for assistance")
        showGame(2)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,3,4,creator=void)
        showQuest(quest,firstOfficer)
        say("I AM "+firstOfficer.name.upper()+" AND I DEMAND YOUR SERVICE.",firstOfficer)

        # add serve quest
        quest = quests.Serve(firstOfficer,creator=void)
        mainChar.serveQuest = quest
        mainChar.assignQuest(quest,active=True)

        # show fluff
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
        showGame(3,trigger={"container":self,"method":"addPlayer"})

    '''
    add the player and place triggers
    '''
    def addPlayer(self):
        mainChar.wakeUp()

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
    '''
    def setState(self,state):
        super().setState(state)

        #bad code: knowingly breaking state instead of setting a camera focus
        if not mainChar.room and not mainChar.terrain:
            terrain.wakeUpRoom.addCharacter(mainChar,3,3)

            if mainChar in terrain.wakeUpRoom.characters:
                terrain.wakeUpRoom.characters.remove(mainChar)
            mainChar.terrain = None

#######################################################################################
###
##   The testing/tutorial phases
#
#    ideally these phases should force the player how rudementary use of the controls. This should be done by 
#    explaining first and then preventing progress until the player proves capability.
#
#######################################################################################

'''
explain and test basic movement and interaction
'''
class BasicMovementTraining(BasicPhase):

    '''
    basic state initialization
    '''
    def __init__(self):
        super().__init__("BasicMovementTraining")
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

        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # smooth over missing info
        # bad code: should not be nessecarry
        if not hasattr(mainChar,"tutorialStart"):
            mainChar.tutorialStart = gamestate.tick - 100

        # smooth over missing info
        # bad code: should not be nessecarry
        if not hasattr(mainChar,"serveQuest"):
            quest = quests.Serve(firstOfficer,creator=void)
            mainChar.serveQuest = quest
            mainChar.assignQuest(quest,active=True)

        super().start()

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
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,4,4,creator=void)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        showMessage("the current quest destination is shown as: "+displayChars.indexedMapping[displayChars.questTargetMarker][1])
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,3,4,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,5,4,creator=void)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,4,4,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,6,7,creator=void)
        showQuest(quest,firstOfficer)
        say("follow me, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,5,7,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)

        # ask player to move around
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,2,7,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,4,3,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,4,4,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,3,3,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        say("move to the designated target, please",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,6,6,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        say("great. You seemed be able to coordinate yourself",firstOfficer)
        showGame(1)
        say("you look thirsty, one more task and you get something to drink",firstOfficer)

        # ask player to move to the lever
        showGame(2)
        say("move over to the lever now",firstOfficer)
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,3,2,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        
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
        quest = quests.ActivateQuestMeta(terrain.wakeUpRoom.lever1,creator=void)
        showQuest(quest,mainChar,trigger={"container":self,"method":"fetchDrink"},container=mainChar.serveQuest)

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
        quest = quests.PickupQuestMeta(drink,creator=void)
        showQuest(quest,mainChar,trigger={"container":self,"method":"drinkStuff"},container=mainChar.serveQuest)
    
    def drinkStuff(self):
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        mainChar.assignQuest(quests.SurviveQuest(creator=void))

        # show instructions
        msg = "you can drink using "+commandChars.drink+". If you do not drink for a longer time you will starve"
        say("great. Drink from the flask you just fetched and come over for a quick talk.",firstOfficer)
        showMessage(msg)

        # ask the player to pick up the flask
        quest = quests.DrinkQuest(creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)

        # make the player talk to the npc
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,6,6,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)
        msg = "you can talk to people by pressing "+commandChars.hail+" and selecting the person to talk to."
        showMessage(msg)
        showText(msg)
                   
        # add chat options
        firstOfficer.basicChatOptions.append({"dialogName":"You wanted to have a chat","chat":chats.FirstChat,"params":{"firstOfficer":firstOfficer,"phase":self}})
        firstOfficer.basicChatOptions.append({"dialogName":"What are these machines in this room?","chat":chats.FurnaceChat,"params":{"firstOfficer":firstOfficer,"phase":self,"terrain":terrain}})

    '''
    make the player fire a furnace. no triggers placed
    '''
    def fireFurnaces(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        furnace = terrain.wakeUpRoom.furnace

        # reward player
        mainChar.reputation += 2
        messages.append("you were rewarded 2 reputation")

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
        quest = quests.FireFurnaceMeta(furnace,creator=void)
        showQuest(quest,mainChar,container=mainChar.serveQuest)

    '''
    abort the optional furnace fireing and place trigger
    '''
    def noFurnaceFirering(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer
        mainChar.reputation -= 1
        messages.append("you were rewarded -1 reputation")

        # place trigger
        showText("i understand. The burns are somewhat unpleasant",trigger={"container":self,"method":"iamready"})

    '''
    make the player examine things
    '''
    def examineStuff(self):
        # show fluff
        showText("""examine the room and learn to find your way around, please""")

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

        # add examine quest
        quest = quests.ExamineQuest(creator=void)
        quest.endTrigger = {"container":self,"method":"iamready"}
        mainChar.serveQuest.addQuest(quest)

    '''
    wait till expected completion time has passed
    '''
    def iamready(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # show evaluation
        text = "you completed the tests and it is time to take on your duty. You will no longer server under my command, but under "+terrain.wakeUpRoom.firstOfficer.name+" as a hopper.\n\nSo please go to the waiting room and report for room duty.\n\nThe waiting room is the next room to the north. Simply go there speak to "+terrain.wakeUpRoom.firstOfficer.name+" and confirm that you are reporting for duty.\nYou will get instruction on how to proceed afterwards.\n\n"
        if (self.didFurnaces):
            text += "A word of advice from my part:\nYou are able to just not report for duty, but you have to expect to die alone.\nAlso staying on a mech with expired permit will get the guards attention pretty fast.\nSo just follow your orders and work hard, so you will be giving the orders."
        showText(text,rusty=True)
        for line in text.split("\n"):
            if line == "":
                continue
            say(line,firstOfficer)

        # get time needed
        timeTaken = gamestate.tick-mainChar.tutorialStart
        normTime = 500
        text = "it took you "+str(timeTaken)+" ticks to complete the tests. The norm completion time is 500 ticks.\n\n"
            
        if timeTaken > normTime:
            # scold the player for taking to long
            text += "you better speed up and stop wasting time.\n\n"
            showText(text)
            self.trainingCompleted()
            mainChar.reputation -= 2
            messages.append("you were rewarded -2 reputation")
        else:
            # make the player wait till norm completion time
            text += "We are "+str(normTime-timeTaken)+" ticks ahead of plan. This means your floor permit is not valid yet. Please wait for "+str(normTime-timeTaken)+" ticks.\n\nNoncompliance will result in a kill order to the military. Military zones and movement restrictions are security and therefore high priority.\n\nIn order to not waste time, feel free to ask questions in the meantime.\n"
            quest = quests.WaitQuest(lifetime=normTime-timeTaken,creator=void)
            showText(text)
            quest.endTrigger = {"container":self,"method":"trainingCompleted"}
            mainChar.serveQuest.addQuest(quest)

            # reward player
            mainChar.reputation += 1
            messages.append("you were rewarded 1 reputation")

    '''
    wrap up
    '''
    def trainingCompleted(self):
        # alias attributes
        firstOfficer = terrain.wakeUpRoom.firstOfficer

        # make player mode to the next room
        # bad pattern: this should be part of the next phase
        quest = quests.MoveQuestMeta(terrain.wakeUpRoom,5,1,creator=void)
        firstOfficer.assignQuest(quest,active=True)

        # move npc to default position
        quest = quests.MoveQuestMeta(terrain.waitingRoom,9,4,creator=void)
        mainChar.assignQuest(quest,active=True)
        mainChar.hasFloorPermit = True

        # trigger final wrap up
        quest.endTrigger = {"container":self,"method":"end"}

    '''
    start next phase
    '''
    def end(self):
        phase = FindWork()
        phase.start()

#######################################################
###
##     the old turorial, needs cleanup and reintegration
#
#######################################################

'''
explain how to steam generation works and give a demonstration
'''
class BoilerRoomWelcome(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("BoilerRoomWelcome")

    '''

    bad code: many inline functions
    '''
    def start(self):
        # alias attributes
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        gamestate.gameWon = True

        # move player to machine room if it doesn't exist yet
        if not (mainChar.room and mainChar.room == terrain.tutorialMachineRoom):
            self.mainCharQuestList.append(quests.EnterRoomQuestMeta(terrain.tutorialMachineRoom,startCinematics="please goto the Machineroom",creator=void))

        # properly hook the players quests
        self.assignPlayerQuests()

        '''
        greet player and trigger next function
        '''
        def doBasicSchooling():
            if not mainChar.gotBasicSchooling:
                # show greeting one time
                cinematics.showCinematic("welcome to the boiler room\n\nplease, try to learn fast.\n\nParticipants with low Evaluationscores will be given suitable Assignments in the Vats")
                cinematic = cinematics.ShowGameCinematic(1,creator=void)
                '''
                start next sub phase
                '''
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
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,creator=void))
            cinematics.showCinematic("the Furnaces burn Coal shown as "+displayChars.indexedMapping[displayChars.coal][1]+" . if a Furnace is burning Coal, it is shown as "+displayChars.indexedMapping[displayChars.furnace_active][1]+" and shown as "+displayChars.indexedMapping[displayChars.furnace_inactive][1]+" if not.\n\nthe Coal is stored in Piles shown as "+displayChars.indexedMapping[displayChars.pile][1]+". the Coalpiles are on the right Side of the Room and are filled through the Pipes when needed.")
            
            # start next step
            cinematic = cinematics.ShowGameCinematic(0,creator=void) # bad code: this cinamatic is a hack
            '''
            start next sub phase
            '''
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
            class CoalRefillEvent(events.Event):
                '''
                basic state initialization
                '''
                def __init__(subself,tick,creator=None):
                    super().__init__(tick,creator=creator)
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
                    self.mainCharRoom.addItems([items.Coal(7,5,creator=void)])
                    self.mainCharRoom.addCharacter(characters.Mouse(creator=void),6,5)

            # add the coal delivery
            self.mainCharRoom.addEvent(CoalRefillEvent(gamestate.tick+11,creator=void))

            # count down to the coal delivery
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("8",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("7",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("by the Way: the Piles on the lower End of the Room are Storage for Replacementparts and you can sleep in the Hutches n the middle of the Room shown as "+displayChars.indexedMapping[displayChars.hutch_free][1]+" or "+displayChars.indexedMapping[displayChars.hutch_occupied][1],creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("6",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("5",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("4",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("3",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("2",creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,tickSpan=1,creator=void))
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("1",creator=void))
            cinematic = cinematics.ShowGameCinematic(1,tickSpan=1,creator=void)
            '''
            advance the game
            '''
            def advance():
                loop.set_alarm_in(0.1, callShow_or_exit, '.')
            cinematic.endTrigger = advance
            cinematics.cinematicQueue.append(cinematic)
            cinematics.cinematicQueue.append(cinematics.ShowMessageCinematic("Coaldelivery now",creator=void))
            cinematic = cinematics.ShowGameCinematic(2,creator=void)
            '''
            start next sub phase
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
            cinematics.cinematicQueue.append(cinematics.ShowGameCinematic(1,creator=void))
            cinematics.showCinematic(self.mainCharRoom.secondOfficer.name+" will demonstrate how to fire a furnace now.\n\nwatch and learn.")

            '''
            add the quests for firering a furnace
            '''
            class AddQuestEvent(events.Event):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick

                '''
                add quests for firering a furnace
                '''
                def handleEvent(subself):
                    quest = quests.FireFurnaceMeta(self.mainCharRoom.furnaces[2],creator=void)
                    self.mainCharRoom.secondOfficer.assignQuest(quest,active=True)

            '''
            event for showing a message
            bad code: should be abstracted
            '''
            class ShowMessageEvent(events.Event):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick

                '''
                show the message
                '''
                def handleEvent(subself):
                    messages.append("*"+self.mainCharRoom.secondOfficer.name+", please fire the Furnace now*")

            # set up the events
            self.mainCharRoom.addEvent(ShowMessageEvent(gamestate.tick+1,creator=void))
            self.mainCharRoom.addEvent(AddQuestEvent(gamestate.tick+2,creator=void))
            cinematic = cinematics.ShowGameCinematic(22,tickSpan=1,creator=void) #bad code: should be showQuest to prevent having a fixed timing

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
            class StartNextPhaseEvent(events.Event):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick

                '''
                start next phase
                '''
                def handleEvent(subself):
                    self.end()

            # schedule the wrap up
            self.mainCharRoom.addEvent(StartNextPhaseEvent(gamestate.tick+1,creator=void))

            # save the game
            gamestate.save()

        # start the action
        doBasicSchooling()

    '''
    start next phase
    '''
    def end(self):
        cinematics.showCinematic("please try to remember the Information. The lesson will now continue with Movement.")
        phase2 = BoilerRoomInteractionTraining()
        phase2.start()

'''
teach basic interaction
'''
class BoilerRoomInteractionTraining(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("BoilerRoomInteractionTraining")

    '''
    explain interaction and make the player apply lessons
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialMachineRoom

        super().start()

        # make the player make a simple move
        questList = []
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,5,5,startCinematics="Movement can be tricky sometimes so please make yourself comfortable with the controls.\n\nyou can move in 4 Directions along the x and y Axis. the z Axis is not supported yet. diagonal Movements are not supported since they do not exist.\n\nthe basic Movementcommands are:\n "+commandChars.move_north+"=up\n "+commandChars.move_east+"=right\n "+commandChars.move_south+"=down\n "+commandChars.move_west+"=right\n\nplease move to the designated Target. the Implant will mark your Way",creator=void))

        # make the player move around
        if not mainChar.gotMovementSchooling:
            quest = quests.MoveQuestMeta(self.mainCharRoom,4,3,creator=void)
            def setPlayerState():
                mainChar.gotMovementSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="thats enough. move back to waiting position",creator=void))

        # make the player examine the map
        if not mainChar.gotExamineSchooling:
            quest = quests.MoveQuestMeta(self.mainCharRoom,4,3,creator=void)
            def setPlayerState():
                mainChar.gotExamineSchooling = True
            quest.endTrigger = setPlayerState
            questList.append(quest)
            questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="Move back to Waitingposition",creator=void))

        # explain interaction
        if not mainChar.gotInteractionSchooling:
            quest = quests.CollectQuestMeta(startCinematics="next on my Checklist is to explain the Interaction with your Environment.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nsee this Piles of Coal marked with ӫ on the right Side and left Side of the Room.\n\nwhenever you bump into an Item that is to big to be walked on, you will promted for giving an extra Interactioncommand. i'll give you an Example:\n\n ΩΩ＠ӫӫ\n\n pressing "+commandChars.move_west+" and "+commandChars.activate+" would result in Activation of the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.activate+" would result in Activation of the Pile\n pressing "+commandChars.move_west+" and "+commandChars.examine+" would result make you examine the Furnace\n pressing "+commandChars.move_east+" and "+commandChars.examine+" would result make you examine the Pile\n\nplease grab yourself some Coal from a pile by bumping into it and pressing j afterwards.",creator=void)
            '''
            start new sub phase
            '''
            def setPlayerState():
                mainChar.gotInteractionSchooling = True
                gamestate.save()
            quest.endTrigger = setPlayerState
            questList.append(quest)
        else:
            # bad code: assumtion of the player having failed the test is not always true
            quest = quests.CollectQuestMeta(startCinematics="Since you failed the Test last time i will quickly reiterate the interaction commands.\n\nthe basic Interationcommands are:\n\n "+commandChars.activate+"=activate/apply\n "+commandChars.examine+"=examine\n "+commandChars.pickUp+"=pick up\n "+commandChars.drop+"=drop\n\nmove over or walk into items and then press the interaction button to be able to interact with it.",creator=void)
            questList.append(quest)
            
        # make the character fire the furnace
        questList.append(quests.ActivateQuestMeta(self.mainCharRoom.furnaces[0],startCinematics="now go and fire the top most Furnace.",creator=void))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please pick up the Coal on the Floor. \n\nyou won't see a whole Year of Service leaving burnable Material next to a Furnace",creator=void))
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position",creator=void))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = {"container":self,"method":"end"}

        # assign first quest
        mainChar.assignQuest(questList[0],active=True)

    '''
    start next phase
    '''
    def end(self):
        cinematics.showCinematic("you recieved your Preparatorytraining. Time for the Test.")
        phase = FurnaceCompetition()
        phase.start()

'''
do a furnace firering competition 
'''
class FurnaceCompetition(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("FurnaceCompetition")

    '''
    run the competition
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
        bad code: basically the same structure within the function as around it
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
            mainChar.assignQuest(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position",creator=void))

            # let the npc prepare itself
            messages.append("your turn Ludwig")
            questList = []
            questList.append(quests.FillPocketsQuest(creator=void))

            # chain quests
            lastQuest = questList[0]
            for item in questList[1:]:
                lastQuest.followUp = item
                lastQuest = item
            questList[-1].followup = None

            '''
            event to make the npc fire another furnace
            '''
            class AnotherOneNpc(events.Event):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,index,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick
                    subself.furnaceIndex = index

                '''
                add another furnace for the npc to fire
                '''
                def handleEvent(subself):
                    self.mainCharRoom.secondOfficer.assignQuest(quests.KeepFurnaceFiredMeta(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=self.end,creator=void),active=True)
                    newIndex = subself.furnaceIndex+1
                    self.npcFurnaceIndex = subself.furnaceIndex
                    if newIndex < 8:
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnaceMeta(self.mainCharRoom.furnaces[newIndex],creator=void),active=True)
                        self.mainCharRoom.addEvent(AnotherOneNpc(gamestate.tick+gamestate.tick%20+10,newIndex,creator=self))

            # remember event type to be able to remove it later
            self.anotherOne2 = AnotherOneNpc

            '''
            the event for waiting for a clean start and making the npc start
            '''
            class WaitForClearStartNpc(events.Event):
                '''
                straightforward state initialization
                '''
                def __init__(subself,tick,index,creator=None):
                    super().__init__(tick,creator=creator)
                    subself.tick = tick

                '''
                wait for a clean start and make the npc start their part of the competition
                '''
                def handleEvent(subself):
                    # check whether the boilers cooled down
                    boilerStillBoiling = False
                    for boiler in self.mainCharRoom.boilers:
                        if boiler.isBoiling:
                            boilerStillBoiling = True    

                    if boilerStillBoiling:
                        # wait some more
                        self.mainCharRoom.addEvent(WaitForClearStartNpc(gamestate.tick+2,0,creator=self))
                    else:
                        # make the npc start
                        cinematics.showCinematic("Liebweg start now.")
                        self.mainCharRoom.secondOfficer.assignQuest(quests.FireFurnaceMeta(self.mainCharRoom.furnaces[0],creator=void),active=True)
                        self.mainCharRoom.addEvent(AnotherOneNpc(gamestate.tick+10,0,creator=self))

            '''
            kickstart the npcs part of the competition
            '''
            def tmpNpc():
                self.mainCharRoom.addEvent(WaitForClearStartNpc(gamestate.tick+2,0,creator=self))

            questList[-1].endTrigger = tmpNpc
            self.mainCharRoom.secondOfficer.assignQuest(questList[0],active=True)

        '''
        event to make the player fire another furnace
        '''
        class AnotherOne(events.Event):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick,index,creator=None):
                super().__init__(tick,creator=creator)
                subself.tick = tick
                subself.furnaceIndex = index

            '''
            add another furnace for the player to fire
            '''
            def handleEvent(subself):
                mainChar.assignQuest(quests.KeepFurnaceFiredMeta(self.mainCharRoom.furnaces[subself.furnaceIndex],failTrigger=endMainChar,creator=void))
                newIndex = subself.furnaceIndex+1
                self.mainCharFurnaceIndex = subself.furnaceIndex
                if newIndex < 8:
                    mainChar.assignQuest(quests.FireFurnaceMeta(self.mainCharRoom.furnaces[newIndex],creator=void))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+gamestate.tick%20+5,newIndex,creator=void))

        '''
        the event for waiting for a clean start and making the player start
        '''
        class WaitForClearStart(events.Event):
            '''
            straightforward state initialization
            '''
            def __init__(subself,tick,index,creator=None):
                super().__init__(tick,creator=creator)
                subself.tick = tick

            '''
            wait for a clean start and make the player start their part of the competition
            '''
            def handleEvent(subself):
                # check whether the boilers cooled down
                boilerStillBoiling = False
                for boiler in self.mainCharRoom.boilers:
                    if boiler.isBoiling:
                        boilerStillBoiling = True    

                if boilerStillBoiling:
                    # wait some more
                    self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0,creator=void))
                else:
                    # make the player start
                    cinematics.showCinematic("start now.")
                    mainChar.assignQuest(quests.FireFurnaceMeta(self.mainCharRoom.furnaces[0],creator=void))
                    self.mainCharRoom.addEvent(AnotherOne(gamestate.tick+10,0,creator=void))

        '''
        kickstart the npcs part of the competition
        bad code: nameing
        '''
        def tmp():
            cinematics.showCinematic("wait for the furnaces to burn out.")
            self.mainCharRoom.addEvent(WaitForClearStart(gamestate.tick+2,0,creator=void))

        tmp()

    '''
    evaluate results and branch phases
    '''
    def end(self):
        # show score
        messages.append("your Score: "+str(self.mainCharFurnaceIndex))
        messages.append("Liebweg Score: "+str(self.npcFurnaceIndex))

        # disable npcs quest
        for quest in self.mainCharRoom.secondOfficer.quests:
            quest.deactivate()
        self.mainCharRoom.secondOfficer.quests = []
        self.mainCharRoom.removeEventsByType(self.anotherOne2)
        mainChar.assignQuest(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move back to the waiting position",creator=void))

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
do opportunity work as hopper until a permanent position was found
'''
class FindWork(BasicPhase):
    '''
    basic state initialization
    '''
    def __init__(self):
        self.cycleQuestIndex = 0
        super().__init__("FindWork")
        self.attributesToStore.extend(["cycleQuestIndex"])
        loadingRegistry.register(self)
        self.initialState = self.getState()

    '''
    create selection and place triggrers
    '''
    def start(self):
        self.mainCharRoom = terrain.waitingRoom

        super().start()

        # create selection
        options = [("yes","Yes"),("no","No")]
        text = "you look like a fresh one. Were you sent to report for duty?"
        cinematic = cinematics.SelectionCinematic(text,options,creator=void)
        cinematic.followUps = {"yes":{"container":self,"method":"getIntroInstant"},"no":{"container":self,"method":"tmpFail"}}
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
        showText("Remeber to report back, your worth will be counted in a mtick.",trigger={"container":self,"method":"end"})

    '''
    drop the player out of the command chain and place trigger for return
    '''
    def tmpFail(self):
        # show 
        say("go on then.")
        showText("go on then.")

        # add option to reenter the command chain
        terrain.waitingRoom.firstOfficer.basicChatOptions.append({"dialogName":"I want to report for duty","chat":chats.ReReport,"params":{"phase":self}})

    '''
    make the player do some tasks until allowing advancement elsewhere
    bad code: very chaotic. probably needs to be split up and partially rewritten
    bad pattern: mostly player only code
    '''
    def end(self):
        terrain.waitingRoom.addAsHopper(mainChar)

        self.didStoreCargo = False

        '''
        check reputation and punish/reward player
        '''
        class ProofOfWorth(events.Event):
            '''
            basic state initialization
            '''
            def __init__(subself,tick,char,toCancel=[],creator=None):
                super().__init__(tick,creator=creator)
                subself.tick = tick
                subself.char = char
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

                # call the player for the speech
                quest = quests.MoveQuestMeta(self.mainCharRoom,6,5,creator=void,lifetime=300)
                quest.endTrigger = {"container":subself,"method":"meeting"}
                '''
                kill player failing to apear for performance evaluation
                '''
                def fail():
                    messages.append("*alarm* non rensponsive personal detected. possible artisan. dispatch kill squads *alarm*")

                    # send out death squads
                    for room in terrain.militaryRooms:
                        quest = quests.MurderQuest(mainChar,creator=void)
                        mainChar.reputation -= 1000
                        room.secondOfficer.assignQuest(quest,active=True)
                        room.onMission = True
                quest.fail = fail
                mainChar.assignQuest(quest,active=True)

            '''
            fake a meeting with the player superordinate
            '''
            def meeting(subself):
                if mainChar.reputation < 15 or self.didStoreCargo:
                    # check if player has the lowest reputation
                    lowestReputation = True
                    for hopper in terrain.waitingRoom.hoppers:
                       if hopper.reputation < mainChar.reputation:
                           lowestReputation = False

                    showText("Time to prove your worth.")
                    if mainChar.reputation <= 0:
                        # punish player for low performance near to killing player
                        showText("You currently have no recieps on you. Please report to vat duty.",trigger={"container":subself,"method":"startVatPhase"})
                    elif lowestReputation and len(terrain.waitingRoom.hoppers) > 3:
                        showText("I have too many hoppers working here and you do the least work. Please report to vat duty.",trigger={"container":subself,"method":"startVatPhase"})
                    elif mainChar.reputation > 5:
                        # do nothing on ok performance
                        showText("great work. Keep on and maybe you will be one of us officers")
                    else:
                        # aplaud the player on good performance
                        showText("I see you did some work. Carry on")

                    # decrease reputation so the player will be forced to work continiously or to save up reputation
                    mainChar.reputation -= 3+(2*len(mainChar.subordinates))
                    self.mainCharRoom.addEvent(ProofOfWorth(gamestate.tick+(15*15*15),subself.char,creator=void))
                else:
                    mainChar.reputation += 5
                    # add the quest
                    showText("logistics command orders us to move some of the cargo in the long term store to accesible storage.\n3 rooms are to be cleared. One room needs to be cleared within 150 ticks\nThis requires the coordinated effort of the hoppers here. Since "+subself.char.name+" did well to far, "+subself.char.name+" will be given the lead.\nThis will be extra to the current workload")
                    quest = quests.HandleDelivery([terrain.tutorialCargoRooms[4]],[terrain.tutorialStorageRooms[1],terrain.tutorialStorageRooms[3],terrain.tutorialStorageRooms[5]],creator=void)
                    quest.endTrigger = {"container":self,"method":"subordinateHandover"}
                    mainChar.assignQuest(quest,active=True)

                    # add subordinates
                    for hopper in terrain.waitingRoom.hoppers:
                        # ignore bad candidates
                        if hopper == subself.char:
                            continue
                        if hopper in mainChar.subordinates:
                            continue
                        if hopper.dead:
                            continue

                        # add subordinate
                        mainChar.subordinates.append(hopper)

            '''
            trigger failure phase
            '''
            def startVatPhase(subself):
                phase = VatPhase()
                phase.start()

        '''
        return subordinates to waiting room
        '''
        def subordinateHandover(self):
            for hopper in terrain.waitingRoom.hoppers:
                if hopper in mainChar.subordinates:
                    if hopper.dead:
                        # punish player if subordinate is returned dead
                        messages.append(hopper.name+" died. that is unfortunate")
                        messages.append("you were rewarded -100 reputation")
                        mainChar.reputation -= 100
                    mainChar.subordinates.remove(hopper)
            self.addRoomConstruction()

        '''
        helper function to make the main char build a room
        '''
        def addRoomConstruction(self):
            for room in terrain.rooms:
                if isinstance(room,rooms.ConstructionSite):
                    constructionSite = room
                    break
            quest = quests.ConstructRoom(constructionSite,terrain.tutorialStorageRooms,creator=void)
            mainChar.assignQuest(quest,active=True)

        # add events to keep loose control
        self.mainCharRoom.addEvent(ProofOfWorth(gamestate.tick+(15*15*15),mainChar,creator=void))

        # add quest to pool
        quest = quests.ClearRubble(creator=void)
        quest.reputationReward = 3
        terrain.waitingRoom.quests.append(quest)

        self.cycleQuestIndex = 0

        # start series of quests that were looped to keep the system active
        self.addNewCircleQuest()

        # add the dialog for getting a job
        terrain.waitingRoom.firstOfficer.basicChatOptions.append({"dialogName":"Can you use some help?","chat":chats.JobChatFirst,"params":{"mainChar":mainChar,"terrain":terrain,"hopperDutyQuest":mainChar.quests[0]}})
        terrain.waitingRoom.secondOfficer.basicChatOptions.append({"dialogName":"Can you use some help?","chat":chats.JobChatSecond,"params":{"mainChar":mainChar,"terrain":terrain,"hopperDutyQuest":mainChar.quests[0]}})
        terrain.wakeUpRoom.firstOfficer.basicChatOptions.append({"dialogName":"Can you use some help?","chat":chats.JobChatFirst,"params":{"mainChar":mainChar,"terrain":terrain,"hopperDutyQuest":mainChar.quests[0]}})
        terrain.tutorialMachineRoom.firstOfficer.basicChatOptions.append({"dialogName":"Can you use some help?","chat":chats.JobChatFirst,"params":{"mainChar":mainChar,"terrain":terrain,"hopperDutyQuest":mainChar.quests[0]}})

    '''
    quest to carry stuff and trigger adding a new quest afterwards
    '''
    def addNewCircleQuest(self):
        labCoordinateList = [(2,1),(3,1),(4,1),(5,1),(6,1),(7,1)]
        shopCoordinateList = [(9,2),(9,7),(9,3),(9,6),(9,4),(9,5)]

        if self.cycleQuestIndex > 2*len(terrain.metalWorkshop.producedItems)-2:
            self.cycleQuestIndex = 0

        if self.cycleQuestIndex < len(terrain.metalWorkshop.producedItems):
            pos = labCoordinateList[self.cycleQuestIndex]
            room = terrain.tutorialLab
            index = self.cycleQuestIndex
        else:
            pos = shopCoordinateList[self.cycleQuestIndex-len(terrain.metalWorkshop.producedItems)]
            room = terrain.metalWorkshop
            index = -(self.cycleQuestIndex-len(terrain.metalWorkshop.producedItems))-1
            
        quest = quests.TransportQuest(terrain.metalWorkshop.producedItems[index],(room,pos[0],pos[1]),creator=void)
        quest.endTrigger = {"container":self,"method":"addNewCircleQuest"}
        quest.reputationReward = 0
        terrain.waitingRoom.quests.append(quest)

        self.cycleQuestIndex += 1

'''
dummmy for the lab phase
should serve as puzzle/testing area
'''
class LabPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("LabPhase")

    '''
    make a dummy movement and switch phase
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialLab

        super().start()

        # do a dummy action
        questList = []
        questList.append(quests.MoveQuestMeta(self.mainCharRoom,3,3,startCinematics="please move to the waiting position",creator=void))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None
        questList[-1].endTrigger = {"container":self,"method":"end"}

        # assign player quest
        mainChar.assignQuest(questList[0])

    '''
    move on to next phase
    '''
    def end(self):
        cinematics.showCinematic("we are done with the tests. return to work")
        BoilerRoomInteractionTraining().start()

'''
dummy for the vat phase
should serve as punishment for player with option to escape
bad pattern: has no known way of escaping
'''
class VatPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("VatPhase")

    '''
    do a dummy action and switch phase
    '''
    def start(self):
        self.mainCharRoom = terrain.tutorialVat

        super().start()

        # remove all player quests
        for quest in mainChar.quests:
            quest.deactivate()
        mainChar.quests = []

        quest = quests.MoveQuestMeta(terrain.tutorialVat,3,3,creator=void,lifetime=500)

        '''
        kill characters not moving into the vat
        '''
        def fail():
            messages.append("*alarm* refusal to honour vat assignemnt detected. likely artisan. Dispatch kill squads *alarm*")
            for room in terrain.militaryRooms:
                quest = quests.MurderQuest(mainChar,creator=void)
                mainChar.reputation -= 1000
                room.secondOfficer.assignQuest(quest,active=True)
                room.onMission = True
        quest.fail = fail
        quest.endTrigger = {"container":self,"method":"revokeFloorPermit"}

        # assign player quest
        mainChar.assignQuest(quest,active=True)

    '''
    take away floor permit to make escape harder
    '''
    def revokeFloorPermit(self):
        mainChar.hasFloorPermit = False

    '''
    move on to next phase
    '''
    def end(self):
        cinematics.showCinematic("you seem to be able to follow orders after all. you may go back to your training.")
        BoilerRoomInteractionTraining().start()

'''
dummy for the machine room phase
should serve to train maintanance
'''
class MachineRoomPhase(BasicPhase):
    '''
    straightforward state initialization
    '''
    def __init__(self):
        super().__init__("MachineRoomPhase")

    '''
    switch completely to free play
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
        questList.append(quests.MoveQuestMeta(terrain.tutorialMachineRoom,3,3,startCinematics="time to do some actual work. report to "+terrain.tutorialMachineRoom.firstOfficer.name,creator=void))

        # chain quests
        lastQuest = questList[0]
        for item in questList[1:]:
            lastQuest.followUp = item
            lastQuest = item
        questList[-1].followup = None

        # assign player quest
        mainChar.assignQuest(questList[0])

        self.end()

    '''
    win the game
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
    phasesByName["BoilerRoomWelcome"] = BoilerRoomWelcome
    phasesByName["BoilerRoomInteractionTraining"] = BoilerRoomInteractionTraining
    phasesByName["FurnaceCompetition"] = FurnaceCompetition
    phasesByName["WakeUpPhase"] = WakeUpPhase
    phasesByName["BrainTesting"] = BrainTestingPhase
    phasesByName["BasicMovementTraining"] = BasicMovementTraining
    phasesByName["FindWork"] = FindWork

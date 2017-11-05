import sys
import json
import time

import src.items as items
import src.quests as quests
import src.rooms as rooms
import src.characters as characters
import src.terrains as terrains
import src.cinematics as cinematics
import src.story as story
import src.gameMath as gameMath
import src.interaction as interaction
import config.commandChars as commandChars
import config.names as names

if len(sys.argv) > 1:
	import config.displayChars_fallback as displayChars
else:
	import config.displayChars as displayChars

##################################################################################################################################
###
##		some stuff that is somehow needed but slated for removal
#
#################################################################################################################################

#import sys, pygame
#pygame.init()
#pygame.mixer.music.load("music/chutulu.mp3")
#pygame.mixer.music.play()

# HACK: common variables with modules
phasesByName = {}

story.phasesByName = phasesByName
story.registerPhases()

cinematics.quests = quests
story.quests = quests

items.displayChars = displayChars
rooms.displayChars = displayChars
terrains.displayChars = displayChars
story.displayChars = displayChars

story.cinematics = cinematics
interaction.cinematics = cinematics

items.commandChars = commandChars
story.commandChars = commandChars
interaction.commandChars = commandChars

story.names = names

story.items = items

items.characters = characters
rooms.characters = characters
story.characters = characters

# HACK: common variables with modules
cinematics.main = interaction.main

cinematics.loop = interaction.loop
quests.loop = interaction.loop

cinematics.callShow_or_exit = interaction.callShow_or_exit
quests.callShow_or_exit = interaction.callShow_or_exit

rooms.calculatePath		= gameMath.calculatePath
quests.calculatePath		= gameMath.calculatePath
characters.calculatePath	= gameMath.calculatePath
terrains.calculatePath 		= gameMath.calculatePath

rooms.Character = characters.Character
		
class GameState():
	def __init__(self):
		self.gameWon = False
		self.currentPhase = phasesByName["FirstTutorialPhase"]
		self.tick = 0

		self.mainChar = characters.Character(displayChars.main_char,3,3,automated=False,name=names.characterFirstNames[self.tick%len(names.characterFirstNames)]+" "+names.characterLastNames[self.tick%len(names.characterLastNames)])
		self.mainChar.terrain = terrain
		self.mainChar.room = terrain.tutorialMachineRoom
		self.mainChar.watched = True
		terrain.tutorialMachineRoom.addCharacter(self.mainChar,3,3)
		mainChar = self.mainChar

	def save(self):
		saveFile = open("gamestate/gamestate.json","w")
		state = self.getState()
		if not state["gameWon"]:
			saveFile.write(json.dumps(state))
		else:
			saveFile.write(json.dumps("Winning is no fun at all"))
		saveFile.close()

	def load(self):
		saveFile = open("gamestate/gamestate.json")
		state = json.loads(saveFile.read())
		saveFile.close()

		self.setState(state)
		self.mainChar.setState(state["mainChar"])

	def setState(self,state):
		self.gameWon = state["gameWon"]
		self.currentPhase = phasesByName[state["currentPhase"]]
		self.tick = state["tick"]

		for room in terrain.rooms:
			room.setState(state["roomStates"][room.id])

		for room in terrain.rooms:
			room.timeIndex = self.tick

	def getState(self):
		roomStates = {}
		roomList = []
		for room in terrain.rooms:
			roomList.append(room.id)
			roomStates[room.id] = room.getState()
		
		return {  "gameWon":self.gameWon,
			  "currentPhase":self.currentPhase.name,
			  "tick":self.tick,
			  "mainChar":self.mainChar.getState(),
		          "rooms":roomList,
		          "roomStates":roomStates,
		       }
gamestate = None

messages = []
items.messages = messages
quests.messages = messages
rooms.messages = messages
characters.messages = messages
terrains.messages = messages
cinematics.messages = messages
story.messages = messages
interaction.messages = messages

quests.showCinematic = cinematics.showCinematic

terrain = terrains.TutorialTerrain()

items.terrain = terrain
story.terrain = terrain
interaction.terrain = terrain

characters.roomsOnMap = terrain.rooms

mapHidden = True

mainChar = None

phasesByName["FirstTutorialPhase"] = story.FirstTutorialPhase
phasesByName["SecondTutorialPhase"] = story.SecondTutorialPhase
phasesByName["ThirdTutorialPhase"] = story.ThirdTutorialPhase
phasesByName["VatPhase"] = story.VatPhase
phasesByName["MachineRoomPhase"] = story.MachineRoomPhase

gamestate = GameState()

try:
	gamestate.load()
except:
	pass

story.gamestate = gamestate
interaction.gamestate = gamestate

mainChar = gamestate.mainChar

rooms.mainChar = mainChar
terrains.mainChar = mainChar
story.mainChar = mainChar
interaction.mainChar = mainChar

cinematics.showCinematic("""

OOO FFF          AAA N N DD
O O FF   mice    AAA NNN D D
OOO F            A A N N DD




MMM   MMM  EEEEEE  CCCCCC  HH   HH  SSSSSSS
MMMM MMMM  EE      CC      HH   HH  SS
MM MMM MM  EEEE    CC      HHHHHHH  SSSSSSS
MM  M  MM  EEEE    CC      HHHHHHH  SSSSSSS
MM     MM  EE      CC      HH   HH        S
MM     MM  EEEEEE  CCCCCC  HH   HH  SSSSSSS
""")

gamestate.currentPhase().start()

def advanceGame():
	global movestate
	for character in terrain.characters:
		character.advance()

	for room in terrain.rooms:
		room.advance()

	gamestate.tick += 1

cinematics.advanceGame = advanceGame
interaction.advanceGame = advanceGame

interaction.loop.set_alarm_in(0.2, interaction.callShow_or_exit, "lagdetection")
interaction.loop.set_alarm_in(0.0, interaction.callShow_or_exit, "~")
interaction.loop.run()

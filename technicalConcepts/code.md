the code is a mess right now. Big cause is that i experimented a lot with the style of the game and most of the code is inactive, but intended to be reintegrated later. Also i got excited and added a lot of stuff with shifting focus. The constant is that i want to build a game that has massive detailed settings and runs fast.

In the current form the game is building things, automate building things and fighting the mold.

src/interaction.py
holds the core of the game.
* most of the relevant action is in processInput. (I do plan to break this function into parts). In the beginning it did things like moving the character when the movement key is pressed and redirecting keystrokes to interaction menues. The first important addition is that this function is called for every npc/monster and not only for the main character. This allows the npcs to do everything what the player can do including saving and quitting the game -_-. The second important addition is kind of a macro language interpreter hooked to the characters CommandKeyQueue. This allows the player to type "10d" wich will be exanded to "dddddddddd" and has conditions, registers and such things. This basically the current core content of the game and the current enemies are automated using this and items.
* The main loop is at the end, but is somewhat confusing since it collects keystrokes from terminal, pygame and network for multiplayer.
* The main loops advance() method doesn't do too much. It basically triggers scheduled events and makes the character loose satiation. The quest+solvers are currently not used, but mostly worked.
* The interaction menues are used by items and similar stuff

src/items.py
There are a lot of in use items. The most important ones are
* AutoTutor - basically the tutorial
* production items. MachineMachine Machine ProductionArtwork BluePrinter
* ressources like Scrap or MetalBars
* automation items. These items manipulate the characters CommanKeyQueue and basically take over control or reprogram the character (player or npc). Examples are Command CommandBloom AutoFarmer MemoryReset ProductionManager Map HiveMind. The production items Machine can also be programmed by the player to run commands on users on certain triggers
* mold and related items are basically the enemy right now. The mold grows into stages, spawns creatures, spawns commandBlooms that build networks and send creatures to the player in a somewhat organized fashion. This is probably very hard to read code, sorry.
* the GrowthTank allows players to spawns npcs
* the roomBuilder allows the player to build rooms

src/characters.py
contains the npc class which is player class and the monster classes. The pathfinding and quest handling and similar is unused now, but is another way of automating things by setting up series of quests that automatically break down to such simple tasks that npcs/the player can solve these quests automatically. Quite a lot of effort went into this and i really need to tie that back into the game.

src/rooms.py
The rooms are intended to contain activity. This allows the player to conver the room to a vehicle and move it around and to push other rooms around. A npc inside the moving room will continue to work since it is using the local coordinate system.

src/terrain.py
contains mostly storymode related code, the terrain currently used is GameplayTest -_-. The terrain is split into tiles, the borders between tiles redirect character movement, which is intended to make automation easier. The player can move between terrains when driving a vehicle. The whole pathfinding is disabled right now because it caused performance issues which need to be solved or the code needs to be deleted.

src/gamestate.py
holds references to everything in the game which is basically some terrains that in turn hold everything

src/events.py
contains a few events that can be triggered. For example used to make the mold grow.

executeMe.py
contains the runner and a LOT of stupid code that needs to replaced

src/story.py
concerns the story mode that basically didn't work out and is unused+broken right now. Basically only the BuildBase Class is important right now. I hope that i will be able to salvage most of this code.

src/canvas.py
holds the buffer for rendering thing. The hack with the Mapping is an abstraction to allow displaying the rendered map on terminal, pygame or networked client (executeYou.py)

src/saveing.py
The saving system used to work with differential savestates, but that resulted in runtime performance issues. It was changed to more simpler system recently, but remains of the old logic is still everywhere

src/quests.py is basically unused right now since storymode is broken, but i really want to reintegrate this code
src/overlays.py allows to draw some extra information on raw rendered maps
src/chats.py contains mostly unused storymode related code right now. Used and important is ChatMenu
src/cinematics.py contains mostly unused storymode related code. The initial cutscene is a TextCinematic
gameMath.py basically unused right now
pseudoUrwid.py is a hack

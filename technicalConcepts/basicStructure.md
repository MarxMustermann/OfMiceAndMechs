# basic structure

other games do exist and this game was not started because i dislike contributing elsewhere. I decided to write my own game for the follwing reasons:

1. Almost all games are propriety or have other bad licences. Often only the engine is open source an the game itself is not
2. Many open source games have a bad story or no story at all
3. Many indy games have huge performance issues and sometimes become unplayable
4. I want to write the game i'd love to play and to try *new things*

WARNIG: much of the things listed below are not implemented and are a concept only at this point of time.

== licence ==

Boring stuff first ;-)

All the games content/art/stories and even concepts and ideas are currently included in the repository itself. This is made to ensure that the game is realy free and will stay that way. This is done because it's the right thing to do, but hope to increase participation this way.

The next that the game may or may not switch to an incomptible licence later. This is not much trouble right now since i (Marx Mustermann) own 99% of the code and such switch would be easy. If this project gains traction, there will be a need to discuss how to keep track of original coders and how to manage the amount of code that is hard to relicense. Right now i'm the worst offender by beeing anonymous, This will have to change.

Ambient music and soundeffects would really be a great thing. There are a lot of creative commons music and sounds and there are very fine candidates. But the thing that's really needed would be open source music, that can be split into track and be controlled by the game to make proper integrated sound. EFF think that GPL doesn't really apply to music and it safely can be bundled. So having a small script downloading preselected music/sounds might be a good option.

== story ==

A good story is a lot of work. So it is often skipped or done by people who eat a lot of money. Story is a core component of a game. The way around this has to be collective effort. There a the follwing ideas to achieve this:

=== having a storyboard and defined lore ===

This should help coders to know what to code and what to write. It also would enable anybody who can edit a Textfile on github to participate. The idea is to split implementation from story design and have skilled people working on the story, while other people work on the engine and on implementing the story. A well working system of many people writing bits of story in a controlled way should give the project an edge on non open source projects.

The storyboard can be found at ../OfMiceAndMechs/storyboard.md. Some kind of soft ownership on story is likely to be needed to keep the story consistent and relatable.
This has time but it's best to never assume you own a story but still take care not to disturb other storylines.

A lore file/folder will be created. To define lore in collaborative projects lore threads in a forum are often used and this seems to work well. Anything in the lore file is truth anything else is not until put into the lore file. The lore should be a list of facts and should be more meaningful than the story. So if a story violates the lore file it has to change and not the other way around.

=== autogenerating story ==

By defining the edges of the story and have the rest generated automatically a big amount of story can be created. Parametized story, where details can be controlled by the evironment, could keep a story interesting many times.

A certain storyline has to have a setting it operates on. For example:

The player is tasked with transporting a valuable mad scientist artifact out of an encircled base through the enemy lines into safety.

At first the setting will be fixed. So the base, the siege and the way to safety will be hardcoded and heavyly scripted. First wave parametrization would make optical stuff parametrized. The names of npcs, less important parts of the base, the siege, good to transport and texts to be random generated. Second wave parametrization would be to use existing npcs, bases and sieges and bend them automatically to result in the needed setup. This would mean the map would not have to grow to support the storyline and more story can fit on less map space. Third wave parametrization would allow to only have minimal prequesites and to be able to detect situations this story fits in. This means the storyline is a mere quest that can be inserted automatically or used as building block later. An example would be a rescue unit for extraction of valuable things and personal trapped behind enemy lines. Such a units communication, base etc would be hardcoded at first and could be parametized later.

This is quite some work, but there is no need for one person to write the initial storyline, implementing it and parametizing it. Each step can be done by a different person or team.

=== generator assisted setting creation ===

Details are important and without a lot of effort it is not feasable to have a large map with proper detail. The idea with this game is to mix both. Use loose definitions to define something and to fill in the rest. For example a mech type X needs 2 boiler rooms, 5 storage rooms and some rooms in certain places. If the position of the boiler and storage rooms are not given, the rooms can be placed automatically into predefined slots. The same thing can be done for the rooms themselfes by placing items into placeholders.

This should result in hierarchy of templates, that should enable us to spawn a city and tweak details afterwards. The process should look some thing like this for a mining city:

1. Subclass a city
2. Create the mining operation by placing templates for the mining equipment and the transportation systems
3. Tweak the settings and roomlists for city generation.
4. Let the generator build the city around the mining operation.

If the generator works well enough, the city generation could be seeded to have a lot of different mining cities.

=== player assisted story generation ===

The game lets the player do many mundane tasks. One idea is to try to give tasks like story generation or detailing an map to the users, since creating is fun.

One way to do this would be to give users callanges to complete. For example the tutorial contains a competition of furnace firering the player has to win. The optimal solver is pretty simple, but nothing the AI could do on their own right now. A perfect completion of the task is rewarded with a branch in the storyline that leads to the competitions.

The sequence of action could be recorded and replayed later in the game or even in the games of other players. The challenges could be modified to make them harder and to get better solutions for important scenarios. Some challenges with solutions can be used to stage competitions and populate a research subject storyline. Other options would be placing items in rooms or designing mechs or to design defences or to plan a siege. One players defence could be the target of the next players siege.

Not all solutions can be recorded directly. So the player has to be put into a position, where useful results are the consequence. For example the player could be first tasked with solving the problem for a specific setting. If the player solves the problem for the specific setting, the next task would be to teach it to a npc. This converts the solution into the quest mechanic. The next reasonable step would be to test the trained npc behaviour against more generalized settings and task somebody with fixing edge cases.

== performance ==

now to the fun things.

Performance in many games suck because they were running reasonably smooth until a lot of features were added and the map grew. Exponential grows hits hard at some point and one of the *new things* is to make things large.

=== self contained units ===

The main idea to combat exponentioal growth is to have self contained units, that don't have to be calculated or can be caculated lazyly. A room is such a self contained unit.

It has an internal state like the items and the position of npc in the room. As long there is no need to observe the internal state, calculation can be skipped and hopefully never be done. At first glance this means a room not viewed by the player has to be rendered, but all other rooms can be ignored.

In reality this does not work. For example when a player views a room that skipped previous turns, the gamestate is out of touch. Also the internal state of rooms with meaning for the bigger picture like an engine room has to be observed.

To make this not break anything rooms may only be freezed as long as they have no interaction with the bigger picture and the state has to be restorable in case the player decides to look at it.

To make this work, rooms will have to be designed to be self contained and have little interaction with this environment. The interfaces are defined and the room and the environment should only interact through these interfaces. For example a boiler room has a door that can be used to transfer items and characters in and out of the room and 2 pipes for coal input and steam output. The environment only needs to care for changes in steam output and things leaving the door. Things and npcs can be put into the room through the door and the coal pipe.

There are plans to build a hierachy of these self contained things. Items make up rooms and rooms make up terrains and terrains make up big structures etc. In the best case whole terrains or big structures can be ignored.

For fixing the state when a player observes the room after some time, the simplest thing is to keep track of the tick a rooms state was calculated the last time. Since the room is self contained, the state can advanced x times till it is up to date. This should already be faster then advancing the rooms one after another, since the memory is not loaded for each time. For longer periods of inactivity a more efficient solution is needed to prevent moving the calculations and lag to the moment a player opens a door.

One way to aproach this is actually skip calculations. For example if it is known that a room will repeat its state, calculation of each repetition is not neccessary. The state can subtract the repetitions from the ticks to recalculate and only calculate the position in the last repetition.

The dirtiest way would be to ignore the state of the room if it wasnt observed for a really long time. The new state could be completely made up and inconsistencies attributed to mice. The new state doesn't have to be completely made up and state that is know to stay valid can be kept.

=== events ===

Checking state often is expensive, especially for non local state. A Quest for activating a object could for example poll the object about its state every round and see whether or not the quest was completed. For one quest this is not much of a problem, for 1000 quests it might be a problem. To avoid this, everything should interact using events and not by state checking. With events activating a object changes the objects external state which triggers an event. The activate quest registers at the object, that it cares for events from this object. Each time the object changes, the quest is notified and can check for completion.

For example the vat processing contains steamers that require the ressource steam to work. The steam is produced externally in the boiler room by npcs firering multiple furnaces. With events the communication is as follows:

1. the npc activates the furnaces.
2. the furnaces send a event to the boilers to tell them they are heated now.
3. The furnace schedules a event to itelf to stop working in some ticks.
4. the boiler reacts to being heated to schedule a event to itself, to indicate it will start to boil.
5. after starting to boil the boiler changes the steam output of the room
6. since the steam output changed the rooms external state, it notifies its listeners like the terrain about the change
7. The terrain has more steam output availabe and assigns them to the vat by sending an event.
8. changing the steam input changes the internal state of the vat and forces a recalculation
9. this finally forces the steamer to recalulate wich sets the correct display

10. after some ticks the furnace recieves the burnout event that was scheduled
11. the furnaces notify the boilers and the quest about the state change
12. the npcs switches task and starts firing the furnace
13. the boiler reacts to not beeing heated anymore by sending itself a event for cooling out
13. the npc activates the furnace
14. the furnace send the boiler a heat up event
15. the boiler cancels the cooling out event

This is somewhat complicated, but allows to treat dynamic behaviour as static behaviour. If we can assume the npc does it job and fires the furnaces reliably, we can assume that the furnaces only go out a short time and the boilers never actually stops boiling. This means that the events do their ping pong within the boiler room, but it stops at the boiler and therefore is contained within the room.

If the room is not observed and the npc is working reliably, the furnace operation is implicit and no events are send. The terrain doesn't have to trigger recalculations and the behaviour is fixed. When the npc actually stops to fire the furnaces, events propagate the change in behaviour and the behaviour is static again afterwards.

If behaviour changes often, for example every turn, this probably will hurt performance. The problematc behaviour should be abstracted, formulated as internal state or rounded away. Rounding away would for example be to just take the lower value and attribute the difference in productivity to mice.

=== abstracted calculation ===

Even if the other performance tweaks work, a truely massive AND detailed map will result in huge amounts of cpu load. In an ideal world, the boiler room would never use its internal detailed state, but use an easier secondary logic, like "produce x steam and consume x times y coal" to calculate state. The npc firering the furnace would not exist, but the interfaces to the environment would still be correct.

This is still a fuzzy idea, but somewhere between events, defined interfaces, player assisted solving and a bit of cheating this should be possible.

=== GPU calculation ===

GPU is insanely powerfull and not used at all in a ascii game. Beeing able to use it to advance and calculate gamestate would give the game massive performance edge.

The rough outline is to formulate the gamestate or other things as matrix and do matrix calculations on them to advance the state. The first problem to solve is how to formulate something from the game in matrix math. I know about some crude examples, but don't think i could use it properly right now. The second smaller issue is to make the matices BIG and do a lot of things with it, since loading things into th GPU and set everything up in there seems to take a lot of time.

=== efficent programming languages ===

The game uses python right now, wich is not famous for beeing fast, but for fast prototyping. This was the reason for using python in the first place. The approaches to performance are mostly on the design level, so python with fast prototyping was good. Also the main goal is to get a working alpha at all, so python is fine for now.

In the long run it probably wont be fine, but there are ways out of this. A slow conversion to c with cython or loading rust libs should work fine, if anybody has the time to do it.

== new things ==

Like most games this game intends to do some new things:

=== scaling ===

The game should play in a massive or infinite world. Since you cannout realy grasp the beauty of large structures if you continue to only see small parts of it, the game should run on many resolutions. For eaxmple:

a placeholder for an item is 1x1m big. This is roughly the size of a small machine equipment.
a tile is 15x15m big with room having about 10x10m size (5/3m height)
a terrain is 225x225m big with a small mech having about 150x150m size (25/15m height)
a sector is 3375x3375m big with the biggest mech beeing about 2250x2250m size (125/75m height)
... and so on.

Each resolution should have a map and things that happpen and mode of operations for each map. A sector map may be used to move normal size mechs, while the terrain map is used to move rooms and mini-mechs.

=== quest as native mechanic ===

Often the player cannot take real control over npcs or even big masses of npcs. This is because the AI of the npcs and the quest of the player work different. This should be different here and the main part of the game automatation and the player quests are the same thing. This means the player can delegate quests to the npcs and take over quests from npc. This hopefully means the player quest can be used to automate npcs and to make everyone busy and detailed. It also emables the player to take any place in the system and not feel left out.

=== steampunk setting ===

A steampunk setting with a lot of steam, geniuses, mechs and otherwise crazy people.

# news

### commit 500-608

The main focus was to make the basic game mechanic visible and understandable and failed to do so. I made the following changes

* forced the player to talk to npc at least a bit
* added chat options hinting at and explaining the automode
* added interaction options to the quest menu
* added more quests and options to the advanced quest menu
* added npc that compete with the player for quests
* added a longish period of repetetive quest to coerce the player into using auto mode
* added a big quest that the player has to delegate to npcs. This is kind of broken.

I made some progress but i kind of failed and there is a lot of work left to do. I hade some people test play the game and getting sidetracked by the issues uncovered and features requested. Notable changes and features added are:

* lot of bugfixes
* added a list of music as a baseline for discussions on how game music should be like. The music can (i think) be put into the game legally. [LIST](technicalConcepts/music)
* added 2 additional terrains. The can only be accessed by using the -T (scrapYard,nothingness) parameter and pretty much broken at this point of time.
* added various dialoge
* added dialog pictures explaining how to move
* added a scolling bar at the bottom of the screen explaining the display characters and the command chars
* tweaked turorialroom
* added a perspective rendered mode. It is still incomplete
* added a crude debug menu

### commit 400-500

The main focus was to solve the missing feeling of purpose, progress, adventure and discovery. I wrote all commits by myself, so this will reflect my perspective only.

I think i created a feeling of

* purpose, by adding hints on what comes after the current phase and the obvious expectation that the player will try to get into the next phase. This is kind of weak, but works well enough for now and can be scaled up. Additional elements of purpose would be great to have.
* progress, by adding chat menues, quests and story phases that have to be unlocked by the player and congratulating the player when a new thing is unlocked. There are only a few things to unlock and the way to get there is pretty grindy, but that can be improved on.
* adventure, by allowing the player to progress, to talk to people, learn some lore and be send through the mech the player doesn't fully know the purpose of. Also some mild element of danger and punishment is added to stress the player a bit. This topic is barely scratched, but i think a combination of the feeling of purpose, progress and discovery will likely create a feeling of adventure.
* discovery, by putting the player into a small room and having the player discover more of the map combined with bits of lore after some progress. Giving the player free movement allows to find some easter egg like functionality that is not bound into the story yet. This should cover both the players that rush for completion and the players who like to look around something to find. I think the way to go is revealing more features/lore/areas as the player progresses combined with experimental stuff that's harder to find.

All in all i think i figuered out a way to make the game feel like a game and hope that continuing this way will make the game feel like a interesting game further down the line. 

I did not only work on the issues above. Other noteble changes and features that were added are:

* many bugfixes
* added chat options that spawn story phases that spawn quests that spawn chat options and other combiations of these things. This is intended to test the waters on a fully dynamic system in this regard.
* added a autocompletion mechanism to the whole story and all quests used in the story. This means basically everything the player does now can be reused to have npcs running around doing these things. Also this is a preperation to give the player the ability to command npcs to complete quests like these as a way to exercise power.
* rebuild many of the quests in a recursive quest structure, that can get quite complex. This is partially intended, but needs to be scaled to not appear ridiculus. Also this is a preperation to have everybody do only one quest and have the rest as a subquest.
* added some elements of a economy, by adding the possibility to produce some items from scrap and by added a half working construction site. This is not embedded into the world in a meaningful way, but i think it is notable since it's a small step into the direction of an economy.
* A reputation system was added to be able to unlock stuff. This only notable since it is not indended to be kept on the long run, so don't get attached to it. 
* added npc specific dialog options to test the waters for a propper dynamic chat system.
* the ability to download and play CC songs to have some background music. This is more a symbolic thing, since it's using mplayer and only plays 2 songs.
* a half working tile based display mode based on pygame
* added quest queues and quest dispensers. These are not really used yet, but these are intended to allow to task quests without caring whom to task with the quest exactly
* added more quests. For example a quest to murder people which surely will be useful later
* added some more rooms.

### commit 0-400

unicode issues are resolved by having a almost pure ASCII renderer as default. Unicode modes can still be configured and can be toggled while playing using '`' (default). This means the game is almost cross platform supporting linux and mac.

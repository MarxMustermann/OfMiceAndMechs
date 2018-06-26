# OfMiceAndMechs
a to be prototype for a game

License: GPLv3
known-dependencies: 

* python3
* python3-urwid
* mplayer (for music)

## how to install and run the game 

### debian based sytems

* install the dependencies
  * sudo apt-get install python3 python3-urwid

* clone or download the game
  * git clone https://github.com/MarxMustermann/OfMiceAndMechs.git
  * or use the download as ZIP button and unzip

* start the game with:
  * cd into the OfMiceAndMechs
  * run with: python3 executeMe.py

## biggest current issue

The biggest issue currently is that the game doesn't feel like a game yet.

* The game looks good enough for me and the mechanics work most of the time, too.
* The cutscenes need more work but they are ok for now, too.
* there is a lot of storytelling (in relation to other content)
* Minigames like fireing the ovens or driving the mechs trough walls are fun for me
* crashes do happen but not constantly
* The game feels like a game (a boring one, but like a game)

I think the biggest issue currenty is that the main game mechanic is not working or is not clearly visible. This is gaining control (over npcs), controlling npcs and exercising power to gain power. The negation of this is also missing. This is loosing power by inefficent use of power or by not defending your position.

## news

### commit 400-500

The main focus was to solve the missing feeling of purpose, progress, adventure and discovery. I wrote all commits by myself, so this will reflect my perspective only.

I think i created a feeling of

* purpose, by adding hints on what comes after the cuurent phase and the obvious expectation that the player will try to get into the next phase. This is kind of weak, but works well enough for now and can be scaled up. Additional elements of purpose would be great to have.
* progress, by adding chat menues, quests and story phases that have to be unlocked by the player and congratulating the player when a new thing is unlocked. There are only a few things to unlock and the way to get there is pretty grindy, but that can be improved on.
* adventure, by allowing the player to progress to talk to people, learn some lore and be send through the mech the player doesn't fully know the purpose of. Also some mild element of danger and punishment is added to stress the player a bit. This topic is barely scratched, but i think a combination of the feeling of purpose, progress and discovery will likely create a feeling of adventure.
* discovery, by putting the player into a small room and having the player discover more of the map combined with bits of lore after some progress. Giving the player free movement allows to find some easter egg like functionality that is not bound into the story yet. This should cover both the players that rush for completion and the players who like to look around something to find. I think the way to go is revealing more features/lore/areas as the player progresses combined with experimental stuff that's harder to find.

All in all i think i figuered out a way to make the game feel like a game and hope that continuing this way will make the game feel like a interesting game further down the line. 

I did not only work on the issues above. Other noteble changes and features that were added are:

* many bugfixes
* added chat options that spawn story phases that spawn quests that spawn chat options and other combiations of these things. This is intended to test the waters on a fully dynamic system in this regard.
* added a autocompletion mechanism to the whole story and all quests used in the story. This means basically everything the player does now can be reused to have npcs running around doing these things. Also this is a preperation to give the player the ability to command npcs to complete quest like these as a way to exercise power.
* rebuild many of the quest in a recursive quest structure, that can get quite complex. This is partially intended, but needs to be scaled to not appear ridiculus. Also this is a preperation to have everybody do only one quest and have the rest as a subquest.
* added some elements of a economy, by adding the possibility to produce some items from scrap and by added a half working construction site. This is not embedded into the world in a meaningful way, but i think it is notable since it's a small step into the direction of an economy.
* A reputation system was added to be able to unlock stuff. This only notable since it is not indended to be kept on the long run, so don't get attached to it. 
* added npc specific dialog options to test the waters for a propper dynamic chat system.
* the ability to download and play CC songs to have some background music. This is more a symbolic thing, since it's using mplayer and only plays 2 songs.
* a half working tile based display mode based on pygame
* added quest queues and quest dispensers. These are not really used yet, but these are intended to allow to task quest without caring who to task with the quest exactly
* added more quests. For example a quest to murder people which surely will be useful later
* added some more room. 

### commit 0-400

unicode issues are resolved by having a almost pure ASCII renderer as default. Unicode modes can still be configured and can be toggled while playing using '`' (default). This means the game is almost cross platform supporting linux and mac.

## credits

the game has a option to download itself some creative commons music. Since most CCs requires attribution here it is...

A huge thanks to everybody releasing under CC! (despite the annoying attribution thing) And big thanks the https://freemusicarchive.org/ for hosting the music. (sorry about the traffic caused)

Background music By:

### Diezel Tea

https://diezeltea.bandcamp.com/

* startup and background music #1
  * Track: Kilikia (Original Mix)
  * Album: Kilikia

* background music #2
  * Track: Arzni (Part 1) [ft. Sam Khachatourian]
  * Album: Arzni

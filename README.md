# OfMiceAndMechs
a to-be prototype for a game

* [install and run](INSTALL.md)
* [screenshots](VISUALS.md)
* [news (latest: "commit 1203-1302")](NEWS.md)
* [credits](CREDITS.md)

## state of the game

Quite some work was done on the game so far. It has a playtime of 11 minutes for a near optimal run at the time of writing ([how to beat the game](HOWTO.md)), actual playtime should be magnitudes longer. You have beaten the game when you see "good job. credits". I try to get playtesters to play the game and meanwhile fix the bugs und broken features. This sadly means now real playtime extension for quite some time and no significant progress with the story board.

If everything goes well there will be a public demo at 35c3 ( Leipzig, Lebkuch.is assembly, 27-30.12.2018 )

At this stage it would really be useful to get help from whoever is reading this. If you notice bugs or have suggestions, please open an issue or contact me by mail. If you want to contribute, please start a pull request or contact me by mail. If you are unsure about something or want to contribute or just want to say hello write a quick mail.

mail:
marxmustermann@riseup.net

I will start to use branches with a dev branch with a lot if crashes and aim to keep the master somewhat stable, so you don't have to suffer through each crash i produce.

The detailed state of the game follows:

* The game looks good enough for me and the mechanics work most of the time, too.
* The cutscenes need more work but they are ok for now, too.
* there is a lot of storytelling (in relation to other content)
* Minigames like fireing the ovens or driving the mechs trough walls are fun for me
* crashes do happen but not constantly
* The game feels like a game (a boring one, but like a game)
* a save/load system exists and loading works most of the time
* The game offers a challenge, but still is somewhat uneventfull

Another round of general cleanup was done, so a more targeted cleanup follows. Since i got an actionable idea on how to better introduce the player to the games logic, i will focus on this for now.

I think the biggest issue is that the main game mechanic is not working or is not clearly visible. This is gaining control (over npcs), controlling npcs and exercising power to gain power. The negation of this is also missing. This is loosing power by inefficent use of power or by not defending your position. The puzzles are not clearly visible, too. This is kind of intended, but everything has to be more obvious.

Development speed depends on Code quality, so it is a important issue. It is a pretty big issue and grows with every change done on the code, so this issue will probably never be solved. But it seems like code quality will improve if i keep a pattern of doing a round of new features and a round of code cleanup. Since code qualtiy cannot be too good it seems more reasonable to skip a feature adding round than skipping a cleanup round.

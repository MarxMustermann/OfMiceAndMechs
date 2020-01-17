# OfMiceAndMechs
a to-be prototype for a game

* [install and run](INSTALL.md)
* [screenshots](VISUALS.md)
* [news (latest: "commit 1203-1302")](NEWS.md)
* [credits](CREDITS.md)

discord: https://discord.gg/uUMWHbS
mail: marxmustermann@riseup.net

## state of the game

I got some useful feedback and think i have an idea how to proceed. Thanks :-)

right now there are three ways so play the game:

* the story mode
has a lot of text and can be a bit overwhelming. This mode should work, but is not currently maintained. It has a playtime of 11 minutes for a near optimal run at the time of writing ([how to beat the game](HOWTO.md)), actual playtime should be magnitudes longer. You have beaten the game when you see "good job. credits".
start with
`python3 excuteMe.py`
* the tutorial
the tutorial has some fluff, but it is less overwhelming. It should explain things, but has a very short runtime. Saving does not work here, which is bad.
start with
`python3 excuteMe.py -T test -p Test`
* the openwold mode. In this mode you can play around with macros and build a base. This is currently the main mode.
start with
`python3 excuteMe.py -T test -p BuildBase`

Quite some work was done on the game so far. I thing a got a working proof of concept for gameplay. I will try to extend this and tie this back into the story mode.

At this stage it would really be useful to get help from whoever is reading this. If you notice bugs or have suggestions, please open an issue or contact me by mail. If you want to contribute, please start a pull request or contact me by mail. If you are unsure about something or want to contribute or just want to say hello write a quick mail.

I will start to use branches with a dev branch with a lot if crashes and aim to keep the master somewhat stable, so you don't have to suffer through each crash i produce. I did however start again to move code to master more often.

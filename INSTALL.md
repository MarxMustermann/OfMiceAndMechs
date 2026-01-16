# installation

## how to install and run the game

### windows

Download zip from  https://github.com/MarxMustermann/OfMiceAndMechs/releases/latest/download/OfMiceAndMechs-Win.zip and double click launch_game.bat
The game will take some moments to start and a console window may open, just give it some time to load.

### Linux

## dependencies

* install the dependencies
  * `sudo apt-get install python3 python3-venv`

* clone or download the game
  * `sudo apt-get install git`
  * `git clone https://github.com/MarxMustermann/OfMiceAndMechs.git`
  * or use the download as ZIP button and unzip

* install the game with:
  * `cd OfMiceAndMechs`
  * `python3 -m venv venvFolder`
  * `venvFolder/bin/python3 -m pip install -r requirements.txt`

* run the game with:
  * `venvFolder/bin/python3 executeMe.py`

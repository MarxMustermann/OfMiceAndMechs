= base mechanism =

* If you control a glass heart each Epoch a wave of enemies is spawned
* The more glass hears are on a terrain the more mana is spawned
* shrines allow to wish for magic effects
* the shrines use the terrains mana to cast the magic
* each terrain can hold a certain amount of mana
* each terrain renegerates mana at the start of every epoch

= code =
* the actual magic effects (things that violate game logic) are in src.magic.py

= work in progress =
Add ability to cast spells.

== done ==
* add ability to cast spells
  * add UI to cast
    * add keybind to cast spell
    * add keybind to recast last spell
  * implement 5 spells
    * close combat damage
  * show mana pool in UI when the hasMagic flag was set
  * make spells consume mana from local terrain

== TODO ==
* add ability to cast spells
  * implement 5 spells
    * heal
    * teleport home
    * ranged damage line
    * speed up

= ideas =
* spell ideas
  * ranged damage random
  * get stronger
  * heal
  * improve equipment
  * displace/push back enemies
* terrain specific minor gods
* have god collect the ecess mana to spawn spontanous magic
* have terrain burn of in random effects
  * spawning enemies

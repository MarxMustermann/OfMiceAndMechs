= base mechanism =

* If you control a glass heart each Epoch a wave of enemies is spawned
* The more glass hears are on a terrain the more mana is spawned
* shrines allow to wish for magic effects
* the shrines use the terrains mana to cast the magic
* each terrain can hold a certain amount of mana
* each terrain renegerates mana at the start of every epoch
* casting spells consume mana from the local terrain
* characters seeking to ascend are able to cast spells
* known spells
  * damage nearby

= code =
* the actual magic effects (things that violate game logic) are in src.magic.py

= instructions = 
* press p recast a spell
* press P to cast a spell
* terraon mana pool is shown in UI when the hasMagic flag was set

= work in progress =
Add ability to cast spells.

== done ==
* add ability to cast spells
  * implement 5 spells
    * close combat damage
    * heal

== TODO ==
* add ability to cast spells
  * implement 5 spells
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
  * spawn equipment
  * spawn blooms
* terrain specific minor gods
* have god collect the ecess mana to spawn spontanous magic
* have terrain burn of in random effects
  * spawning enemies

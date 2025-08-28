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
  * damage distance line
  * heal yourself
  * teleport home
  * temporary speed  

= code =
* the actual magic effects (things that violate game logic) are in src.magic.py

= instructions = 
* press p recast a spell
* press P to cast a spell
* terraon mana pool is shown in UI when the hasMagic flag was set

= work in progress =
== done ==
== TODO ==

= ideas =
* spell ideas
  * ranged damage random
  * get stronger
  * heal
  * improve equipment
  * displace/push back enemies
  * spawn equipment
  * spawn blooms
  * teleport tile/terrain
* terrain specific minor gods
* have god collect the ecess mana to spawn spontanous magic
* have terrain burn of in random effects
  * spawning enemies

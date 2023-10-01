== main goal ==

The magic system is supposed to allow to do things that break normal game rules.

The main motivation is to allow the player to skip game rules on occation. This should give the player more agency and should tone the base building aspect of the game a little.
For example if the player did not set up the things needed to spawn workers, the magic should allow to spawn some workers anyway.

The second motivation for this is to be able to drive story and breaking the game logic on the way. I could and did just hardcode the effects, but i feel i could get a cleaner structure by using magic.

== constraints ==

* The magic system should not dominate, but support the main gameplay
* everything doable by magic should be doable with ingame rules
* everything doable with ingame rules should be doable by magic
* the magic system should allow the story modules act within the world
* the magic system should self balance

== base mechanism ==

* mana is added to each terrain every epoch (15 * 15 * 15 ticks). The amount of mana dispensed can be tweaked and a terrain has a maximum mana amount.
For exapmle the starting terrain for the bases generates 5 mana per epoch a normal terrain 1. That means a base can grow anywhere, but the starting terrains are the correct choice.

* mana can be used as currency to shop for magic effects. This is done using shrines. Shrines serve as shops where you can buy magical effects. The terrains mana is removed when doing magic.
For example workers can be spawned and character stats can be upgraded. This is used to get the starting terrains the ressources needed right away, but a base could be build in other places.

* Different shrines give different rewards, that should allow to have the option sorted and categorized. The shrines differ by the god they are matched to. The shrines should be user buildable
For example one shrine allows to spawn workers another one is used to spawn basic ressources.

* Costs in the shrines should increase depending on how well the player is doing. The price increase should be specific to the category.
For example the cost of spawning workers increases with the the amount of workers there and how many of the specific worker type are there.

== extension (special items) ==

The main mechanic of the game is a CTF challenge that binds the other components together. Special items are scattered around and the faction wins the game, that collects all of those items.
To make game progress more smooth, rewards are handed out to the factions for each special item controlled.
To make the difficulty curve increasing, there are also negative effects handed out for each special item controlled. The negative effects should outweigh the positive effects.

=== mechanisms ===

* The special items are god themed to bind them into the magic system lore wise. The special items a are glass hearts and are set into glass statues.
* For each special item the terrain that controls it gains 5 mana per epoch. That means controlling the special item means you can buy an arbitrary reward from the shrines.
* For each special item an item specific negative magic effect should happen. The more special items the harsher the effect for all special items.
* For each special item an item specific positive magic effect should happen. This should give more meaning to controlling a specific special item.

== extension (challenges) ==

The story uses challenges to support desired player actions and reward the player for accomplishing things.
You get a reward for every room you build, for example.
This could be done using the magic system.

=== mechanisms ===

* shrines offer challenges to do and reward mana. This allows to feed the player some extra rewards. The story could add/disables challenges to steer player behaviour.
For example a shrine rewards mana for building rooms
* The god has a mana pool that get drained, when dispensing mana. If the mana pool runs low it dispenses less mana. If the mana pool is empty no rewards will be given.
This is ment to restrict the total effect of magic on the world
* Each god has its own mana pool. So doing the challenges of one god will only drain the pool of that god, but not of the other gods. So to get all mana, all types of challenges have to be done
* Each god regains 10 mana per epoch to allow the challenges to replenish.





== extension (god cut) ==

The mana spent at shrines could be shared with the god the shrine is assigned to. This would allow to replenish the gods mana pool.
The amount of mana the god gets can be set.

== extension (mana overflow) ==

If mana is assigned to a mana pool, but it has reached maximum a random magic effect can be done to burn that mana.

This means that each terrain gets some random magic

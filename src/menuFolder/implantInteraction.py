import src
import random

class ImplantInteraction(src.menues.SubMenu):
    """
    a menu showing a text
    """

    type = "ImplantInteraction"

    def __init__(self,character):
        '''
        initialise internal state

        Parameters:
            text: the text to show
        '''

        super().__init__()
        self.character = character
        self.submenu = None

    def getTitle(self):
        '''
        returns a title
        '''
        return "IMPLANT INTERACTION"
    
    def _spawnSpawnTaskMenu(self,base_text,task_type,offerSkip=False):
        '''
        spawns a menu that allows to accept the task as quest
        '''
        options = [("yes","yes"),("no","no")]
        if offerSkip:
            options.append(("skip","skip"))
        extraDescriptions = {
                "yes":"Assigns the quest to you. Press q to see quest details afterwards",
                "no":"No quest will be assigned.",
                "skip":"Skip the step altogether",
            }
        self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options,extraDescriptions=extraDescriptions)
        self.submenu.extraInfo["task_type"] = task_type

    def handleKey(self, key, noRender=False, character = None):
        '''
        show the actual with the implant

        Parameters:
            key: the key pressed
            noRender: flag to skip rendering
        Returns:
            returns True when done
        '''

        # close the menu
        if key == "esc":
            return True

        # open quest menu
        if key == "q":
            character.add_submenu(src.menues.menuMap["QuestMenu"](char=character))
            return True

        # set up helper variable
        terrain = character.getHomeTerrain()
        # wake builder
        wakeable_builder = False
        groundskeepers_place = None
        for room in terrain.rooms:
            if room.tag != src.story.groundskeeper_room_tag:
                continue
            groundskeepers_place = room
            items = room.getItemsByType("StasisTank")
            if not items:
                continue
            wakeable_builder = True

        # handle submenu
        if self.submenu:
            if self.submenu.tag == "implant_meta_action_selection":

                # handle interaction while a quest is runninig
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection == "abort quest":
                    character.clear_quests()

            elif self.submenu.tag == "implant_room_planning_selection":

                # handle interaction for planning rooms
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection:
                    if selection not in ("continue",):
                        room_type = selection
                        empty_rooms = terrain.get_empty_rooms()
                        if not empty_rooms:
                            character.notify("no empty rooms")
                            return
                        room_pos = empty_rooms[0].getPosition()
                        quest = src.quests.questMap["AssignFloorPlan"](floorPlanType=room_type,roomPosition=room_pos,reason="make use of the available rooms")
                        character.clear_quests()
                        character.assignQuest(quest)
                    self.submenu = None
                    self.done = True
                    return True
                return False

            elif self.submenu.tag == "implant_idle_selection":

                # handle interaction for waiting for the groundskeeper to build stuff
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection:
                    quests = []
                    if selection == "help":
                        quests.append(src.quests.questMap["HelpGroundskeeper"](lifetime=500))
                    if selection == "heal":
                        src.gamestate.gamestate.stern["last_heal"] = src.gamestate.gamestate.tick
                        quests.append(src.quests.questMap["StoryHeal"]())
                    if selection == "improve equipment":
                        src.gamestate.gamestate.stern["last_improve_equipment"] = src.gamestate.gamestate.tick
                        quests.append(src.quests.questMap["StoryImproveEquipment"]())
                    if selection == "explore":
                        quests.append(src.quests.questMap["StoryExploreHomeTerrain"](lifetime=500))
                    if selection == "getweapon":
                        quests.append(src.quests.questMap["ClearInventory"]())
                        quests.append(src.quests.questMap["Scavenge"](toCollect="Rod",amountToCollect=1,ignoreAlarm=True))
                        quests.append(src.quests.questMap["Equip"]())
                    if selection.startswith("fetch ") and len(selection.split(" ")) > 1:

                        # get item type
                        item_type = selection.split(" ")[1]

                        # loot rooms containing the item
                        found_loot_room = False
                        for room in terrain.rooms:
                            if room.tag != "ruin":
                                continue
                            if not room.getItemsByType(item_type):
                                continue
                            found_loot_room = True

                            if room.getEnemiesOnTile(character):
                                quests.append(src.quests.questMap["SecureTile"](toSecure=room.getPosition(),endWhenCleared=True))

                            if item_type == "MetalWorkingBench":
                                quests.append(src.quests.questMap["FetchMetalWorkingBench"](targetPositionBig=room.getPosition()))
                            elif item_type == "Anvil":
                                quests.append(src.quests.questMap["FetchAnvil"](targetPositionBig=room.getPosition()))
                            else:
                                quests.append(src.quests.questMap["LootRoom"](targetPositionBig=room.getPosition(),collectBig=True))
                            break
                    if selection.startswith("place ") and len(selection.split(" ")) > 1:

                        # get item type
                        item_type = selection.split(" ")[1]

                        # create quest
                        for buildSite in groundskeepers_place.buildSites:
                            if buildSite[1] == item_type:
                                quests.append(src.quests.questMap["PlaceItem"](itemType=item_type,targetPositionBig=groundskeepers_place.getPosition(),targetPosition=buildSite[0],boltDown=True, clearPath=True, clearSpace=True, tryHard=True))
                                break
                    if selection == "spawn_clone":
                        quests.append(src.quests.questMap["SpawnClone"]())
                    if selection == "kill_outside":
                        characters = terrain.characters[:]
                        random.choice(characters)
                        for check_character in characters:
                            if check_character.faction == character.faction:
                                continue
                            quests.append(src.quests.questMap["Huntdown"](target=check_character,alwaysfollow=True,lifetime=2000))
                            break
                    if selection == "break_stasisTank":
                        has_stasisTank = False
                        for room in terrain.rooms:
                            if room.tag != "ruin":
                                continue
                            stasisTank = room.getItemByType("StasisTank")
                            if not stasisTank:
                                continue
                            quests.append(src.quests.questMap["ActivateItem"](targetPositionBig=stasisTank.getBigPosition(),targetPosition=stasisTank.getPosition()))
                            break

                    character.clear_quests()
                    for quest in quests:
                        character.assignQuest(quest)
                    self.submenu = None
                    self.done = True
                    return True
                return False

            else:

                # handle the player having selected a new task
                self.submenu.handleKey(key, noRender, character)
                selection = self.submenu.selection
                if selection:
                    task_type = self.submenu.extraInfo.get("task_type")

                    # generate a quest for the player
                    if selection == "yes":

                        # show notification to hint at quest menu
                        if src.gamestate.gamestate.stern.get("first_quest_assign") == None:
                            src.gamestate.gamestate.stern["first_quest_assign"] = True
                        if src.gamestate.gamestate.stern["first_quest_assign"]:
                            src.gamestate.gamestate.stern["first_quest_assign"] = False
                            character.showTextMenu(["""
The quest description and general instructions are shown in the quest menu.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""You can open the quest menu by pressing q"""),"""
"""],allowQuests=True,do_not_scale=True)

                        # set up helper variables
                        terrain = character.getHomeTerrain()
                        groundskeepers_place = None
                        for room in terrain.rooms:
                            if room.tag != src.story.groundskeeper_room_tag:
                                continue
                            groundskeepers_place = room

                        # generate actual quest
                        quests = []
                        if task_type == "escape_lab":
                            quests.append(src.quests.questMap["EscapeLab"]())
                        elif task_type == "reach_shelter":
                            quests.append(src.quests.questMap["GoToTile"](targetPosition=groundskeepers_place.getPosition()))
                        elif task_type == "free_groundskeeper":
                            quests.append(src.quests.questMap["ActivateItem"](targetPosition=(6,6,0),targetPositionBig=groundskeepers_place.getPosition()))
                        elif task_type == "fix_groundskeeper":
                            quests.append(src.quests.questMap["FixGroundskeeper"]())
                        elif task_type == "help_groundskeeper":
                            quests.append(src.quests.questMap["HelpGroundskeeper"](lifetime=500))
                        elif task_type == "wait_explosion":
                            quests.append(src.quests.questMap["WatchLabBurn"]())
                        elif task_type == "equip":
                            quests.append(src.quests.questMap["Equip"]())
                        elif task_type == "kill_spiderling":
                            quests.append(src.quests.questMap["SecureTile"](toSecure=(7,5,0),endWhenCleared=True,reason="clear the path",simpleAttacksOnly=True,noHeal=True))
                        elif task_type == "explore":
                            quests.append(src.quests.questMap["StoryExploreHomeTerrain"](lifetime=500))
                        elif task_type == "observe":
                            quests.append(src.quests.questMap["OpenObserveMenu"]())
                        elif task_type == "help":
                            quests.append(src.quests.questMap["OpenHelpMenu"]())
                        elif task_type == "spawn_clone":
                            quests.append(src.quests.questMap["SpawnClone"]())

                        # assign the quest
                        if not quests:
                            character.notify("failed generating quest")
                        for quest in quests:
                            character.assignQuest(quest)

                    # skip special sections
                    if selection == "skip":
                        if task_type == "wait_explosion":
                            src.gamestate.gamestate.stern["skipped_explosion"] = True
                        if task_type == "observe":
                            src.gamestate.gamestate.stern["opened_observe"] = True
                        if task_type == "help":
                            src.gamestate.gamestate.stern["opened_help"] = True
                        self.submenu = None

                    # close the menu
                    if self.submenu:
                        character.changed("completed implant interaction")
                        self.done = True
                        return True

                # wait for keystrokes
                if self.submenu:
                    return False

        # show special text for first reach out
        implant_intro_text = ""
        if src.gamestate.gamestate.stern.get("first_reachout_done") is None:
            src.gamestate.gamestate.stern["first_reachout_done"] = False
        if not src.gamestate.gamestate.stern["first_reachout_done"]:
            implant_intro_text = [(src.interaction.urwid.AttrSpec("#0af","black"),"""
You must be confused.

I'm your implant and i'm here to help you.
You can contact me any time by pressing tab.
""")]
            src.gamestate.gamestate.stern["first_reachout_done"] = True

        # handle interation while there are quests assigned
        if len(character.quests) > 0 and not character.quests[0].type == "ReachOutStory":
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


""",(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You already have an active quest."),"""

Press q to open the quest menu and see the quest description.
I also try to calcuate the keystrokes needed to solve the quest.
This suggested action is shown on the left side of the screen.

What do you want to do?
"""]
            options = [("abort quest","abort active quests"),("continue","continue")]
            self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options)
            self.submenu.handleKey(key, noRender, character)
            self.submenu.tag = "implant_meta_action_selection"
            return False

        # leave the inital room
        if character.container.tag == "the architects tomb":    
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

Hello!

""",implant_intro_text,"""

The machinery around you is """,(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"burning and exploding"),f""".
So i recommend leaving the room before you get hurt.

""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"The exit is on the north side, you can move by pressing the wasd keys."),"""
You can move my clicking on the map as well.

Big items like the machinery will block your movement.


""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Shall i assign you a quest to leave the room to avoid the explosion?"""),"""
"""]
            self._spawnSpawnTaskMenu(base_text,"escape_lab")
            return False

        # wait for lab to burn down
        if not src.gamestate.gamestate.stern.get("skipped_explosion"):
            tombCandidates = terrain.getRoomByPosition((7,7,0))
            if tombCandidates and tombCandidates[0].tag == "the architects tomb":
                base_text = ["""
You made it out of the burning room.
We are safe for a second, but the room will explode soon.

Watch the room burn down.
""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""You can pass time by pressing the "." key."""),"""

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Shall i assign you a quest to watch the room explode?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"wait_explosion",offerSkip=True)
                return False

        # indroduce help menu
        if not src.gamestate.gamestate.stern.get("opened_help"):
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

I am not sure how many of your memories survived.

If you don't remember how to to interact with the world,
use the """,(src.pseudoUrwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"help menu"),""" to refresh your memories.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to open the help menu?"""),"""
"""]
            self._spawnSpawnTaskMenu(base_text,"help",offerSkip=True)
            return False

        # wake builder
        wakeable_builder = False
        groundskeepers_place = None
        for room in terrain.rooms:
            if room.tag != src.story.groundskeeper_room_tag:
                continue
            groundskeepers_place = room
            items = room.getItemsByType("StasisTank")
            if not items:
                continue
            wakeable_builder = True
        if wakeable_builder: 

            # kill enemy
            if character.getBigPosition() == (7,6,0) and terrain.getCharactersOnTile((7,5,0)):
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""
""",implant_intro_text,f"""
You are outside and need to find shelter.

There is shelter to the north,
but """,(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""there is an enemy blocking your path."""),"""
kill the enemy. Enemy are shown with red edges.

The simplest way to fight enemies is to bump into them.
""",(src.pseudoUrwid.AttrSpec(src.interaction.ui_hint_color,"black"),"""You can do this by walking against them."""),"""
This will trigger an attack.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to kill the enemy?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"kill_spiderling")
                return False


            # go inside
            if not character.container.isRoom:
                directions = []
                char_position = character.getBigPosition()
                room_position = groundskeepers_place.getPosition()
                if char_position[0] > room_position[0]:
                    amount = char_position[0]-room_position[0]
                    directions.append(f"{amount} tiles to the west")
                if char_position[0] < room_position[0]:
                    amount = room_position[0]-char_position[0]
                    directions.append(f"{amount} tiles to the east")
                if char_position[1] < room_position[1]:
                    amount = room_position[1]-char_position[1]
                    directions.append(f"{amount} tiles to the south")
                if char_position[1] > room_position[1]:
                    amount = char_position[1]-room_position[1]
                    directions.append(f"{amount} tiles to the north")
                directionString = "It is "+" and ".join(directions)+"."
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""
""",implant_intro_text,"""
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""You are outside and need to find shelter."""),f"""

The old groundskeepers place is nearby.
Go there. {directionString}

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to find shelter?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"reach_shelter")
                return False

            # go to the groundskeepers place
            if not character.container.tag == src.story.groundskeeper_room_tag:
                directions = []
                char_position = character.getBigPosition()
                room_position = groundskeepers_place.getPosition()
                if char_position[0] > room_position[0]:
                    amount = char_position[0]-room_position[0]
                    directions.append(f"{amount} tiles to the west")
                if char_position[0] < room_position[0]:
                    amount = room_position[0]-char_position[0]
                    directions.append(f"{amount} tiles to the east")
                if char_position[1] < room_position[1]:
                    amount = room_position[1]-char_position[1]
                    directions.append(f"{amount} tiles to the south")
                if char_position[1] > room_position[1]:
                    amount = char_position[1]-room_position[1]
                    directions.append(f"{amount} tiles to the north")
                directionString = "It is "+" and ".join(directions)+"."
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""


Explore the rooms and try to find something useful.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""There surely is something in the groundskeepers place."""),f"""
Look there. {directionString}

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to go to the groundskeepers place?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"reach_shelter")
                return False

            # teach how to observe
            if not src.gamestate.gamestate.stern.get("opened_observe"):
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You are safe for now."),"""

Look around to see if you can find something useful.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to observe the environment?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"observe",offerSkip=True)
                return False

            # free the groundskeeper
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""


There is a StasisTank in this room. 
It should contain a survivior.
That could be useful for us.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Free the survivor."""),"""

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to free the survivor?"""),"""
"""]
            self._spawnSpawnTaskMenu(base_text,"free_groundskeeper")
            return False

        # find the groundskeeper
        groundsKeeper = None
        for check_character in terrain.getAllCharacters():
            if not check_character.faction == character.faction:
                continue
            if check_character == character:
                continue
            if not isinstance(check_character,src.characters.characterMap["GroundsKeeper"]):
                continue
            groundsKeeper = check_character

        # check for workers
        workers = []
        for check_character in terrain.getAllCharacters():
            if not check_character.faction == character.faction:
                continue
            if check_character == character:
                continue
            if check_character.burnedIn:
                continue
            workers.append(check_character)
        
        # interact with the groundskeeper
        if groundsKeeper or workers:

            # initiate groundskeeper
            if groundsKeeper and not groundsKeeper.registers.get("startedWorking"):
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""The groundskeeper lives."""),"""
He looks like this: @@

This could be very useful.

It doesn't work though.
Find out why.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to talk to the survivor?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"fix_groundskeeper")
                return False

            # ensure the groundskeeper has a painter
            if groundsKeeper:
                hasPainter = groundsKeeper.hasPainter()
                if not groundsKeeper.registers.get("gotPainter") or not hasPainter:
                    if not self.character.searchInventory("Painter"):
                        base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

The groundskeeper is working now,
but """,(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""it seems to missing something very essential."""),"""
This could be very useful.

Check if you can help out.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to help to groundskeeper?"""),"""
"""]
                    else:
                        base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"You obtained a Painter."),"""

Bring it to the groundskeeper.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to help to groundskeeper?"""),"""
"""]
                    self._spawnSpawnTaskMenu(base_text,"help_groundskeeper")
                    return False

            # equip yourself
            equipment_availabe = False
            for room in terrain.rooms:
                if room.tag == "ruin":
                    continue
                weapons = []
                weapons.extend(room.getItemsByType("Rod"))
                weapons.extend(room.getItemsByType("Sword"))
                if weapons and character.weapon is None:
                    equipment_availabe = True
                    break
                for weapon in weapons:
                    if weapon.baseDamage > character.weapon.baseDamage:
                        equipment_availabe = True
                        break
                armors = []
                armors.extend(room.getItemsByType("Armor"))
                if armors and character.armor is None:
                    equipment_availabe = True
                    break
                for armor in armors:
                    if armor.armorValue > character.armor.armorValue:
                        equipment_availabe = True
                        break
            if equipment_availabe:
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""There is better equipment available."""),"""

Equip yourself with that equipment.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to help to groundskeeper?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"equip")
                return False

            # set floorplans
            hasEmptyRoom = False
            hasCityPlaner = False
            hasStorage = False
            hasGooProcessing = False
            hasTemple = False
            for room in terrain.rooms:
                if room.tag is None:
                    hasEmptyRoom = True
                    continue
                if room.tag == "ruin":
                    continue
                if room.tag == "storage":
                    hasStorage = True
                    continue
                if room.tag == "gooProcessing":
                    hasGooProcessing = True
                    continue
                if room.tag == "temple":
                    hasTemple = True
                    continue
                if room.getItemsByType("CityPlaner",needsBolted=True):
                    hasCityPlaner = True
            if hasEmptyRoom and hasCityPlaner:
                available_roomTypes = []
                extraDescriptions = {}
                extraDescriptions["storage"] = "Allow to more stuff"
                extraDescriptions["gooProcessing"] = "Allows to produce goo and to spawn Clones"
                extraDescriptions["temple"] = "Allows to pray and wish for miracles"
                if not hasStorage:
                    available_roomTypes.append("storage")
                if not hasGooProcessing:
                    available_roomTypes.append("gooProcessing")
                if not hasTemple:
                    available_roomTypes.append("temple")
                if available_roomTypes:
                    base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Your base has an empty room to fill."""),"""

Use the CityPlaner to set room should be build there.
"""]

                    base_text.extend(["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to make use of the empty room?"""),"""
"""])
                    options = []
                    for room_type in available_roomTypes:
                        options.append((room_type,f"plan a {room_type} room"))
                    options.append(("continue","continue with quest"))
                    self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options,extraDescriptions=extraDescriptions)
                    self.submenu.tag = "implant_room_planning_selection"
                    return False

            # pass time till groundskeeper is ready
            current_time = src.gamestate.gamestate.tick
            if groundsKeeper and groundskeepers_place.floorPlan or src.gamestate.gamestate.stern.get("no_groundskeeper_quest",0) > current_time-200:
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

The groundskeeper seems to be busy.
We cannot help right now.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""I think we should explore the ruins around us a bit."""),"""

There are many useful items around.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you a quest to explore the environment?"""),"""
"""]
                self._spawnSpawnTaskMenu(base_text,"explore")
                return False

            # help groundskeeper set up
            base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

The groundskeeper is working now.
It will start to rebuild its working area.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Help the groundskeeper or help yourself.""")]

            if not groundsKeeper:
                base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),f"""

The workers are working now.
They will complete tasks on the base.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"""Help the workers or help yourself.""")]

            base_text.extend(["""

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""What quest shall i assign?"""),"""
"""])

            # generate quests to choose from
            options = []
            extraDescriptions = {}

            # obtain weapon
            shown_obtain_weapon = False
            extraDescriptions["getweapon"] = "Find a weapon to be able to defend yourself"
            if not character.weapon and (src.gamestate.gamestate.stern.get("no_weapon_quest_abort") or groundsKeeper):
                options.append(("getweapon","obtain weapon"))
                shown_obtain_weapon = True

            # help groundskeeper
            shown_help = False
            extraDescriptions["help"] = "Helping the groundskeeper will make it complete its work faster."
            if groundsKeeper and not groundskeepers_place.getItemByType("Anvil") or not groundskeepers_place.getItemByType("MetalWorkingBench"):
                options.append(("help","help groundskeeper"))
                shown_help = True

            # work around dead groundskeeper
            extraDescriptions["fetch Anvil"] = "The base needs an Anvil to produce MetalBars."
            extraDescriptions["fetch MetalWorkingBench"] = "The base needs an MetalWorkingBench to start production."
            extraDescriptions["fetch CityPlaner"] = "The base needs a CityPlaner to expand."
            if not groundsKeeper:
                missing_anvil = False
                missing_metalWorkingBench = False
                missing_cityPlaner = False
                for buildSite in groundskeepers_place.buildSites:
                    if buildSite[1] == "Anvil":
                        missing_anvil = True
                    if buildSite[1] == "MetalWorkingBench":
                        missing_metalWorkingBench = True
                    if buildSite[1] == "CityPlaner":
                        missing_cityPlaner = True

                has_anvil = False
                has_metalWorkingBench = False
                has_cityPlaner = False
                if character.searchInventory("Anvil"):
                    has_anvil = True
                if character.searchInventory("MetalWorkingBench"):
                    has_metalWorkingBench = True
                if character.searchInventory("CityPlaner"):
                    has_cityPlaner = True
                for room in terrain.rooms:
                    if room.tag == "ruin":
                        continue
                    if room.getNonEmptyOutputslots("Anvil"):
                        has_anvil = True
                    if room.getNonEmptyOutputslots("MetalWorkingBench"):
                        has_metalWorkingBench = True
                    if room.getNonEmptyOutputslots("CityPlaner"):
                        has_cityPlaner = True

                if missing_anvil:
                    if not has_anvil:
                        options.append(("fetch Anvil","fetch Anvil"))
                    else:
                        options.append(("place Anvil","place Anvil"))
                if missing_metalWorkingBench:
                    if not has_metalWorkingBench:
                        options.append(("fetch MetalWorkingBench","fetch MetalWorkingBench"))
                    else:
                        options.append(("place MetalWorkingBench","place MetalWorkingBench"))
                if missing_cityPlaner:
                    if not has_cityPlaner:
                        options.append(("fetch CityPlaner","fetch CityPlaner"))
                    else:
                        options.append(("place CityPlaner","place CityPlaner"))

            # spawn workers
            extraDescriptions["spawn_clone"] = "More workers means more work getting done"
            shown_spawn_worker = False
            num_workers = 0
            for check_char in character.getTerrain().getAllCharacters():
                if check_char.faction != character.faction:
                    continue
                if check_char == character:
                    continue
                if not isinstance(check_char,src.characters.characterMap["Clone"]):
                    continue
                if check_char.burnedIn:
                    continue
                num_workers += 1
            num_base_rooms = 0
            for room in character.getTerrain().rooms:
                if room.tag == "ruin":
                    continue
                num_base_rooms += 1
            if groundsKeeper:
                if num_base_rooms-2 > num_workers:
                    options.append(("spawn_clone","spawn worker"))
                    shown_spawn_worker = True
            else:
                if num_base_rooms > num_workers:
                    options.append(("spawn_clone","spawn worker"))
                    shown_spawn_worker = True

            # improve equipment
            extraDescriptions["improve equipment"] = "Much of you combat power is based on your equipment. Upgrade it regulary"
            has_equipment = False
            if character.armor or isinstance(character.weapon,src.items.itemMap["Sword"]):
                has_equipment = True
            shown_improve_equipment = False
            last_improve_equipment = src.gamestate.gamestate.stern.get("last_improve_equipment",0)
            if has_equipment and last_improve_equipment < src.gamestate.gamestate.tick-500 and (character.weapon or character.armor):
                options.append(("improve equipment","improve your equipment"))
                shown_improve_equipment = True

            # heal
            shown_heal = False
            extraDescriptions["heal"] = "Staying in good health is essential to staying alive"
            last_heal = src.gamestate.gamestate.stern.get("last_heal",0)
            if character.health < character.adjustedMaxHealth//2 and last_heal < src.gamestate.gamestate.tick-500:
                options.append(("heal","heal yourself"))
                shown_heal = True

            # explore
            extraDescriptions["explore"] = "See if you can find anything useful"
            shown_explore = False
            if random.random() < 0.5:
                options.append(("explore","explore terrain"))
                shown_explore = True

            # kill things
            extraDescriptions["kill_outside"] = "The insects outside are a constant threat. Remove the threat"
            found_outside_enemies = False
            shown_kill_outside = False
            for check_character in terrain.characters:
                if check_character.faction == character.faction:
                    continue
                found_outside_enemies = True
            if random.random() < 0.5:
                if found_outside_enemies and character.health > character.adjustedMaxHealth*2//3:
                    options.append(("kill_outside","kill insects"))
                    shown_kill_outside = True

            # wake left over workers
            extraDescriptions["break_stasisTank"] = "Maybe more survivors can be found in the remaining StasisTanks. Break them and find out"
            has_stasisTank = False
            for room in terrain.rooms:
                if room.tag != "ruin":
                    continue
                if room.getItemsByType("StasisTank"):
                    has_stasisTank = True
            if has_stasisTank:
                options.append(("break_stasisTank","break StasisTank"))

            # show options not yet shown
            if groundsKeeper and not shown_help:
                options.append(("help","help groundskeeper"))
            if not shown_obtain_weapon and not character.weapon:
                options.append(("getweapon","obtain weapon"))
            if has_equipment and not shown_improve_equipment:
                options.append(("improve equipment","improve your equipment"))
            if not shown_heal and character.health < character.adjustedMaxHealth:
                options.append(("heal","heal yourself"))
            if not shown_explore:
                options.append(("explore","explore terrain"))
            if not shown_spawn_worker:
                options.append(("spawn_clone","spawn worker"))
            if found_outside_enemies:
                options.append(("kill_outside","kill insects"))

            # show the options to the player
            options.append(("continue","continue without quest"))
            self.submenu = src.menues.menuMap["SelectionMenu"](base_text,options=options,extraDescriptions=extraDescriptions)
            self.submenu.tag = "implant_idle_selection"
            return False

        # help groundskeeper set up
        base_text = ["""
""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"You reach out to your implant and it answers:"),"""

Everyone around you is dead and gone.
This will complicate things.

""",(src.interaction.urwid.AttrSpec(src.interaction.highlighted_ui_color,"black"),"Spawn a new Clone"),""" to replace groundskeeper.

""",(src.interaction.urwid.AttrSpec(src.interaction.disabled_ui_color,"black"),"""Shall i assign you the quest to spawn a Clone?"""),"""
"""]

        self._spawnSpawnTaskMenu(base_text,"spawn_clone")
        return False

    def render(self,size=None):
        '''
        show the text of the menu
        '''
        if self.submenu:
            return self.submenu.render(size=size)
        else:
            return ["""something went wrong"""]

# register the menu type
src.menues.add_menu(ImplantInteraction)

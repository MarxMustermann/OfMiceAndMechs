import src
import random

class Promoter(src.items.Item):
    '''
    ingame item for marking official progress in the hierarchy
    '''
    type = "Promoter"
    def __init__(self,):
        super().__init__(display="PR")
        self.faction = None
        self.walkable = False
        self.bolted = True

    def apply(self,character):
        '''
        handle activation by trying to promote the user
        '''

        # filter input
        if not character.rank:
            character.addMessage("you need a rank to use this machine")
            return
        if not self.faction:
            self.faction = character.faction

        # check if promotion to rank 5 applies
        highestAllowed = None
        if character.rank > 5:
            numCharacters = 0
            terrain = character.getTerrain()
            for checkChar in terrain.characters:
                if not checkChar.faction == character.faction:
                    continue
                if not checkChar.charType == "Clone":
                    continue
                if checkChar.burnedIn:
                    continue
                numCharacters += 1
            for room in terrain.rooms:
                for checkChar in room.characters:
                    if not checkChar.faction == character.faction:
                        continue
                    if not checkChar.charType == "Clone":
                        continue
                    if checkChar.burnedIn:
                        continue
                    numCharacters += 1

            if numCharacters < 2 and not highestAllowed:
                character.addMessage(f"promotions locked")

                submenu = src.menuFolder.textMenu.TextMenu("""
Promotions to rank 5 are blocked.

There need to be at least 1 clone besides you on the base to allow any promptions.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                return

            highestAllowed = 5

        if character.rank > 2:
            foundEnemies = []
            terrain = self.getTerrain()
            for otherChar in terrain.characters:
                if otherChar.faction == character.faction:
                    continue
                foundEnemies.append(otherChar)

            for room in terrain.rooms:
                for otherChar in room.characters:
                    if otherChar.faction == character.faction:
                        continue
                    foundEnemies.append(otherChar)

            if foundEnemies and not highestAllowed:
                character.addMessage(f"promotions locked")

                submenu = src.menuFolder.textMenu.TextMenu("""
Promotions to rank 2 are blocked.
Enemies are nearby.

Kill all enemies on this terrain, to unlock the promotions to rank 2.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                return

            highestAllowed = 2

        while character.rank > highestAllowed:
            if character.rank == 6:
                 character.hasSpecialAttacks = True
            character.rank -= 1

        character.addMessage(f"you were promoted to rank {highestAllowed}")
        submenu = src.menuFolder.textMenu.TextMenu(f"""
You put your head into the machine.

Its tendrils reach out and touch your implant.

It is upgraded to rank {highestAllowed}.
""")
        character.macroState["submenue"] = submenu
        character.runCommandString("~",nativeKey=True)

        character.changed("got promotion",{})

# register item type
src.items.addType(Promoter)

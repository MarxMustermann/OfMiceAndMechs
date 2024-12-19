import src
import random

class Promoter(src.items.Item):
    """
    """

    type = "Promoter"

    def __init__(self,):
        """
        configure the superclass
        """

        super().__init__(display="PR")
        self.faction = None

        self.walkable = False
        self.bolted = True

    def apply(self,character):
        if not self.faction:
            self.faction = character.faction

        if character.rank > 5:
            numCharacters = 0
            terrain = character.getTerrain()
            for checkChar in terrain.characters:
                if not checkChar.faction == character.faction:
                    continue
                if not checkChar.charType == "Character":
                    continue
                if checkChar.burnedIn:
                    continue
                numCharacters += 1
            for room in terrain.rooms:
                for checkChar in room.characters:
                    if not checkChar.faction == character.faction:
                        continue
                    if not checkChar.charType == "Character":
                        continue
                    if checkChar.burnedIn:
                        continue
                    numCharacters += 1

            if numCharacters < 2:
                character.addMessage(f"promotions locked")

                submenu = src.menuFolder.TextMenu.TextMenu("""
Promotions to rank 5 are blocked.

There need to be at least 1 clone besides you on the base to allow any promptions.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                return

            character.rank = 5
            character.hasSpecialAttacks = True
            
            character.addMessage(f"you were promoted to rank 5")
            submenu = src.menuFolder.TextMenu.TextMenu("""
You put your head into the machine.

Its tendrils reach out and touch your implant.

It is upgraded to rank 5.
This means you can do special attacks now.""")
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)

        elif character.rank > 2:
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

            if foundEnemies:
                character.addMessage(f"promotions locked")

                submenu = src.menuFolder.TextMenu.TextMenu("""
Promotions to rank 2 are blocked.
Enemies are nearby.

Kill all enemies on this terrain, to unlock the promotions to rank 2.
""")
                character.macroState["submenue"] = submenu
                character.runCommandString("~",nativeKey=True)

                character.changed("promotion blocked",{"reason":"needs 2 clones on base"})
                return

            character.rank = 2
            character.addMessage(f"you were promoted to base commander")
            submenu = src.menuFolder.TextMenu.TextMenu("""
You put your head into the machine.

Its tendrils reach out and touch your implant.

It is upgraded to rank 2.
""")
            character.macroState["submenue"] = submenu
            character.runCommandString("~",nativeKey=True)
        character.changed("got promotion",{})

src.items.addType(Promoter)

class PathsOverlay(object):
    def apply(self,chars,terrain):
        if not terrain.hidden:
            import urwid
            grey = urwid.AttrSpec("#888","default")
            lightGrey = urwid.AttrSpec("#ccc","default")
            yellow = urwid.AttrSpec("#ff5","default")
            lightYellow = urwid.AttrSpec("#ff5","default")
            white = urwid.AttrSpec("#fff","default")
            for dualPair,path in terrain.foundPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] =  (grey,"::")

            for coordinate in terrain.watershedStart:
                chars[coordinate[1]][coordinate[0]] =  (yellow,"::")

            for path in terrain.foundSuperPathsComplete.values():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (lightGrey,"::")

            for dualPair,path in terrain.foundSuperPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (lightYellow,"::")

class QuestMarkerOverlay(object):
    def apply(self,chars,mainChar,displayChars):
        if not mainChar.room and mainChar.path:
            for item in mainChar.path:
                chars[item[1]][item[0]] = displayChars.pathMarker

class NPCsOverlay(object):
    def apply(self,chars,terrain):
        for character in terrain.characters:
            chars[character.yPosition][character.xPosition] = character.display

class MainCharOverlay(object):
    def apply(self,chars,mainChar):
        chars[mainChar.yPosition][mainChar.xPosition] =  mainChar.display



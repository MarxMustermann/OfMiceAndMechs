'''
Overlay showing the precalculated paths
'''
class PathsOverlay(object):
    '''
    add overlayed information
    '''
    def apply(self,chars,terrain):
        if not terrain.hidden:
            import urwid
            grey = urwid.AttrSpec("#777","black")
            ltgrey = urwid.AttrSpec("#999","black")
            yelow = urwid.AttrSpec("#066","black")
            ltyellow = urwid.AttrSpec("#088","black")

            # add paths
            for dualPair,path in terrain.foundPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] =  (grey,"::")

            # add intersections
            for coordinate in terrain.watershedStart:
                chars[coordinate[1]][coordinate[0]] =  (yellow,"::")

            # add important paths
            for path in terrain.foundSuperPathsComplete.values():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (ltgrey,"::")
            for dualPair,path in terrain.foundSuperPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (ltyellow,"::")

'''
Overlay showing quest marker
'''
class QuestMarkerOverlay(object):
    '''
    add overlayed information
    '''
    def apply(self,chars,mainChar,displayChars):
        if not mainChar.room and mainChar.path:
            for item in mainChar.path:
                # highlight chars on the path 
                if not chars[item[1]][item[0]] in (displayChars.pathMarker,"!!","??"):
                    import urwid
                    display = chars[item[1]][item[0]]
                    if isinstance(display, int):
                        display = displayChars.indexedMapping[chars[item[1]][item[0]]]
                    if isinstance(display, str):
                        display = (urwid.AttrSpec("default","black"),display)
                    chars[item[1]][item[0]] = (urwid.AttrSpec(display[0].foreground,"#333"),display[1])

'''
adds npcs
'''
class NPCsOverlay(object):
    '''
    add overlayed information
    '''
    def apply(self,chars,terrain):
        for character in terrain.characters:
            chars[character.yPosition][character.xPosition] = character.display

'''
adds main char
'''
class MainCharOverlay(object):
    '''
    add overlayed information
    '''
    def apply(self,chars,mainChar):
        if not mainChar.dead:
            chars[mainChar.yPosition][mainChar.xPosition] =  mainChar.display



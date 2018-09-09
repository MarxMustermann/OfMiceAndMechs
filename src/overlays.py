'''
Overlay showing the precalculated paths
bad code: path was hidden instead of disabling the overlay
'''
class PathsOverlay(object):
    '''
    add overlayed information
    '''
    def apply(self,chars,terrain):
        if not terrain.hidden:
            import urwid
            grey = urwid.AttrSpec("#666","black")

            # add paths
            for dualPair,path in terrain.foundPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] =  (grey,"::")

            # add intersections
            for coordinate in terrain.watershedStart:
                chars[coordinate[1]][coordinate[0]] =  (grey,"::")

            # add important paths
            for path in terrain.foundSuperPathsComplete.values():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (grey,"::")
            for dualPair,path in terrain.foundSuperPaths.items():
                for coordinate in path:
                    chars[coordinate[1]][coordinate[0]] = (grey,"::")

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



##########################################################################
###
##    drawing and related code should be here
#     bad code: drawstuff is everywhere
#
##########################################################################

# import basic libs
# bad code: should not be imported when using tile based display only
import urwid

"""
maps things to abstrect representation and back
"""
class Mapping(object):

    mappedThings = {}
    globalCounter = [0] # non intuitive: list to make counter same object for all instances

    """
    (re) builds the mapping
    """
    def buildMap(self):

        # get configuration
        rawConfig = self.loadMapping()
        import inspect
        self.indexedMapping = []
        raw = inspect.getmembers(rawConfig, lambda a:not(inspect.isroutine(a)))

        # map configuration entries
        for item in raw:
            # ignore internal state
            if item[0].startswith("__"):
                continue

            # convert lists to lists containing abstract ids
            if isinstance(item[1], list):
                subList = []
                counter = 0
                for subItem in item[1]:
                    # get abstract id
                    if not item[0] in self.mappedThings:
                        self.mappedThings[item[0]] = []
                    if len(self.mappedThings[item[0]])-1 < counter: 
                        while len(self.mappedThings[item[0]])-1 < counter: 
                            self.mappedThings[item[0]].append(None)
                        self.mappedThings[item[0]][counter] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    # add id to mapping
                    index = self.mappedThings[item[0]][counter]
                    self.mapToIndex(index,subItem)
                    subList.append(index)
                    counter += 1

                # set the actual attribute
                setattr(self, item[0], subList)

            # convert dicts to dicts containing abstract ids
            elif isinstance(item[1], dict):
                subDict = {}
                for k,v in item[1].items():
                    # get abstract id
                    if not item[0] in self.mappedThings: 
                        self.mappedThings[item[0]] = {}
                    if not k in self.mappedThings[item[0]]:
                        self.mappedThings[item[0]][k] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    # add id to mapping
                    index = self.mappedThings[item[0]][k]
                    subDict[k] = index
                    self.mapToIndex(index,v)

                # set the actual attribute
                setattr(self, item[0], subDict)

            # add non special entries
            else:
                # get abstract id
                if not item[0] in self.mappedThings: 
                    self.mappedThings[item[0]] = self.globalCounter[0]
                    self.globalCounter[0] += 1

                # add to mapping
                index = self.mappedThings[item[0]]
                self.mapToIndex(index,item[1])

                # set the actual attribute
                setattr(self, item[0], index)

    """
    set mapping value for an index
    """
    def mapToIndex(self,index,value):
        # ensure minimum lenght
        while len(self.indexedMapping)-1 < index:
            self.indexedMapping.append(None)

        # set the value
        self.indexedMapping[index] = value

"""
maps an abstract representation to tiles.
"""
class TileMapping(Mapping):
    """
    basic state setting
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        super().__init__()
        self.modes = {"testTiles":"","pseudeUnicode":"","testTiles2":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the tile map
    """
    def setRenderingMode(self,mode):
        # input validation
        if mode not in self.modes:
            raise Exception("tried to switch to unkown mode: "+mode)

        # set mode
        self.mode = mode

        # rebiuld abstract mapping
        self.buildMap()

    """
    fetch correct configuration for mode
    """
    def loadMapping(self):
        # bad pattern: no way to load arbitrary files
        if self.mode == "testTiles":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap as rawConfig
        if self.mode == "testTiles2":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap2 as rawConfig
        return rawConfig

"""
this maps an abstract representation to actual chars.
"""
class DisplayMapping(Mapping):
    """
    basic state setting
    bad code: hardcoded modes for now
    """
    def __init__(self,mode):
        super().__init__()
        self.modes = {"unicode":"","pureASCII":""}
        self.setRenderingMode(mode)

    """
    set the rendering mode AND recalculate the char map
    """
    def setRenderingMode(self,mode):
        # validate input
        if not mode in self.modes:
            raise Exception("tired to switch to unkown mode: "+mode)

        # set mode
        self.mode = mode

        # create the actual mapping
        self.buildMap()

    """
    fetch the config depending on the mode
    """
    def loadMapping(self):
        if self.mode == "unicode":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.displayChars as rawConfig
        elif self.mode == "pureASCII":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.displayChars_fallback as rawConfig
        return rawConfig


"""
The canvas is supposed to hold the content of a piece screen.
It is used to allow for pixel setting and to be able to cache rendered state.
Recursive canvases would be great but are not implemented yet.

bad code: actual rendering beyond the abstracted form (urwid formatting, tiles) is done here
"""
class Canvas(object):
    """
    set up state AND fill the canvas with the (default) chars
    bad code: should be split into 3 methods
    """
    def __init__(self,size=(41,41),chars=None,defaultChar="::",coordinateOffset=(0,0),shift=(0,0),displayChars=None,tileMapping=None,tileMapping2=None):
        # set basic information
        self.size = size
        self.coordinateOffset = coordinateOffset
        self.shift = shift # this should be temporary only and be solved by overlaying canvas
        self.defaultChar = defaultChar
        self.displayChars = displayChars
        self.tileMapping = tileMapping
        self.tileMapping2 = tileMapping2

        # fill the canvas with the default char
        self.chars = []
        for x in range(0,41):
            line = []
            for y in range(0,41):
                line.append(defaultChar)
            self.chars.append(line)

        # copy the supplied canvas into the current canvas
        for x in range(self.coordinateOffset[0],self.coordinateOffset[0]+self.size[0]):
            for y in range(self.coordinateOffset[1],self.coordinateOffset[1]+self.size[1]):
                if x >= 0 and y >= 0 and x <= 224 and y <= 224:
                    self.setPseudoPixel(x,y,chars[x][y])

    """
    plain and simple pseudo pixel setting
    """
    def setPseudoPixel(self,x,y,char):
        # shift coordinates
        x -= self.coordinateOffset[0]
        y -= self.coordinateOffset[1]

        # validate input
        if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
            raise Exception("painted out of bounds")

        # set pixel
        self.chars[x][y] = char

    """
    get the Canvas prepared for use with urwid,
    this basically returns urwid.AttrSpecs
    bad code: urwid specific code should be in one place not everywhere
    """
    def getUrwirdCompatible(self):
        # the to be result
        out = []

        # add newlines over the drawing area
        if self.shift[0] > 0:
            for x in range(0,self.shift[0]):
                 out.append("\n")
        
        # add rendered content to result
        for line in self.chars:

            # add spaces to the left of the drawing area
            if self.shift[1] > 0:
                for x in range(0,self.shift[1]):
                    out.append((urwid.AttrSpec("default","default"),"  "))

            # add this lines content
            for char in line:
                # render the character via the abstraction layer
                if isinstance(char, int):
                    if self.displayChars.indexedMapping[char] == None:
                        debugMessages.append("failed rendering "+str(char)+" "+str(self.displayChars.indexedMapping[char-10])+" "+str(self.displayChars.indexedMapping[char+10]))
                    else:
                        out.append(self.displayChars.indexedMapping[char])
                # render the character directly
                else:
                    out.append(char)

            # start new line
            out.append("\n")
        return out

    """
    draw the display onto a pygame display
    bad code: pygame specific code should be in one place not everywhere
    bad code: the method should return a rendered result instead of rendering directly
    """
    def setPygameDisplay(self,pydisplay,pygame,tileSize):
        # fill game area
        pydisplay.fill((0,0,0))

        # add rendered content
        # bad pattern: this rendering relies on strict top left to bottom right rendering with overlapping tiles to create perspective without having propper mechanism to enforce and control this
        counterY = 0
        for line in self.chars:
            counterX = 0
            for char in line:

                def renderText(text,colour):
                    image = pygame.image.load('config/Images/perspectiveTry/textChar.png')
                    pydisplay.blit(image,(250+counterX*(tileSize+1), 110+counterY*(tileSize+1)))

                    font = pygame.font.Font(None,12)
                    text = font.render(text, True, colour)
                    pydisplay.blit(text,(250+(counterX*(tileSize+1))+2, 110+(counterY*(tileSize+1))+8))

                # bad code: colour information is lost
                if isinstance(char, int):
                    # scale the tile
                    # bad code: rescales each tile individually and on each render
                    try:
                        # fetch image
                        image = self.tileMapping.indexedMapping[char]

                        # scale image
                        if not tileSize == 10:
                            image = pygame.transform.scale(image,(int(tileSize*(image.get_width()/10)),int(tileSize*(image.get_height()/10))))

                        # render image
                        pydisplay.blit(image,(250+counterX*(tileSize+1), 110+counterY*(tileSize+1)))
                    except:
                        if debug:
                            raise Exception("unable to scale image")
                elif isinstance(char, str):
                    renderText(char,(255, 255, 255))
                else:
                    renderText(char[1],char[0].get_rgb_values()[0:3])

                counterX += 1
            counterY += 1

        # refresh display
        pygame.display.update()

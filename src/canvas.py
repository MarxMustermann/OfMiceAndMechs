"""
drawing and related code should be here
bad code: drawstuff is everywhere
"""

# import basic libs
import src.logger

# bad code: this is unintuitive, ugly and unnecessary it should be replaced by a simpler solution
class Mapping(object):
    """
    maps things to abstract representation and back
    """

    mappedThings = {}
    globalCounter = [
        0
    ]  # non intuitive: list to make counter same object for all instances

    def buildMap(self):
        """
        (re) builds the mapping
        """

        # get configuration
        rawConfig = self.loadMapping()
        import inspect

        self.indexedMapping = []
        raw = inspect.getmembers(rawConfig, lambda a: not (inspect.isroutine(a)))

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
                    if item[0] not in self.mappedThings:
                        self.mappedThings[item[0]] = []
                    if len(self.mappedThings[item[0]]) - 1 < counter:
                        while len(self.mappedThings[item[0]]) - 1 < counter:
                            self.mappedThings[item[0]].append(None)
                        self.mappedThings[item[0]][counter] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    # add id to mapping
                    index = self.mappedThings[item[0]][counter]
                    self.mapToIndex(index, subItem)
                    subList.append(index)
                    counter += 1

                # set the actual attribute
                setattr(self, item[0], subList)

            # convert dicts to dicts containing abstract ids
            elif isinstance(item[1], dict):
                subDict = {}
                for k, v in item[1].items():
                    # get abstract id
                    if item[0] not in self.mappedThings:
                        self.mappedThings[item[0]] = {}
                    if k not in self.mappedThings[item[0]]:
                        self.mappedThings[item[0]][k] = self.globalCounter[0]
                        self.globalCounter[0] += 1

                    # add id to mapping
                    index = self.mappedThings[item[0]][k]
                    subDict[k] = index
                    self.mapToIndex(index, v)

                # set the actual attribute
                setattr(self, item[0], subDict)

            # add non special entries
            else:
                # get abstract id
                if item[0] not in self.mappedThings:
                    self.mappedThings[item[0]] = self.globalCounter[0]
                    self.globalCounter[0] += 1

                # add to mapping
                index = self.mappedThings[item[0]]
                self.mapToIndex(index, item[1])

                # set the actual attribute
                setattr(self, item[0], index)


    def mapToIndex(self, index, value):
        """
        set mapping value for an index

        Parameters:
            index: the index to set the value for
            value: the value to set
        """

        # ensure minimum length
        while len(self.indexedMapping) - 1 < index:
            self.indexedMapping.append(None)

        # set the value
        self.indexedMapping[index] = value




class TileMapping(Mapping):
    """
    maps an abstract representation to tiles.
    """

    def __init__(self, mode):
        """
        basic state setting
        bad code: hardcoded modes for now

        Parameters:
            mode: the mode to load
        """

        super().__init__()
        self.modes = {"testTiles": "", "pseudeUnicode": "", "testTiles2": ""}
        self.setRenderingMode(mode)

        # add fallback values for missing tiles
        mapping = Mapping

    def setRenderingMode(self, mode):
        """
        set the rendering mode AND recalculate the tile map

        Parameters:
            mode: the mode to load
        """

        # input validation
        if mode not in self.modes:
            raise Exception("tried to switch to unkown mode: " + mode)

        # set mode
        self.mode = mode

        # rebuild abstract mapping
        self.buildMap()

    def loadMapping(self):
        """
        load the correct mapping tile
        """

        # bad pattern: no way to load arbitrary files
        if self.mode == "testTiles":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap as rawConfig
        if self.mode == "testTiles2":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.tileMap2 as rawConfig

        self.addFallbackChars(rawConfig)

        return rawConfig

    def addFallbackChars(self,rawConfig):
        """
        add missing tiles by loading data from the tile based mode

        Parameters:
            rawConfig: the unmodified config 
        """

        # load the fallback chars
        import config.displayChars_fallback as fallback

        # add missing tiles from fallbackChars
        import inspect
        raw = inspect.getmembers(fallback, lambda a: not (inspect.isroutine(a)))
        for item in raw:
            # ignore internal state
            if item[0].startswith("__"):
                continue
        
            # skip non missing tiles
            if hasattr(rawConfig,item[0]):
                continue

            # add placholder for missing tile
            setattr(rawConfig,item[0],item[1])

"""
this maps an abstract representation to actual chars.
"""


class DisplayMapping(Mapping):
    """
    basic state setting
    bad code: hardcoded modes for now
    """

    def __init__(self, mode):
        """
        initilise own state

        Parameters:
            mode: the mode to load
        """

        super().__init__()
        self.modes = {"unicode": "", "pureASCII": ""}
        self.setRenderingMode(mode)


    def setRenderingMode(self, mode):
        """
        set the rendering mode AND recalculate the char map

        Parameters:
            mode: the mode to load
        """

        # validate input
        if mode not in self.modes:
            raise Exception("tired to switch to unkown mode: " + mode)

        # set mode
        self.mode = mode

        # create the actual mapping
        self.buildMap()

    def loadMapping(self):
        """
        fetch the config depending on the mode
        """

        if self.mode == "unicode":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.displayChars as rawConfig
        elif self.mode == "pureASCII":
            # bad code: reimport the config as library, i don't think this is a good thing to do
            import config.displayChars_fallback as rawConfig
        return rawConfig

# bad code: actual rendering beyond the abstracted form (urwid formatting, tiles) is done here
class Canvas(object):
    """
    The canvas is supposed to hold the content of a piece screen.
    It is used to allow for pixel setting and to be able to cache rendered state.
    Recursive canvases would be great but are not implemented yet.

    """

    # bad code: should be split into 3 methods
    def __init__(
        self,
        size=(81, 81),
        chars=None,
        defaultChar=None,
        coordinateOffset=(0, 0),
        shift=(0, 0),
        displayChars=None,
        tileMapping=None,
        tileMapping2=None,
    ):
        """
        set up state AND fill the canvas with the (default) chars
        """

        if defaultChar is None:
            defaultChar = displayChars.void

        # set basic information
        self.size = size
        self.coordinateOffset = coordinateOffset
        self.shift = (
            shift  # this should be temporary only and be solved by overlaying canvas
        )
        self.defaultChar = defaultChar
        self.displayChars = displayChars
        self.tileMapping = tileMapping
        self.tileMapping2 = tileMapping2

        # fill the canvas with the default char
        self.chars = []
        for x in range(0, size[0]):
            line = []
            for y in range(0, size[1]):
                line.append(defaultChar)
            self.chars.append(line)

        # copy the supplied canvas into the current canvas
        for x in range(
            self.coordinateOffset[0], self.coordinateOffset[0] + self.size[0]
        ):
            for y in range(
                self.coordinateOffset[1], self.coordinateOffset[1] + self.size[1]
            ):
                if x >= 0 and y >= 0 and x <= 224 and y <= 224:
                    try:
                        self.setPseudoPixel(x, y, chars[x][y])
                    except:
                        pass

    def setPseudoPixel(self, x, y, char):
        """
        sets a pseudo pixel on the canvas
        Parameters:
            x: the x coordinate
            y: the y coordinate 
            char: 
        """

        # shift coordinates
        x -= self.coordinateOffset[0]
        y -= self.coordinateOffset[1]

        # validate input
        if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
            raise Exception("painted out of bounds")

        # set pixel
        self.chars[x][y] = char

    def printTcod(self, console, y):

        def stringifyUrwid(inData):
            outData = ""
            for item in inData:
                if isinstance(item, tuple):
                    outData += stringifyUrwid(item[1])
                if isinstance(item, list):
                    outData += stringifyUrwid(item)
                if isinstance(item, str):
                    outData += item
            return outData

        out = []
        for line in self.chars:
            y += 1
            x = 0
            for char in line:
                mapped = None
                if isinstance(char, int):
                    mapped = self.displayChars.indexedMapping[char]
                else:
                    mapped = char

                if not isinstance(mapped, list):
                    mapped = [mapped]

                tcodPrepared = []
                for item in mapped:
                    if isinstance(item, str):
                        tcodPrepared.append(((255,255,255),item))
                    if isinstance(item, tuple):
                        tcodPrepared.append((tuple(item[0].get_rgb_values()[:3]),item[1]))

                numPrinted = 0
                for item in tcodPrepared:
                    text = item[1]
                    text = text.replace("ò","o")
                    text = text.replace("＠","@ ")
                    text = text.replace("🝆","<")
                    text = text.replace("´","'")
                    console.print(x=2*x+numPrinted,y=y,fg=item[0],string=text)
                    numPrinted += 1
                x += 1

    # bad code: urwid specific code should be in one place not everywhere
    def getUrwirdCompatible(self, warning=False):
        """
        get the Canvas prepared for use with urwid,
        this basically returns urwid.AttrSpecs

        Parameters:
            warning: flag if warning indicators should be shown
        """

        # the to be result
        out = []
        if warning:
            blank = (src.interaction.urwid.AttrSpec("default", "#f00"), "  ")
        else:
            blank = (src.interaction.urwid.AttrSpec("default", "default"), "  ")

        # add newlines over the drawing area
        if self.shift[0] > 0:
            for x in range(0, self.shift[0]):
                out.append("\n")

        # add rendered content to result
        for line in self.chars:

            # add spaces to the left of the drawing area
            if self.shift[1] > 0:
                for x in range(0, self.shift[1]):
                    out.append(blank)

            # add this lines content
            for char in line:
                # render the character via the abstraction layer
                if isinstance(char, int):
                    if self.displayChars.indexedMapping[char] is None:
                        src.logger.debugMessages.append(
                            "failed rendering "
                            + str(char)
                            + " "
                            + str(self.displayChars.indexedMapping[char - 10])
                            + " "
                            + str(self.displayChars.indexedMapping[char + 10])
                        )
                    else:
                        out.append(self.displayChars.indexedMapping[char])
                # render the character directly
                else:
                    out.append(char)

            # start new line
            out.append("\n")
        return out

    # bad code: pygame specific code should be in one place not everywhere
    # bad code: the method should return a rendered result instead of rendering directly
    def setPygameDisplay(self, pydisplay, pygame, tileSize):
        """
        draw the display onto a pygame display
        
        Parameters:
            pydisplay: the display from pygame
            pygame: the pygame itself
            tileSize: the size of the drawing area
        """

        # fill game area
        pydisplay.fill((0, 0, 0))

        # add rendered content
        # bad pattern: this rendering relies on strict top left to bottom right rendering with overlapping tiles to create perspective without having a proper mechanism to enforce and control this
        counterY = 0
        for line in self.chars:
            counterX = 0
            for char in line:

                def renderText(text, colour):
                    if text[0].isupper():
                        image = pygame.image.load(
                            "config/Images/perspectiveTry/textChar.png"
                        )
                        pydisplay.blit(
                            image,
                            (
                                250 + counterX * (tileSize + 1),
                                110 + counterY * (tileSize + 1),
                            ),
                        )
                        textOffset = (2, 8)
                    else:
                        textOffset = (3, tileSize + 1)

                    font = pygame.font.Font("config/DejaVuSansMono.ttf", 10)
                    text = font.render(text, True, colour)
                    pydisplay.blit(
                        text,
                        (
                            250 + (counterX * (tileSize + 1)) + textOffset[0],
                            110 + (counterY * (tileSize + 1)) + textOffset[1],
                        ),
                    )

                # bad code: colour information is lost
                if isinstance(char, int):
                    # scale the tile
                    # bad code: rescales each tile individually and on each render
                    try:
                        image = self.tileMapping.indexedMapping[char]
                    except:
                        image = None

                    if image:
                        try:
                            # fetch image
                            image = self.tileMapping.indexedMapping[char]

                            # scale image
                            if not tileSize == 10:
                                image = pygame.transform.scale(
                                    image,
                                    (
                                        int(tileSize * (image.get_width() / 10)),
                                        int(tileSize * (image.get_height() / 10)),
                                    ),
                                )

                            # render image
                            pydisplay.blit(
                                image,
                                (
                                    250 + counterX * (tileSize + 1),
                                    110 + counterY * (tileSize + 1),
                                ),
                            )
                        except:
                            if src.interaction.debug:
                                raise Exception("unable to scale image")
                    else:
                        try:
                            char = self.displayChars.indexedMapping[char]
                            renderText(char[1], char[0].get_rgb_values()[0:3])
                        except:
                            print(char)
                elif isinstance(char, str):
                    renderText(char, (255, 255, 255))
                else:
                    renderText(char[1], char[0].get_rgb_values()[0:3])

                counterX += 1
            counterY += 1

        # refresh display
        pygame.display.update()

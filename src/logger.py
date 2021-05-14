"""
Contains the logger.
"""

debugMessages = None


def setup(debug):
    global debugMessages

    if debug:
        """
        logger object for logging to file
        """

        class debugToFile(object):
            """
            clear file
            """

            def __init__(self):
                logfile = open("debug.log", "w")
                logfile.close()

            """
            add log message to file
            """

            def append(self, message):
                logfile = open("debug.log", "a")
                logfile.write(str(message) + "\n")
                logfile.close()

        # set debug mode
        debugMessages = debugToFile()
    else:
        """
        dummy logger
        """

        class FakeLogger(object):
            """
            discard input
            """

            def append(self, message):
                pass

        debugMessages = FakeLogger()

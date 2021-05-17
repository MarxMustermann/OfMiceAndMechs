"""
Contains the logger.
"""

debugMessages = None


def setup(debug):
    """
    set up either the real or a fake logger
    """

    global debugMessages

    if debug:

        class debugToFile(object):
            """
            logger object for logging to file
            """

            def __init__(self):
                """
                clear file
                """

                logfile = open("debug.log", "w")
                logfile.close()

            def append(self, message):
                """
                add log message to file

                Parameters:
                    message: the message to handle
                """

                logfile = open("debug.log", "a")
                logfile.write(str(message) + "\n")
                logfile.close()

        # set debug mode
        debugMessages = debugToFile()
    else:

        class FakeLogger(object):
            """
            dummy logger
            """

            def append(self, message):
                """
                discard input

                Parameters:
                    message: the message to handle
                """
                pass

        debugMessages = FakeLogger()

import configparser

global urlConfig

def setup():
    urlConfig = readConfigSection("downloader.ini", "URL")
    outputConfig = readConfigSection("downloader.ini", "OUTPUT")
    extensionsConfig = readConfigSection("downloader.ini", "EXTENSIONS")
    exceptionsConfig = readConfigSection("downloader.ini", "EXCEPTIONS")

def readConfigSection(configFile, section):
    """ Reads in the given config file and returns the requested section
    """
    config = configparser.ConfigParser()
    config.read(configFile)
    return config[section]

def getBaseURL():
    urlConfig = readConfigSection("downloader.ini", "URL")
    return urlConfig['base']

def getRetries():
    urlConfig = readConfigSection("downloader.ini", "URL")
    return urlConfig['retries']

def getMaxDepth():
    urlConfig = readConfigSection("downloader.ini", "URL")
    return urlConfig['maxDepth']

def getUserAgent():
    urlConfig = readConfigSection("downloader.ini", "URL")
    return urlConfig['user-agent']

def getOutputFolder():
    outputConfig = readConfigSection("downloader.ini", "OUTPUT")
    return outputConfig['outputFolder']

def getOutputTmpFolderPrefix():
    outputConfig = readConfigSection("downloader.ini", "OUTPUT")
    return outputConfig['outputTmpFolderPrefix']

def getMinimumFileSize():
    outputConfig = readConfigSection("downloader.ini", "OUTPUT")
    return outputConfig['minimumFileSize']

def getMinimumContentLength():
    outputConfig = readConfigSection("downloader.ini", "OUTPUT")
    return outputConfig['minimumContentLength']


import downloader,re,logging,sys,getopt
from bs4 import BeautifulSoup
from datetime import datetime


def setup_logger(logger_name, log_config, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    fileHandler = logging.FileHandler(generate_logger_name(log_config), mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

def generate_logger_name(loggingConfig):
    if loggingConfig['includeDateInName'] in ['true', 'TRUE']:
        # Find the last instance of . in the filename and add _date just before that.
        configFileName = loggingConfig['filename']
        pos = configFileName.rfind(".")
        return configFileName[:pos] + "_" + downloader.getProgramTime() + configFileName[pos:]
    else:
        return loggingConfig['filename']

def printHelpOptions():
    print ("Usage:")
    print ("  python3 testDownloader.py")
    print ("  python3 testDownloader.py -h -c <configuration file location> -i -r")
    print ("")
    print ("Options:")
    print ("  -h --help \t\t Show this screen.")
    print ("  -c --config \t\t Set the location of the configuration file to use.")
    print ("  -i --images \t\t Download images only (i.e. don't navigate to other pages.")
    print ("  -r --regenerate \t (Re)Generate the index.htm file for all of the generated output locations.")

def main(argv):
    configFile = "downloader.ini"
    imagesOnly = 'false'
    
    try:
        opts,args = getopt.getopt(argv,"hciro:",["help", "config", "images", "regenerate"])
    except getopt.GetoptError:
        printHelpOptions()
        sys.exit(2)
    
    for opt in opts:
        if (opt[0] == '-h' or opt[0] == '--help'):
            printHelpOptions()
            sys.exit(0)
        if (opt[0] == '-c'):
            print("Configuration file defined, using: "+opt[1])
            configFile = opt[1]
        if (opt[0] == '-i'):
        	print("Downloading images only.")
        	imagesOnly = 'true'
        if (opt[0] == '-r'):
        	print("Regenerating all HTML.")
        	downloader.regenerateAllHTML()
        	sys.exit(0)
    
    loggingConfig = downloader.readConfigSection(configFile, "LOGGER")
    accessloggingConfig = downloader.readConfigSection(configFile, "ACCESSLOGGER")
    setup_logger('debug', loggingConfig)
    setup_logger('access', accessloggingConfig)
    logger = logging.getLogger('debug')

    urlConfig = downloader.readConfigSection(configFile, "URL")
    outputConfig = downloader.readConfigSection(configFile, "OUTPUT")
    extensionsConfig = downloader.readConfigSection(configFile, "EXTENSIONS")
    exceptionsConfig = downloader.readConfigSection(configFile, "EXCEPTIONS")
    
    startTime = datetime.now()
    print("Starting at: "+str(startTime))
    logger.info("Starting at: "+str(startTime))

    downloadUrl = urlConfig['base']
    retries = int(urlConfig['retries'])

    result = downloader.downloadRequests3(downloadUrl)
    if result == None:
        logging.error("URL ("+downloadUrl+") returns an error")
        sys.exit()
    soup = BeautifulSoup(result, "html.parser")

    # Downloads the images:
    downloader.downloadDepth(soup, downloadUrl, urlConfig, outputConfig, extensionsConfig, exceptionsConfig, 0, imagesOnly)
    if outputConfig['downloadVideos'] in ['true','TRUE']:
        downloader.get_videos(soup, downloadUrl, outputConfig, exceptionsConfig)
    if outputConfig['outputHTML'] in ['true','TRUE']:
        downloader.outputHTML(downloader.getOutputFolder(outputConfig))

    endTime = datetime.now()
    print("Complete at: "+str(endTime))
    print("Total time was: "+str(endTime - startTime))
    print("Pages requested: "+str(downloader.getPages()))
    print("Total downloads: "+str(downloader.getDownloads()))
    print("Total saves: "+str(downloader.getSaved()))
    print("Final URL cache size: "+str(downloader.getCacheSize()))
    logger.info("Complete at: "+str(endTime))
    logger.info("Total time was: "+str(endTime - startTime))
    logger.info("Pages requested: "+str(downloader.getPages()))
    logger.info("Total downloads: "+str(downloader.getDownloads()))
    logger.info("Total saves: "+str(downloader.getSaved()))
    logger.info("Final URL cache size: "+str(downloader.getCacheSize()))

if '__main__' == __name__:
    main(sys.argv[1:])
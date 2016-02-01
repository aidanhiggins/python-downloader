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


def main(argv):
    configFile = "downloader.ini"
    try:
        opts,args = getopt.getopt(argv,"hc:",["help", "config"])
    except getopt.GetoptError:
        print ("Usage : python3 test_requests_download_logger.py -c <configuration file> or python3 test_requests_download_logger.py")
        sys.exit(2)
    
    for opt in opts:
        if (opt[0] == '-h' or opt[0] == '--help'):
            print ("Usage : python3 test_requests_download_logger.py -c <configuration file> or python3 test_requests_download_logger.py")
        if (opt[0] == '-c'):
            print("Configuration file defined, using: "+opt[1])
            configFile = opt[1]
    
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
    downloader.downloadDepth(soup, downloadUrl, urlConfig, outputConfig, extensionsConfig, exceptionsConfig, 0)
    if outputConfig['downloadVideos'] in ['true','TRUE']:
        downloader.get_videos(soup, downloadUrl, outputConfig, exceptionsConfig)

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
import urllib.parse,urllib.request,urllib3.exceptions
import shutil,os,configparser,logging,sys,requests
import downloaderConfig
from bs4 import BeautifulSoup
from datetime import datetime
from yattag import Doc, indent
from PIL import Image

urlsCache = set()
logger = logging.getLogger('debug')
accesslogger = logging.getLogger('access')
programTime = ''
outputFolder = ''


def downloadRequests3(url):
    if (url in urlsCache):
        logger.info("Cache Hit for: "+url)
        return None
    else:
        urlsCache.add(url)
        logger.info("urlsCache updated, current size: "+str(len(urlsCache)))

    try:
        pages() # log a counter of a page being requested
        r = requests.get(url.strip())
        printAccessLog(str(r.status_code), r.headers, url)
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            logger.error("error response code: "+str(r.status_code)+" for URL: "+url)
            return None
            
    except requests.exceptions.ConnectionError as e1:
        logger.error("A ConnectionError occurred while requesting "+url)
        logError(e1)
    except requests.exceptions.TooManyRedirects as e2:
        logger.error("A TooManyRedirects occurred while requesting "+url)
        logError(e2)
        
def downloadRequestsImage3(imgUrl, refererUrl, outputConfig):
    """ Downloads a single image using the Requests package
    """
    if (imgUrl in urlsCache):
        logger.info("Cache Hit for: "+imgUrl)
        return None
    else:
        urlsCache.add(imgUrl)
        logger.info("urlsCache updated, current size: "+str(len(urlsCache)))
        
    if imgUrl != None:
        file_name = buildLocalFilename(imgUrl)
        if file_name != "":
            # retries = urllib3.util.retry.Retry(connect=5, read=2, redirect=5) # todo: fix hardcoding
            # req = urllib3.PoolManager(retries=retries)
            downloads() # log a counter of a download being made
            headers = {'user-agent': downloaderConfig.getUserAgent(), 'referer': refererUrl}
            try:
                resp = requests.get(imgUrl.strip(), headers=headers)
                printAccessLog(str(resp.status_code), resp.headers, imgUrl)
                if resp.status_code != requests.codes.ok:
                    logger.error("error response code: "+str(resp.status_code)+" for image URL: "+imgUrl)
                    return None
                
                if 'Content-Length' in resp.headers and resp.headers['Content-Length'] != None:
                    if (int(resp.headers['Content-Length']) < int(outputConfig['minimumContentLength'])):
                        logger.info("Image Content-Length is less than the minimum ("+outputConfig['minimumContentLength']+")")
                        return None
                    else:
                        urllib.request.urlretrieve(imgUrl, buildTmpFileOutputLocation(outputConfig['outputTmpFolderPrefix'], \
                            getOutputFolder(outputConfig), file_name))
                        logger.debug("image saved("+resp.headers['Content-Type']+"), filename: "+file_name)
                else:
                    logger.error("Content-Length == None for URL: "+imgUrl)
            except requests.exceptions.ConnectionError as e1:
                logger.error("A ConnectionError occurred while requesting "+imgUrl)
                logError(e1)
            except requests.exceptions.TooManyRedirects as e2:
                logger.error("A TooManyRedirects occurred while requesting "+imgUrl)
                logError(e2)
            except urllib.error.HTTPError as e3:
                logger.error("A urllib.error.HTTPError occurred while requesting "+imgUrl)
                logError(e3)

def downloadRequestsVideo3(videoUrl, videoType, refererUrl, outputConfig):
    """ Downloads a single video using the Requests package
    """
    if (videoUrl in urlsCache):
        logger.info("Cache Hit for: "+videoUrl)
        return None
    else:
        urlsCache.add(videoUrl)
        logger.info("urlsCache updated, current size: "+str(len(urlsCache)))
        
    if videoUrl != None:
        file_name = buildLocalFilename(videoUrl)
        if file_name != "":
            file_name = file_name + '.' + videoType
            # retries = urllib3.util.retry.Retry(connect=5, read=2, redirect=5) # todo: fix hardcoding
            # req = urllib3.PoolManager(retries=retries)
            downloads() # log a counter of a download being made
            headers = {'user-agent': downloaderConfig.getUserAgent(), 'referer': refererUrl}
            try:
                resp = requests.get(videoUrl.strip(), headers=headers)
                printAccessLog(str(resp.status_code), resp.headers, videoUrl)
                if resp.status_code != requests.codes.ok:
                    logger.error("error response code: "+str(resp.status_code)+" for video URL: "+videoUrl)
                    return None
                
                if 'Content-Length' in resp.headers and resp.headers['Content-Length'] != None:
                    if (int(resp.headers['Content-Length']) < int(outputConfig['minimumContentLength'])):
                        logger.info("Image Content-Length is less than the minimum ("+outputConfig['minimumContentLength']+")")
                        return None
                    else:
                        urllib.request.urlretrieve(videoUrl, buildTmpFileOutputLocation(outputConfig['outputTmpFolderPrefix'], \
                            getOutputFolder(outputConfig), file_name))
                        logger.debug("video saved("+resp.headers['Content-Type']+"), filename: "+file_name)
                else:
                    logger.error("Content-Length == None for URL: "+videoUrl)
            except requests.exceptions.ConnectionError as e1:
                logger.error("A ConnectionError occurred while requesting "+videoUrl)
                logError(e1)
            except requests.exceptions.TooManyRedirects as e2:
                logger.error("A TooManyRedirects occurred while requesting "+videoUrl)
                logError(e2)

def get_images(soup, baseUrl, outputConfig, exceptionsConfig):
    images = [img for img in soup.findAll('img')]
    logger.info(str(len(images)) + " images found.")
    logger.info('Downloading images to \''+getOutputFolder(outputConfig)+'\'')
    #compile our unicode list of image links
    image_links = [each.get('src') for each in images]
    
    for each in image_links:
        if each != None:
            if not isURLBlacklisted(exceptionsConfig, each):
                file_name = buildLocalFilename(each)
                if file_name != "":
    		        # todo: Only do this if it doesn't already contain http
                    fullyQualifiedName = buildFullyQualifiedURL(each,baseUrl)
                    result = downloadRequestsImage3(fullyQualifiedName, baseUrl, outputConfig)
                    if (result == None):
                        logger.debug("Failing image request. Printing imageUrl ("+each+") and baseUrl ("+baseUrl+")")
    # Check whether the file is the minimum size and copies it if it meets the minimum size
    tmpFileLocation = buildTmpFileOutputLocation(outputConfig['outputTmpFolderPrefix'], getOutputFolder(outputConfig), "")
    copyCounter = 0
    for eachImage in os.listdir(tmpFileLocation):
        imgFile = tmpFileLocation+eachImage
        if (os.path.getsize(imgFile) > (int(outputConfig['minimumFileSize'])*1000)):
            logger.info("File " + imgFile + " is greater than " + str(outputConfig['minimumFileSize']) + "k")
            # Copy the file to the actual location
            saved() # log a counter of a object being moved
            os.makedirs(getOutputFolder(outputConfig), exist_ok=True)
            shutil.move(imgFile, getOutputFolder(outputConfig)+eachImage)
            copyCounter += 1
    # Delete the file
    shutil.rmtree(tmpFileLocation)
    logger.info("Temporary files and folder deleted.")
    logger.info(str(copyCounter)+" images saved.")
    return image_links

def get_videos(soup, baseUrl, outputConfig, exceptionsConfig):
    localheaders = {'User-Agent': downloaderConfig.getUserAgent()}

    with requests.Session() as session:
        session.headers = localheaders

        try:
            localresponse = session.get(baseUrl)
            localsoup = BeautifulSoup(localresponse.content, "html.parser")

            # follow the iframe url
            iframes = localsoup.findAll('iframe', src=True)

            for soup_iframe in iframes:
                src = soup_iframe['src']
                if src:
                    iframeResponse = session.get(soup_iframe['src'], headers={'Referer': baseUrl})
                    iframeSoup = BeautifulSoup(iframeResponse.content, "html.parser")
                    iframeSources = [source for source in iframeSoup.findAll('source')]

                    for iframeSourceLink in iframeSources:
                        pos = iframeSourceLink['type'].rfind('/')
                        type = iframeSourceLink['type'][:pos]
                        extension = iframeSourceLink['type'][pos+1:]
                        if type == 'video':
                            result = downloadRequestsVideo3(iframeSourceLink['src'], extension, baseUrl, outputConfig)
        except requests.exceptions.ConnectionError as e1:
            logger.error("A ConnectionError occurred.")
            logError(e1)
        except requests.exceptions.TooManyRedirects as e2:
            logger.error("A TooManyRedirects occurred.")
            logError(e2)
        except urllib.error.HTTPError as e3:
            logger.error("A urllib.error.HTTPError occurred.")
            logError(e3)
        except requests.exceptions.MissingSchema as e4:
            logger.error("A requests.exceptions.MissingSchema occurred.")
            logError(e4)
        
        # Check whether the file is the minimum size and copies it if it meets the minimum size
        tmpFileLocation = buildTmpFileOutputLocation(outputConfig['outputTmpFolderPrefix'], getOutputFolder(outputConfig), "")
        copyCounter = 0
        for eachVideo in os.listdir(tmpFileLocation):
            videoFile = tmpFileLocation+eachVideo
            if (os.path.getsize(videoFile) > (int(outputConfig['minimumFileSize'])*1000)):
                logger.info("File " + videoFile + " is greater than " + str(outputConfig['minimumFileSize']) + "k")
                # Copy the file to the actual location
                saved() # log a counter of a object being moved
                os.makedirs(getOutputFolder(outputConfig), exist_ok=True)
                shutil.move(videoFile, getOutputFolder(outputConfig)+eachVideo)
                copyCounter += 1
        # Delete the file
        shutil.rmtree(tmpFileLocation)
        logger.info("Temporary files and folder deleted.")
        logger.info(str(copyCounter)+" videos saved.")
        

def downloadDepth(soup, downloadUrl, urlConfig, outputConfig, extensionsConfig, exceptionsConfig, currentDepth, imagesOnly):
    print("CurrentDepth: "+str(currentDepth))
    if not isURLBlacklisted(exceptionsConfig, downloadUrl): 
        imageResults = get_images(soup, downloadUrl, outputConfig, exceptionsConfig)
        linkResults = get_links(soup, downloadUrl, outputConfig)
    for url in linkResults:
        if not isURLBlacklisted(exceptionsConfig, url): 
            if checkURLContainsExtension(extensionsConfig, url):

                downloadRequestsImage3(url, downloadUrl, outputConfig)
            else:
                urlResult = downloadRequests3(url)
                if urlResult == None:
                    logger.error("URL ("+url+") returns an error, continuing")
                else: 
                    urlSoup = BeautifulSoup(urlResult, "html.parser")
                    urlImageResults = get_images(urlSoup, url, outputConfig, exceptionsConfig)
                    if(imagesOnly in ['false', 'FALSE'] and currentDepth < int(urlConfig['maxDepth'])):
                        downloadDepth(urlSoup, url, urlConfig, outputConfig, extensionsConfig, exceptionsConfig, currentDepth+1, 'false')

def get_links(soup, baseUrl, outputConfig):
    urls = []
    links = [href for href in soup.findAll('a')]
    logger.info(str(len(links)) + " links found.")
    #compile our unicode list of image links
    allLinks = [each.get('href') for each in links]
    
    for each in allLinks:
        if each != None:
            urls.append(buildFullyQualifiedURL(each, baseUrl))
    return urls

def buildFullyQualifiedURL(srcName, baseUrl):
    if "http" not in srcName:
        return urllib.parse.urljoin(baseUrl,srcName)
    return srcName

def buildLocalFilename(url):
    fileName=url.split('/')[-1]
    if "?" in fileName:
        fileName = fileName[0:fileName.find("?")]
    if "&" in fileName:
        fileName = fileName[0:fileName.find("&")]
    if fileName == "":
        logger.error("local filename shortened from \""+url+"\" to \""+fileName+"\"")
        return fileName
    if url != fileName:
        logger.debug("local filename shortened from \""+url+"\" to \""+fileName+"\"")
    return fileName

def buildFileOutputLocation(directory, fileName):
    """ Takes the given directory, creates it and returns the new filename location
    """
    os.makedirs(directory, exist_ok=True)
    return directory + fileName

def buildTmpFileOutputLocation(prefix, directory, fileName):
    """ Takes the given directory and prepends the tmp directory prefix to it, and then creates it
    if it doesn't already exist
    """
    # Check whether the location contains /
    slashLocation = directory.find("/")
    if (slashLocation == -1):
        tmpDir = prefix+directory
    else:
        tmpDir = directory[0:slashLocation+1]+prefix+directory[slashLocation+1:len(directory)]
    os.makedirs(tmpDir, exist_ok=True)
    return tmpDir + fileName

def readConfigSection(configFile, section):
    """ Reads in the given config file and returns the requested section
    """
    config = configparser.ConfigParser()
    config.read(configFile)
    return config[section]

def checkURLContainsExtension(extensionConfig, url):
    """ Checks whether any of the extensions from the config file exist in the given url
    """
    for type in extensionConfig:
        # Return true if it ends with one of the extensions, and debug log it
        if url.endswith(extensionConfig[type]):
            logger.info("url ("+url+") ends with "+extensionConfig[type])
            return True
        # Return true if it exists with a '?' after it, and debug log it
        updExt = extensionConfig[type] + "?"
        if updExt in url:
            logger.info("url ("+url+") contains "+updExt)
            return True
    return False

def isURLBlacklisted(exceptionsConfig, url):
    """ Checks whether the given URL contains any of the blacklisted exceptions
    """
    #print("Processing isURLBlacklisted for url: "+url)
    for blacklistUrl in exceptionsConfig:
        # Return true if the url contains the blacklisted snippet
        if exceptionsConfig[blacklistUrl] in url:
            logger.info("Given URL ("+url+") contains "+exceptionsConfig[blacklistUrl])
            return True
    return False

def outputHTML(downloadFolder):
    #downloadFolder = getOutputFolder(outputConfig)
    videos = ('.mp4','.webm')
    #downloadFolder = './images_20160214_2129/'
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text('Any old title')
            with tag('style'):
                text('body { background-color: black; }')
                text('h1 { color: maroon; margin-left: 40px; } ')
                text('img.displayed { display: block; margin-left: auto; margin-right: auto }')
                text('video.displayed { display: block; margin-left: auto; margin-right: auto }')
        with tag('body'):
            for eachItem in os.listdir(downloadFolder):
                if (eachItem.endswith(videos)):
                    doc.asis('<video width="540" class="displayed" controls><source src="'+eachItem+'" ></video>')
                    #with tag('video', width='540', klass='displayed', src=eachItem):
                    #with tag('video', width='540', klass='displayed'):
                    #    doc.stag('source', src=eachItem)
                    doc.stag('br')
                elif (not eachItem.startswith('.')):
                    image = os.path.join(downloadFolder, eachItem)
                    try:
                        img = Image.open(image)
                        width,height = img.size
                        outputWidth, outputHeight = calculateImgOutputSizes(width,height)
                        with tag('a', href=eachItem):
                            doc.stag('img', style="width:"+str(outputWidth)+"px; height:"+str(outputHeight)+"px;)", klass='displayed', src=eachItem)
                            doc.stag('br')
                    except:
                        logger.error("An error occurred while processing "+image+". Skipping.")
    
    with open(downloadFolder+'index.htm', 'a') as out: out.write(indent(doc.getvalue(), indent_text = True))
    print('HTML saved to '+downloadFolder+'index.htm')
    logger.info('HTML saved to '+downloadFolder+'index.htm')

def regenerateAllHTML():
    # Generate the correct download folder
    downloadFolder = '.'
    # list all folders that match the name format in downloader.ini
    for eachItem in os.listdir(downloadFolder):
        # print(os.path.join(downloadFolder, eachItem))
        eachItem = os.path.join(downloadFolder, eachItem)
        if (os.path.isdir(eachItem)):
            # for each folder, check if it has an index.htm
            fileToProcess = os.path.join(eachItem, "index.htm")
            if (checkIfFolderMatchesOutputConfigPattern(eachItem) in ['true', 'TRUE']):
                # print("index.htm exists in "+eachItem+", deleting")
                #checkIfFolderMatchesOutputConfigPattern(eachItem)
                if (os.path.isfile(fileToProcess)):
                    os.remove(fileToProcess)
                outputHTML(eachItem+"/")

def checkIfFolderMatchesOutputConfigPattern(folder):
    configOutFolderFormat = downloaderConfig.getOutputFolder()
    # remove trailing slash
    configOutFolderFormat = configOutFolderFormat[0:len(configOutFolderFormat)-1]
    # check if the passed folder starts with this
    if (folder.startswith(configOutFolderFormat)):
        return 'true'
    else:
        return 'false'

def calculateImgOutputSizes(width,height):
    """ Calculates the image output width and height based on a configurage max width
    """
    maxOutputWidth = 540 # TODO: read from config
    if (width > maxOutputWidth):
        divider = width / maxOutputWidth
        outputHeight = height / divider
        return (maxOutputWidth, outputHeight)
    else:
        # If it's already smaller, we don't need to modify it
        return (width,height)
    

def printAccessLog(statusCode, headers, url):
    contentLength = '-'
    contentType = '-'
    if ('Content-Length' in headers):
        contentLength = headers['Content-Length']
    if ('Content-Type' in headers):
        contentType = headers['Content-Type']
    
    accesslogger.info(statusCode+" "+contentLength+" "+contentType+" "+url)

def getProgramTime():
    """ Checks whether a unique system time has been generated and generates and returns it
    """
    global programTime
    if programTime == '':
        programTime = datetime.strftime(datetime.now(), '%Y%m%d_%H%M')
    return programTime

def getOutputFolder(outputConfig):
    """ Checks whether the output folder has been set and generates (if required) and returns it
    """
    global outputFolder
    if outputFolder == '':
        if outputConfig['includeDateInOutputName'] in ['true', 'TRUE']:
            # Add the date to the name
            outputFolderName = outputConfig['outputFolder']
            pos = outputFolderName.rfind("/")
            outputFolder = outputFolderName[:pos] + "_" + getProgramTime() + outputFolderName[pos:]
        else:
            outputFolder = outputConfig['outputFolder']
    return outputFolder

def getCacheSize():
    return len(urlsCache)

def logError(error):
    if error != None and error.args != None and len(error.args) > 0:
        logger.error("Error {0}".format(str(error.args[0])))

# Counters for stats
def pages():
    pages.counter += 1

def downloads():
    downloads.counter += 1

def saved():
    saved.counter += 1

def getPages():
    return pages.counter

def getDownloads():
    return downloads.counter

def getSaved():
    return saved.counter

pages.counter = 0
downloads.counter = 0
saved.counter = 0

